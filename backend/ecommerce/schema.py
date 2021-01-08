from django.db.models import Q
import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required

from .models import *


class CartType(DjangoObjectType):
    class Meta:
        model = CartObj


class ReviewType(DjangoObjectType):
    class Meta:
        model = Review

    likes_count = graphene.Int()
    is_liked = graphene.Boolean()

    def resolve_likes_count(parent, info):
        return Like.objects.filter(review=parent).count()

    @login_required
    def resolve_is_liked(parent, info):
        return Like.objects.filter(review=parent, user=info.context.user).count()


class LikeType(DjangoObjectType):
    class Meta:
        model = Like


class AddressType(DjangoObjectType):
    class Meta:
        model = Address


class ProductType(DjangoObjectType):
    class Meta:
        model = Product


class PhotoType(DjangoObjectType):
    class Meta:
        model = Photo


class ProductOrderInputType(graphene.InputObjectType):
    product_id = graphene.String(required=True)
    qty = graphene.Int(required=True)


class OrderObjType(DjangoObjectType):
    class Meta:
        model = OrderObj
        exclude = ("order",)


class OrderType(DjangoObjectType):
    class Meta:
        model = Order

    product_objects = graphene.List(OrderObjType)

    def resolve_product_objects(parent, info):
        return OrderObj.objects.filter(order=parent)


class UserType(DjangoObjectType):
    class Meta:
        model = User
        exclude = ("password",)  # dont allow password

    cart = graphene.List(CartType)

    def resolve_cart(parent, info):
        return CartObj.objects.filter(user=parent)


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

    orders = graphene.List(OrderType)
    order = graphene.Field(OrderType, id=graphene.String())

    @login_required
    def resolve_me(self, info):
        return info.context.user

    @login_required
    def resolve_orders(self, info):
        return Order.objects.filter(user=info.context.user)

    @login_required
    def resolve_order(self, info, id):
        product = Order.objects.get(pk=id)
        if product.user != info.context.user:
            raise Exception("Not the owner of the order")
        return product

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

    @login_required
    def mutate(self, info, name, address1, address2, pincode, city, state, country):
        user = info.context.user

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


class DeleteAddress(graphene.Mutation):
    id = graphene.String()

    class Arguments:
        addressId = graphene.String()

    @login_required
    def mutate(self, info, addressId):
        user = info.context.user
        address = Address.objects.get(pk=addressId)

        if address.user.id != user.id:
            raise Exception("You must the owner of that address to remove it!")

        address.delete()

        return DeleteAddress(id=addressId)


class CreateUser(graphene.Mutation):
    id = graphene.String()
    name = graphene.String()
    email = graphene.String()
    phone = graphene.String()

    class Arguments:
        name = graphene.String()
        email = graphene.String()
        phone = graphene.String()
        password = graphene.String()

    def mutate(self, info, name, email, phone, password):
        user = User(name=name, email=email, phone=phone)
        user.set_password(password)
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
            raise Exception("You must be author of the review to delete it.")

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


class UpdateSelf(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        phone = graphene.String()
        name = graphene.String()

    @login_required
    def mutate(self, info, **kwargs):
        user = info.context.user
        if "phone" in kwargs.keys():
            user.phone = kwargs.get("phone")
        if "name" in kwargs.keys():
            user.name = kwargs.get("name")
        user.save()
        return UpdateSelf(user=user)


class UpdatePassword(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        old_pass = graphene.String()
        new_pass = graphene.String()

    @login_required
    def mutate(self, info, old_pass, new_pass):
        user = info.context.user

        if not user.check_password(old_pass):
            raise Exception("Old password not correct")
        else:
            user.set_password(new_pass)
            user.save()
            return UpdatePassword(user=user)


class PlaceOrder(graphene.Mutation):
    order = graphene.Field(OrderType)

    class Arguments:
        product_objects = graphene.List(ProductOrderInputType)

    @login_required
    def mutate(self, info, product_objects):
        order = Order.objects.create(user=info.context.user)

        for product_obj in product_objects:
            product = Product.objects.get(pk=product_obj.product_id)

            if product.stock < product_obj.qty:
                raise Exception("Stock Error")

            product.stock -= product_obj.qty
            product.save()

            order.product_objects.add(
                product_obj.product_id, through_defaults={"qty": product_obj.qty}
            )
        return PlaceOrder(order=order)


class SetCart(graphene.Mutation):
    cart = graphene.List(CartType)

    class Arguments:
        cart_obj = ProductOrderInputType()

    @login_required
    def mutate(self, info, cart_obj):
        user = info.context.user

        try:
            _cart_obj = CartObj.objects.get(user=user, product_id=cart_obj.product_id)
            if cart_obj.qty > 0:
                _cart_obj.qty = cart_obj.qty
                _cart_obj.save()
            else:
                user.cart.remove(cart_obj.product_id)
        except CartObj.DoesNotExist:
            if cart_obj.qty > 0:
                user.cart.add(cart_obj.product_id, through_defaults={"qty": cart_obj.qty})

        return SetCart(cart=CartObj.objects.filter(user=user))


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    create_address = CreateAddress.Field()
    delete_address = DeleteAddress.Field()
    add_review = AddReview.Field()
    delete_review = DeleteReview.Field()
    like_review = LikeReview.Field()
    unlike_review = UnlikeReview.Field()
    update_me = UpdateSelf.Field()
    update_password = UpdatePassword.Field()
    place_order = PlaceOrder.Field()
    set_cart = SetCart.Field()
