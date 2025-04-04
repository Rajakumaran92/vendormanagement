from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import ( VendorViewSet, ProductViewSet, 
    ProductRegistrationViewSet, InvoiceViewSet, ProductSearchViewSet,
    PurchaseOrderViewSet, WarrantyClaimViewSet, ui_login, product_list,
    customer_login, vendor_login, purchase_order_list, vendor_register, register_product, test_email
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
    path('ar-traders/', ui_login, name='login'),
    path('ar-traders/register/', ARTradersViewSet.as_view({'post': 'register'}), name='artraders-register'),
    path('customer/', customer_login, name='customer-login'),
    path('customer/register-product/', register_product, name='register-product'),  # New URL for product registration
    path('vendors/', vendor_login, name='vendor-login'),
    path('vendors/register/', vendor_register, name='vendor-register'),  # New UI-based registration URL
    path('vendors/orders/', purchase_order_list, name='purchase-order-list'),
    path('products/', product_list, name='product-list'),
    path('logout/', LogoutView.as_view(next_page='customer-login'), name='logout'),
    path("api/", include(router.urls)),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path('api/test-email/', test_email, name='test-email'),  # Changed the path to be under /api/
    path('', lambda request: redirect('customer-login'), name='root'),
]
