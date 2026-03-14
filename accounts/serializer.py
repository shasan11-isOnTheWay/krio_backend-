from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Profile, User
from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'name', 'age', 'gender', 'address', 'phone']
        read_only_fields = ['id']  # Prevent ID modification

    def update(self, instance, validated_data):
        # Update profile fields dynamically
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
    
class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'profile']
        extra_kwargs = {'password': {'write_only': True}}  # Security: never return password

    def create(self, validated_data):
        # Uses UserManager's create_user to hash passwords
        profile_data = validated_data.pop('profile', None)
        user = User.objects.create_user(**validated_data)
        if profile_data:
            Profile.objects.create(user=user, **profile_data)
        return user

    def update(self, instance, validated_data):
        # Handles email/password updates + nested profile
        profile_data = validated_data.pop('profile', None)
        if 'password' in validated_data:
            instance.set_password(validated_data.pop('password'))
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if profile_data:
            profile = instance.profile if hasattr(instance, 'profile') else None
            serializer = UserProfileSerializer(profile, data=profile_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=instance)
        return instance
        
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if user and user.is_active:
            return user
        raise serializers.ValidationError('Invalid credentials')
    

class RegisterSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    phone_number = serializers.CharField(required=True, max_length=15)
    password = serializers.CharField(required=True, write_only=True, min_length=8)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def validate_phone_number(self, value):
        if Profile.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Phone number already exists.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password']
        )
        Profile.objects.create(
            user=user,
            name=validated_data['name'],
            phone=validated_data['phone_number']
        )
        return user
    
class GoogleAuthSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate(self, data):
        try:
            idinfo = id_token.verify_oauth2_token(
                data['token'],
                requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )

            email = idinfo['email']
            return {"email": email}

        except Exception:
            raise serializers.ValidationError("Invalid Google token")