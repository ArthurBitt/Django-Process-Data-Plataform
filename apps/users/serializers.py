from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from apps.users.models import User


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        # api request can create only staff and common users - to create admin need to use django admin
        # in this implemantation username always will be email
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'password', 'is_staff']
        read_only_fields = ['id']
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': False, 'allow_blank': True},
            'password': {'write_only': True, 'required': True},
            'is_staff': {'default': False, 'required': False},
        }

    def create(self, validated_data):
        if 'username' not in validated_data or not validated_data['username']:
            validated_data['username'] = validated_data.get('email')

        password = validated_data.pop('password')
        user = User(**validated_data)
        error = user.check_password_strength(password=password)
        if error:
            raise serializers.ValidationError({'password': error})

        user.set_password(password) # encrypted password
        user.save()
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

class UserRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'is_active', 'is_superuser', 'is_staff']
        read_only_fields = ['id', 'email', 'username', 'first_name', 'last_name', 'is_active', 'is_superuser', 'is_staff']

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']

    def validate(self, attrs):
        id = self.context.get('id')
        try:
            user = User.objects.get(id=id)
        except ObjectDoesNotExist:
            raise serializers.ValidationError({'detail': 'User not found'})

        if not user.is_active:
            raise serializers.ValidationError({'detail': 'This user is not activated'})

        attrs['user'] = user
        return attrs

class UserInactivateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id']
        read_only_fields = ['id']

    def validate(self, attrs):
        # Recupera o id do contexto
        id = self.context.get('id')
        try:
            user = User.objects.get(id=id)
        except ObjectDoesNotExist:
            raise serializers.ValidationError({'detail': ['User not found']})

        if not user.is_active:
            raise serializers.ValidationError({'detail': ['User already inactivated']})

        # Adiciona o usuário validado aos atributos
        attrs['user'] = user
        return attrs

class UserActivateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id']
        read_only_fields = ['id']

    def validate(self, attrs):
        # Recupera o id do contexto
        id = self.context.get('id')
        try:
            user = User.objects.get(id=id)
        except ObjectDoesNotExist:
            raise serializers.ValidationError({'detail': ['User not found']})

        if user.is_active:
            raise serializers.ValidationError({'detail': ['User already Activated']})

        # Adiciona o usuário validado aos atributos
        attrs['user'] = user
        return attrs
