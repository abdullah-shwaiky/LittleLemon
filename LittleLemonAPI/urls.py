from django.urls import path, include
from . import views

urlpatterns = [
    path('', include('djoser.urls')),
    path('menu-items', views.menuitemsView),
    path('menu-items/<int:pk>', views.menu_item_single),
    path('groups/manager/users', views.manager_users),
    path('groups/manager/users/<int:pk>', views.manager_single_user),
    path('groups/delivery-crew/users', views.delivery_users),
    path('groups/delivery-crew/users/<int:pk>', views.delivery_single_user),
    path('cart/menu-items', views.cart_items),
    path('orders', views.orders),
    path('orders/<int:pk>', views.single_orders),
]