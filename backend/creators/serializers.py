from rest_framework import serializers
from .models import Creator, CreatorSocialLinks
from accounts.serializers import UserSerializer

class CreatorSocialLinksSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreatorSocialLinks
        fields = '__all__'
        read_only_fields = ['creator']

class CreatorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    social_links = CreatorSocialLinksSerializer(read_only=True)
    earnings_after_fee = serializers.ReadOnlyField()
    
    class Meta:
        model = Creator
        fields = [
            'id', 'user', 'display_name', 'category', 'cover_image',
            'description', 'subscription_price', 'subscriber_count',
            'total_posts', 'total_earnings', 'earnings_after_fee',
            'is_active', 'accepts_tips', 'allows_messages',
            'is_adult_content', 'created_at', 'social_links'
        ]
        read_only_fields = [
            'id', 'user', 'subscriber_count', 'total_posts',
            'total_earnings', 'created_at'
        ]

class CreatorCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Creator
        fields = [
            'display_name', 'category', 'cover_image', 'description',
            'subscription_price', 'accepts_tips', 'allows_messages',
            'is_adult_content'
        ]
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class CreatorUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Creator
        fields = [
            'display_name', 'category', 'cover_image', 'description',
            'subscription_price', 'accepts_tips', 'allows_messages',
            'is_adult_content'
        ]

class CreatorListSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Creator
        fields = [
            'id', 'user', 'display_name', 'category', 'cover_image',
            'description', 'subscription_price', 'subscriber_count',
            'total_posts', 'is_adult_content', 'created_at'
        ]