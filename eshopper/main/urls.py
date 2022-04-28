from django.urls import path

from eshopper.main.views import HomeView, UserRegisterView, UserLoginView, ProfileDetailsView, \
    UserLogoutView, ProductDetailsView, add_to_cart, OrderSummaryView, remove_from_cart, \
    decrease_quantity_of_item_from_cart, CheckoutView, shop, contact

urlpatterns = [
    path('', HomeView.as_view(), name='index'),
    path('registration/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('profile/<int:pk>/', ProfileDetailsView.as_view(), name='profile'),
    path('shop/', shop, name='shop'),
    path('contact/', contact, name='contact'),
    path('product/<slug>/', ProductDetailsView.as_view(), name='product_details'),
    path('cart/', OrderSummaryView.as_view(), name='cart'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('add-to-cart/<slug>', add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<slug>', remove_from_cart, name='remove_from_cart'),
    path('decrease-quantity-of-item-from-cart/<slug>', decrease_quantity_of_item_from_cart,
         name='decrease_quantity_of_item_from_cart'),

]
