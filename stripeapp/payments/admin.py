from django.contrib import admin

from payments.models import Discount, Item, Order, OrderItem, Tax


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "price", "currency"]
    search_fields = ["name"]


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "percent", "amount", "active"]
    list_filter = ["active"]
    search_fields = ["name"]


@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "percent", "active"]
    list_filter = ["active"]
    search_fields = ["name"]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    can_delete = False
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "created_at",
        "currency",
        "get_total_amount_display",
    ]
    list_filter = ["created_at", "currency"]
    search_fields = ["user__username", "id"]
    inlines = [OrderItemInline]

    def get_total_amount_display(self, obj):
        return f"{obj.get_total_amount()} {obj.currency.upper()}"

    get_total_amount_display.short_description = "Сумма заказа"


__all__ = ()
