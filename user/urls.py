from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .utils import validate_email

urlpatterns = [
    path('ajax/validate_email', validate_email, name='validate_email'),
    path('dashboard/', views.Dashboard.as_view(), name='dashboard'),
    path('admin/', views.AdminView.as_view(), name='admin_view'),
    path('order/', views.OrderView.as_view(), name='orders'),
    path('product/', views.ProductView.as_view(), name='product'),
    path('notifications/', views.Notification.as_view(), name='notification'),
    path('profile/', views.UpdateProfileView.as_view(), name='update-profile'),
    path('api/data/', views.get_data, name="get_data"),
    path('api/chart/data', views.ChartData.as_view(), name="chart-data"),
    path('blog', views.BlogPostDashboardView.as_view(), name="blog-post-dashboard"),
]
