from decimal import Decimal

from django.conf import settings
from django.db import models


class Item(models.Model):
    CURRENCY_CHOICES = [
        ("usd", "USD"),
        ("rub", "RUB"),
        ("eur", "EUR"),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Цена в единицах (например, 100.00)",
    )
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default="usd",
    )

    def __str__(self):
        return f"{self.name} ({self.price} {self.currency.upper()})"


class Discount(models.Model):
    name = models.CharField(max_length=100)
    percent = models.PositiveSmallIntegerField(
        default=0,
        help_text="Процент скидки (0–100). Если задан, то amount игнорируется.",
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Фиксированная сумма скидки. Будет применена, если percent=0.",
    )
    active = models.BooleanField(default=True)

    def __str__(self):
        if self.percent:
            return f"{self.name} – {self.percent}%"
        return f"{self.name} – {self.amount} (currency)"

    def get_amount(self, total: Decimal) -> Decimal | models.DecimalField:
        if not self.active:
            return Decimal("0.00")
        if self.percent:
            return (Decimal(self.percent) / Decimal(100)) * total
        if self.amount:
            return self.amount
        return Decimal("0.00")


class Tax(models.Model):
    name = models.CharField(max_length=100)
    percent = models.PositiveSmallIntegerField(
        default=0,
        help_text="Процент налога (0–100).",
    )
    active = models.BooleanField(default=True)

    def __str__(self):
        return (
            f"{self.name} – {self.percent}%"
            if self.active
            else f"{self.name} (inactive)"
        )

    def get_amount(self, total: Decimal) -> Decimal:
        if not self.active:
            return Decimal("0.00")
        return (Decimal(self.percent) / Decimal(100)) * total


class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    discounts = models.ManyToManyField(
        Discount,
        blank=True,
        related_name="orders",
    )
    taxes = models.ManyToManyField(
        Tax,
        blank=True,
        related_name="orders",
    )
    currency = models.CharField(
        max_length=3,
        choices=Item.CURRENCY_CHOICES,
        default="usd",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.id} by {self.user.username} ({self.get_total_amount()} {self.currency})"

    def get_items_total(self) -> Decimal:
        total = Decimal("0.00")
        for oi in self.items.all():
            total += oi.unit_price * oi.quantity
        return total

    def get_total_amount(self) -> Decimal:
        items_total = self.get_items_total()
        discount_sum = sum(
            [
                discount.get_amount(items_total)
                for discount in self.discounts.all()
            ]
        )
        taxed_base = items_total - discount_sum
        tax_sum = sum([tax.get_amount(taxed_base) for tax in self.taxes.all()])
        return (taxed_base + tax_sum).quantize(Decimal("0.01"))


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Фиксированная цена при создании заказа",
    )

    def __str__(self):
        return f"{self.item.name} × {self.quantity} (Order #{self.order.id})"
