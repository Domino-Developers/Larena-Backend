import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required

from .models import *


class CartType(DjangoObjectType):
    class Meta:
        model = CartObj
        exclude = ("user",)


class PProductType(DjangoObjectType):
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

    @login_required
    def resolve_me(self, info):
        return info.context.user
