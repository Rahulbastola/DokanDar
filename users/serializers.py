from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'is_approved', 'phone', 'date_joined',
        ]
        read_only_fields = ['role', 'is_approved', 'date_joined']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    # Self-registration is limited to "user" and "admin" (pending approval).
    # "super_admin" accounts can only be created via createsuperuser / the admin site.
    role = serializers.ChoiceField(
        choices=[(User.Role.USER, User.Role.USER.label), (User.Role.ADMIN, User.Role.ADMIN.label)],
        default=User.Role.USER,
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'phone', 'role']

    def create(self, validated_data):
        role = validated_data.pop('role', User.Role.USER)
        password = validated_data.pop('password')
        user = User(role=role, **validated_data)
        user.set_password(password)
        user.is_approved = role != User.Role.ADMIN
        user.save()
        return user
