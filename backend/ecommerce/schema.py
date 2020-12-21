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


class CreateUser(graphene.Mutation):
    id = graphene.Int()
    name = graphene.String()
    email = graphene.String()
    phone = graphene.Int()

    class Arguments:
        name = graphene.String()
        email = graphene.String()
        phone = graphene.Int()
        password = graphene.String()

    def mutate(self, info, name, email, phone, password):
        user = User(name=name, email=email, phone=phone)
        user.set_password = password
        user.save()

        return CreateUser(
            id=user.id,
            name=user.name,
            email=user.email,
            phone=user.phone,
        )


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()