from rest_framework.serializers import (ModelSerializer,
                                        HyperlinkedIdentityField,
                                        SerializerMethodField)

from accounts.api.serializers import UserDetailSerializer
from posts.models import Post
from comments.models import Comment
from comments.api.serializers import CommentListSerializer


class PostListSerializer(ModelSerializer):
    url = HyperlinkedIdentityField(
        view_name='posts-api:detail',
        lookup_field='slug'
    )
    # delete_url = HyperlinkedIdentityField(
    #     view_name='posts-api:delete',
    #     lookup_field='slug'
    # )
    user = UserDetailSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ['url', 'user', 'title', 'publish']    # 'delete_url',


class PostCreateUpdateSerializer(ModelSerializer):
    class Meta:
        model = Post
        fields = ['title', 'content', 'publish']


class PostDetailSerializer(ModelSerializer):
    user = UserDetailSerializer(read_only=True)
    image = SerializerMethodField()
    comments = SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'title', 'slug', 'content',
                  'publish', 'user', 'image', 'comments']

    def get_image(self, obj):
        try:
            image = obj.image.url
        except:
            image = None
        return image

    def get_comments(self, obj):
        comments_qs = Comment.objects.filter_by_instance(obj)
        comments = CommentListSerializer(comments_qs, many=True).data
        return comments
