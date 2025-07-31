from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.utils import timezone
from datetime import timedelta
import stripe
from django.conf import settings
from .models import Subscription, SubscriptionHistory
from .serializers import (
    SubscriptionSerializer,
    SubscriptionCreateSerializer,
    MySubscriptionsSerializer,
    SubscriptionHistorySerializer
)

# Set Stripe API key
stripe.api_key = settings.STRIPE_SECRET_KEY

class MySubscriptionsView(generics.ListAPIView):
    """List user's subscriptions"""
    serializer_class = MySubscriptionsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Subscription.objects.filter(subscriber=self.request.user)

class SubscriptionCreateView(generics.CreateAPIView):
    """Create a new subscription"""
    serializer_class = SubscriptionCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        creator = serializer.validated_data['creator_id']
        payment_method_id = serializer.validated_data['payment_method_id']
        subscriber = request.user
        
        try:
            # Create or get Stripe customer
            if not subscriber.stripe_customer_id:
                customer = stripe.Customer.create(
                    email=subscriber.email,
                    name=subscriber.full_name
                )
                subscriber.stripe_customer_id = customer.id
                subscriber.save()
            
            # Attach payment method to customer
            stripe.PaymentMethod.attach(
                payment_method_id,
                customer=subscriber.stripe_customer_id
            )
            
            # Create Stripe subscription
            stripe_subscription = stripe.Subscription.create(
                customer=subscriber.stripe_customer_id,
                items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f'Subscription to {creator.display_name}',
                        },
                        'unit_amount': int(creator.subscription_price * 100),  # Convert to cents
                        'recurring': {
                            'interval': 'month',
                        },
                    },
                }],
                default_payment_method=payment_method_id,
                expand=['latest_invoice.payment_intent'],
            )
            
            # Create local subscription record
            subscription = Subscription.objects.create(
                subscriber=subscriber,
                creator=creator,
                stripe_subscription_id=stripe_subscription.id,
                status='active' if stripe_subscription.status == 'active' else 'pending',
                price=creator.subscription_price,
                current_period_start=timezone.datetime.fromtimestamp(
                    stripe_subscription.current_period_start, tz=timezone.utc
                ),
                current_period_end=timezone.datetime.fromtimestamp(
                    stripe_subscription.current_period_end, tz=timezone.utc
                )
            )
            
            # Update creator subscriber count
            creator.subscriber_count += 1
            creator.save()
            
            # Create subscription history record
            SubscriptionHistory.objects.create(
                subscription=subscription,
                action='created',
                amount=creator.subscription_price,
                notes='Subscription created successfully'
            )
            
            return Response({
                'subscription': SubscriptionSerializer(subscription).data,
                'message': 'Subscription created successfully'
            }, status=status.HTTP_201_CREATED)
            
        except stripe.error.StripeError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class SubscriptionDetailView(generics.RetrieveAPIView):
    """Get subscription details"""
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Subscription.objects.filter(subscriber=self.request.user)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_subscription(request, subscription_id):
    """Cancel a subscription"""
    try:
        subscription = Subscription.objects.get(
            id=subscription_id,
            subscriber=request.user
        )
        
        # Cancel in Stripe
        stripe.Subscription.modify(
            subscription.stripe_subscription_id,
            cancel_at_period_end=True
        )
        
        # Update local record
        subscription.status = 'cancelled'
        subscription.cancelled_at = timezone.now()
        subscription.save()
        
        # Update creator subscriber count
        subscription.creator.subscriber_count -= 1
        subscription.creator.save()
        
        # Create history record
        SubscriptionHistory.objects.create(
            subscription=subscription,
            action='cancelled',
            notes='Subscription cancelled by user'
        )
        
        return Response({
            'message': 'Subscription cancelled successfully'
        })
        
    except Subscription.DoesNotExist:
        return Response({
            'error': 'Subscription not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except stripe.error.StripeError as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def reactivate_subscription(request, subscription_id):
    """Reactivate a cancelled subscription"""
    try:
        subscription = Subscription.objects.get(
            id=subscription_id,
            subscriber=request.user,
            status='cancelled'
        )
        
        # Reactivate in Stripe
        stripe.Subscription.modify(
            subscription.stripe_subscription_id,
            cancel_at_period_end=False
        )
        
        # Update local record
        subscription.status = 'active'
        subscription.cancelled_at = None
        subscription.save()
        
        # Update creator subscriber count
        subscription.creator.subscriber_count += 1
        subscription.creator.save()
        
        # Create history record
        SubscriptionHistory.objects.create(
            subscription=subscription,
            action='reactivated',
            notes='Subscription reactivated by user'
        )
        
        return Response({
            'message': 'Subscription reactivated successfully'
        })
        
    except Subscription.DoesNotExist:
        return Response({
            'error': 'Subscription not found or not cancelled'
        }, status=status.HTTP_404_NOT_FOUND)
    except stripe.error.StripeError as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def subscription_history(request, subscription_id):
    """Get subscription history"""
    try:
        subscription = Subscription.objects.get(
            id=subscription_id,
            subscriber=request.user
        )
        
        history = SubscriptionHistory.objects.filter(subscription=subscription)
        serializer = SubscriptionHistorySerializer(history, many=True)
        
        return Response(serializer.data)
        
    except Subscription.DoesNotExist:
        return Response({
            'error': 'Subscription not found'
        }, status=status.HTTP_404_NOT_FOUND)
