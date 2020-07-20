from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.store, name="store"),
    path('cart/', views.cart, name="cart"),
    path('product/<int:id>', views.product, name="product"),
    path('checkout/', views.checkout, name="checkout"),
    path('update_item/', views.update_item, name="update_item"),
    path('process_order/', views.process_order, name="process_order"),

    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),
]
