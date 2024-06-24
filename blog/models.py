from django.db import models
from django.core.validators import MinLengthValidator
from managment.models import Operator
# Create your models here.

class Article (models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField( validators=[MinLengthValidator(20)])
    auther = models.ForeignKey(Operator,on_delete=models.CASCADE,related_name='auther')
    image = models.ImageField(upload_to='store/images',null=True,blank=True)
    create_date = models.DateTimeField(auto_now=True)
    update_date = models.DateTimeField(auto_now=True)

