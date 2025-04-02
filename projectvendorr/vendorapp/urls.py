from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import ( VendorViewSet, ProductViewSet, 
    ProductRegistrationViewSet, InvoiceViewSet, ProductSearchViewSet,
    PurchaseOrderViewSet, WarrantyClaimViewSet, ui_login, product_list,
    customer_login
)
from .views import ARTradersViewSet, CustomersViewSet
from django.contrib.auth.views import LogoutView
from django.shortcuts import redirect

from vendorapp.views import UserViewSet

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
router.register(r"ar-traders", ARTradersViewSet, basename="ar-traders")
router.register(r"customers", CustomersViewSet, basename="customers")

# ✅ Define URL patterns
urlpatterns = [
    path('ar-traders/', ui_login, name='login'),  # Changed root URL to ar-traders prefix
    path('ar-traders/register/', ARTradersViewSet.as_view({'post': 'register'}), name='artraders-register'),
    path('customer/', customer_login, name='customer-login'),  # Add customer login URL
    path('products/', product_list, name='product-list'),  # Add products page URL
    path('logout/', LogoutView.as_view(next_page='customer-login'), name='logout'),  # Changed logout redirect
    path("api/", include(router.urls)),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path('', lambda request: redirect('customer-login'), name='root'),  # Redirect root to customer login
]
