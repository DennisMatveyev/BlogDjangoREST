import uuid
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer, EmailField, CharField

User = get_user_model()


class UserDetailSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']


class UserCreateSerializer(ModelSerializer):
    email = EmailField(label='Email')
    email2 = EmailField(label='Confirm Email')

    class Meta:
        model = User
        fields = ['username', 'email', 'email2', 'password']
        extra_kwargs = {'password':
                            {'write_only': True}
                        }

    def validate(self, data):
        email = data['email']
        user = User.objects.filter(email=email)
        if user.exists():
            raise ValidationError('User with this email already exists.')
        return data

    def validate_email2(self, value):
        data = self.get_initial()
        email1 = data.get('email')
        email2 = value
        if email1 != email2:
            raise ValidationError('Emails must match.')
        return value

    def create(self, validated_data):
        username = validated_data['username']
        password = validated_data['password']
        email = validated_data['email']
        user_obj = User(username=username, email=email)
        user_obj.set_password(password)
        user_obj.save()
        return validated_data


class UserLoginSerializer(ModelSerializer):
    token = CharField(allow_blank=True, read_only=True)
    username = CharField(required=False, allow_blank=True)
    email = EmailField(label='Email', required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'token']
        extra_kwargs = {'password':
                            {'write_only': True}
                        }

    def validate(self, data):
        user_obj = None
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        if not email and not username:
            raise ValidationError('A username or email is required to log in.')

        user = User.objects.filter(
            Q(username=username) |
            Q(email=email)
        ).distinct()
        user = user.exclude(email__isnull=True).exclude(email__iexact='')
        if user.exists() and user.count() == 1:
            user_obj = user.first()
        else:
            raise ValidationError('This username/email is not valid.')

        if user_obj:
            if not user_obj.check_password(password):
                raise ValidationError('Incorrect password.')

        data['token'] = uuid.uuid4()

        return data
















