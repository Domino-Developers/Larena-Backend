from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import ugettext_lazy as _

from .managers import UserManager

# PRODUCT models


class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    discount = models.IntegerField(default=0)
    stock = models.IntegerField(default=0)

    class Kind(models.TextChoices):
        JEWELLERY = "JEWELLERY"
        CLOTH = "CLOTH"

    kind = models.CharField(max_length=50, choices=Kind.choices)
    description = models.TextField()

    def __str__(self):
        return self.name


# USER models


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    is_staff = models.BooleanField(
        default=False, help_text=_("Designates if a user can log into this admin site")
    )
    phone = models.IntegerField(
        validators=[MinValueValidator(1000000000), MaxValueValidator(9999999999)]
    )
    cart = models.ManyToManyField(Product, through="CartObj")

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = ["name", "phone"]

    objects = UserManager()


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(_("Address name"), max_length=255)
    address1 = models.CharField(_("Address Line 1"), max_length=255)
    address2 = models.CharField(_("Address Line 2"), max_length=255)
    pincode = models.IntegerField(
        validators=[MinValueValidator(100000), MaxValueValidator(999999)]
    )
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    country = models.CharField(max_length=255)


# Order and cart orders


class CartObj(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.IntegerField(_("Quantity of product"), default=1)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through="OrderObj")
    order_timestamp = models.DateTimeField(auto_now_add=True)

    class DeliveryStatus(models.TextChoices):
        OR = "OR", "ordered"
        OFD = "OFD", "out_for_delivery"
        DL = "DL", "delivered"

    status = models.CharField(
        max_length=3, choices=DeliveryStatus.choices, default=DeliveryStatus.OR
    )


class OrderObj(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.IntegerField(_("Quantity of product"), default=1)

    class Meta:
        unique_together = ("order", "product")


# REVIEW model


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    text = models.CharField(max_length=255, null=True)

    class Meta:
        unique_together = ("user", "product")


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="likes")

    class Meta:
        unique_together = ("user", "review")