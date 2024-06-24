# from django.urls import path
# from . import views

# # URLConf
# urlpatterns = [
#     path('products/', views.ProductList.as_view()),
#     # path('products/', views.product_list),
#     path('products/<int:id>', views.product_detail),
#     path('collections/', views.collection_list),
#     path('collections/<int:pk>/', views.collection_detail, name='collection-detail'),
# ]


from django.urls import path
from django.urls.conf import include
from  rest_framework.routers import SimpleRouter
from  rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
# router = SimpleRouter()
# router = DefaultRouter()
router.register('products', views.ProductViewSet, basename='products')
router.register('collections', views.CollectionViewSet,basename='collections')
router.register('customers', views.CustomerView , basename="customers")
router.register('carts', views.CartViewSet,basename='carts')
router.register('carts', views.CartItemViewSet,basename='carts-items')
router.register('orders', views.OrderViewSet, basename='orders')

adress_router = routers.NestedDefaultRouter(router, 'customers', lookup='customer')
adress_router.register('adresses', views.AddAdressView, basename='customer-adresses')

# products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
# products_router.register('reviews', views.ReviewViewSet, basename='product-reviews')
# products_router.register(
#     'images', views.ProductImageViewSet, basename='product-images')

# carts_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
# carts_router.register('items', views.CartItemViewSet, basename='carts-items')


# URLConf
# urlpatterns = router.urls +adress_router.urls
# urlpatterns = router.urls + products_router.urls 
# + carts_router.urls

urlpatterns = [
    path('', include(router.urls,)),
    path('', include(adress_router.urls)),
    # path('', include(carts_router.urls)),
    path('auth/send-code-otp', views.SendCodeView.as_view()),
    path('auth/verification-code-otp', views.VerificationView.as_view()),
    path('auth/login', views.Login.as_view()),
   
]





