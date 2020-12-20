import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required
from django.db.models import Q

from .models import *


class CartType(DjangoObjectType):
    class Meta:
        model = CartObj
        exclude = ("user",)


class ReviewType(DjangoObjectType):
    class Meta:
        model = Review


class ProductType(DjangoObjectType):
    class Meta:
        model = Product


class UserType(DjangoObjectType):
    class Meta:
        model = User

    cart = graphene.List(CartType)

    def resolve_cart(parent, info):
        result = CartObj.objects.filter(user=parent)
        return result


class Query(graphene.ObjectType):
    me = graphene.Field(UserType)

    products = graphene.List(
        ProductType,
        first=graphene.Int(),
        skip=graphene.Int(),
        search=graphene.String(),
        kind=graphene.String(),
    )
    product = graphene.Field(ProductType, id=graphene.String())

    @login_required
    def resolve_me(self, info):
        return info.context.user

    def resolve_product(self, info, id, **kwargs):
        return Product.objects.get(pk=id)

    def resolve_products(
        self, info, first=None, skip=None, search=None, kind=None, **kwargs
    ):
        qs = Product.objects.all()

        if search:
            qs = qs.filter(Q(name__icontains=search))

        if kind:
            qs = qs.filter(Q(kind=kind))

        if skip:
            qs = qs[skip:]

        if first:
            qs = qs[:first]

        return qs
