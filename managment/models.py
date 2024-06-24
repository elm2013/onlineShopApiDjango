from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
User = get_user_model()
# Create your models here.
class Operator(models.Model):    
    mobile = models.CharField(max_length=11)
    birth_date = models.DateField(null=True, blank=True)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'