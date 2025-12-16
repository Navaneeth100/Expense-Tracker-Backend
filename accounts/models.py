from django.db import models

# Create your models here.

class MenuList(models.Model):
    menu_name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=100, unique=True)
    path = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.menu_name