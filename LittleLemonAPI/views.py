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
        items = models.MenuItem.objects.all().values()
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
@permission_classes([IsAuthenticated])
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