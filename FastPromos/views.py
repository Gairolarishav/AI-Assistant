from django.shortcuts import render
from .models import QuoteRequest,ChatConversations,VoiceConversations,FAQ
from django.http import JsonResponse
import json
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework import viewsets,status
from django.shortcuts import render
from rest_framework.decorators import action
from .serializers import FAQSerializer
from django.conf import settings
import requests
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

@csrf_exempt
@require_POST
def quote_request(request):
    try:
        data = request.POST

        print("data ===", data)

        user_id = data.get("user_id", "").strip()

        # Try to get chat conversation
        try:
            user = ChatConversations.objects.get(user_id=user_id)
        except ChatConversations.DoesNotExist:
            user = None

        # If no chat, respond with error (or handle as you wish)
        if not user:
            return JsonResponse({"error": "Chat session not found for this user_id"}, status=400)
        
        # ✅ Mark chat as quote requested
        user.quote_requested = True
        user.save(update_fields=['quote_requested'])

        # Convert & clean up inputs
        decoration_requested = data.get("decoration_requested", "").strip().lower() == "yes"

        quote = QuoteRequest.objects.create(
            chat=user,  # ✅ use ForeignKey, not `chat_id`
            name=data.get("name", "").strip(),
            email=data.get("email", "").strip(),
            phone_no=data.get("phone_number", "").strip(),
            post_code=data.get("postcode", "").strip(),
            product_id=data.get("product_id", "").strip(),
            product_name=data.get("product_name", "").strip(),
            quantity=data.get("quantity", "0").strip(),
            decoration_requested=decoration_requested,
            decoration_mode=data.get("decoration_mode", "").strip(),
            decoration_mode_id=data.get("decoration_mode_id", "0").strip(),
            logo_colours = data.get("logo_colours_count", "").strip(),
            total_logos = data.get("logo_count", "").strip(),
            colour_size=data.get("colour_size", "").strip(),  # keep the typo if your model has it as `color_szie`
            colour_size_id=data.get("colour_size_id", "0").strip(),
            delivery_time=data.get("delivery_time", "").strip(),
        )

        return JsonResponse({
            "message": f"Quote request saved successfully for {quote.product_name} — Order ID: {quote.id}"
        }, status=201)

    except Exception as e:
        print("======", str(e))
        return JsonResponse({"error": str(e)}, status=400)

def add_faqs(request):
    token = settings.AUTH_TOKEN
    return render(request,'fastpromos/FAQ.html',{'token':token})

def chatbot(request):
    return render(request,'fastpromos/index6.html')

@csrf_exempt
def save_chat(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
        print("data ==", data)

        user_id = data.get('user_id')
        chat = data.get('transcript')

        if not user_id  or not chat:
            return JsonResponse({'error': 'Missing fields'}, status=400)

        obj, created = ChatConversations.objects.update_or_create(
            user_id=user_id,
            defaults={'chat': chat}
        )

        return JsonResponse({
            'status': 'success',
            'created': created,   # True if new, False if updated
            'id': obj.id
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
        

def get_transcript(request):
    user_id = request.GET.get('user_id')

    if not user_id:
        return JsonResponse({'error': 'Missing user_id'}, status=400)

    try:
        chatdata = ChatConversations.objects.get(id=user_id)

        if not chatdata:
            return JsonResponse({'transcript': []})

        return JsonResponse({'transcript': chatdata.chat})
    
    except ChatConversations.DoesNotExist:
        return JsonResponse({'transcript': []})


class FAQViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    
    def list(self, request):
        """Get paginated FAQs"""
        page = self.paginate_queryset(self.get_queryset())
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'success': True,
                'data': serializer.data
            })

        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    def create(self, request):
        """Create new FAQ"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'FAQ created successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, pk=None):
        """Get single FAQ"""
        try:
            faq = self.get_object()
            serializer = self.get_serializer(faq)
            return Response({
                'success': True,
                'data': serializer.data
            })
        except FAQ.DoesNotExist:
            return Response({
                'success': False,
                'message': 'FAQ not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def update(self, request, pk=None):
        """Update FAQ"""
        try:
            faq = self.get_object()
            serializer = self.get_serializer(faq, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': True,
                    'message': 'FAQ updated successfully',
                    'data': serializer.data
                })
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except FAQ.DoesNotExist:
            return Response({
                'success': False,
                'message': 'FAQ not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def destroy(self, request, pk=None):
        """Delete FAQ"""
        try:
            faq = self.get_object()
            faq.delete()
            return Response({
                'success': True,
                'message': 'FAQ deleted successfully'
            }, status=status.HTTP_200_OK)  # Changed status code
        except FAQ.DoesNotExist:
            return Response({
                'success': False,
                'message': 'FAQ not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Create multiple FAQs at once"""
        faqs_data = request.data.get('faqs', [])
        
        if not faqs_data:
            return Response({
                'success': False,
                'message': 'No FAQs provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        created_faqs = []
        errors = []
        
        for idx, faq_data in enumerate(faqs_data):
            serializer = self.get_serializer(data=faq_data)
            if serializer.is_valid():
                faq = serializer.save()
                created_faqs.append(serializer.data)
            else:
                errors.append({
                    'index': idx,
                    'errors': serializer.errors
                })
        
        if errors:
            return Response({
                'success': False,
                'message': 'Some FAQs could not be created',
                'created': created_faqs,
                'errors': errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'success': True,
            'message': f'{len(created_faqs)} FAQs created successfully',
            'data': created_faqs
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search FAQs by question or answer"""
        query = request.query_params.get('q', '')
        
        if not query:
            return Response({
                'success': False,
                'message': 'Search query is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        faqs = FAQ.objects.filter(
            models.Q(question__icontains=query) | 
            models.Q(answer__icontains=query)
        )
        
        serializer = self.get_serializer(faqs, many=True)
        return Response({
            'success': True,
            'count': faqs.count(),
            'query': query,
            'data': serializer.data
        })
    



VOICEFLOW_API_KEY = settings.VOICEFLOW_API_KEY
TABLE_UPLOAD_URL = "https://api.voiceflow.com/v1/knowledge-base/docs/upload/table"

def upload_faqs_to_voiceflow(request):
    try:
        # Step 1: Get all FAQs
        faq_objects = FAQ.objects.all()
        if not faq_objects.exists():
            return JsonResponse({"success": False, "message": "No FAQs available to upload."}, status=400)

        # Step 2: Prepare FAQ items
        faq_items = [
            {
                "id": faq.id,
                "question": faq.question,
                "answer": faq.answer,
                "created_at": faq.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            for faq in faq_objects
        ]

        # Step 3: Prepare payload
        payload = {
            "data": {
                "name": "FAQ Knowledgebase",
                "schema": {
                    "searchableFields": ["question", "answer"],
                    "metadataFields": ["created_at","id"]
                },
                "items": faq_items
            }
        }

        # Step 4: Make POST request to Voiceflow
        headers = {
            "Authorization": f"{VOICEFLOW_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        params = {"overwrite": "true"}

        response = requests.post(TABLE_UPLOAD_URL, json=payload, headers=headers, params=params)

        # Step 5: Handle response
        if response.status_code == 200:
            return JsonResponse({"success": True, "message": "FAQs uploaded successfully.", "response": response.json()})
        else:
            return JsonResponse({"success": False, "message": "Upload failed", "error": response.text}, status=response.status_code)

    except Exception as e:
        return JsonResponse({"success": False, "message": "Something went wrong", "error": str(e)}, status=500)

import requests
from decimal import Decimal, ROUND_HALF_UP

def generate_quote(request):
    try:
        quote_id = request.GET.get('id')
        if not quote_id:
            return JsonResponse({"error": "Missing quote_id"}, status=400)

        try:
            quote = QuoteRequest.objects.get(id=int(quote_id))
        except QuoteRequest.DoesNotExist:
            return JsonResponse({"error": "Quote not found"}, status=404)

        product_id = quote.product_id
        quantity = int(quote.quantity or 0)
        logo_colours = int(quote.logo_colours or 0)
        total_logos = int(quote.total_logos or 0)
        decoration_mode_id = int(quote.decoration_mode_id or 0)

        print(f"[DEBUG] product_id={product_id}, quantity={quantity}, logo_colours={logo_colours}, total_logos={total_logos}, decoration_mode_id={decoration_mode_id}")

        wc_url = f"https://fastpromos.com.au/wp-json/wc/v3/products/{product_id}"
        params = {
            "consumer_key": settings.CONSUMER_KEY,
            "consumer_secret": settings.CONSUMER_SECRET
        }

        response = requests.get(wc_url, params=params)
        if response.status_code != 200:
            return JsonResponse({"error": f"Error fetching product data. Status: {response.status_code}"}, status=500)

        product_data = response.json()
        meta_data = product_data.get("meta_data", [])

        fp_pricing = None
        fp_additional_costs = None

        for meta in meta_data:
            if meta.get("key") == "fp_pricing":
                fp_pricing = meta.get("value")
            if meta.get("key") == "fp_additional_costs":
                fp_additional_costs = meta.get("value")

        if not fp_pricing:
            return JsonResponse({"error": "No pricing found in product metadata."}, status=500)

        unit_price = None
        breaks = sorted(map(int, fp_pricing.keys()))
        for b in breaks:
            if quantity >= b:
                unit_price = Decimal(str(fp_pricing[str(b)]))
        if not unit_price:
            unit_price = Decimal(str(fp_pricing[str(breaks[0])]))

        # Branding logic
        if quote.decoration_requested and decoration_mode_id:
            selected_deco = next(
                (deco for deco in fp_additional_costs if deco["id"] == decoration_mode_id),
                None
            )
            if not selected_deco:
                return JsonResponse({"error": "No matching decoration option found."}, status=500)

            deco_unit_price = Decimal(str(selected_deco["unit_price"]))
            setup_fee = Decimal(str(selected_deco["setup"]))

            placements = logo_colours * total_logos
            # Better fallback: if no colour given, but logos exist, assume 1 colour
            if placements == 0 and total_logos > 0:
                placements = total_logos

            # Or safer: default to 1 only if both are zero
            if placements == 0:
                placements = 1

            deco_cost_per_unit = deco_unit_price * placements
            setup_cost_total = setup_fee * placements

            decoration_total = (deco_cost_per_unit * quantity) + setup_cost_total
            decoration_cost_per_unit = decoration_total / quantity

            all_in_unit_cost = unit_price + decoration_cost_per_unit
            final_unit_price = all_in_unit_cost / Decimal('0.70')

        else:
            print("[DEBUG] Unbranded: skipping decoration")
            deco_unit_price = Decimal('0.00')
            placements = 0
            setup_fee = Decimal('0.00')
            deco_cost_per_unit = Decimal('0.00')
            setup_cost_total = Decimal('0.00')
            decoration_total = Decimal('0.00')
            all_in_unit_cost = unit_price
            final_unit_price = all_in_unit_cost / Decimal('0.70')

        final_unit_price = final_unit_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        total_quote = (final_unit_price * quantity).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        print(f"[DEBUG] total_quote = {total_quote}")

        return JsonResponse({
            "base_unit_price": str(unit_price),
            "decoration_unit_price": str(deco_unit_price),
            "placements": placements,
            "setup_fee": str(setup_fee),
            "deco_cost_per_unit": str(deco_cost_per_unit.quantize(Decimal('0.01'))),
            "setup_cost_total": str(setup_cost_total.quantize(Decimal('0.01'))),
            "decoration_total": str(decoration_total.quantize(Decimal('0.01'))),
            "all_in_unit_cost": str(all_in_unit_cost.quantize(Decimal('0.01'))),
            "final_unit_price": str(final_unit_price),
            "total_quote": str(total_quote),
            "quantity": quantity,
            "branding_applied": quote.decoration_requested
        })

    except Exception as e:
        print("[ERROR] Exception in generate_quote:", str(e))
        return JsonResponse({"error": "Internal server error", "detail": str(e)}, status=500)
