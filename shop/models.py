from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from uuid import uuid4
# Create your models here.

class State(models.Model):
    name = models.CharField(max_length=50)

class City(models.Model):
    parent = models.ForeignKey(State, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

class Collection (models.Model):
    title = models.CharField(max_length=20)
    # slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='store/images')
    featured_product = models.ForeignKey(
        'Product', on_delete=models.SET_NULL, null=True, related_name='+', blank=True)
    
    
    def __str__(self) -> str:
        return self.title

# class Customer(models.Model):   
    # mobile = models.CharField(max_length=11,unique=True)
    # birth_date = models.DateField(null=True, blank=True)   
    # user = models.OneToOneField(
    #    User , on_delete=models.CASCADE)
    # USERNAME_FIELD = 'mobile'
    # def __str__(self):
    #     return f'{self.user.first_name} {self.user.last_name}'
    
class Account(AbstractUser):
    ROLE_ADMIN = 'admin'
    ROLE_OPERATOR = 'operator'
    ROLE_CUSTOMER = 'customer'
    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Admin'),
        (ROLE_OPERATOR , 'Operator'),
        (ROLE_CUSTOMER , 'Customer'),
       
    ]

    STATUS_PENDING = '0'
    STATUS_COMPLETE = '1'    
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_COMPLETE, 'Complete'),
       
    ]
    mobile = models.CharField(max_length=11, unique=True)
    birth_date = models.DateField(null=True, blank=True)  
    status = models.CharField(
        max_length=1, choices=STATUS_CHOICES, default=STATUS_PENDING)  
    role =  models.CharField(
        max_length=10, choices=ROLE_CHOICES, default=ROLE_CUSTOMER)  
    # REQUIRED_FIELDS = ["username"]
    USERNAME_FIELD = 'mobile'

class OTP(models.Model):
    code = models.CharField(max_length=6,null=True,blank=True)
    mobile = models.CharField(max_length=11, unique=True)
    send_date = models.DateTimeField(null=True, blank=True)    

class Address(models.Model):
    state = models.ForeignKey(
        State, on_delete=models.CASCADE)
    city = models.ForeignKey(
        City, on_delete=models.CASCADE)
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE)
    address = models.TextField(max_length=700, blank=True, null=True)
    postalCode = models.CharField(max_length=15, blank=True, null=True)
    # lat = models.
    # long = models.lon
    is_Active = models.BooleanField(default=False)
   
class Product(models.Model):
    title = models.CharField(max_length=50)
    slug = models.SlugField()
    description = models.TextField(max_length=500)
    unit_price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(1)])
    inventory = models.IntegerField(validators=[MinValueValidator(0)])
    last_update = models.DateTimeField(auto_now=True)
    is_show = models.BooleanField(default=True)
    collection = models.ForeignKey(
        Collection, on_delete=models.PROTECT, related_name='products')
    
    # promotions = models.ManyToManyField(Promotion, blank=True)
    # brand = models.ForeignKey(Collection, on_delete=models.PROTECT, related_name='products')

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ['title']

class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(
        upload_to='store/images')

class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    account = models.OneToOneField(Account, on_delete=models.PROTECT)
    create_date = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)]
    )

    class Meta:
        unique_together = [['cart', 'product']]

class Order(models.Model):
    PAYMENT_STATUS_PENDING = 'P'
    PAYMENT_STATUS_COMPLETE = 'C'
    PAYMENT_STATUS_FAILED = 'F'
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, 'Pending'),
        (PAYMENT_STATUS_COMPLETE, 'Complete'),
        (PAYMENT_STATUS_FAILED, 'Failed')
    ]
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    adress =  models.ForeignKey(Address, on_delete=models.PROTECT)
    serial = models.UUIDField(primary_key=True, default=uuid4)
    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=1, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_PENDING)

    class Meta:
        permissions = [
            ('cancel_order', 'Can cancel order')
        ]

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name='orderitems')
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
