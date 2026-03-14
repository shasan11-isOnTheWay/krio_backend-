from django.contrib import admin
from .models import Profile, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'is_staff', 'is_admin']
    list_filter = ['is_staff', 'is_admin']
    search_fields = ['email']
    ordering = ['email']

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'age', 'gender']
    list_filter = ['age', 'gender']
    search_fields = ['name', 'user__email']