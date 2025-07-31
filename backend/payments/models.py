from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal

class Tip(models.Model):
    """One-time tips from subscribers to creators"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    tipper = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tips_sent'
    )
    creator = models.ForeignKey(
        'creators.Creator',
        on_delete=models.CASCADE,
        related_name='tips_received'
    )
    
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    message = models.TextField(max_length=500, blank=True)
    
    # Stripe details
    stripe_payment_intent_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Platform fee calculation
    platform_fee = models.DecimalField(max_digits=6, decimal_places=2)
    creator_amount = models.DecimalField(max_digits=6, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"${self.amount} tip from {self.tipper.username} to {self.creator.display_name}"
    
    def save(self, *args, **kwargs):
        if not self.platform_fee:
            self.platform_fee = self.amount * Decimal(settings.PLATFORM_FEE_PERCENTAGE / 100)
            self.creator_amount = self.amount - self.platform_fee
        super().save(*args, **kwargs)

class Earning(models.Model):
    """Track all earnings for creators from subscriptions and tips"""
    EARNING_TYPE_CHOICES = [
        ('subscription', 'Subscription'),
        ('tip', 'Tip'),
        ('bonus', 'Bonus'),
    ]
    
    creator = models.ForeignKey(
        'creators.Creator',
        on_delete=models.CASCADE,
        related_name='earnings'
    )
    
    earning_type = models.CharField(max_length=20, choices=EARNING_TYPE_CHOICES)
    gross_amount = models.DecimalField(max_digits=8, decimal_places=2)
    platform_fee = models.DecimalField(max_digits=8, decimal_places=2)
    net_amount = models.DecimalField(max_digits=8, decimal_places=2)
    
    # Reference to related objects
    subscription = models.ForeignKey(
        'subscriptions.Subscription',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    tip = models.OneToOneField(
        Tip,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    
    # Payout status
    is_paid_out = models.BooleanField(default=False)
    payout_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.creator.display_name}: ${self.net_amount} ({self.get_earning_type_display()})"

class Payout(models.Model):
    """Weekly payouts to creators"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    creator = models.ForeignKey(
        'creators.Creator',
        on_delete=models.CASCADE,
        related_name='payouts'
    )
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Date range for this payout
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Stripe details
    stripe_transfer_id = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Metadata
    earnings_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['creator', 'period_start', 'period_end']
    
    def __str__(self):
        return f"Payout: ${self.amount} to {self.creator.display_name} ({self.period_start} - {self.period_end})"

class PaymentMethod(models.Model):
    """Store user payment methods (cards, etc.)"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payment_methods'
    )
    
    # Stripe details
    stripe_payment_method_id = models.CharField(max_length=255, unique=True)
    
    # Card details (for display)
    brand = models.CharField(max_length=20)  # visa, mastercard, etc.
    last4 = models.CharField(max_length=4)
    exp_month = models.PositiveIntegerField()
    exp_year = models.PositiveIntegerField()
    
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        return f"{self.brand.title()} **** {self.last4} ({self.user.username})"

class Transaction(models.Model):
    """Log all financial transactions"""
    TRANSACTION_TYPE_CHOICES = [
        ('subscription_payment', 'Subscription Payment'),
        ('tip_payment', 'Tip Payment'),
        ('payout', 'Creator Payout'),
        ('refund', 'Refund'),
        ('chargeback', 'Chargeback'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    
    transaction_type = models.CharField(max_length=30, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Stripe details
    stripe_transaction_id = models.CharField(max_length=255, blank=True)
    
    # References
    subscription = models.ForeignKey(
        'subscriptions.Subscription',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    tip = models.ForeignKey(
        Tip,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    payout = models.ForeignKey(
        Payout,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_transaction_type_display()}: ${self.amount} ({self.user.username})"
