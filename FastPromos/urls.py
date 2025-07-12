from django.urls import path,include
from .views import quote_request ,add_faqs,upload_faqs_to_voiceflow,FAQViewSet,save_chat,chatbot,get_transcript
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'faqs', FAQViewSet, basename='faq')

urlpatterns = [
    path('save-chat/', save_chat, name='save-chat'),
    path('add-faqs/', add_faqs, name='add_faqs'),
    path('upload-faqs/', upload_faqs_to_voiceflow, name='upload_faqs_to_voiceflow'),
    path('quote-request/', quote_request, name='quote_request'),
    path('generate-quote/', generate_quote, name='generate_quote'),
    path('', include(router.urls)),
    path('transcript/', get_transcript, name='transcript'),
    path('chat/', chatbot, name='chatbot')
]
