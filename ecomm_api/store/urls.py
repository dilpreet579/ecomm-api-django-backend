from django.urls import path

from . import views

urlpatterns = [
    # products
    path("products/", views.ProductListView.as_view()),
    path("products/<int:pk>/", views.ProductDetailView.as_view()),
    # cart
    path("cart/", views.CartView.as_view()),
    path("cart/items/", views.CartItemView.as_view()),
    path("cart/items/<int:pk>/", views.CartItemView.as_view()),
    # orders
    path("orders/", views.OrderListView.as_view()),
    path("orders/<int:pk>/", views.OrderDetailView.as_view()),
]
