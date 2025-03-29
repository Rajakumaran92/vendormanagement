from rest_framework import viewsets, permissions, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.timezone import now
from .models import User, Vendor, PurchaseOrder, Product, ProductRegistration, Invoice, WarrantyClaim
from .serializers import (
    UserSerializer, VendorSerializer, PurchaseOrderSerializer, 
    ProductSerializer, ProductRegistrationSerializer, InvoiceSerializer, 
    WarrantyClaimSerializer
)

from rest_framework.permissions import IsAuthenticated


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
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name", "contact_email", "phone"]

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
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
    permission_classes = [permissions.IsAuthenticated]
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
    permission_classes = [permissions.IsAuthenticated]
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
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["invoice_number"]

# ✅ Warranty Claim ViewSet
class WarrantyClaimViewSet(viewsets.ModelViewSet):
    queryset = WarrantyClaim.objects.all()
    serializer_class = WarrantyClaimSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["status"]

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        """Approve a warranty claim."""
        claim = self.get_object()
        claim.status = "Approved"
        claim.approved_by = request.user
        claim.save()
        return Response({"status": "Warranty claim approved"})

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
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
    permission_classes = [IsAuthenticated]  # Require authentication
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description', 'category']  # Searchable fields
