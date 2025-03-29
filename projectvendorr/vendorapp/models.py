from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import timedelta
from django.contrib.auth import get_user_model

# ✅ Custom User Model
class User(AbstractUser):
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"  # ✅ Login with email instead of username
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

# ✅ Vendor Model (Added `is_approved`)
class Vendor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    name = models.CharField(max_length=255,null=True)
    contact_email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20,null=True)
    address = models.TextField()
    gstin = models.CharField(max_length=15, unique=True, blank=True, null=True)  # GSTIN for tax compliance
    is_approved = models.BooleanField(default=False)  # ✅ Vendor approval status

    def __str__(self):
        return self.name

# ✅ Purchase Order Model (Linked to Products)
class PurchaseOrder(models.Model):
    po_number = models.CharField(max_length=50, unique=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    order_date = models.DateField(auto_now_add=True)
    expected_delivery_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('Completed', 'Completed'),
            ('Partially Fulfilled', 'Partially Fulfilled')
        ],
        default='Pending'
    )
    products = models.ManyToManyField('Product', through='PurchaseOrderProduct')  # ✅ Track ordered products

    def __str__(self):
        return f"PO {self.po_number} - {self.status}"

# ✅ Many-to-Many Relationship for Purchase Order and Products
class PurchaseOrderProduct(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

def get_default_vendor():
    
    return Vendor.objects.first().id  # ✅ Picks the first Vendor (Make sure at least one exists)

class Product(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, default=get_default_vendor)  # ✅ Auto-assign vendor
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.CharField(max_length=255, null=True, blank=True)
    warranty_days = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

# ✅ Product Registration Model (Added Customer + Warranty Expiry)
class ProductRegistration(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE,null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE,null=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE,null=True)  # ✅ Who registered the product
    serial_number = models.CharField(max_length=100, unique=True, blank=True,null=True)
    registration_date = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Save first to get an ID
        if not self.serial_number:
            self.serial_number = f"SN-{self.product.id}-{self.id}"
            super().save(*args, **kwargs)  # Save again with serial number

    @property
    def warranty_expiry_date(self):
        return self.registration_date + timedelta(days=self.product.warranty_days)  # ✅ Added warranty expiry

    def __str__(self):
        return f"{self.product.name} - {self.serial_number}"

# ✅ Invoice Model (Added Payment Status)
class Invoice(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, null=True, blank=True)  # ✅ Allow null values
    invoice_number = models.CharField(max_length=50, unique=True,null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    issue_date = models.DateField()
    due_date = models.DateField()
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('Unpaid', 'Unpaid'),
            ('Paid', 'Paid'),
            ('Overdue', 'Overdue')
        ],
        default='Unpaid'
    )

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.amount} - {self.payment_status}"

# ✅ Warranty Claim Model (Linked to Invoice & Fixed Email Reference)
class WarrantyClaim(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE,null=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE,null=True)  # ✅ Only purchased products can be claimed
    claim_date = models.DateField(auto_now_add=True)
    issue_description = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('Approved', 'Approved'),
            ('Rejected', 'Rejected'),
            ('Replaced', 'Replaced')
        ],
        default='Pending'
    )
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_claims")  # ✅ Track who approved the claim

    def __str__(self):
        return f"Claim {self.id} - {self.product.name} ({self.status})"
