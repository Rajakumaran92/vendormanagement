from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Vendor, ProductRegistration, Invoice, Product, PurchaseOrder, WarrantyClaim

User = get_user_model()  # Get the custom user model

# ✅ User Serializer (With Password Hashing)
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  # Ensure password is not exposed in API responses

    class Meta:
        model = User
        fields = ["id", "email", "username", "password"]

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)  # Use create_user to hash the password
        return user


# ✅ Vendor Serializer
class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = "__all__"


# ✅ Product Serializer (Includes Vendor Details)
class ProductSerializer(serializers.ModelSerializer):
    vendor_name = serializers.ReadOnlyField(source="vendor.name")  # Read-only vendor name

    class Meta:
        model = Product
        fields = "__all__"


# ✅ Purchase Order Serializer
class PurchaseOrderSerializer(serializers.ModelSerializer):
    vendor_name = serializers.ReadOnlyField(source="vendor.name")  # Read-only vendor name

    class Meta:
        model = PurchaseOrder
        fields = "__all__"


# ✅ Product Registration Serializer (Includes Product & Vendor Details)
class ProductRegistrationSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")
    vendor_name = serializers.ReadOnlyField(source="vendor.name", default=None)

    class Meta:
        model = ProductRegistration
        fields = "__all__"


# ✅ Invoice Serializer (Includes Vendor Details)
class InvoiceSerializer(serializers.ModelSerializer):
    vendor_name = serializers.ReadOnlyField(source="vendor.name")  # Read-only vendor name

    class Meta:
        model = Invoice
        fields = "__all__"


# ✅ Warranty Claim Serializer (Includes Customer, Product, and Approval Details)
class WarrantyClaimSerializer(serializers.ModelSerializer):
    customer_username = serializers.ReadOnlyField(source="customer.username")
    product_name = serializers.ReadOnlyField(source="product.name")
    approved_by_username = serializers.ReadOnlyField(source="approved_by.username", default=None)

    class Meta:
        model = WarrantyClaim
        fields = "__all__"
        extra_kwargs = {
            "approved_by": {"required": False},  # Make approved_by optional
        }