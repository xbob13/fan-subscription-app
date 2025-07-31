from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class Subscription(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
        ('pending', 'Pending'),
    ]
    
    subscriber = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    creator = models.ForeignKey(
        'creators.Creator',
        on_delete=models.CASCADE,
        related_name='subscribers'
    )
    
    # Stripe subscription details
    stripe_subscription_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Pricing
    price = models.DecimalField(max_digits=6, decimal_places=2)
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['subscriber', 'creator']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.subscriber.username} -> {self.creator.display_name}"
    
    @property
    def is_active(self):
        return (
            self.status == 'active' and 
            self.current_period_end > timezone.now()
        )
    
    @property
    def days_remaining(self):
        if self.is_active:
            return (self.current_period_end - timezone.now()).days
        return 0

class SubscriptionHistory(models.Model):
    """Track subscription changes and billing history"""
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='history'
    )
    
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('renewed', 'Renewed'),
        ('cancelled', 'Cancelled'),
        ('reactivated', 'Reactivated'),
        ('expired', 'Expired'),
        ('payment_failed', 'Payment Failed'),
    ]
    
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    amount = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    stripe_invoice_id = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.subscription} - {self.get_action_display()}"
