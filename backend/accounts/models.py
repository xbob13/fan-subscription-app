from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class User(AbstractUser):
    ACCOUNT_TYPE_CHOICES = [
        ('creator', 'Creator'),
        ('subscriber', 'Subscriber'),
    ]
    
    account_type = models.CharField(
        max_length=20,
        choices=ACCOUNT_TYPE_CHOICES,
        default='subscriber'
    )
    email = models.EmailField(unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    is_age_verified = models.BooleanField(default=False)
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        null=True,
        blank=True
    )
    bio = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Stripe customer ID for payment processing
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    
    # For creators
    stripe_account_id = models.CharField(max_length=255, blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return f"{self.username} ({self.get_account_type_display()})"
    
    @property
    def is_creator(self):
        return self.account_type == 'creator'
    
    @property
    def is_subscriber(self):
        return self.account_type == 'subscriber'
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    
    # Privacy settings
    show_subscriber_count = models.BooleanField(default=True)
    show_earnings = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
