from django.urls import path
from payments.views import (
    ItemDetailView,
    ItemSuccessView,
    ItemCancelView,
    OrderDetailView,
    OrderSuccessView,
    OrderCancelView,
    CreateCheckoutSessionItem,
    CreateCheckoutSessionOrder,
)

app_name = "payments"

urlpatterns = [
    path("item/<int:pk>/", ItemDetailView.as_view(), name="item_detail"),
    path("item/success/", ItemSuccessView.as_view(), name="item_success"),
    path("item/cancel/", ItemCancelView.as_view(), name="item_cancel"),
    path(
        "order/<int:order_id>/",
        OrderDetailView.as_view(),
        name="order_detail",
    ),
    path("order/success/", OrderSuccessView.as_view(), name="order_success"),
    path("order/cancel/", OrderCancelView.as_view(), name="order_cancel"),
    path(
        "api/buy/item/<int:item_id>/",
        CreateCheckoutSessionItem.as_view(),
        name="api_buy_item",
    ),
    path(
        "api/buy/order/<int:order_id>/",
        CreateCheckoutSessionOrder.as_view(),
        name="api_buy_order",
    ),
]
