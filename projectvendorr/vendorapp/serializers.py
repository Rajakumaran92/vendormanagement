from rest_framework import serializers
from .models import User, Vendor, ProductRegistration, Invoice, Product, PurchaseOrder, WarrantyClaim

# ✅ User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

# ✅ Vendor Serializer
class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = '__all__'

# ✅ Product Serializer (Includes vendor details)
class ProductSerializer(serializers.ModelSerializer):
    vendor_name = serializers.ReadOnlyField(source='vendor.name')

    class Meta:
        model = Product
        fields = '__all__'

# ✅ Purchase Order Serializer
class PurchaseOrderSerializer(serializers.ModelSerializer):
    vendor_name = serializers.ReadOnlyField(source='vendor.name')

    class Meta:
        model = PurchaseOrder
        fields = '__all__'

# ✅ Product Registration Serializer (Includes product & vendor details)
class ProductRegistrationSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    vendor_name = serializers.ReadOnlyField(source='vendor.name')

    class Meta:
        model = ProductRegistration
        fields = '__all__'

# ✅ Invoice Serializer (Includes vendor details)
class InvoiceSerializer(serializers.ModelSerializer):
    vendor_name = serializers.ReadOnlyField(source='vendor.name')

    class Meta:
        model = Invoice
        fields = '__all__'

# ✅ Warranty Claim Serializer (Includes product, customer, and approval details)
class WarrantyClaimSerializer(serializers.ModelSerializer):
    customer_username = serializers.ReadOnlyField(source='customer.username')
    product_name = serializers.ReadOnlyField(source='product.name')
    approved_by_username = serializers.ReadOnlyField(source='approved_by.username')

    class Meta:
        model = WarrantyClaim
        fields = '__all__'
