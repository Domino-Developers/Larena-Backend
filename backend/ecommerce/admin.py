from .models import Product
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin import TabularInline
from django.utils.translation import ugettext_lazy as _

from .models import User, Address, Product


class AddressInline(TabularInline):
    model = Address


class CustomUserAdmin(UserAdmin):
    list_display = ("id", "email", "name", "phone")
    list_filter = ("is_staff", "groups")
    search_fields = (
        "name",
        "email",
    )
    ordering = ("email",)
    filter_horizontal = (
        "groups",
        "user_permissions",
    )
    fieldsets = (
        (None, {"fields": ("name", "email", "password", "phone")}),
        (_("Permissions"), {"fields": ("is_staff", "is_superuser")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "name", "phone"),
            },
        ),
    )
    inlines = [
        AddressInline,
    ]



admin.site.register(User, CustomUserAdmin)
admin.site.register(Address)
admin.site.register(Product)
