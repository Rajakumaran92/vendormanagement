from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

# ✅ Custom User Admin Panel
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ("id", "username", "email", "is_staff", "is_superuser")
    search_fields = ("username", "email")
    list_filter = ("is_staff", "is_superuser", "groups")
    ordering = ("id",)
    fieldsets = (
        (None, {"fields": ("username", "email", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "groups")}),
        ("Important Dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "password1", "password2"),
        }),
    )

# ✅ Vendor Admin Panel
class VendorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "contact_email", "phone", "is_approved")
    search_fields = ("name", "contact_email", "phone")
    list_filter = ("is_approved",)

# ✅ Purchase Order Admin
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ("id", "po_number", "vendor", "order_date", "status")
    search_fields = ("po_number", "vendor__name")
    list_filter = ("status",)

# ✅ Product Admin
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "vendor", "price", "stock_quantity")
    search_fields = ("name", "vendor__name", "category")
    list_filter = ("category", "vendor")

# ✅ Product Registration Admin
class ProductRegistrationAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "vendor", "customer", "serial_number", "registration_date")
    search_fields = ("serial_number", "product__name", "customer__username")
    list_filter = ("registration_date",)

# ✅ Invoice Admin
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("id", "invoice_number", "vendor", "amount", "payment_status")
    search_fields = ("invoice_number", "vendor__name")
    list_filter = ("payment_status", "issue_date")

# ✅ Warranty Claim Admin
class WarrantyClaimAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "product", "invoice", "status", "claim_date")
    search_fields = ("customer__username", "product__name", "invoice__invoice_number")
    list_filter = ("status", "claim_date")

# ✅ Register all models
admin.site.register(User, CustomUserAdmin)
admin.site.register(Vendor, VendorAdmin)
admin.site.register(PurchaseOrder, PurchaseOrderAdmin)
admin.site.register(PurchaseOrderProduct)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductRegistration, ProductRegistrationAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(WarrantyClaim, WarrantyClaimAdmin)
