import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required
from django.db.models import Q
from graphql import GraphQLError

from .models import *


class CartType(DjangoObjectType):
    class Meta:
        model = CartObj
        exclude = ("user",)


class ReviewType(DjangoObjectType):
    class Meta:
        model = Review


class LikeType(DjangoObjectType):
    class Meta:
        model = Like


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


class CreateAddress(graphene.Mutation):
    name = graphene.String()
    address1 = graphene.String()
    address2 = graphene.String()
    pincode = graphene.Int()
    city = graphene.String()
    state = graphene.String()
    country = graphene.String()

    class Arguments:
        name = graphene.String()
        address1 = graphene.String()
        address2 = graphene.String()
        pincode = graphene.Int()
        city = graphene.String()
        state = graphene.String()
        country = graphene.String()

    def mutate(self, info, name, address1, address2, pincode, city, state, country):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("You must be logged in to update Address!")

        address = Address(
            user=user,
            name=name,
            address1=address1,
            address2=address2,
            pincode=pincode,
            city=city,
            state=state,
            country=country,
        )
        address.save()

        return CreateAddress(
            name=address.name,
            address1=address.address1,
            address2=address.address2,
            pincode=address.pincode,
            city=address.city,
            state=address.state,
            country=address.country,
        )


class CreateUser(graphene.Mutation):
    id = graphene.String()
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


class AddReview(graphene.Mutation):
    id = graphene.String()
    rating = graphene.Int()
    text = graphene.String()

    class Arguments:
        rating = graphene.Int()
        text = graphene.String()
        productId = graphene.String()

    @login_required
    def mutate(self, info, rating, productId, **kwargs):
        text = kwargs.get("text", None)
        user = info.context.user
        review = Review(user=user, product_id=productId, rating=rating, text=text)
        review.save()

        return AddReview(id=review.id, rating=review.rating, text=review.text)


class DeleteReview(graphene.Mutation):
    id = graphene.String()

    class Arguments:
        reviewId = graphene.String()

    @login_required
    def mutate(self, info, reviewId):
        user = info.context.user
        review = Review.objects.get(pk=reviewId)

        if review.user.id != user.id:
            raise GraphQLError("You must be author of the review to delete it.")

        review.delete()

        return DeleteReview(id=reviewId)


class LikeReview(graphene.Mutation):
    id = graphene.String()

    class Arguments:
        reviewId = graphene.String()

    @login_required
    def mutate(self, info, reviewId):
        user = info.context.user
        like = Like(user=user, review_id=reviewId)
        like.save()

        return LikeReview(id=like.id)


class UnlikeReview(graphene.Mutation):
    id = graphene.String()

    class Arguments:
        reviewId = graphene.String()

    @login_required
    def mutate(self, info, reviewId):
        user = info.context.user
        like = Like.objects.get(user=user, review_id=reviewId)
        id = like.id
        like.delete()

        return UnlikeReview(id=id)


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    create_address = CreateAddress.Field()
    add_review = AddReview.Field()
    delete_review = DeleteReview.Field()
    like_review = LikeReview.Field()
    unlike_review = UnlikeReview.Field()
