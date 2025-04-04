import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projectvendorr.settings')
django.setup()

from vendorapp.models import Vendor, Product, User
from django.contrib.auth.models import Group

def create_sample_data():
    # Create Vendor group if it doesn't exist
    vendor_group, _ = Group.objects.get_or_create(name="Vendor")

    # Create a test vendor user
    vendor_user, created = User.objects.get_or_create(
        email="testvendor@example.com",
        username="testvendor@example.com",
        defaults={
            'is_active': True
        }
    )
    if created:
        vendor_user.set_password("test123")  # Set a password for the user
        vendor_user.save()
        vendor_user.groups.add(vendor_group)
    
    # Create an unapproved vendor
    vendor, created = Vendor.objects.get_or_create(
        user=vendor_user,
        name="Test Electronics",
        contact_email="testvendor@example.com",
        phone="9876543210",
        address="456 Test Street, Test City",
        gstin="TEST1234567890",
        is_approved=False  # Make sure vendor is not approved
    )
    
    if created:
        print("Created unapproved vendor:", vendor.name)
    
    # Create sample products only for approved vendor
    approved_vendor, _ = Vendor.objects.get_or_create(
        name="AR Traders Sample",
        contact_email="artraders@example.com",
        phone="1234567890",
        address="123 Sample Street",
        is_approved=True
    )
    
    products = [
        {
            "name": "LED TV 55 inch",
            "description": "4K Ultra HD Smart LED Television",
            "price": "45000.00",
            "stock_quantity": 10,
            "category": "Electronics",
            "warranty_days": 365
        },
        {
            "name": "Washing Machine",
            "description": "8KG Front Load Washing Machine with Smart Features",
            "price": "35000.00",
            "stock_quantity": 5,
            "category": "Appliances",
            "warranty_days": 730
        },
        {
            "name": "Refrigerator",
            "description": "Double Door Frost Free Refrigerator",
            "price": "28000.00",
            "stock_quantity": 8,
            "category": "Appliances",
            "warranty_days": 365
        }
    ]
    
    for product_data in products:
        Product.objects.get_or_create(
            vendor=approved_vendor,
            **product_data
        )
    
    print("Sample data created successfully!")

if __name__ == "__main__":
    create_sample_data()