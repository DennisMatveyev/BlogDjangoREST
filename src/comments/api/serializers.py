from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import (ModelSerializer,
                                        HyperlinkedIdentityField,
                                        SerializerMethodField)

from accounts.api.serializers import UserDetailSerializer
from comments.models import Comment

User = get_user_model()


def create_comment_serializer(model_type='post', slug=None, parent_id=None, user=None):
    class CommentCreateSerializer(ModelSerializer):
        class Meta:
            model = Comment
            fields = ['id', 'content', 'timestamp']

        def __init__(self, *args, **kwargs):
            self.model_type = model_type
            self.slug = slug
            self.parent_obj = None
            if parent_id:
                parent_qs = Comment.objects.filter(id=parent_id)
                if parent_qs.exists() and parent_id.count() == 1:
                    self.parent_obj = parent_qs.first()
            super(CommentCreateSerializer, self).__init__(*args, **kwargs)

        def validate(self, data):
            model_type = self.model_type
            model_qs = ContentType.objects.filter(model=model_type)
            if not model_qs.exists() or model_qs.count() != 1:
                raise ValidationError('This is not a valid content type.')

            SomeModel = model_qs.first().model_class()   # Post model in our case
            obj_qs = SomeModel.objects.filter(slug=self.slug)
            if not obj_qs.exists() or obj_qs.count() != 1:
                raise ValidationError('This is not a valid slug for this content type.')

            return data

        def create(self, validated_data):
            content = validated_data.get('content')
            if user:
                main_user = user
            else:
                main_user = User.objects.first()
            model_type = self.model_type
            slug = self.slug
            parent_obj = self.parent_obj
            comment = Comment.objects.create_by_model_type(model_type=model_type, slug=slug,
                                                                 content=content, user=main_user, parent_obj=parent_obj)
            return comment

    return CommentCreateSerializer


class CommentListSerializer(ModelSerializer):
    url = HyperlinkedIdentityField(view_name='comments-api:thread')
    reply_count = SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['url', 'id', 'content', 'reply_count', 'timestamp']

    def get_reply_count(self, obj):
        if obj.is_parent:
            return obj.children().count()
        return 0


class CommentChildSerializer(ModelSerializer):
    user = UserDetailSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['user', 'id', 'content', 'timestamp']


class CommentDetailSerializer(ModelSerializer):
    user = UserDetailSerializer(read_only=True)
    replies = SerializerMethodField()
    reply_count = SerializerMethodField()
    content_object_url = SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['user', 'id', 'content', 'replies',
                  'reply_count', 'timestamp', 'content_object_url']
        read_only_fields = ['replies', 'reply_count']

    def get_content_object_url(self, obj):
        try:
            return obj.content_object.get_api_url()
        except:
            return None

    def get_replies(self, obj):
        if obj.is_parent:
            return CommentChildSerializer(obj.children(), many=True).data
        return None

    def get_reply_count(self, obj):
        if obj.is_parent:
            return obj.children().count()
        return 0
