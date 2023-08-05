from django.contrib.postgres.search import SearchVector
from django.db.models import Prefetch, Q
from django_filters import rest_framework as filters

from ob_dj_store.core.stores.models import (
    Category,
    Order,
    Product,
    ProductVariant,
    Store,
)
from ob_dj_store.core.stores.models._inventory import Inventory


class StoreFilter(filters.FilterSet):
    """Store filters"""

    location = filters.CharFilter(method="by_location")
    shipping_methods = filters.CharFilter(method="by_shipping_methods")
    search = filters.CharFilter(method="search_filter")

    class Meta:
        model = Store
        fields = [
            "delivery_charges",
            "min_free_delivery_amount",
        ]

    def by_location(self, queryset, name, value):
        return queryset.filter(poly__contains=value)

    def by_shipping_methods(self, queryset, name, value):
        return queryset.filter(
            shipping_methods__name__in=[
                value,
            ]
        )

    def search_filter(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector("name", "address__address_line")
        ).filter(Q(search=value) | Q(search__icontains=value))


class ProductFilter(filters.FilterSet):
    """Product filters"""

    store = filters.CharFilter(method="by_store")

    class Meta:
        model = Product
        fields = [
            "is_featured",
            "category__name",
        ]

    def by_store(self, queryset, name, value):
        return queryset.prefetch_related(
            Prefetch(
                "products",
                queryset=Product.objects.filter(
                    product_variants__inventories__store=value
                ),
            )
        ).filter(product_variants__inventories__store=value)


class VariantFilter(filters.FilterSet):
    """Variant filters"""

    class Meta:
        model = ProductVariant
        fields = [
            "product__name",
            "product__category__name",
        ]


class CategoryFilter(filters.FilterSet):
    """Category filters"""

    store = filters.CharFilter(method="by_store")

    class Meta:
        model = Category
        fields = [
            "name",
        ]

    def by_store(self, queryset, name, value):
        return queryset.prefetch_related(
            Prefetch(
                "products",
                queryset=Product.objects.filter(
                    product_variants__inventories__store=value
                ),
            )
        ).filter(products__product_variants__inventories__store=value)


class OrderFilter(filters.FilterSet):
    """Order filters"""

    class Meta:
        model = Order
        fields = [
            "status",
        ]


class InventoryFilter(filters.FilterSet):
    """Category filters"""

    class Meta:
        model = Inventory
        fields = [
            "store",
            "variant",
        ]
