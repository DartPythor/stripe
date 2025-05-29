from django.conf import settings
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import TemplateView
import stripe
from rest_framework.views import APIView
from rest_framework.response import Response

from payments.models import Item, Order

stripe.api_key = settings.STRIPE_SECRET_KEY


class ItemDetailView(TemplateView):
    template_name = "payments/item_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        item = get_object_or_404(Item, pk=self.kwargs.get("pk"))
        context.update(
            {
                "item": item,
                "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
            },
        )
        return context


class OrderDetailView(TemplateView):
    template_name = "payments/order_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = get_object_or_404(
            Order,
            pk=self.kwargs.get("order_id"),
            user=self.request.user,
        )
        context.update(
            {
                "order": order,
                "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
            },
        )
        return context


class CreateCheckoutSessionItem(APIView):
    def get(self, request, item_id):
        item = get_object_or_404(Item, pk=item_id)

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": item.currency,
                        "unit_amount": int(item.price * 100),
                        "product_data": {
                            "name": item.name,
                            "description": item.description,
                        },
                    },
                    "quantity": 1,
                },
            ],
            mode="payment",
            success_url=request.build_absolute_uri(
                reverse("payments:item_success"),
            )
            + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=request.build_absolute_uri(
                reverse("payments:item_cancel"),
            ),
            metadata={
                "item_id": str(item.id),
                "user_id": str(request.user.id),
            },
        )
        return Response({"id": session.id})


class ItemSuccessView(TemplateView):
    template_name = "payments/success.html"


class ItemCancelView(TemplateView):
    template_name = "payments/cancel.html"


class CreateCheckoutSessionOrder(APIView):
    def get(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id, user=request.user)

        line_items = []
        for order_item in order.items.all():
            line_items.append(
                {
                    "price_data": {
                        "currency": order.currency,
                        "unit_amount": int(order_item.unit_price * 100),
                        "product_data": {
                            "name": order_item.item.name,
                            "description": order_item.item.description,
                        },
                    },
                    "quantity": order_item.quantity,
                },
            )

        discounts = []
        active_discounts = order.discounts.filter(active=True)

        if active_discounts.exists():
            discount = active_discounts.first()
            coupon_params = {
                "duration": "once",
                "name": discount.name,
            }

            if discount.percent:
                coupon_params["percent_off"] = discount.percent
            elif discount.amount:
                coupon_params["amount_off"] = int(discount.amount * 100)
                coupon_params["currency"] = order.currency

            try:
                coupon = stripe.Coupon.create(**coupon_params)
                discounts.append({"coupon": coupon.id})
            except stripe.error.StripeError as e:
                return Response({"error": str(e)}, status=400)

        taxes = []
        for tax in order.taxes.filter(active=True):
            tr = stripe.TaxRate.create(
                display_name=tax.name,
                percentage=tax.percent,
                inclusive=False,
                country="US",
                state="",
            )
            taxes.append(tr.id)

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            discounts=discounts if discounts else None,
            tax_id_collection={"enabled": False},
            success_url=request.build_absolute_uri(
                reverse("payments:order_success"),
            )
            + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=request.build_absolute_uri(
                reverse("payments:order_cancel"),
            ),
            metadata={
                "order_id": str(order.id),
                "user_id": str(request.user.id),
            },
        )
        return Response({"id": session.id})


class OrderSuccessView(TemplateView):
    template_name = "payments/success.html"


class OrderCancelView(TemplateView):
    template_name = "payments/cancel.html"


__all__ = ()
