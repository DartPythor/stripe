import stripeapp
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from payments.models import Item, Order, OrderItem

stripeapp.api_key = settings.STRIPE_SECRET_KEY


class ItemDetailView(TemplateView):
    template_name = "shop/item_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        item = get_object_or_404(Item, pk=self.kwargs.get('pk'))
        context.update({
            "item": item,
            "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
        })
        return context


class CreateCheckoutSessionItem(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, item_id):
        item = get_object_or_404(Item, pk=item_id)

        session = stripeapp.checkout.Session.create(
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
                }
            ],
            mode="payment",
            success_url=request.build_absolute_uri(
                reverse("shop:item_success")) + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=request.build_absolute_uri(
                reverse("shop:item_cancel")),
            metadata={
                "item_id": str(item.id),
                "user_id": str(request.user.id),
            }
        )
        return Response({"id": session.id})


class ItemSuccessView(TemplateView):
    template_name = "shop/success.html"


class ItemCancelView(TemplateView):
    template_name = "shop/cancel.html"


class CreateCheckoutSessionOrder(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id, user=request.user)

        # Собираем line_items из OrderItem
        line_items = []
        for order_item in order.items.all():
            line_items.append({
                "price_data": {
                    "currency": order.currency,
                    "unit_amount": int(order_item.unit_price * 100),
                    "product_data": {
                        "name": order_item.item.name,
                        "description": order_item.item.description,
                    },
                },
                "quantity": order_item.quantity,
            })

        discounts = []
        for discount in order.discounts.filter(active=True):
            if discount.percent:
                discounts.append({
                    "coupon_data": {
                        "percent_off": discount.percent,
                        "name": discount.name,
                        "duration": "once",
                    }
                })
            elif discount.amount:
                discounts.append({
                    "coupon_data": {
                        "amount_off": int(discount.amount * 100),
                        "currency": order.currency,
                        "name": discount.name,
                        "duration": "once",
                    }
                })

        taxes = []
        for tax in order.taxes.filter(active=True):
            tr = stripeapp.TaxRate.create(
                display_name=tax.name,
                percentage=tax.percent,
                inclusive=False,
                country="US",
                state="",
            )
            taxes.append(tr.id)

        session = stripeapp.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            discounts=discounts or None,
            tax_id_collection={"enabled": False},
            success_url=request.build_absolute_uri(
                reverse("shop:order_success")) + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=request.build_absolute_uri(
                reverse("shop:order_cancel")),
            metadata={
                "order_id": str(order.id),
                "user_id": str(request.user.id),
            }
        )
        return Response({"id": session.id})


class OrderSuccessView(TemplateView):
    template_name = "shop/success.html"


class OrderCancelView(TemplateView):
    template_name = "shop/cancel.html"
