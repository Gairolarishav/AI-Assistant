from django.urls import path,include
from .views import quote_request,send_quotes,fetch_voiceflow_ready_products,add_faqs,upload_faqs_to_voiceflow,FAQViewSet,save_chat,chatbot,get_transcript,generate_quote,generate_pending_quotations,get_quotation_details
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'faqs', FAQViewSet, basename='faq')

urlpatterns = [
    path('save-chat/', save_chat, name='save-chat'),
    path('add-faqs/', add_faqs, name='add_faqs'),
    path('upload-faqs/', upload_faqs_to_voiceflow, name='upload_faqs_to_voiceflow'),
    path('upload-product-data/', fetch_voiceflow_ready_products),
    path('quote-request/', quote_request, name='quote_request'),
    path('generate-quote/', generate_quote, name='generate_quote'),
    path('generate-all-quote/', generate_pending_quotations, name='generate_pending_quotations'),
    path('send-quotes/', send_quotes, name='send_quotes'),
    path('get-quotation-details/',get_quotation_details, name='get_quotation_details'),
    path('', include(router.urls)),
    path('transcript/', get_transcript, name='transcript'),
    path('chat/', chatbot, name='chatbot')
]
