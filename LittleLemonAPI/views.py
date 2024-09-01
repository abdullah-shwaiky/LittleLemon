import json
from datetime import date
from django.forms.models import model_to_dict
from django.shortcuts import render
from django.contrib.auth.models import User, Group
from . import models, serializers
from .permissions import IsManager
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator, EmptyPage
from rest_framework.throttling import UserRateThrottle
# Create your views here.

@api_view(['GET','POST',])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def menuitemsView(request):
    user_groups =  [group.name for group in  request.user.groups.all()]
    if request.method == 'GET':
        search_title = request.query_params.get('title')
        search_price = request.query_params.get('price')
        page = request.query_params.get('page', default = 1)
        perpage = request.query_params.get('per_page', default = 2)
        items = models.MenuItem.objects.all().values()
        if search_title:
            items = items.filter(title=search_title).values()
        if search_price:
            items = items.order_by(search_price)
        paginator = Paginator(items, per_page=perpage)
        try:
            items = [page for page in paginator.page(number=page)]
        except EmptyPage:
            items = []
        print(items)
        return Response({"menuitems":items}, status.HTTP_200_OK)
    else:
        if 'Manager' not in user_groups:
            return Response({"error": "Only managers can edit menu-items"}, status.HTTP_403_FORBIDDEN)
        try:
            body = json.loads(request.body.decode('utf-8'))
            title = body['title']
            price = body['price']
            featured = body['featured']
            category = body['category']
        except:
            return Response({"message": "Missing arguments"}, status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            body = json.loads(request.body.decode('utf-8'))
            category_check = models.Category.objects.filter(title=category)
            if not category_check:
                category_object = models.Category.objects.create(title = category)
                category_object.save()
            category_object = models.Category.objects.filter(title=category).first()
                
            object = models.MenuItem(title=title, price=price, featured=featured, category=category_object)
            object.save()
            return Response({"message": "Item Created Successfully"}, status.HTTP_201_CREATED)


@api_view(['GET','PUT','PATCH','DELETE'])
@permission_classes([IsAuthenticated | IsAdminUser])
@throttle_classes([UserRateThrottle])
def menu_item_single(request, pk):
    
    if request.method == 'GET':
        try:
            object = models.MenuItem.objects.get(pk=pk)
            data = serializers.MenuItemSerializer().to_representation(object)
            return Response(data, status.HTTP_200_OK)
        except:
            return Response({"error": "Object Not Found"}, status.HTTP_404_NOT_FOUND)
        
    if request.method == 'PUT':
        body = json.loads(request.body.decode('utf-8'))
        try:
                title = body['title']
                price = body['price']
                featured = body['featured']
                category = body['category']
        except:
            return Response({"message": "Missing arguments"}, status.HTTP_400_BAD_REQUEST)
        category_check = models.Category.objects.filter(title=category)
        if not category_check:
            category_object = models.Category.objects.create(title = category)
            category_object.save()
        category_object = models.Category.objects.filter(title=category).first()
            
        object = models.MenuItem(id = pk, title=title, price=price, featured=featured, category=category_object)
        object.save()
        return Response({"message": "Item Created Successfully"}, status.HTTP_201_CREATED)
    
    if request.method == 'PATCH':
        try:
            object = models.MenuItem.objects.get(pk=pk)
        except:
            return Response({"error": "Object Not Found"}, status.HTTP_404_NOT_FOUND)
        try:
            data = request.data
            if 'category' in request.data:
                try:
                    category = models.Category.objects.get(title=request.data['category'])
                except:
                    category = models.Category(title=request.data['category'])
                    category.save()
                data['category'] = category.pk
                
            serializer = serializers.MenuItemSerializer(object, data=data, partial = True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Item edited successfully."}, status.HTTP_201_CREATED)
            else:
                print('HERE', serializer.errors)
                return Response({"error": "Change only one field"}, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({"error": "Change only one field"}, status.HTTP_400_BAD_REQUEST)
        
            
    if request.method == 'DELETE':
        try:
            object = models.MenuItem.objects.get(pk=pk)
            object.delete()
            return Response({"message": "Object deleted successfully"}, status.HTTP_200_OK)
        except:
            return Response({"error": "Object Not Found"}, status.HTTP_404_NOT_FOUND)

@api_view(['GET','POST',])
@permission_classes([IsAuthenticated | IsAdminUser, IsManager | IsAdminUser])
@throttle_classes([UserRateThrottle])
def manager_users(request):
    if request.method == 'GET':
        managers = User.objects.filter(groups__name='Manager')
        result = [manager.get_username() for manager in managers]
        return Response({"managers": result}, status.HTTP_200_OK)
    else:
        try:
            body = json.loads(request.body.decode('utf-8'))
            user = User.objects.get(username=body['username'])
        except:
            return Response({"error": "User not found"}, status.HTTP_400_BAD_REQUEST)
        group = Group.objects.get(name='Manager')
        user.groups.add(group)
        return Response({"message": "User added to managers."}, status.HTTP_201_CREATED)

@api_view(['DELETE',])
@permission_classes([IsAuthenticated, IsManager | IsAdminUser])
@throttle_classes([UserRateThrottle])
def manager_single_user(request, pk):
    try:
        user = User.objects.get(pk=pk)
        group = Group.objects.get(name='Manager')
        user.groups.remove(group)
        return Response({"message": "User removed from Managers"}, status.HTTP_200_OK)
    except:
        return Response({"error": "User not found."}, status.HTTP_404_NOT_FOUND)
    
    
@api_view(['GET','POST',])
@permission_classes([IsAuthenticated, IsManager | IsAdminUser])
@throttle_classes([UserRateThrottle])
def delivery_users(request):
    if request.method == 'GET':
        delivery = User.objects.filter(groups__name='delivery-crew')
        result = [driver.get_username() for driver in delivery]
        return Response({"delivery-crew": result}, status.HTTP_200_OK)
    else:
        try:
            body = json.loads(request.body.decode('utf-8'))
            user = User.objects.get(username=body['username'])
        except:
            return Response({"error": "User not found"}, status.HTTP_400_BAD_REQUEST)
        group = Group.objects.get(name='delivery-crew')
        user.groups.add(group)
        return Response({"message": "User added to delivery crew."}, status.HTTP_201_CREATED)
        

@api_view(['DELETE',])
@permission_classes([IsAuthenticated, IsManager | IsAdminUser])
@throttle_classes([UserRateThrottle])
def delivery_single_user(request, pk):
    try:
        user = User.objects.get(pk=pk)
        group = Group.objects.get(name='delivery-crew')
        user.groups.remove(group)
        return Response({"message": "User removed from delivery crew"}, status.HTTP_200_OK)
    except:
        return Response({"error": "User not found."}, status.HTTP_404_NOT_FOUND)


@api_view(['GET','POST','DELETE',])
@permission_classes([IsAuthenticated | IsAdminUser])
@throttle_classes([UserRateThrottle])
def cart_items(request):
    current_user = request.user
    if request.method == 'GET':
        try:
            cart = models.Cart.objects.filter(user=current_user).values()
            return Response({"cart": cart}, status.HTTP_200_OK)
        except:
            return Response({"error": "No cart for current user."}, status.HTTP_404_NOT_FOUND)
    elif request.method == 'POST':
        body = json.loads(request.body.decode('utf-8'))
        try:
            item_id = body['item_id']
            item = models.MenuItem.objects.get(pk = item_id)
        except:
            return Response({"message": "Item not found."}, status.HTTP_404_NOT_FOUND)
        try:
            cart = models.Cart(user = current_user, menuitem = item, quantity = 1, unit_price = item.price, price = item.price)
            cart.save()
        except:
            return Response({"error": "Item already in cart"}, status.HTTP_400_BAD_REQUEST)
        
        return Response({"message": "Cart created successfully."}, status.HTTP_201_CREATED)
    else:
        try:
            cart = models.Cart.objects.filter(user=current_user)
            cart.delete()
            return Response({"message": "Cart deleted successfully."}, status.HTTP_200_OK)
        except:
            return Response({"error": "No cart for current user."}, status.HTTP_404_NOT_FOUND)


@api_view(['GET','POST',])
@permission_classes([IsAuthenticated | IsAdminUser])
@throttle_classes([UserRateThrottle])
def orders(request):
    user_groups =  [group.name for group in  request.user.groups.all()]
    current_user = request.user
    if 'delivery-crew' in user_groups:
        if request.method != 'GET':
            return Response({"error": "Unauthorized request"}, status.HTTP_403_FORBIDDEN)
        else:
            search_title = request.query_params.get('title')
            search_price = request.query_params.get('price')
            page = request.query_params.get('page', default = 1)
            perpage = request.query_params.get('per_page', default = 2)
            order_items = models.Order.objects.filter(delivery_crew=current_user).values()
            if search_title:
                order_items = order_items.filter(title=search_title).values()
            if search_price:
                order_items = order_items.order_by(search_price).values()
            paginator = Paginator(order_items, per_page= perpage)
            try: 
                order_items = [page for page in paginator.page(number=page)]
            except EmptyPage:
                order_items = []
            return Response({"orders": order_items}, status.HTTP_200_OK)
    elif 'Manager' not in user_groups:
        if request.method == 'POST':
            try:
                cart = models.Cart.objects.filter(user=current_user)
                assert cart
                cart_values = cart.values()
            except:
                return Response({"error": "No cart for current user."}, status.HTTP_404_NOT_FOUND)
            total = 0
            for item in cart_values:
                total += item['price']
            try:
                order = models.Order(user=current_user, total = total, date=date.today())
                order.save()
                for item in cart_values:
                    menuitem = models.MenuItem.objects.get(pk = item['menuitem_id'])
                    order_item = models.OrderItem(order=current_user,menuitem =menuitem, quantity = item['quantity'],unit_price = item['unit_price'], price = item['price'])
                    print('HERE')
                    order_item.save()
            except:
                return Response({"error": "Order already exists"}, status.HTTP_400_BAD_REQUEST)
            cart.delete()
            return Response({"message": f"Order {order.id} created successfully."}, status.HTTP_201_CREATED)
        else:
            search_title = request.query_params.get('title')
            search_price = request.query_params.get('price')
            page = request.query_params.get('page', default = 1)
            perpage = request.query_params.get('per_page', default = 2)
            order_items = models.Order.objects.filter(user=current_user)
            if search_title:
                order_items = order_items.filter(title=search_title).values()
            if search_price:
                order_items = order_items.order_by(search_price)
            paginator = Paginator(order_items, per_page= perpage)
            try: 
                order_items = [page for page in paginator.page(number=page)]
            except EmptyPage:
                order_items = []
            order_items = [model_to_dict(item) for item in order_items]
            return Response({"orders": order_items}, status.HTTP_200_OK)
    else:
        if request.method == 'POST':
            return Response({"error": "Managers cannot add orders"})
        else:
            order_items = models.Order.objects.all()
            search_title = request.query_params.get('title')
            search_price = request.query_params.get('price')
            page = request.query_params.get('page', default = 1)
            perpage = request.query_params.get('per_page', default = 2)
            if search_title:
                order_items = order_items.filter(title=search_title).values()
            if search_price:
                order_items = order_items.order_by(search_price)
            paginator = Paginator(order_items, per_page= perpage)
            try: 
                order_items = [page for page in paginator.page(number=page)]
            except EmptyPage:
                order_items = []
            order_items = [model_to_dict(item) for item in order_items]
            return Response({"orders": order_items}, status.HTTP_200_OK)

@api_view(['GET','PUT','PATCH','DELETE'])
@permission_classes([IsAuthenticated | IsAdminUser])
@throttle_classes([UserRateThrottle])
def single_orders(request, pk):
    user_groups =  [group.name for group in  request.user.groups.all()]
    if 'Manager' in user_groups or request.user.is_staff:
        if request.method == 'GET':
            try:
                order = models.Order.objects.filter(pk = pk).values()
                return Response({"order": order}, status.HTTP_200_OK)
            except:
                return Response({"error": "Order does not exist or expired"}, status.HTTP_404_NOT_FOUND)
        elif request.method == 'DELETE':
            try:
                order = models.Order.objects.filter(pk = pk).values()
                order.delete()
                return Response({"message": "Order deleted successfully"}, status.HTTP_200_OK)
            except:
                return Response({"error": "Order does not exist or expired"}, status.HTTP_404_NOT_FOUND)
        elif request.method == 'PATCH':
            try:
                order = models.Order.objects.get(pk = pk)
            except:
                return Response({"error": "Order does not exist or expired"}, status.HTTP_404_NOT_FOUND)
            body = json.loads(request.body.decode('utf-8'))
            username = body['username']
            del body['username']
            if len(body.keys()):
                return Response({"error": "Only assigning driver is allowed"}, status.HTTP_400_BAD_REQUEST)
            try:
                user = User.objects.get(username=username)
            except:
                return Response({"error": "Delivery crew member not found"}, status.HTTP_404_NOT_FOUND)
            order.delivery_crew = user
            order.save()
            return Response({"message": f"Driver {username} assigned"}, status.HTTP_200_OK)
    elif 'delivery-crew' in user_groups:
        if request.method == 'PATCH':
            body = json.loads(request.body.decode('utf-8'))
            try:
                body_status = body['status']
                del body['status']
                print(body)
            except:
                if len(body.keys()):
                    return Response({"error": "Only status changing is allowed"}, status.HTTP_403_FORBIDDEN)
            
            try:
                order = models.Order.objects.get(pk = pk)
            except:
                return Response({"error": "Order does not exist or expired"}, status.HTTP_404_NOT_FOUND)
            order.status = body_status
            order.save()
            return Response({"message": "Status updated. Thank you for delivering."}, status.HTTP_201_CREATED)
        elif request.method == 'GET':
            order = models.Order.objects.get(pk = pk)
            if order.delivery_crew == request.user:
                return Response({"order": model_to_dict(order)})
    else:
        try:
            order = models.Order.objects.filter(pk = pk).first()
            assert order
        except:
            return Response({"error": "Order does not exist or expired"}, status.HTTP_404_NOT_FOUND)
        if order.user == request.user:
            return Response({"order": model_to_dict(order)}, status.HTTP_200_OK)
        else:
            return Response({"error": "You cannot view this order"}, status.HTTP_403_FORBIDDEN)