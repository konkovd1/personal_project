import random

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django_countries.fields import CountryField

def default_random_transaction_id():
    rand_num = random.randrange(1, 1000)
    return rand_num

class Customer(models.Model):
    first_name = models.CharField(
        max_length=30,
    )

    last_name = models.CharField(
        max_length=30,
    )
    email = models.EmailField()

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Product(models.Model):
    name = models.CharField(
        max_length=100,
        null=True,
    )

    price = models.FloatField()

    price_with_discount = models.FloatField(
        default=0,
        null=True,
        blank=True,
    )

    digital = models.BooleanField(
        default=False,
        null=True,
        blank=False,
    )

    image = models.ImageField(
        null=True,
        blank=True,
    )

    description = models.TextField()

    slug = models.SlugField()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_details', kwargs={
            'slug': self.slug,
        })

    def get_add_to_cart_url(self):
        return reverse('add_to_cart', kwargs={
            'slug': self.slug,
        })

    def get_remove_from_cart_url(self):
        return reverse('remove_from_cart', kwargs={
            'slug': self.slug,
        })

class OrderItem(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    quantity = models.IntegerField(
        default=1,
        null=True,
        blank=True,
    )

    date_added = models.DateTimeField(
        auto_now_add=True,
    )

    ordered = models.BooleanField(
        default=False,
        null=True,
        blank=False,
    )

    def __str__(self):
        return self.product.name

    def get_total_price(self):
        return self.quantity * self.product.price

    def get_total_price_with_discount(self):
        return self.quantity * self.product.price_with_discount

    def total_amount(self):
        if self.product.price_with_discount:
            return self.get_total_price_with_discount()
        return self.get_total_price()


class Order(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    products = models.ManyToManyField(
        OrderItem,
    )

    date_ordered = models.DateTimeField(
        auto_now_add=True,
    )

    ordered = models.BooleanField(
        default=False,
        null=True,
        blank=False,
    )

    transaction_id = models.CharField(
        max_length=100,
        null=True,
        default=default_random_transaction_id
    )

    def __str__(self):
        return self.transaction_id

    def get_sub_total(self):
        total = 0
        for order_item in self.products.all():
            total += order_item.total_amount()
        return total

    def get_shipping_price(self):
        shipping_price = self.get_sub_total() * 0.02
        return shipping_price

    def get_total_cart(self):
        total = self.get_sub_total() + self.get_shipping_price()
        return total


class ShippingAddress(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    first_name = models.CharField(
        max_length=30,
    )

    last_name = models.CharField(
        max_length=30,
    )

    email = models.EmailField()

    mobile_phone = models.CharField(
        max_length=30,
    )

    address = models.CharField(
        max_length=30,
    )

    country = CountryField()

    city = models.CharField(
        max_length=30,
    )

    zip_code = models.CharField(
        max_length=30,
    )

    date_added = models.DateTimeField(
        auto_now_add=True,
    )
