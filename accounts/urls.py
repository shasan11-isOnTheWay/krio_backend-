from .views import RegisterView, UserLoginView, UserProfileView, UserUpdateView, UserLogoutView, GoogleAuthView
from django.urls import path


urlpatterns = [
    path('register/', RegisterView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('logout/', UserLogoutView.as_view(), name='user-logout'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('profile/update/', UserUpdateView.as_view(), name='user-update'),
    path('google/', GoogleAuthView.as_view(), name='google-auth'),
]
