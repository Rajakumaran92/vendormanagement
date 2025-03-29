from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(Vendor)
admin.site.register(PurchaseOrder)
admin.site.register(PurchaseOrderProduct)
admin.site.register(Product)
admin.site.register(ProductRegistration)
admin.site.register(Invoice)
admin.site.register(WarrantyClaim)
