from rest_framework import generics, permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from config.permissions import IsSuperAdmin

from .models import User
from .serializers import RegisterSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        message = (
            'Registration received. Your admin account is pending approval by a super admin.'
            if user.role == User.Role.ADMIN
            else 'Registration successful.'
        )
        return Response(
            {'user': UserSerializer(user).data, 'detail': message},
            status=status.HTTP_201_CREATED,
        )


class RoleAwareTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['is_approved'] = user.is_approved
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        if user.role == User.Role.ADMIN and not user.is_approved:
            raise serializers.ValidationError(
                'Your admin account is still pending approval by a super admin.'
            )
        data['user'] = UserSerializer(user).data
        return data


class LoginView(TokenObtainPairView):
    serializer_class = RoleAwareTokenObtainPairSerializer


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class PendingVendorListView(generics.ListAPIView):
    """Super admin: list admin accounts awaiting approval."""

    serializer_class = UserSerializer
    permission_classes = [IsSuperAdmin]

    def get_queryset(self):
        return User.objects.filter(role=User.Role.ADMIN, is_approved=False)


class ApproveVendorView(APIView):
    permission_classes = [IsSuperAdmin]

    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk, role=User.Role.ADMIN)
        except User.DoesNotExist:
            return Response({'detail': 'Admin user not found.'}, status=status.HTTP_404_NOT_FOUND)
        user.is_approved = True
        user.save(update_fields=['is_approved'])
        return Response(UserSerializer(user).data)

    def delete(self, request, pk):
        try:
            user = User.objects.get(pk=pk, role=User.Role.ADMIN, is_approved=False)
        except User.DoesNotExist:
            return Response({'detail': 'Pending admin user not found.'}, status=status.HTTP_404_NOT_FOUND)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
