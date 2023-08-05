from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from ob_dj_store.core.stores.managers import (
    InventoryManager,
    InventoryOperationsManager,
)
from ob_dj_store.utils.model import DjangoModelCleanMixin


class Inventory(DjangoModelCleanMixin, models.Model):
    """model to manage store inventory"""

    variant = models.ForeignKey(
        "stores.ProductVariant", on_delete=models.CASCADE, related_name="inventories"
    )
    store = models.ForeignKey(
        "stores.Store", on_delete=models.CASCADE, related_name="inventories"
    )
    quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_percent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_deliverable = models.BooleanField(default=False)
    # Add is_primary for variant
    is_primary = models.BooleanField(default=False)
    preparation_time = models.DurationField(
        default=timedelta(minutes=0),
        help_text=_("Preparation time in minutes"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = InventoryManager()

    # Add unique together constraint for store and variant
    class Meta:
        unique_together = (("store", "variant"),)
        verbose_name_plural = _("Inventories")
        verbose_name = _("Inventory")

    def __str__(self):
        return f"Inventory - {self.variant.product.name} - {self.store.name}"

    @property
    def discounted_price(self) -> Decimal:
        if self.discount_percent:
            return self.price - (self.price * (self.discount_percent / 100))
        return self.price


class InventoryOperations(DjangoModelCleanMixin, models.Model):
    """model to log inventory operations"""

    class Type_of_operation(models.TextChoices):
        STOCK_IN = "STOCK_IN", _("stock in")
        STOCK_OUT = "STOCK_OUT", _("stock out")

    inventory = models.ForeignKey(
        Inventory, on_delete=models.CASCADE, related_name="inventory_operations"
    )
    product_variant = models.ForeignKey(
        "stores.ProductVariant",
        on_delete=models.CASCADE,
        related_name="inventory_operations",
    )
    type_of_operation = models.CharField(
        max_length=32,
        default=Type_of_operation.STOCK_IN,
        choices=Type_of_operation.choices,
    )
    store = models.ForeignKey(
        "stores.Store", on_delete=models.CASCADE, related_name="inventory_operations"
    )
    quantity = models.PositiveIntegerField(default=0)
    # User who will make the operation
    operator = models.ForeignKey(
        get_user_model(), related_name="inventory_operations", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    objects = InventoryOperationsManager()
    # string representation of the model

    def __str__(self):
        return f"InventoryOperation - {self.inventory.variant.product.name} - {self.store.name}"
