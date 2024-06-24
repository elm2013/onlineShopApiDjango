from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializer import *
# Create your views here.
class ReviewViewSet(ModelViewSet): 

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_content_type(self):
        if 'product_id' in self.kwargs:
            return ContentType.objects.get(model='product')
        elif 'article_id' in self.kwargs:
            return ContentType.objects.get(model='article')
        return None
    
    def perform_create(self, serializer):
        content_type = self.get_content_type()
        if content_type:
            serializer.validated_data['content_type'] = content_type
            serializer.validated_data['object_id'] = self.kwargs.get('product_id') or self.kwargs.get('article_id')
        else:
            return Response({'error': 'Invalid content type'}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()