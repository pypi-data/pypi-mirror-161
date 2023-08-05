import contextlib
import typing
from datetime import date, time

from django.conf import settings
from django.contrib.gis.geos import Point
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from ob_dj_store.core.stores.models import (
    Attribute,
    AttributeChoice,
    Cart,
    CartItem,
    Category,
    Favorite,
    Feedback,
    FeedbackAttribute,
    FeedbackConfig,
    OpeningHours,
    Order,
    OrderHistory,
    OrderItem,
    PhoneContact,
    Product,
    ProductAttribute,
    ProductMedia,
    ProductTag,
    ProductVariant,
    ShippingMethod,
    Store,
)
from ob_dj_store.core.stores.models._inventory import Inventory
from ob_dj_store.core.stores.utils import distance


class AttributeChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeChoice
        fields = (
            "id",
            "name",
            "price",
        )


class AttributeSerializer(serializers.ModelSerializer):
    attribute_choices = AttributeChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Attribute
        fields = (
            "id",
            "name",
            "attribute_choices",
        )


class InventoryValidationMixin:
    def validate(self, attrs: typing.Dict) -> typing.Dict:
        validated_data = super().validate(attrs)
        if (
            validated_data["product_variant"].has_inventory
            and validated_data["quantity"] < 1
        ):
            raise serializers.ValidationError(_("Quantity must be greater than 0."))
        # validate quantity in inventory
        stock_quantity = (
            validated_data["product_variant"]
            .inventories.get(store=validated_data["store"])
            .quantity
        )
        if (
            validated_data["product_variant"].has_inventory
            and validated_data["quantity"] > stock_quantity
        ):
            raise serializers.ValidationError(
                _("Quantity is greater than the stock quantity.")
            )
        return validated_data


class CartItemSerializer(InventoryValidationMixin, serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = (
            "id",
            "cart",
            "product_variant",
            "quantity",
            "store",
            "unit_price",
            "total_price",
            "notes",
            "attribute_choices",
        )

    def create(self, validated_data):
        return super().create(**validated_data)


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)

    class Meta:
        model = Cart
        fields = (
            "customer",
            "items",
            "total_price",
        )
        read_only_fields = ("id", "total_price")

    def update(self, instance, validated_data):
        instance.items.all().delete()
        # update or create instance items
        for item in validated_data["items"]:
            cart_item = CartItem.objects.create(
                cart=instance,
                product_variant=item["product_variant"],
                quantity=item["quantity"],
                notes=item["notes"],
                store=item["store"],
            )
            cart_item.attribute_choices.set(item["attribute_choices"])
            cart_item.save()
        return instance


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("name", "description", "is_active")


class OpeningHourSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpeningHours
        fields = "__all__"


class ShippingMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingMethod
        fields = "__all__"


class OrderHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderHistory
        fields = (
            "id",
            "order",
            "status",
            "created_at",
        )


class OrderItemSerializer(InventoryValidationMixin, serializers.ModelSerializer):
    store = serializers.IntegerField(required=True, write_only=True)

    class Meta:
        model = OrderItem
        fields = (
            "id",
            "product_variant",
            "quantity",
            "store",
            "total_amount",
            "preparation_time",
            "notes",
            "attribute_choices",
        )

    def create(self, validated_data):
        validated_data.pop("store")
        return super().create(**validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["attribute_choices"] = AttributeChoiceSerializer(
            instance.attribute_choices.all(), many=True
        ).data

        return representation


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    history = OrderHistorySerializer(many=True, read_only=True)
    cart = serializers.IntegerField(write_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "store",
            "shipping_method",
            "payment_method",
            "shipping_address",
            "customer",
            "status",
            "items",
            "total_amount",
            "preparation_time",
            "history",
            "cart",
            "pickup_time",
            "created_at",
            "updated_at",
        )
        extra_kwargs = {
            "customer": {"read_only": True},
            "store": {"read_only": True, "required": False},
        }

    def validate(self, attrs):
        # The Cart items must not be empty
        user = self.context["request"].user
        if not user.cart.items.exists():
            raise serializers.ValidationError(_("The Cart must not be empty"))

        if "pickup_time" in attrs:
            # validate that the pickup_time is always in the future
            if attrs["pickup_time"] < now():
                raise serializers.ValidationError(
                    _("Pickup time must be in the future")
                )
            # validate that the pickup_time is part of day (between 00:00 and 23:59)
            if not (
                attrs["pickup_time"].time() >= time(hour=0, minute=0)
                and attrs["pickup_time"].time() <= time(hour=23, minute=59)
            ):
                raise serializers.ValidationError(_("Pickup time must be part of day"))
            # validate that the pickup_time is between store's opening hours and closing hours
            if (
                attrs["store"]
                .opening_hours.filter(weekday=attrs["pickup_time"].weekday())
                .exists()
            ) and (
                attrs["pickup_time"].hour
                > (
                    attrs["store"]
                    .opening_hours.filter(weekday=attrs["pickup_time"].weekday())
                    .first()
                    .to_hour.hour
                )
                or attrs["pickup_time"].hour
                < (
                    attrs["store"]
                    .opening_hours.filter(weekday=attrs["pickup_time"].weekday())
                    .first()
                    .from_hour.hour
                )
            ):
                raise serializers.ValidationError(
                    _("Pickup time must be between store's opening hours")
                )

        return super().validate(attrs)

    def create(self, validated_data: typing.Dict):
        cart_id = validated_data.pop("cart")
        cart = Cart.objects.get(pk=cart_id)
        stores = Store.objects.filter(store_items__cart=cart)
        orders = []
        for store in stores:
            order = Order.objects.create(
                store=store, customer=cart.customer, **validated_data
            )
            items = store.store_items.filter(cart=cart)
            for item in items:
                order_item = OrderItem.objects.create(
                    order=order,
                    product_variant=item.product_variant,
                    quantity=item.quantity,
                )
                order_item.attribute_choices.set(item.attribute_choices.all())
            items.delete()
            orders.append(order)
        return orders


class ProductTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductTag
        fields = (
            "id",
            "name",
            "text_color",
            "background_color",
        )


class ProductAttributeSerializer(serializers.ModelSerializer):
    attribute_choices = AttributeChoiceSerializer(many=True)

    class Meta:
        model = ProductAttribute
        fields = (
            "id",
            "name",
            "attribute_choices",
        )


class ProductVariantSerializer(serializers.ModelSerializer):
    product_attributes = ProductAttributeSerializer(many=True)
    is_primary = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant
        fields = ("id", "name", "sku", "product_attributes", "is_primary")

    def get_is_primary(self, obj):
        return True if obj.inventories.filter(is_primary=True).exists() else False


class ProductMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductMedia
        fields = (
            "id",
            "is_primary",
            "image",
            "order_value",
        )


class ProductSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, source="product_variants")
    product_images = ProductMediaSerializer(many=True, source="images")
    is_favorite = serializers.SerializerMethodField()
    default_variant = ProductVariantSerializer(read_only=True, many=False)

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "is_favorite",
            "product_images",
            "variants",
            "default_variant",
        )

    def get_is_favorite(self, obj):
        if user := self.context["request"].user:
            # The context manager slightly shortens the code and significantly clarifies the author's intention to ignore the specific errors.
            # The standard library feature was introduced following a [discussion](https://bugs.python.org/issue15806), where the consensus was that
            # A key benefit here is in the priming effect for readers...
            # The with statement form makes it clear before you start reading the code that certain exceptions won't propagate.
            # https://docs.python.org/3/library/contextlib.html
            with contextlib.suppress(Favorite.DoesNotExist):
                Favorite.objects.favorite_for_user(obj, user)
                return True
        return False

    def to_representation(self, instance: Product):
        data = super().to_representation(instance=instance)
        return data


class ProductListSerializer(ProductSerializer):
    product_variants = ProductVariantSerializer(many=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "product_images",
            "product_variants",
            "default_variant",
        )


class CategorySerializer(serializers.ModelSerializer):
    products = ProductListSerializer(many=True)

    class Meta:
        model = Category
        fields = ("id", "name", "description", "products", "is_active")


class FeedbackConfigSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=False)
    attribute = serializers.CharField(read_only=True)

    class Meta:
        model = FeedbackConfig
        fields = ("id", "attribute", "attribute_label", "values")


class FeedbackAttributeSerializer(serializers.ModelSerializer):
    config = FeedbackConfigSerializer(many=False, read_only=True)
    attribute = serializers.CharField(write_only=True)

    class Meta:
        model = FeedbackAttribute
        fields = ("attribute", "config", "value", "review")

    # TODO: do we need validations when creating the value


class FeedbackSerializer(serializers.ModelSerializer):
    attributes = FeedbackAttributeSerializer(many=True, required=False)

    class Meta:
        model = Feedback
        fields = (
            "id",
            "attributes",
            "notes",
            "review",
        )

    def validate(self, attrs: typing.Dict):
        # Validate Order Status
        if self.instance.status not in [
            Order.OrderStatus.PAID,
            Order.OrderStatus.CANCELLED,
        ]:
            raise serializers.ValidationError(
                _("The Order must be PAID or CANCELLED to give a feedback")
            )
        return attrs

    def update(self, instance: Order, validated_data: typing.Dict):
        user = self.context["request"].user
        attributes = validated_data.pop("attributes", [])
        feedback = Feedback.objects.create(
            order=self.instance, user=user, **validated_data
        )

        for attr in attributes:
            feedback.attributes.create(**attr)
        feedback.order.save()
        return feedback


class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = (
            "id",
            "variant",
            "store",
            "quantity",
            "price",
            "preparation_time",
            "discount_percent",
            "discounted_price",
            "is_primary",
        )

    def to_representation(self, instance):
        data = super(InventorySerializer, self).to_representation(instance)
        data["variant"] = ProductVariantSerializer(instance=instance.variant).data
        return data


class PhoneContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneContact
        fields = (
            "id",
            "phone_number",
            "is_default",
            "is_active",
        )


class StoreSerializer(serializers.ModelSerializer):

    opening_hours = OpeningHourSerializer(many=True, read_only=True)
    phone_contacts = serializers.SerializerMethodField()
    in_range_delivery = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()
    address_line = serializers.SerializerMethodField()
    shipping_methods = ShippingMethodSerializer(many=True, read_only=True)
    distance = serializers.SerializerMethodField()
    inventories = InventorySerializer(many=True, read_only=True, required=False)
    current_day_opening_hours = serializers.SerializerMethodField()

    class Meta:
        model = Store
        fields = (
            "id",
            "name",
            "address",
            "address_line",
            "location",
            "distance",
            "is_active",
            "currency",
            "minimum_order_amount",
            "delivery_charges",
            "shipping_methods",
            "min_free_delivery_amount",
            "opening_hours",
            "in_range_delivery",
            "is_favorite",
            "created_at",
            "updated_at",
            "inventories",
            "phone_contacts",
            "current_day_opening_hours",
        )

    def get_in_range_delivery(self, obj):
        user_location = self.context["request"].query_params.get("point")
        if user_location and obj.poly:
            long, lat = user_location.split(",")
            return obj.poly.contains(Point(float(long), float(lat)))
        return False

    def get_is_favorite(self, obj):
        if user := self.context["request"].user:
            # The context manager slightly shortens the code and significantly clarifies the author's intention to ignore the specific errors.
            # The standard library feature was introduced following a [discussion](https://bugs.python.org/issue15806), where the consensus was that
            # A key benefit here is in the priming effect for readers...
            # The with statement form makes it clear before you start reading the code that certain exceptions won't propagate.
            # https://docs.python.org/3/library/contextlib.html
            with contextlib.suppress(Favorite.DoesNotExist):
                Favorite.objects.favorite_for_user(obj, user)
                return True
        return False

    def get_address_line(self, obj):
        return obj.address.address_line

    def get_distance(self, obj):
        # get the distance between the user location and store location
        user_location = self.context["request"].query_params.get("point")
        if user_location and obj.location:

            lat, long = user_location.split(",")
            store_lat, store_long = obj.location.x, obj.location.y
            return round(
                distance((float(lat), float(long)), (store_lat, store_long)), 1
            )

    def get_phone_contacts(self, obj):
        phone_contacts = obj.phone_contacts.filter(is_active=True).order_by(
            "-is_default"
        )
        return PhoneContactSerializer(phone_contacts, many=True).data

    def get_current_day_opening_hours(self, obj):
        for op_hour in obj.opening_hours.all().only("id"):
            if op_hour.weekday == date.today().weekday():
                return OpeningHourSerializer(op_hour).data
            else:
                op_hour = OpeningHourSerializer(op_hour).data
                op_hour["from_hour"] = settings.DEFAULT_OPENING_HOURS[0]["from_hour"]
                op_hour["to_hour"] = settings.DEFAULT_OPENING_HOURS[0]["to_hour"]
                return op_hour
