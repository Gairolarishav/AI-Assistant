from django.db import models

# Create your models here.
class ChatConversations(models.Model):
    user_id = models.CharField(max_length=255)
    chat = models.JSONField()  # entire session turns list
    quote_requested = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Chat Conversation"
    
class VoiceConversations(models.Model):
    user_id = models.CharField(max_length=255)
    duration = models.CharField(max_length=20)  # e.g. "01:00"
    audio_file = models.URLField(blank=True, help_text="URL to call recording")
    chat = models.JSONField()  # entire session turns list
    quote_requested = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Voice Conversation"
    
class QuoteRequest(models.Model):
    chat = models.ForeignKey(
        'ChatConversations',  # or use ChatConversations directly if it's already imported
        on_delete=models.CASCADE,
        related_name='quote_requests'
    )
    source = models.CharField(max_length=255,default='Chat')
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_no = models.CharField(max_length=20)
    post_code = models.CharField(max_length=20)
    product_id = models.CharField(max_length=255)
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    decoration_requested = models.BooleanField(default=False)
    decoration_mode = models.CharField(max_length=255, blank=True, null=True) 
    decoration_mode_id = models.PositiveIntegerField(blank=True, null=True)              
    color_size = models.CharField(max_length=100, blank=True, null=True)            
    color_size_id = models.PositiveIntegerField(blank=True, null=True)
    delivery_time =  models.CharField(max_length=255, blank=True, null=True)     
    quote_status = models.CharField(max_length=100, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Quote Request"

class FAQ(models.Model):
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'faq'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"FAQ: {self.question[:50]}..."
