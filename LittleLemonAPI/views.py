import json
from django.shortcuts import render
from . import models, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
# Create your views here.

@api_view(['GET','POST',])
@permission_classes([IsAuthenticated])
def menuitemsView(request):
    user_groups =  [group.name for group in  request.user.groups.all()]
    if request.method == 'GET':
        if 'Manager' in user_groups:
            return Response({"error": "Managers can't view menu-items"}, status.HTTP_403_FORBIDDEN)
        items = models.MenuItem.objects.all().values()
        return Response({"menuitems":items}, status.HTTP_200_OK)
    else:
        if 'Manager' not in user_groups:
            return Response({"error": "Only managers can edit menu-items"}, status.HTTP_403_FORBIDDEN)
        try:
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
@permission_classes([IsAuthenticated])
def menu_item_single(request, pk):
    
    if request.method == 'GET':
        try:
            object = models.MenuItem.objects.get(pk=pk)
            data = serializers.MenuItemSerializer().to_representation(object)
            return Response(data, status.HTTP_200_OK)
        except:
            return Response({"error": "Not Found"}, status.HTTP_404_NOT_FOUND)
        
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