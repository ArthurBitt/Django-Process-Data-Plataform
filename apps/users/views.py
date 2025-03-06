from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework import status

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone

from .serializers import (
    UserCreateSerializer,
    UserLoginSerializer,
    UserRetrieveSerializer,
    UserUpdateSerializer,
    UserInactivateSerializer,
    UserActivateSerializer
)

from .models import User


class IsStaffOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow staff or admin users to access the view.
    """
    def has_permission(self, request, view):
        return request.user.is_staff or request.user.is_superuser

class ListUsers(ListAPIView):
    """
    View for listing all users.
    :permission_classes: Only authenticated staff or admin users can access this view.
    """
    permission_classes = [IsAuthenticated, IsStaffOrAdmin]
    serializer_class = UserRetrieveSerializer
    pagination_class = PageNumberPagination
    queryset = User.objects.all()

    def get(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        if not response.data['results']:
            response.data['message'] = 'No users found'
        return response

class LoginView(APIView):
    """
    View for user login.
    :permission_classes: Allow any user (unauthenticated) to access this view.
    :param email: User's email (required).
    :param password: User's password (required).
    """
    permission_classes = [AllowAny]
    @staticmethod
    def post(request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            try:
                user = User.objects.get(email=email)
            except ObjectDoesNotExist:
                return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
            try:
                if not user.is_active:
                    return Response({'message': 'User is inactive'}, status=status.HTTP_401_UNAUTHORIZED)
            except ObjectDoesNotExist:
                return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

            if not user.check_password(password):
                return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])

            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SignUpView(APIView):
    """
    View for user registration.
    :permission_classes: Allow any user (unauthenticated) to access this view.
    :param email: User's email (required).
    :param password: User's password (required).
    :param first_name: User's first name (optional).
    :param last_name: User's last name (optional).
    """
    permission_classes = [AllowAny]
    @staticmethod
    def post(request, *args, **kwargs):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateUser(APIView):
    """
    View for updating user information.
    :permission_classes: Only authenticated staff or admin users can access this view.
    :param id: User's ID (required).
    :param email: User's email (optional).
    :param first_name: User's first name (optional).
    :param last_name: User's last name (optional).
    """
    permission_classes = [IsAuthenticated, IsStaffOrAdmin]

    @staticmethod
    def put(request, id, *args, **kwargs):
        serializer = UserUpdateSerializer(
            data=request.data,
            context={'id': id, 'request': request}
        )

        if serializer.is_valid():
            user = serializer.validated_data['user']
            # Atualiza os campos recebidos
            for field, value in serializer.validated_data.items():
                if field != 'user':
                    setattr(user, field, value)
            user.username = user.email # mantling the user creation username logic
            user.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class InactivateUser(APIView):
    """
    View for inactivating a user.
    :permission_classes: Only authenticated staff or admin users can access this view.
    :param id: User's ID (required).
    """
    @staticmethod
    def delete(request, id, *args, **kwargs):
        serializer = UserInactivateSerializer(
            data={},
            context={'id': id, 'request': request}
        )

        if serializer.is_valid():
            user = serializer.validated_data['user']
            user.is_active = False
            user.save()
            return Response({'message': 'User sucessfully inactivated!'}, status=status.HTTP_204_NO_CONTENT)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ActivateUser(APIView):
    """
    View for activating a user.
    :permission_classes: Only authenticated staff or admin users can access this view.
    :param id: User's ID (required).
    """
    @staticmethod
    def put(request, id, *args, **kwargs):
        serializer = UserActivateSerializer(
            data={},
            context={'id': id, 'request': request}
        )

        if serializer.is_valid():
            user = serializer.validated_data['user']
            user.is_active = True
            user.save()
            return Response({'message': 'User sucessfully activated!'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RecoverPassword(APIView):
    permission_classes = [AllowAny]

    @staticmethod
    def get(request):
        return render(request, 'recover_password.html')

    @staticmethod
    def post(request):
        try:
            user = User.objects.get(email=request.data['email'])
            user.forgot_password(user=user)
            messages.success(request, 'Uma nova senha foi enviada para o seu email.')
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, 'Este email não está registrado.')
            return redirect('recover_password')
        except Exception as e:
            messages.error(request, f"Erro ao recuperar a senha: {e}")
            return redirect('recover_password')

