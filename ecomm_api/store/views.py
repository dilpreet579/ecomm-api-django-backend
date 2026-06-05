from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Cart
from .models import CartItem
from .models import Order
from .models import OrderItem
from .models import Product
from .serializers import CartSerializer
from .serializers import OrderSerializer
from .serializers import ProductSerializer
from .tasks import send_order_confirmation

# --- Product Views ---


class ProductListView(APIView):
    permission_classes = [AllowAny]  # anyone can browse products

    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class ProductDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
            serializer = ProductSerializer(product)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND,
            )


# --- Cart Views ---


class CartView(APIView):
    permission_classes = [IsAuthenticated]  # must be logged in

    def get(self, request):
        # get or create cart for this user
        cart, _created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class CartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # add item to cart
        cart, created = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity", 1)

        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND,
            )

        # if item already in cart, increase quantity
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()

        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def delete(self, request, pk):
        # remove item from cart
        try:
            cart_item = CartItem.objects.get(pk=pk, cart__user=request.user)
            cart_item.delete()
            return Response(
                {"message": "Item removed"}, status=status.HTTP_204_NO_CONTENT,
            )
        except CartItem.DoesNotExist:
            return Response(
                {"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND,
            )


# --- Order Views ---


class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # list all orders for this user
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        # place order from cart
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response(
                {"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST,
            )

        cart_items = cart.items.all()
        if not cart_items:
            return Response(
                {"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST,
            )

        # create the order
        order = Order.objects.create(
            user=request.user, total=cart.get_total(), status="pending",
        )

        # copy cart items to order items
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,  # snapshot price at time of order
            )

        # clear the cart after ordering
        cart_items.delete()

        # .delay() means "run this in background, don't wait for it"
        send_order_confirmation.delay(
            order_id=order.id, user_email=request.user.email, total=order.total,
        )

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            order = Order.objects.get(pk=pk, user=request.user)
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND,
            )
