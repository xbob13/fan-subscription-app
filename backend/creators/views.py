from django.shortcuts import render
from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Creator, CreatorSocialLinks
from .serializers import (
    CreatorSerializer,
    CreatorCreateSerializer,
    CreatorUpdateSerializer,
    CreatorListSerializer,
    CreatorSocialLinksSerializer
)

# Create your views here.

class CreatorListView(generics.ListAPIView):
    """Public list of creators for discovery"""
    serializer_class = CreatorListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_adult_content']
    search_fields = ['display_name', 'description', 'user__username']
    ordering_fields = ['subscriber_count', 'created_at', 'total_posts']
    ordering = ['-subscriber_count']
    
    def get_queryset(self):
        queryset = Creator.objects.filter(is_active=True)
        
        # Filter adult content based on user age verification
        if not (self.request.user.is_authenticated and self.request.user.is_age_verified):
            queryset = queryset.filter(is_adult_content=False)
        
        return queryset

class CreatorDetailView(generics.RetrieveAPIView):
    """Public creator profile view"""
    serializer_class = CreatorSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'id'
    
    def get_queryset(self):
        queryset = Creator.objects.filter(is_active=True)
        
        # Filter adult content based on user age verification
        if not (self.request.user.is_authenticated and self.request.user.is_age_verified):
            queryset = queryset.filter(is_adult_content=False)
        
        return queryset

class CreatorCreateView(generics.CreateAPIView):
    """Create creator profile (requires user to be creator type)"""
    serializer_class = CreatorCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        user = self.request.user
        
        # Check if user is creator type
        if user.account_type != 'creator':
            user.account_type = 'creator'
            user.save()
        
        # Check if creator profile already exists
        if hasattr(user, 'creator_profile'):
            from rest_framework import serializers
            raise serializers.ValidationError("Creator profile already exists")
        
        serializer.save(user=user)

class CreatorUpdateView(generics.RetrieveUpdateAPIView):
    """Update creator profile (only by creator themselves)"""
    serializer_class = CreatorUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        try:
            return self.request.user.creator_profile
        except Creator.DoesNotExist:
            raise generics.Http404("Creator profile not found")
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = CreatorSerializer(instance)
        return Response(serializer.data)

class CreatorSocialLinksView(generics.RetrieveUpdateAPIView):
    """Manage creator social links"""
    serializer_class = CreatorSocialLinksSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        try:
            creator = self.request.user.creator_profile
            social_links, created = CreatorSocialLinks.objects.get_or_create(creator=creator)
            return social_links
        except Creator.DoesNotExist:
            raise generics.Http404("Creator profile not found")

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def featured_creators(request):
    """Get featured creators for homepage"""
    creators = Creator.objects.filter(
        is_active=True,
        subscriber_count__gte=100  # Minimum subscribers to be featured
    ).order_by('-subscriber_count')[:6]
    
    # Filter adult content for non-verified users
    if not (request.user.is_authenticated and request.user.is_age_verified):
        creators = creators.filter(is_adult_content=False)
    
    serializer = CreatorListSerializer(creators, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def trending_creators(request):
    """Get trending creators based on recent activity"""
    # This is a simplified version - in production, you'd calculate based on
    # recent subscriber growth, engagement, etc.
    creators = Creator.objects.filter(
        is_active=True
    ).order_by('-total_posts', '-subscriber_count')[:10]
    
    # Filter adult content for non-verified users
    if not (request.user.is_authenticated and request.user.is_age_verified):
        creators = creators.filter(is_adult_content=False)
    
    serializer = CreatorListSerializer(creators, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def categories(request):
    """Get all content categories"""
    from django.conf import settings
    return Response([
        {'key': key, 'label': label}
        for key, label in settings.CONTENT_CATEGORIES
    ])
