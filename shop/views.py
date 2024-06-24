from django_filters.rest_framework import DjangoFilterBackend
from django.db.models.aggregates import Count
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import  DestroyModelMixin, RetrieveModelMixin,UpdateModelMixin
from rest_framework.permissions import AllowAny, DjangoModelPermissions, DjangoModelPermissionsOrAnonReadOnly, IsAdminUser, IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .filter import ProductFilter
from .pagination import DefaultPagination
from .models import *
from .serializer import *
import random
from django.utils import timezone
from datetime import timedelta
import datetime

# Create your views here.
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.select_related('collection').all()
    # .prefetch_related('images').all()
    serializer_class =product_serializer
    filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]
    # filterset_fields = ['collection_id']
    filterset_class = ProductFilter
    pagination_class = DefaultPagination
    search_fields = ['title', 'description']
    # ordering_fields = ['unit_price', 'last_update']
    # permission_classes = [IsAdminOrReadOnly]



    def get_serializer_context(self):
        return {'request': self.request}
    
    def destroy(self, request,*args,**kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count()>0:
            return Response({'error': 'Product cannot be deleted because it is associated with an order item.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)

class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(products_count=Count('products')).all()
    serializer_class= collection_serializer

    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection_id=kwargs['pk']):
            return Response({'error': 'Collection cannot be deleted because it includes one or more products.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        return super().destroy(request, *args, **kwargs)

class SendCodeView(APIView):
    permission_classes = (AllowAny,)
    
    """
    Send a verification code to a user's phone number
    """
    @swagger_auto_schema(request_body=OTPSerializer)
    def post(self, request):
        serializer = OTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data['mobile']       
        otp, created = OTP.objects.get_or_create(mobile=phone_number)        
        current_time = timezone.now()
        if otp.send_date is not None and (current_time - otp.send_date) <= timedelta(minutes=2):
            return Response({"message":"after 2 min try again ."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        code = random.randrange(100000, 999999)
        otp.code = code
        otp.send_date = timezone.now()
        otp.save()
        
        # sendSms(phone_number, code)        
        print(code)
        return Response({"message":"Successfuly code send ."}, status=status.HTTP_200_OK)

class VerificationView(APIView):
    permission_classes = (AllowAny,)
    @swagger_auto_schema(request_body=VerificationSerializer)
    def post(self,request):
        serializer = VerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data['mobile']
        otp= OTP.objects.filter(mobile=phone_number).first()
        if otp.send_date> timezone.now():
           raise ValidationError({"message": "Your code has expired."})
        if otp.code != serializer.validated_data['code']:
            raise ValidationError({"message": "Your code is invalid."})
        #create user
        user, created = Account.objects.get_or_create(mobile=phone_number)
        Cart.objects.get_or_create(account=user)
        token=get_tokens_for_user(user)
        
        return Response({"message":"success","token":token}, status=status.HTTP_200_OK)

class Login(APIView):    
    permission_classes = (AllowAny,)
    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self,request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data['mobile']
        user = Account.objects.get(mobile=phone_number)  
        ViewCustomer = ViewCustomerSerializer(user)
        # if not user or user.password != hash(serializer.validated_data['password']):
        if not user.check_password(serializer.validated_data['password']):
            return Response({"message":"user not found"}, status=status.HTTP_404_NOT_FOUND) 
        token = get_tokens_for_user(user)
        Cart.objects.get_or_create(account=user)
        
        return Response({"message":"success","token":token,"user":ViewCustomer.data}, status=status.HTTP_200_OK)

class CustomerView( viewsets.GenericViewSet)  :
    queryset= Account.objects.all()
   
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ViewCustomerSerializer
        return UpdateCustomerSerializer

    permission_classes =(IsAdminUser,)
   
    @action(detail=False, methods=['GET','PATCH','PUT'], permission_classes=[IsAuthenticated,])
    def me(self, request):
        customer = Account.objects.get(
            pk=request.user.id)
        if request.method == 'GET':
            serializer = ViewCustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == 'PUT' or  request.method == 'PATCH':
            serializer = UpdateCustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

class AddAdressView(ModelViewSet):
    serializer_class = AdressSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        customer_pk = self.kwargs.get('customer_pk')  # Get customer_pk from kwargs with default None
        if customer_pk is not None:
            return Address.objects.filter(account_id=customer_pk)
        return Address.objects.none()  # Return empty queryset if customer_pk is not present
    
    def get_serializer_context(self):
        customer_pk = self.kwargs.get('customer_pk')  # Get customer_pk from kwargs with default None
        return {'user_id': customer_pk}        
  
class CartViewSet(GenericViewSet):
    queryset =  Cart.objects.prefetch_related('items__product').all()  
    serializer_class = CartSerializer
 
    @action(detail=False, methods=['GET'], )
    def myCart(self, request):
        cart= Cart.objects.prefetch_related('items__product').get(account=request.user.id)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

class CartItemViewSet(ModelViewSet):
    http_method_names = [ 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_serializer_context(self):
        cart_pk= Cart.objects.prefetch_related('items__product').get(account=self.request.user.id).pk
        return {'cart_id': cart_pk}

    def get_queryset(self):
        cart_pk= Cart.objects.prefetch_related('items__product').get(account=self.request.user.id).pk  # Get customer_pk from kwargs with default None
        if cart_pk is not None:
            return CartItem.objects \
            .filter(cart_id=cart_pk) \
            .select_related('product')
        return CartItem.objects.none()  # Return empty queryset if customer_pk is not present

class OrderViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(
            data=request.data,
            context={'user_id': self.request.user.id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        elif self.request.method == 'PATCH':
            return UpdateOrderSerializer
        return OrderSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Order.objects.all()
        customer= Account.objects.get(pk=user.id)
        return Order.objects.filter(account=customer)
        
    

 