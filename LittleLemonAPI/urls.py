from django.urls import path, include
from . import views

urlpatterns = [
    path('', include('djoser.urls')),
    path('menu-items', views.menuitemsView),
    path('menu-items/<int:pk>', views.menu_item_single)
]