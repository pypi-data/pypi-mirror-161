from django import forms
from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin

from ob_dj_store.core.stores import models


class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "description",
        "shipping_fee_option",
        "shipping_fee",
        "is_active",
    ]


class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "description",
        "payment_provider",
        "is_active",
    ]


class StoreAdmin(LeafletGeoAdmin):
    list_display = [
        "name",
        "location",
        "is_active",
        "currency",
        "minimum_order_amount",
        "delivery_charges",
        "min_free_delivery_amount",
    ]
    # define the pickup addresses field as a ManyToManyField
    # to the address model
    filter_horizontal = ["pickup_addresses"]
    # define the shipping methods field as a ManyToManyField
    # to the shipping method model
    filter_horizontal = ["shipping_methods"]


class OpeningHoursAdmin(admin.ModelAdmin):
    list_display = [
        "store",
        "from_hour",
        "to_hour",
    ]


class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name"]


class AttributeChoiceInlineAdmin(admin.TabularInline):
    model = models.AttributeChoice


class ProductVariantInlineAdmin(admin.TabularInline):
    model = models.ProductVariant
    extra = 1


class ProductMediaInlineAdmin(admin.TabularInline):
    model = models.ProductMedia
    extra = 1


class ProductVariantAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "product",
        "has_inventory",
    ]


class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
    ]
    inlines = [ProductVariantInlineAdmin, ProductMediaInlineAdmin]


class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]


class AttributeChoiceAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "price",
    ]


class ProductTagAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        form.base_fields["text_color"].widget = forms.TextInput(attrs={"type": "color"})
        form.base_fields["background_color"].widget = forms.TextInput(
            attrs={"type": "color"}
        )
        return form


class CartItemInlineAdmin(admin.TabularInline):
    readonly_fields = [
        "unit_price",
    ]
    list_display = [
        "product_variant",
        "quantity",
    ]
    model = models.CartItem


class CartAdmin(admin.ModelAdmin):
    list_display = ["customer", "total_price"]
    inlines = [CartItemInlineAdmin]


class AdressAdmin(LeafletGeoAdmin):
    list_display = [
        "id",
        "address_line",
        "postal_code",
        "city",
        "region",
        "country",
        "is_active",
    ]


class FeedbackAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "order",
        "review",
        "notes",
    ]


class FeedbackAttributeAdmin(admin.ModelAdmin):
    list_display = [
        "feedback",
        "config",
        "value",
        "review",
    ]


class FeedbackConfigAdmin(admin.ModelAdmin):
    list_display = [
        "attribute",
        "attribute_label",
        "values",
    ]


class PhoneContactAdmin(admin.ModelAdmin):
    list_display = [
        "phone_number",
        "store",
    ]


admin.site.register(models.Store, StoreAdmin)
admin.site.register(models.OpeningHours, OpeningHoursAdmin)
admin.site.register(models.ShippingMethod, ShippingMethodAdmin)
admin.site.register(models.PaymentMethod, PaymentMethodAdmin)
admin.site.register(models.Category, CategoryAdmin)
admin.site.register(models.Product, ProductAdmin)
admin.site.register(models.ProductAttribute, ProductAttributeAdmin)
admin.site.register(models.ProductVariant, ProductVariantAdmin)
admin.site.register(models.ProductTag, ProductTagAdmin)
admin.site.register(models.Cart, CartAdmin)
admin.site.register(models.Address, AdressAdmin)
admin.site.register(models.Feedback, FeedbackAdmin)
admin.site.register(models.FeedbackAttribute, FeedbackAttributeAdmin)
admin.site.register(models.FeedbackConfig, FeedbackConfigAdmin)
admin.site.register(models.AttributeChoice, AttributeChoiceAdmin)
admin.site.register(models.PhoneContact, PhoneContactAdmin)
