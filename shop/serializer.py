from decimal import Decimal
from django.db import transaction
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import *
User = get_user_model()
class collection_serializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count']

    products_count = serializers.IntegerField(read_only=True)

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']
    def create(self, validated_data):
        product_id = self.context['product_id']
        return ProductImage.objects.create(product_id=product_id, **validated_data)
    
class product_serializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    collection = collection_serializer()
    
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'slug', 'inventory', 'unit_price', 'price_with_tax', 'collection','images']

    price_with_tax = serializers.SerializerMethodField(
        method_name='calculate_tax')

    def calculate_tax(self, product: Product):
        return product.unit_price * Decimal(1.1)

    def calculate_price(self,product:Product):
        return product.unit_price * Decimal(10)

class ViewCustomerSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Account
        fields = ['id', 'mobile','first_name','last_name','birth_date','email','role','status']
    
class UpdateCustomerSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Account
        fields = [ 'first_name','last_name','birth_date','email','password']
        

    def update(self, instance:Account, validated_data):      
        super().update(instance, validated_data)
        instance.set_password(validated_data['password'])
        if validated_data['first_name']!='' or validated_data['last_name']!='':
            instance.status=Account.STATUS_COMPLETE
        instance.save()
        return instance

class OTPSerializer(serializers.Serializer):   
    code = serializers.CharField(read_only=True)
    mobile = serializers.CharField(max_length=11,)
    send_date = serializers.DateTimeField(read_only=True)    

    # class Meta:
    #     model = OTP
    #     fields = [ 'mobile']
    
class VerificationSerializer(serializers.Serializer):   
    code = serializers.CharField(max_length=6,)
    mobile = serializers.CharField(max_length=11,)
    send_date = serializers.DateTimeField(read_only=True)  

class LoginSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=11,)
    password = serializers.CharField()
    
class AdressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        exclude = ('account', )
    
    def create(self, validated_data):
        account_id = self.context['user_id']
        return Address.objects.create(account_id=account_id, **validated_data)
  
class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'unit_price']


class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart_item: CartItem):
        return cart_item.quantity * cart_item.product.unit_price

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']


class CartSerializer(serializers.ModelSerializer):  
    id = serializers.UUIDField(read_only=True) 
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart):
        return sum([item.quantity * item.product.unit_price for item in cart.items.all()])
  

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price']


class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError(
                'No product with the given ID was found.')
        return value

    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']

        try:
            cart_item = CartItem.objects.get(
                cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(
                cart_id=cart_id, **self.validated_data)

        return self.instance

    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']


class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'unit_price', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        # fields = ['id', 'account', 'placed_at', 'payment_status', 'items']
        fields = '__all__'


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status']

class CreateOrderSerializer(serializers.Serializer):
    # cart_id = serializers.UUIDField(read_only=True)

    def save(self, **kwargs):
        with transaction.atomic():
            
            if not Cart.objects.filter(account=self.context['user_id']).exists():
                 raise serializers.ValidationError(
                'No cart with the given ID was found.')
            cart_id=Cart.objects.get(account=self.context['user_id']).pk
            if CartItem.objects.filter(cart_id=cart_id).count() == 0:
                raise serializers.ValidationError('The cart is empty.')
            
            
            if not Address.objects.filter(account=self.context['user_id'],is_Active=True).exists():
                 raise serializers.ValidationError(
                'pleas befor submit order  select your  adress.')
            selected_adress = Address.objects.get(account=self.context['user_id'],is_Active=True)

            customer = Account.objects.get(pk=self.context['user_id'])
            order = Order.objects.create(account=customer,adress=selected_adress)

            cart_items = CartItem.objects \
                .select_related('product') \
                .filter(cart_id=cart_id)
            order_items = [
                OrderItem(
                    order=order,
                    product=item.product,
                    unit_price=item.product.unit_price,
                    quantity=item.quantity
                ) for item in cart_items
            ]
            OrderItem.objects.bulk_create(order_items)

            Cart.objects.filter(pk=cart_id).delete()
            Cart.objects.create(account=self.context['user_id'])

            # order_created.send_robust(self.__class__, order=order)

            return order
