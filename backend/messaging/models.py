from django.db import models
from django.conf import settings
from django.utils import timezone

class Conversation(models.Model):
    """A conversation between a creator and a subscriber"""
    creator = models.ForeignKey(
        'creators.Creator',
        on_delete=models.CASCADE,
        related_name='conversations'
    )
    subscriber = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conversations'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Last message info for quick access
    last_message_at = models.DateTimeField(null=True, blank=True)
    last_message_preview = models.CharField(max_length=100, blank=True)
    
    # Read status
    creator_last_read = models.DateTimeField(null=True, blank=True)
    subscriber_last_read = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['creator', 'subscriber']
        ordering = ['-last_message_at', '-updated_at']
    
    def __str__(self):
        return f"Conversation: {self.creator.display_name} <-> {self.subscriber.username}"
    
    def get_unread_count(self, user):
        """Get unread message count for a user"""
        if user == self.creator.user:
            last_read = self.creator_last_read or timezone.datetime.min.replace(tzinfo=timezone.utc)
        else:
            last_read = self.subscriber_last_read or timezone.datetime.min.replace(tzinfo=timezone.utc)
        
        return self.messages.filter(created_at__gt=last_read).count()

class Message(models.Model):
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('tip', 'Tip Notification'),
    ]
    
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, default='text')
    content = models.TextField(blank=True)
    
    # For media messages
    media_file = models.FileField(upload_to='messages/', null=True, blank=True)
    media_thumbnail = models.ImageField(upload_to='message_thumbnails/', null=True, blank=True)
    
    # For tip notifications
    tip_amount = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Message status
    is_deleted = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        if self.message_type == 'tip':
            return f"Tip: ${self.tip_amount} from {self.sender.username}"
        return f"{self.sender.username}: {self.content[:50]}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Update conversation's last message info
        self.conversation.last_message_at = self.created_at
        if self.message_type == 'tip':
            self.conversation.last_message_preview = f"Tip: ${self.tip_amount}"
        else:
            self.conversation.last_message_preview = self.content[:100]
        self.conversation.save(update_fields=['last_message_at', 'last_message_preview'])

class MessageReadStatus(models.Model):
    """Track when messages are read by recipients"""
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='read_status'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    read_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['message', 'user']
    
    def __str__(self):
        return f"{self.user.username} read message at {self.read_at}"
