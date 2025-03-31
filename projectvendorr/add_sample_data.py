import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projectvendorr.settings')
django.setup()

from vendorapp.models import Vendor, Product

def create_sample_data():
    # Create a vendor first
    vendor, created = Vendor.objects.get_or_create(
        name="AR Traders Sample",
        contact_email="artraders@example.com",
        phone="1234567890",
        address="123 Sample Street",
        is_approved=True
    )
    
    # Create sample products
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
            vendor=vendor,
            **product_data
        )
    
    print("Sample data created successfully!")

if __name__ == "__main__":
    create_sample_data()