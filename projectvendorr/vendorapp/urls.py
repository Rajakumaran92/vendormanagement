from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    UserViewSet, VendorViewSet, ProductViewSet, 
    ProductRegistrationViewSet, InvoiceViewSet, ProductSearchViewSet,
    PurchaseOrderViewSet, WarrantyClaimViewSet
)

# ✅ Create a router and register viewsets
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'vendors', VendorViewSet, basename='vendors')
router.register(r'products', ProductViewSet, basename='products')
router.register(r'product-registrations', ProductRegistrationViewSet, basename='product-registrations')
router.register(r'invoices', InvoiceViewSet, basename='invoices')
router.register(r'product-search', ProductSearchViewSet, basename='product-search')
router.register(r'purchase-orders', PurchaseOrderViewSet, basename='purchase-orders')
router.register(r'warranty-claims', WarrantyClaimViewSet, basename='warranty-claims')

# ✅ Define URL patterns
urlpatterns = [
    path("api/", include(router.urls)),  # Corrected: Avoid duplicate router inclusion
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),  # Access & Refresh Token
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),  # Refresh Token
]
