from django.db import models
from django.conf import settings
from django.utils import timezone

class Post(models.Model):
    POST_TYPE_CHOICES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('mixed', 'Mixed Media'),
    ]
    
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('subscribers', 'Subscribers Only'),
        ('premium', 'Premium Subscribers'),
    ]
    
    creator = models.ForeignKey(
        'creators.Creator',
        on_delete=models.CASCADE,
        related_name='posts'
    )
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    post_type = models.CharField(max_length=20, choices=POST_TYPE_CHOICES, default='text')
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='subscribers')
    
    # Engagement
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    
    # Metadata
    is_pinned = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_pinned', '-created_at']
    
    def __str__(self):
        return f"{self.creator.display_name}: {self.title or self.content[:50]}"
    
    def can_view(self, user):
        """Check if user can view this post"""
        if self.visibility == 'public':
            return True
        
        if not user.is_authenticated:
            return False
            
        if user == self.creator.user:
            return True
            
        # Check subscription
        from subscriptions.models import Subscription
        return Subscription.objects.filter(
            subscriber=user,
            creator=self.creator,
            status='active'
        ).exists()

class Media(models.Model):
    MEDIA_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
    ]
    
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='media'
    )
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPE_CHOICES)
    file = models.FileField(upload_to='content/')
    thumbnail = models.ImageField(upload_to='thumbnails/', null=True, blank=True)
    
    # Metadata
    file_size = models.PositiveIntegerField(null=True, blank=True)  # in bytes
    duration = models.PositiveIntegerField(null=True, blank=True)  # in seconds for video/audio
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return f"{self.get_media_type_display()} for {self.post}"

class PostLike(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'post']
    
    def __str__(self):
        return f"{self.user.username} likes {self.post}"

class Comment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField(max_length=500)
    
    # For nested comments
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.user.username}: {self.content[:50]}"
