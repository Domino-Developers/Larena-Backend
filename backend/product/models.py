from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

# Create your models here.


User = get_user_model()


class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    discount = models.IntegerField(default=0)
    stock = models.IntegerField(default=0)

    class Type(models.TextChoices):
        JEWELLERY = "JEWELLERY"
        CLOTH = "CLOTH"

    type = models.CharField(max_length=50, choices=Type.choices)
    description = models.TextField()

    def __str__(self):
        return self.name


class CartObject(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.IntegerField(_("Quantity of the item"), default=1)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.IntegerField(_("Quantity of the item"), default=1)
