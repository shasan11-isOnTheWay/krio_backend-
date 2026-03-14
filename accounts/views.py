from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from .serializer import UserSerializer, UserLoginSerializer, RegisterSerializer, GoogleAuthSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()

class RegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]  # Public: no token needed

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        refresh = RefreshToken.for_user(user)  # Generate JWT tokens
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        })
        

class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
  
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class UserUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

class UserLogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Must be logged in to logout

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            token = RefreshToken(refresh_token)
            token.blacklist()  # Revoke token
            return Response({"detail": "Logout successful"})
        except Exception as e:
            return Response({"detail": str(e)}, status=400)
        
class GoogleAuthView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = GoogleAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']

        user, created = User.objects.get_or_create(email=email)
        
        if created:
            Profile.objects.create(user=user, name=email.split('@')[0], phone=None)  # Create profile for new user
        


        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "new_user": created
        })