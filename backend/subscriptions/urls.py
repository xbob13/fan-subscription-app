from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('', views.MySubscriptionsView.as_view(), name='my-subscriptions'),
    path('create/', views.SubscriptionCreateView.as_view(), name='create-subscription'),
    path('<int:pk>/', views.SubscriptionDetailView.as_view(), name='subscription-detail'),
    path('<int:subscription_id>/cancel/', views.cancel_subscription, name='cancel-subscription'),
    path('<int:subscription_id>/reactivate/', views.reactivate_subscription, name='reactivate-subscription'),
    path('<int:subscription_id>/history/', views.subscription_history, name='subscription-history'),
]