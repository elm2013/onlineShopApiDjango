from rest_framework import serializers
from .models import *
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'date', 'name', 'description']

    # def create(self, validated_data):
    #     product_id = self.context['product_id']
    #     return Review.objects.create(object_id=product_id,content_type=self.context['content_type'], **validated_data)