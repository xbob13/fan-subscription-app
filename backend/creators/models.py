from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Creator(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='creator_profile'
    )
    display_name = models.CharField(max_length=100)
    category = models.CharField(
        max_length=20,
        choices=settings.CONTENT_CATEGORIES,
        default='lifestyle'
    )
    cover_image = models.ImageField(
        upload_to='creator_covers/',
        null=True,
        blank=True
    )
    description = models.TextField(max_length=1000, blank=True)
    
    # Subscription settings
    subscription_price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=9.99,
        validators=[MinValueValidator(4.99), MaxValueValidator(49.99)]
    )
    
    # Stats
    subscriber_count = models.PositiveIntegerField(default=0)
    total_posts = models.PositiveIntegerField(default=0)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Settings
    is_active = models.BooleanField(default=True)
    accepts_tips = models.BooleanField(default=True)
    allows_messages = models.BooleanField(default=True)
    
    # Age verification for adult content
    is_adult_content = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.display_name} (@{self.user.username})"
    
    @property
    def earnings_after_fee(self):
        """Calculate earnings after platform fee"""
        platform_fee = (settings.PLATFORM_FEE_PERCENTAGE / 100) * self.total_earnings
        return self.total_earnings - platform_fee

class CreatorSocialLinks(models.Model):
    creator = models.OneToOneField(
        Creator,
        on_delete=models.CASCADE,
        related_name='social_links'
    )
    website = models.URLField(blank=True)
    twitter = models.CharField(max_length=100, blank=True)
    instagram = models.CharField(max_length=100, blank=True)
    youtube = models.CharField(max_length=100, blank=True)
    tiktok = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.creator.display_name}'s Social Links"
