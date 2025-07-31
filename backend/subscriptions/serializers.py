from rest_framework import serializers
from .models import Subscription, SubscriptionHistory
from creators.serializers import CreatorListSerializer
from accounts.serializers import UserSerializer

class SubscriptionSerializer(serializers.ModelSerializer):
    creator = CreatorListSerializer(read_only=True)
    subscriber = UserSerializer(read_only=True)
    is_active = serializers.ReadOnlyField()
    days_remaining = serializers.ReadOnlyField()
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'subscriber', 'creator', 'stripe_subscription_id',
            'status', 'price', 'created_at', 'current_period_start',
            'current_period_end', 'cancelled_at', 'is_active', 'days_remaining'
        ]
        read_only_fields = [
            'id', 'subscriber', 'stripe_subscription_id', 'created_at'
        ]

class SubscriptionCreateSerializer(serializers.Serializer):
    creator_id = serializers.IntegerField()
    payment_method_id = serializers.CharField(max_length=255)
    
    def validate_creator_id(self, value):
        from creators.models import Creator
        try:
            creator = Creator.objects.get(id=value, is_active=True)
            return creator
        except Creator.DoesNotExist:
            raise serializers.ValidationError("Creator not found or inactive")
    
    def validate(self, attrs):
        creator = attrs['creator_id']
        subscriber = self.context['request'].user
        
        # Check if subscription already exists
        if Subscription.objects.filter(subscriber=subscriber, creator=creator).exists():
            raise serializers.ValidationError("Already subscribed to this creator")
        
        # Check if trying to subscribe to own content
        if creator.user == subscriber:
            raise serializers.ValidationError("Cannot subscribe to your own content")
        
        return attrs

class SubscriptionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionHistory
        fields = '__all__'

class MySubscriptionsSerializer(serializers.ModelSerializer):
    creator = CreatorListSerializer(read_only=True)
    is_active = serializers.ReadOnlyField()
    days_remaining = serializers.ReadOnlyField()
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'creator', 'status', 'price', 'created_at',
            'current_period_end', 'is_active', 'days_remaining'
        ]