from django.db import models
from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Creates a regular user after validating email and normalizing it.
        """
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)  # Hashes the password automatically
        user.save(using=self._db)
        return user
    def create_staffuser(self, email, password=None):
        user = self.create_user(email,
                password=password
        )
        user.is_staff = True
        user.save(using=self._db)
        
        return user
    def create_superuser(self, email, password=None):
        user = self.create_user(email,
                password=password
        )
        user.is_staff = True
        user.is_admin = True
        user.save(using=self._db)
        
        return user
    
    
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)  # Replaces username
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Admin site access
    is_admin = models.BooleanField(default=False)  # Custom admin flag
    objects = UserManager()  # Uses the custom manager
    USERNAME_FIELD = 'email'  # Login identifier
    def __str__(self):
        return self.email


    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, if admin
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, if admin
        return self.is_admin  
    

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, unique=True)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    def __str__(self):
          return self.user.email