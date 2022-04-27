from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, TemplateView, DetailView, ListView

from eshopper.main.forms import CreateProfileForm, CheckoutForm
from eshopper.main.models import Customer, Product, Order, OrderItem


class HomeView(TemplateView):
    template_name = 'index.html'


class UserRegisterView(CreateView):
    form_class = CreateProfileForm
    template_name = 'register.html'
    success_url = reverse_lazy('index')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')

        return super().dispatch(request, *args, **kwargs)


class UserLoginView(LoginView):
    template_name = 'login.html'
    success_url = reverse_lazy('index')

    def get_success_url(self):
        if self.success_url:
            return self.success_url
        return super().get_success_url()


class UserLogoutView(LogoutView):
    pass


class ProfileDetailsView(DetailView):
    model = Customer
    template_name = 'profile_details.html'
    context_object_name = 'profile'


class ShopView(ListView):
    model = Product
    template_name = 'shop.html'
    context_object_name = 'products'
    paginate_by = 5


class ProductDetailsView(DetailView):
    model = Product
    template_name = 'product_detail.html'


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'cart.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect('index')


class CheckoutView(View):
    def get(self, *args, **kwargs):
        form = CheckoutForm()
        context = {
            'form': form
        }
        return render(self.request, 'checkout.html', context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.Post or None)
        if form.is_valid():
            return redirect('checkout')


@login_required
def add_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    order_product, created = OrderItem.objects.get_or_create(
        product=product,
        user=request.user,
        ordered=False,
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if order item is in order
        if order.products.filter(product__slug=product.slug).exists():
            order_product.quantity += 1
            order_product.save()
            messages.info(request, 'The quantity of this item was updated')
        else:
            messages.info(request, 'This item was added to your cart')
            order.products.add(order_product)
        return redirect('cart')
    else:
        order = Order.objects.create(customer=request.user)
        order.products.add(order_product)
        messages.info(request, 'This item was added to your cart')
    return redirect('cart')


@login_required
def remove_from_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if order item is in order
        if order.products.filter(product__slug=product.slug).exists():
            order_product = OrderItem.objects.filter(
                product=product,
                user=request.user,
                ordered=False,
            )[0]
            messages.info(request, 'This item was removed from your cart')
            order.products.remove(order_product)
        else:
            messages.info(request, 'The item was not in your cart')
        return redirect('cart')
    else:
        messages.info(request, 'You do not have an active order')
        return redirect('cart')


@login_required
def decrease_quantity_of_item_from_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if order item is in order
        if order.products.filter(product__slug=product.slug).exists():
            order_product = OrderItem.objects.filter(
                product=product,
                user=request.user,
                ordered=False,
            )[0]
            if order_product.quantity > 1:
                order_product.quantity -= 1
                order_product.save()
                messages.info(request, 'The quantity of this item was updated')
            else:
                order.products.remove(order_product)
        else:
            messages.info(request, 'The item was not in your cart')
        return redirect('cart')
    else:
        messages.info(request, 'You do not have an active order')
        return redirect('cart')
