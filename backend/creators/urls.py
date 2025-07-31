from django.urls import path
from . import views

app_name = 'creators'

urlpatterns = [
    path('', views.CreatorListView.as_view(), name='creator-list'),
    path('<int:id>/', views.CreatorDetailView.as_view(), name='creator-detail'),
    path('create/', views.CreatorCreateView.as_view(), name='creator-create'),
    path('profile/', views.CreatorUpdateView.as_view(), name='creator-profile'),
    path('social-links/', views.CreatorSocialLinksView.as_view(), name='creator-social-links'),
    path('featured/', views.featured_creators, name='featured-creators'),
    path('trending/', views.trending_creators, name='trending-creators'),
    path('categories/', views.categories, name='categories'),
]