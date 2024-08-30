from rest_framework import serializers
from . import models
class MenuItemSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=models.Category.objects.all())
    class Meta:
        model = models.MenuItem
        fields = ['id', 'title', 'price','featured','category']