from django.contrib import admin

from .models import Cart
from .models import CartItem
from .models import Order
from .models import OrderItem
from .models import Product

admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
