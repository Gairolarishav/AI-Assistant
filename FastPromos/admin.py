from django.contrib import admin
from .models import ChatConversations, VoiceConversations, QuoteRequest
from django.utils.html import format_html
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.template.loader import render_to_string
from django.urls import reverse

class MyAdminSite(admin.AdminSite):

    def index(self, request, extra_context=None):
        # Add your custom data here
        # Initialize extra_context
        extra_context = extra_context or {}

        # Inside your index method...
        today = timezone.now().date()

        # 1️⃣ Total conversations today (Chat + Voice)
        total_conversations_today = (
            ChatConversations.objects.filter(created_at__date=today).count() +
            VoiceConversations.objects.filter(created_at__date=today).count()
        )

        # 2️⃣ Quote requests today
        quote_requests_today = QuoteRequest.objects.filter(created_at__date=today).count()

        # 3️⃣ Quotes sent today (assuming quote_status = 'sent')
        quotes_sent_today = QuoteRequest.objects.filter(
            created_at__date=today, quote_status='sent'
        ).count()

        # Add to your context
        extra_context.update({
            'total_conversations_today': total_conversations_today,
            'quote_requests_today': quote_requests_today,
            'quotes_sent_today': quotes_sent_today,
        })

        return super().index(request, extra_context)

# Register your admin site
custom_admin_site = MyAdminSite(name='myadmin')
custom_admin_site.register(User, UserAdmin)
custom_admin_site.register(Group, GroupAdmin)

class ChatConversationsAdmin(admin.ModelAdmin):
    list_display = ('id', 'short_chat','quote_requested', 'view_transcript','created_at')
    # search_fields = ('id',)
    # list_filter = ('quote_requested', 'created_at')
    list_display_links = None 
    readonly_fields = ('id','chat', 'view_transcript','quote_requested', 'created_at')

    def has_add_permission(self, request):
        return False  # no add

    def has_change_permission(self, request, obj=None):
        return False  # no edit
    
    def short_chat(self, obj):
        if not obj.chat:
            return "-"
        
        preview_lines = []
        for turn in obj.chat[:2]:  # Get first 2 turns
            text = turn['text']
            words = text.split()
            snippet = ' '.join(words[:5])
            if len(words) > 5:
                snippet += ' ...'
            preview_lines.append(f"<strong>{turn['source']}:</strong> {snippet}")

        return format_html("<br>".join(preview_lines))

    short_chat.short_description = "Chat"

    def view_transcript(self, obj):
        return format_html(

            '<a href="javascript:void(0);" class="btn btn-sm btn-primary" onclick="openTranscriptModal(\'{}\')">View</a>',
            obj.id
        )
    view_transcript.short_description = 'View Transcription'

class VoiceConversationsAdmin(admin.ModelAdmin):
    list_display = ('id', 'duration', 'quote_requested', 'created_at')
    # search_fields = ('id', 'duration')
    # list_filter = ('quote_requested', 'created_at')
    list_display_links = None  # Only 'name' will be clickable
    readonly_fields = ('duration', 'audio_file', 'chat', 'quote_requested', 'created_at')

    def has_add_permission(self, request):
        return False  # no add

    def has_change_permission(self, request, obj=None):
        return False  # no edit

class QuoteRequestAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'chat_id_column' ,'name', 'email', 'phone_no','post_code','product_name',
        'delivery_time','quote_status_badge','view_more_column','view_quotation_column'   
    )
    # list_display_links = ('chat_id_column',)  # Only 'name' will be clickable
    readonly_fields = ('created_at', 'updated_at')

    def chat_id_column(self, obj):
        if obj.chat_id:
            # Build link to changelist with filter
            url = (
                reverse('admin:FastPromos_chatconversations_changelist')
                + f"?id__exact={obj.chat_id}"
            )
            return format_html('<a href="{}">{}</a>', url, obj.chat_id)
        return "-"
    chat_id_column.short_description = "Chat ID"

    def quote_status_badge(self, obj):
        status = obj.quote_status.lower()
        colors = {
            'pending': 'orange',
            'generated': 'green',
            'not generated': 'red',
            'in progress': 'blue',
            # add more statuses if needed
        }
        color = colors.get(status, 'gray')
        return format_html(
            '<span style="background-color:{}; color:white; padding:2px 6px; border-radius:4px; font-weight:bold;">{}</span>',
            color,
            obj.quote_status.capitalize()
        )
    quote_status_badge.short_description = "Quote Status"
    quote_status_badge.admin_order_field = 'quote_status'
    
    def view_more_column(self, obj):
        return render_to_string("admin/quote_request_modal.html", {"obj": obj})
    view_more_column.short_description = "More"
    
    def view_quotation_column(self, obj):
        return render_to_string("admin/quotation_modal.html", {"obj": obj})
    view_quotation_column.short_description = "Quotation"

    def has_add_permission(self, request):
        return False  # no add, only edit existing

from django.http import HttpResponseRedirect
from django.contrib import messages
class QuotationAdmin(admin.ModelAdmin):
    change_list_template = "admin/quotations_changelist.html"
    list_display = (
        'id', 'quote_request_id_column' ,'quote_number', 'quantity', 'quote_status_badge','decoration_requested','base_unit_price',
        'decoration_unit_price','no_placement','setup_fee', 'total_decoration_cost','total_setup_cost','decoration_total'
        ,'all_in_unit_cost','final_unit_cost','total_cost'
        
    )
    readonly_fields = ('created_at', 'updated_at')

    def quote_request_id_column(self, obj):
        if obj.quote_request_id:
            # Build link to changelist with filter
            url = (
                reverse('admin:FastPromos_quoterequest_changelist')
                + f"?id__exact={obj.quote_request_id}"
            )
            return format_html('<a href="{}">{}</a>', url, obj.quote_request_id)
        return "-"
    quote_request_id_column.short_description = "Quote Request ID"
    
    def view_more_column(self, obj):
        return render_to_string("admin/quote_request_modal.html", {"obj": obj})
    view_more_column.short_description = "More"

    def changelist_view(self, request, extra_context=None):
        if 'generate' in request.GET:
            pending_requests = QuoteRequest.objects.filter(quote_status='not generated')
            created = []
            for qr in pending_requests:
                create_quotation_from_request(qr)
                qr.quote_status = 'generated'
                qr.save()
                created.append(qr.id)

            self.message_user(request, f"✅ Created {len(created)} quotations.")
            return HttpResponseRedirect(request.path)

        return super().changelist_view(request, extra_context=extra_context)
    
    def quote_status_badge(self, obj):
        status = obj.quote_status.lower()
        colors = {
            'pending': 'orange',
            'sent': 'green',
            'not generated': 'red',
            'in progress': 'blue',
            # add more statuses if needed
        }
        color = colors.get(status, 'gray')
        return format_html(
            '<span style="background-color:{}; color:white; padding:2px 6px; border-radius:4px; font-weight:bold;">{}</span>',
            color,
            obj.quote_status.capitalize()
        )
    quote_status_badge.short_description = "Quote Status"
    quote_status_badge.admin_order_field = 'quote_status'

    def has_add_permission(self, request):
        return False  # no add, only edit existing

# Remove the @admin.register decorators and register with custom site instead
custom_admin_site.register(ChatConversations, ChatConversationsAdmin)
custom_admin_site.register(VoiceConversations, VoiceConversationsAdmin)
custom_admin_site.register(QuoteRequest, QuoteRequestAdmin)
custom_admin_site.register(Quotation, QuotationAdmin)
