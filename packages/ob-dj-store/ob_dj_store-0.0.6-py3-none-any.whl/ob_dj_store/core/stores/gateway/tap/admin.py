from django.contrib import admin

from ob_dj_store.core.stores.gateway.tap.models import TapPayment


class TapPaymentAdmin(admin.ModelAdmin):
    list_display = [
        "charge_id",
        "amount",
        "source",
        "status",
    ]
    list_filter = ("status", "source")
    search_fields = [
        "charge_id",
    ]


admin.site.register(TapPayment, TapPaymentAdmin)
