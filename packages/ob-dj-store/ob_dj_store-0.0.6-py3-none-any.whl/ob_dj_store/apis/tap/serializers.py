from rest_framework import serializers

from ob_dj_store.core.stores.gateway.tap.models import TapPayment


class TapPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TapPayment
        fields = [
            "id",
            "status",
            "payment",
            "result",
            "payment_url",
            "charge_id",
            "source",
            "amount",
            "init_response",
            "callback_response",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "status",
            "result",
            "payment_url",
            "init_response",
            "callback_response",
            "charge_id",
        ]
        extra_kwargs = {"payment": {"write_only": True}}

    def create(self, validated_data):
        payment = validated_data.get("payment")
        source = validated_data.get("source")
        user = self.context.get("request").user
        instance = TapPayment.objects.create(payment=payment, source=source, user=user)

        return instance
