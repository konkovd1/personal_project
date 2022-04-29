from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, TemplateView, DetailView

from eshopper.main.forms import CreateProfileForm, CheckoutForm, ContactForm
from eshopper.main.models import Customer, Product, Order, OrderItem


def is_valid_queryparam(param):
    return param != '' and param is not None


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


def filter(request):
    qs = Product.objects.all().order_by('price_with_discount', 'price')
    name_contains_query = request.GET.get('name_contains')
    price_until_hundred = request.GET.get('price_until_hundred')
    price_until_two_hundred = request.GET.get('price_until_two_hundred')
    price_until_three_hundred = request.GET.get('price_until_three_hundred')
    price_until_four_hundred = request.GET.get('price_until_four_hundred')
    price_until_five_hundred = request.GET.get('price_until_five_hundred')
    size_xs = request.GET.get('size_xs')
    size_s = request.GET.get('size_s')
    size_m = request.GET.get('size_m')
    size_l = request.GET.get('size_l')
    size_xl = request.GET.get('size_xl')

    if is_valid_queryparam(name_contains_query):
        qs = qs.filter(name__icontains=name_contains_query)

    if is_valid_queryparam(price_until_hundred):
        qs = qs.filter(price__range=(0, 100))

    elif is_valid_queryparam(price_until_two_hundred):
        qs = qs.filter(price__range=(100, 200))

    elif is_valid_queryparam(price_until_three_hundred):
        qs = qs.filter(price__range=(200, 300))

    elif is_valid_queryparam(price_until_four_hundred):
        qs = qs.filter(price__range=(300, 400))

    elif is_valid_queryparam(price_until_five_hundred):
        qs = qs.filter(price__range=(400, 500))

    if is_valid_queryparam(size_xs):
        qs = qs.filter(sizes__exact='XS')

    elif is_valid_queryparam(size_s):
        qs = qs.filter(sizes__exact='S')

    elif is_valid_queryparam(size_m):
        qs = qs.filter(sizes__exact='M')

    elif is_valid_queryparam(size_l):
        qs = qs.filter(sizes__exact='L')

    elif is_valid_queryparam(size_xl):
        qs = qs.filter(sizes__exact='XL')

    return qs


def shop(request):
    qs = filter(request)
    context = {
        'queryset': qs,
    }
    return render(request, 'shop.html', context)


def shop_only_shirts(request):
    qs = Product.objects.filter(categories__exact='T-shirts').order_by('-price_with_discount', 'price')
    context = {
        'queryset': qs,
    }
    return render(request, 'shop_only_shirts.html', context)


def shop_only_dresses(request):
    qs = Product.objects.filter(categories__exact='dresses').order_by('-price_with_discount', 'price')
    context = {
        'queryset': qs,
    }
    return render(request, 'shop_only_dresses.html', context)


def shop_only_jeans(request):
    qs = Product.objects.filter(categories__exact='jeans').order_by('-price_with_discount', 'price')
    context = {
        'queryset': qs,
    }
    return render(request, 'shop_only_jeans.html', context)


def shop_only_jackets(request):
    qs = Product.objects.filter(categories__exact='jackets').order_by('-price_with_discount', 'price')
    context = {
        'queryset': qs,
    }
    return render(request, 'shop_only_jackets.html', context)


# class ShopView(ListView):
#     model = Product
#     template_name = 'shop.html'
#     context_object_name = 'products'
#     paginate_by = 5


class ProductDetailsView(DetailView):
    model = Product
    template_name = 'product_detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        # add extra field
        context['products'] = Product.objects.all()
        return context


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
        order = Order.objects.get(user=self.request.user, ordered=False)
        form = CheckoutForm()
        context = {
            'form': form,
            'order': order,
        }
        return render(self.request, 'checkout.html', context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')


def add_to_cart(request, slug):
    if not request.user.is_authenticated:
        messages.warning(request, 'You are not logged in')
        return redirect('shop')
    product = get_object_or_404(Product, slug=slug)
    order_product, created = OrderItem.objects.get_or_create(
        product=product,
        user=request.user,
        ordered=False,
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.products.filter(product__slug=product.slug).exists():
            order_product.quantity += 1
            order_product.save()
            messages.info(request, 'The quantity of this item was updated')
        else:
            messages.info(request, 'This item was added to your cart')
            order.products.add(order_product)
        return redirect('cart')
    else:
        order = Order.objects.create(user=request.user)
        order.products.add(order_product)
        messages.info(request, 'This item was added to your cart')
    return redirect('cart')


def remove_from_cart(request, slug):
    if not request.user.is_authenticated:
        messages.warning(request, 'You are not logged in')
        return redirect('shop')
    product = get_object_or_404(Product, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
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


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.info(request, 'Than you for your message!')
            return redirect('index')
    else:
        form = ContactForm()
    context = {
        'form': form,
    }
    return render(request, 'contact.html', context)
