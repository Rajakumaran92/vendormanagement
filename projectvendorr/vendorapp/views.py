from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes, authentication_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.timezone import now
from datetime import timedelta
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.models import Group
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from datetime import datetime
from .tasks import send_registration_email, send_product_registration_email, send_email_task

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

    @action(detail=False, methods=["post"], permission_classes=[permissions.AllowAny])
    def register(self, request):
        """Register a new Vendor"""
        # Create user first
        user_data = {
            'email': request.data.get('email'),
            'username': request.data.get('email'),  # Use email as username
            'password': request.data.get('password')
        }
        user_serializer = UserSerializer(data=user_data)
        if user_serializer.is_valid():
            user = user_serializer.save()
            user.set_password(user_data['password'])  # Hash password
            user.save()

            # Create vendor
            vendor_data = {
                'user': user.id,
                'name': request.data.get('name'),
                'contact_email': request.data.get('email'),
                'phone': request.data.get('phone', ''),
                'address': request.data.get('address', ''),
                'gstin': request.data.get('gstin'),
                'is_approved': False  # New vendors need approval
            }
            vendor_serializer = self.get_serializer(data=vendor_data)
            if vendor_serializer.is_valid():
                vendor = vendor_serializer.save()
                
                # Add user to Vendor group
                vendor_group, _ = Group.objects.get_or_create(name="Vendor")
                user.groups.add(vendor_group)

                # Generate JWT Token
                refresh = RefreshToken.for_user(user)
                return Response({
                    'user': user_serializer.data,
                    'vendor': vendor_serializer.data,
                    'access_token': str(refresh.access_token),
                    'refresh_token': str(refresh)
                })
            else:
                user.delete()  # Roll back user creation if vendor creation fails
                return Response(vendor_serializer.errors, status=400)
        return Response(user_serializer.errors, status=400)

# ✅ Purchase Order ViewSet
class PurchaseOrderViewSet(viewsets.ModelViewSet):
    serializer_class = PurchaseOrderSerializer
    permission_classes = [permissions.IsAuthenticated]  # Base authentication
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["status"]
    search_fields = ["po_number"]

    def get_queryset(self):
        """Filter queryset based on user type"""
        user = self.request.user
        if user.groups.filter(name="AR Traders").exists():
            return PurchaseOrder.objects.all()
        elif user.groups.filter(name="Vendor").exists():
            vendor = user.vendor_set.first()
            if vendor:
                return PurchaseOrder.objects.filter(vendor=vendor)
        return PurchaseOrder.objects.none()

    def get_permissions(self):
        """Different permissions for different actions"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsARTrader()]
        return [permissions.IsAuthenticated()]

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
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action == 'register':
            return [permissions.AllowAny()]
        return super().get_permissions()

    @action(detail=False, methods=["post"])
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

def is_vendor(user):
    """Check if user is in Vendor group"""
    return user.groups.filter(name="Vendor").exists()

def vendor_login(request):
    """Handle Vendor UI-based login"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if email and password:
            user = authenticate(request, email=email, password=password)
            if user is not None and is_vendor(user):
                login(request, user)
                return redirect('purchase-order-list')  # Redirect to purchase orders page
            else:
                return render(request, 'vendorapp/vendor_login.html', 
                            {'error': 'Invalid credentials or not a vendor account'})
        else:
            return render(request, 'vendorapp/vendor_login.html', 
                        {'error': 'Please provide both email and password'})
    
    return render(request, 'vendorapp/vendor_login.html')

@login_required(login_url='vendors/login/')
@user_passes_test(is_vendor)
def purchase_order_list(request):
    """Display list of purchase orders for vendor."""
    # Get vendor associated with logged in user
    vendor = Vendor.objects.get(user=request.user)
    orders = PurchaseOrder.objects.filter(vendor=vendor)
    return render(request, 'vendorapp/purchase_order_list.html', {'orders': orders})

def vendor_register(request):
    """Handle vendor registration through UI"""
    if request.method == 'POST':
        # Get form data
        email = request.POST.get('email')
        password = request.POST.get('password')
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        gstin = request.POST.get('gstin')

        # Create user first
        user_data = {
            'email': email,
            'username': email,  # Use email as username
            'password': password
        }
        user_serializer = UserSerializer(data=user_data)
        if user_serializer.is_valid():
            user = user_serializer.save()
            user.set_password(password)  # Hash password
            user.save()

            # Create vendor
            vendor_data = {
                'user': user.id,
                'name': name,
                'contact_email': email,
                'phone': phone,
                'address': address,
                'gstin': gstin,
                'is_approved': False
            }
            vendor_serializer = VendorSerializer(data=vendor_data)
            if vendor_serializer.is_valid():
                vendor = vendor_serializer.save()
                
                # Add user to Vendor group
                vendor_group, _ = Group.objects.get_or_create(name="Vendor")
                user.groups.add(vendor_group)

                # Log the user in
                login(request, user)
                return redirect('purchase-order-list')
            else:
                # If vendor creation fails, delete the user and show error
                user.delete()
                return render(request, 'vendorapp/vendor_register.html', 
                            {'error': 'Invalid vendor data: ' + str(vendor_serializer.errors)})
        else:
            return render(request, 'vendorapp/vendor_register.html', 
                        {'error': 'Invalid user data: ' + str(user_serializer.errors)})
    
    return render(request, 'vendorapp/vendor_register.html')

@login_required(login_url='customer-login')
@user_passes_test(is_customer, login_url='customer-login')
def register_product(request):
    """Handle product registration for customers"""
    if request.method == 'POST':
        product_id = request.POST.get('product')
        purchase_date = request.POST.get('purchase_date')
        
        if product_id and purchase_date:
            try:
                product = Product.objects.get(id=product_id)
                # Create product registration
                registration = ProductRegistration.objects.create(
                    customer=request.user,
                    product=product,
                    vendor=product.vendor,
                    registration_date=purchase_date
                )
                
                # Prepare context for email
                context = {
                    'customer_name': request.user.get_full_name() or request.user.email,
                    'product_name': product.name,
                    'serial_number': registration.serial_number,
                    'registration_date': registration.registration_date.strftime('%Y-%m-%d'),
                    'warranty_expiry_date': (registration.registration_date + timedelta(days=product.warranty_days)).strftime('%Y-%m-%d')
                }

                # Send email asynchronously using Celery
                send_product_registration_email.delay(context, request.user.email)

                return render(request, 'vendorapp/register_product.html', {
                    'success': 'Product registered successfully! Your warranty is valid until ' + 
                             (registration.registration_date + timedelta(days=product.warranty_days)).strftime('%Y-%m-%d') +
                             '. A confirmation email will be sent to your email address.',
                    'products': Product.objects.all()
                })
            except Product.DoesNotExist:
                return render(request, 'vendorapp/register_product.html', {
                    'error': 'Invalid product selected.',
                    'products': Product.objects.all()
                })
            except Exception as e:
                return render(request, 'vendorapp/register_product.html', {
                    'error': str(e),
                    'products': Product.objects.all()
                })
        else:
            return render(request, 'vendorapp/register_product.html', {
                'error': 'Please provide all required information.',
                'products': Product.objects.all()
            })
    
    # GET request - show the registration form
    return render(request, 'vendorapp/register_product.html', {
        'products': Product.objects.all()
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_email(request):
    """
    Test endpoint to send email using Celery
    Expects JSON body with:
    {
        "subject": "Email subject",
        "message": "Email message",
        "to_email": "recipient@example.com"
    }
    """
    subject = request.data.get('subject')
    message = request.data.get('message')
    to_email = request.data.get('to_email')
    
    if not all([subject, message, to_email]):
        return Response({
            'error': 'Please provide subject, message and to_email'
        }, status=400)
    
    # Send email task to Celery
    task = send_email_task.delay(
        subject=subject,
        message=message,
        recipient_list=[to_email]
    )
    
    return Response({
        'message': 'Email task has been queued',
        'task_id': task.id
    })
