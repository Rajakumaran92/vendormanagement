from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.timezone import now
from datetime import timedelta
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.models import Group
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test

from .models import Vendor, PurchaseOrder, Product, ProductRegistration, Invoice, WarrantyClaim
from .serializers import (
    UserSerializer, VendorSerializer, PurchaseOrderSerializer, 
    ProductSerializer, ProductRegistrationSerializer, InvoiceSerializer, 
    WarrantyClaimSerializer
)
from .permissions import IsARTrader, IsCustomer

User = get_user_model()  # Get the User model dynamically

# ✅ User ViewSet
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["email", "username"]

# ✅ Vendor ViewSet
class VendorViewSet(viewsets.ModelViewSet):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    permission_classes = [permissions.IsAuthenticated, IsARTrader]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name", "contact_email", "phone"]

    @action(detail=True, methods=["post"], permission_classes=[IsARTrader])
    def approve(self, request, pk=None):
        """Approve a vendor."""
        vendor = self.get_object()
        vendor.is_approved = True
        vendor.save()
        return Response({"status": "Vendor approved"})

# ✅ Purchase Order ViewSet
class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsARTrader]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["status"]
    search_fields = ["po_number"]

# ✅ Product ViewSet
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name", "category"]

# ✅ Product Registration ViewSet
class ProductRegistrationViewSet(viewsets.ModelViewSet):
    queryset = ProductRegistration.objects.all()
    serializer_class = ProductRegistrationSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomer]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["serial_number"]

    def perform_create(self, serializer):
        """Ensure serial number is correctly assigned."""
        instance = serializer.save()
        if not instance.serial_number:
            instance.serial_number = f"SN-{instance.product.id}-{instance.id}"
            instance.save()

    @action(detail=True, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def warranty_status(self, request, pk=None):
        """Check if the product warranty is still valid."""
        registration = self.get_object()
        expiry_date = registration.registration_date + timedelta(days=registration.product.warranty_days)
        is_valid = now().date() <= expiry_date
        return Response({"warranty_expiry_date": expiry_date, "is_valid": is_valid})

# ✅ Invoice ViewSet
class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated, IsARTrader]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["invoice_number"]

# ✅ Warranty Claim ViewSet
class WarrantyClaimViewSet(viewsets.ModelViewSet):
    queryset = WarrantyClaim.objects.all()
    serializer_class = WarrantyClaimSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomer]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["status"]

    @action(detail=True, methods=["post"], permission_classes=[IsARTrader])
    def approve(self, request, pk=None):
        """Approve a warranty claim."""
        claim = self.get_object()
        claim.status = "Approved"
        claim.approved_by = request.user
        claim.save()
        return Response({"status": "Warranty claim approved"})

    @action(detail=True, methods=["post"], permission_classes=[IsARTrader])
    def reject(self, request, pk=None):
        """Reject a warranty claim."""
        claim = self.get_object()
        claim.status = "Rejected"
        claim.approved_by = request.user
        claim.save()
        return Response({"status": "Warranty claim rejected"})

# ✅ Product Search ViewSet
class ProductSearchViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for searching products by name, description, or category.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description', 'category']

# ✅ AR Traders ViewSet
class ARTradersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(groups__name="AR Traders")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsARTrader]

    @action(detail=False, methods=["post"], permission_classes=[permissions.AllowAny])
    def register(self, request):
        """Register a new AR Trader"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(serializer.validated_data["password"])  # Hash password
            user.save()

            ar_traders_group, _ = Group.objects.get_or_create(name="AR Traders")
            user.groups.add(ar_traders_group)

            # Generate JWT Token
            refresh = RefreshToken.for_user(user)
            return Response({
                "user": serializer.data,
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh)
            })
        return Response(serializer.errors, status=400)

# ✅ Customers ViewSet
class CustomersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(groups__name="Customers")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomer]

    @action(detail=False, methods=["post"], permission_classes=[permissions.AllowAny])
    def register(self, request):
        """Register a new Customer"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(serializer.validated_data["password"])  # Hash password
            user.save()

            customer_group, _ = Group.objects.get_or_create(name="Customers")
            user.groups.add(customer_group)

            # Generate JWT Token
            refresh = RefreshToken.for_user(user)
            return Response({
                "user": serializer.data,
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh)
            })
        return Response(serializer.errors, status=400)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Login view that returns JWT tokens and redirects to products page"""
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response({'error': 'Please provide both email and password'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(email=email, password=password)
    
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'redirect': '/api/products/',  # Redirect URL for frontend
            'user': {
                'email': user.email,
                'username': user.username,
                'id': user.id
            }
        })
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

def ui_login(request):
    """Handle UI-based login"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if email and password:
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('product-list')  # Redirect to products page after login
            else:
                return render(request, 'vendorapp/login.html', {'error': 'Invalid credentials'})
        else:
            return render(request, 'vendorapp/login.html', {'error': 'Please provide both email and password'})
    
    return render(request, 'vendorapp/login.html')

def is_valid_user(user):
    """Check if user is either a Customer or AR Trader"""
    return user.groups.filter(name__in=["Customers", "AR Traders"]).exists()

@login_required(login_url='login')
@user_passes_test(is_valid_user, login_url='customer-login')
def product_list(request):
    """Display list of products. Accessible to both Customers and AR Traders."""
    products = Product.objects.all()
    return render(request, 'vendorapp/product_list.html', {'products': products})

def is_ar_trader(user):
    """Check if user is in AR Traders group"""
    return user.groups.filter(name="AR Traders").exists()

def is_customer(user):
    """Check if user is in Customers group"""
    return user.groups.filter(name="Customers").exists()

def customer_login(request):
    """Handle Customer UI-based login"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if email and password:
            user = authenticate(request, email=email, password=password)
            if user is not None and is_customer(user):
                login(request, user)
                return redirect('product-list')
            else:
                return render(request, 'vendorapp/customer_login.html', 
                            {'error': 'Invalid credentials or not a customer account'})
        else:
            return render(request, 'vendorapp/customer_login.html', 
                        {'error': 'Please provide both email and password'})
    
    return render(request, 'vendorapp/customer_login.html')
