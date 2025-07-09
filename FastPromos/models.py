from django.db import models

# Create your models here.
class ChatConversations(models.Model):
    user_id = models.CharField(max_length=255, verbose_name="User ID")
    chat = models.JSONField()  # entire session turns list
    quote_requested = models.BooleanField(default=False, verbose_name="Quote Requested")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    class Meta:
        verbose_name = "Chat Conversation"
    
class VoiceConversations(models.Model):
    user_id = models.CharField(max_length=255, verbose_name="User ID")
    duration = models.CharField(max_length=20)  # e.g. "01:00"
    audio_file = models.URLField(blank=True, help_text="URL to call recording", verbose_name="Audio File")
    chat = models.JSONField()  # entire session turns list
    quote_requested = models.BooleanField(default=False, verbose_name="Quote Requested")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    class Meta:
        verbose_name = "Voice Conversation"
    
class QuoteRequest(models.Model):
    chat = models.ForeignKey(
        'ChatConversations',  # or use ChatConversations directly if it's already imported
        on_delete=models.CASCADE,
        related_name='quote_requests',
        verbose_name="Chat ID"
    )
    source = models.CharField(max_length=255,default='Chat')
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_no = models.CharField(max_length=20, verbose_name="Phone No.")
    post_code = models.CharField(max_length=20, verbose_name="Postcode")
    product_id = models.CharField(max_length=255, verbose_name="Product ID")
    product_name = models.CharField(max_length=255, verbose_name="Product Name")
    quantity = models.PositiveIntegerField()
    decoration_requested = models.BooleanField(default=False, verbose_name="Decoration Requested")
    decoration_mode = models.CharField(max_length=255, blank=True, null=True, verbose_name="Decoration Mode") 
    decoration_mode_id = models.PositiveIntegerField(blank=True, null=True, verbose_name="Decoration Mode ID")              
    color_size = models.CharField(max_length=100, blank=True, null=True, verbose_name="Color/Size")            
    color_size_id = models.PositiveIntegerField(blank=True, null=True, verbose_name="Color/Size ID")
    delivery_time =  models.CharField(max_length=255, blank=True, null=True, verbose_name="Delivery Time")     
    quote_status = models.CharField(max_length=100, default='pending', verbose_name="Quote Status")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

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
