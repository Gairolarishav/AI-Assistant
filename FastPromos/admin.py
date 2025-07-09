from django.contrib import admin
from .models import ChatConversations, VoiceConversations, QuoteRequest
from django.utils.html import format_html
# from datetime import timedelta
# from django.db.models import Count, Avg, Q, Sum
# from django.contrib.auth.models import User, Group
# from django.contrib.auth.admin import UserAdmin, GroupAdmin

# class MyAdminSite(admin.AdminSite):

#     def index(self, request, extra_context=None):
#         # Add your custom data here
#         # Initialize extra_context
#         extra_context = extra_context or {}

#         today = timezone.now().date()
#         week_ago = today - timedelta(days=7)
#         month_ago = today - timedelta(days=30)
        
#         # Basic Stats
#         total_leads = Lead.objects.count()
#         total_calls_today = CallHistory.objects.filter(created_at__date=today).count()
        
#         # Success rate calculation
#         successful_calls = CallHistory.objects.filter(
#             call_successful='True',
#             created_at__date=today
#         ).count()

#         success_rate = (successful_calls / total_calls_today * 100) if total_calls_today > 0 else 0
        
#         # Average call duration (in minutes)
#         avg_duration = CallHistory.objects.aggregate(
#             avg_duration=Avg('duration')
#         )['avg_duration'] or 0
#         avg_duration_minutes = round(avg_duration / 60, 1) if avg_duration else 0
        
#         # Weekly comparison
#         calls_this_week = CallHistory.objects.filter(created_at__date__gte=week_ago).count()
#         calls_last_week = CallHistory.objects.filter(
#             created_at__date__gte=week_ago - timedelta(days=7),
#             created_at__date__lt=week_ago
#         ).count()
        
#         weekly_growth = 0
#         if calls_last_week > 0:
#             weekly_growth = round(((calls_this_week - calls_last_week) / calls_last_week) * 100, 1)
        
#         # Main metrics for the metric cards
#         extra_context.update({
#             'total_leads': total_leads,
#             'total_calls_today': total_calls_today,
#             'weekly_growth': weekly_growth,  # positive growth
#             'success_rate': success_rate,
#             'avg_duration_minutes': avg_duration_minutes,
#         })

#         # Agent performance
#         agent_performance = CallHistory.objects.values('agent_id').annotate(
#             total_calls=Count('id'),
#             successful_calls=Count('id', filter=Q(call_successful='True'))
#         ).order_by('-successful_calls')[:5]
        
#         # Agent performance data
#         client = Retell(api_key=settings.RETELL_API_KEY)
#         agents = client.agent.list()

#         # Step 1: Get latest version of each agent
#         agent_map = {}
#         for agent in agents:
#             if (agent.agent_id not in agent_map) or (agent.version > agent_map[agent.agent_id].version):
#                 agent_map[agent.agent_id] = agent

#         # Step 2: Prepare the performance list
#         agent_perf_list = []
#         for entry in agent_performance:
#             agent_id = entry['agent_id']
#             info = agent_map.get(agent_id)

#             agent_perf_list.append({
#                 "agent_id": agent_id,
#                 "agent_name": getattr(info, "agent_name", "Unknown"),
#                 "total_calls": entry['total_calls'],
#                 "successful_calls": entry['successful_calls']
#             })

#         # Step 3: Add to context
#         extra_context['agent_performance'] = agent_perf_list

#         # Daily call volume for chart (last 7 days)
#         extra_context['daily_calls'] = []
#         for i in range(6, -1, -1):
#             date = today - timedelta(days=i)
#             count = CallHistory.objects.filter(created_at__date=date).count()
#             extra_context['daily_calls'].append({
#                 'date': date.strftime('%m/%d'),
#                 'count': count
#             })
        
#         # Call outcomes distribution for pie chart
#         # Call outcome distribution
#         call_outcomes = CallHistory.objects.values('disconnection_reason').annotate(
#             count=Count('id')
#         ).order_by('-count')
#         extra_context['call_outcomes'] = call_outcomes
        
#         # Sample lead names and phone numbers
#         # Recent call history
#         recent_calls = CallHistory.objects.select_related('lead').order_by('-created_at')[:5]
        
#         extra_context['recent_calls'] = recent_calls

#         return super().index(request, extra_context)

# # Register your admin site
# custom_admin_site = MyAdminSite(name='myadmin')
# custom_admin_site.register(User, UserAdmin)
# custom_admin_site.register(Group, GroupAdmin)

@admin.register(ChatConversations)
class ChatConversationsAdmin(admin.ModelAdmin):
    list_display = ('id', 'short_chat','quote_requested', 'view_transcript','created_at')
    search_fields = ('id',)
    list_filter = ('quote_requested', 'created_at')
    readonly_fields = ('chat', 'quote_requested', 'created_at')

    def has_add_permission(self, request):
        return False  # no add

    def has_change_permission(self, request, obj=None):
        return False  # no edit
    
    def short_chat(self, obj):
        # obj.chat is your JSON list
        if not obj.chat:
            return "-"
        # Show up to first 2 messages
        preview = []
        for turn in obj.chat[:2]:
            preview.append(f"<strong>{turn['source']}:</strong> {turn['text']}")
        return format_html("<br>".join(preview))

    short_chat.short_description = "Chat"

    def view_transcript(self, obj):
        return format_html(

            '<a href="javascript:void(0);" class="btn btn-sm btn-primary" onclick="openTranscriptModal(\'{}\')">View</a>',
            obj.id
        )
    view_transcript.short_description = 'View Transcription'


@admin.register(VoiceConversations)
class VoiceConversationsAdmin(admin.ModelAdmin):
    list_display = ('id', 'duration', 'quote_requested', 'created_at')
    search_fields = ('id', 'duration')
    list_filter = ('quote_requested', 'created_at')
    readonly_fields = ('duration', 'audio_file', 'chat', 'quote_requested', 'created_at')

    def has_add_permission(self, request):
        return False  # no add

    def has_change_permission(self, request, obj=None):
        return False  # no edit


@admin.register(QuoteRequest)
class QuoteRequestAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'chat_id' ,'name', 'email', 'phone_no', 'quote_status',
        'quantity', 'decoration_requested', 'created_at', 'updated_at'
    )
    search_fields = ('id', 'name', 'email', 'phone_no')
    list_filter = ('quote_status', 'decoration_requested', 'created_at')
    readonly_fields = ('created_at', 'updated_at')

    def has_add_permission(self, request):
        return False  # no add, only edit existing
