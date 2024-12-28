from django.shortcuts import render, redirect
from .models import *
from django.views.generic import ListView, DetailView
from .forms import LoginForm, RegisterForm, ShippingForm
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from .utils import CartForAuthenticatedUser, get_cart_data
from shop.settings import STRIPE_SECRET_KEY
import stripe


# Create your views here.

class ProductListView(ListView):
    model = Product
    context_object_name = 'categories'
    template_name = 'loft/index.html'
    extra_context = {'title': 'LOFT МЕБЕЛЬ'}

    def get_queryset(self):
        categories = Category.objects.filter(parent=None)
        return categories


# Вьюшка для страницы детали товара
class ProductDetail(DetailView):
    model = Product
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        product = Product.objects.get(slug=self.kwargs['slug'])
        products = Product.objects.filter(category=product.category).exclude(
            slug=product.slug)  # РЕкомендованные товары

        context['title'] = product.title
        context['products'] = products
        return context


class ProductByCategoryView(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'loft/category_page.html'
    paginate_by = 2

    def get_queryset(self):
        sub = self.request.GET.get('sub')
        color_name = self.request.GET.get('color_name')
        model = self.request.GET.get('model')
        price_from = self.request.GET.get('from')
        price_till = self.request.GET.get('till')

        category = Category.objects.get(slug=self.kwargs['slug'])
        subcategories = category.subcategories.all()
        products = Product.objects.filter(category__in=subcategories)

        if sub:
            products = products.filter(category__title=sub)
        if color_name:
            products = products.filter(color_name=color_name)
        if model:
            products = products.filter(model__title=model)
        if price_from:
            products = [i for i in products if int(i.price) >= int(price_from)]
        if price_till:
            products = [i for i in products if int(i.price) <= int(price_till)]

        return products

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        category = Category.objects.get(slug=self.kwargs['slug'])
        context['title'] = category.title
        subcategories = category.subcategories.all()
        products = Product.objects.filter(category__in=subcategories)
        context['color_names'] = list(set([i.color_name for i in products]))
        context['models'] = list(set([i.model for i in products]))
        context['prices'] = [i for i in range(500, 10000, 500)]
        context['subcategories'] = subcategories

        # context['sub'] = self.request.GET.get('sub')
        # context['color_name'] = self.request.GET.get('color_name')
        # context['model'] = self.request.GET.get('model')
        # context['price_from'] = self.request.GET.get('from')
        # context['price_till'] = self.request.GET.get('till')
        print(self.request.GET, '=========================')
        context['query'] = self.request.GET

        return context


def user_login_view(request):
    if request.user.is_authenticated:
        return redirect('main')
    else:
        if request.method == 'POST':
            form = LoginForm(data=request.POST)
            if form.is_valid():
                user = form.get_user()
                if user:
                    login(request, user)
                    return redirect('main')
                else:
                    return redirect('login')
            else:
                return redirect('login')
        else:
            form = LoginForm()

        context = {
            'title': 'Авторизация',
            'login_form': form
        }
        return render(request, 'loft/login.html', context)


def user_logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('main')
    else:
        return redirect('main')


def register_user_view(request):
    if request.user.is_authenticated:
        return redirect('main')
    else:
        if request.method == 'POST':
            form = RegisterForm(data=request.POST)
            if form.is_valid():
                user = form.save()
                return redirect('login')
            else:
                return redirect('register')
        else:
            form = RegisterForm()
        context = {
            'title': 'Регистрация',
            'register_form': form
        }
        return render(request, 'loft/register.html', context)


# Вьюшка для добавления твоара в Избранное
def save_favorite_product(request, slug):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        user = request.user
        product = Product.objects.get(slug=slug)
        favorite_products = FavoriteProduct.objects.filter(user=user)
        if user:
            if product in [i.product for i in favorite_products]:
                fav_product = FavoriteProduct.objects.get(product=product, user=user)
                fav_product.delete()
            else:
                FavoriteProduct.objects.create(product=product, user=user)

        next_page = request.META.get('HTTP_REFERER', 'main')
        return redirect(next_page)


class FavoriteListView(LoginRequiredMixin, ListView):
    model = FavoriteProduct
    context_object_name = 'products'
    template_name = 'loft/favorite.html'
    login_url = 'login'
    extra_context = {
        'title': 'Моё избранное'
    }

    def get_queryset(self):
        favorites = FavoriteProduct.objects.filter(user=self.request.user)
        favorites = [i.product for i in favorites]
        return favorites


class SalesProductListView(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'loft/favorite.html'
    login_url = 'login'
    extra_context = {
        'title': 'Товары по акции'
    }

    def get_queryset(self):
        products = Product.objects. all()
        products = [i for i in products if i.discount]
        return products



# Вьюшка для добавления товара в корзину и удаления
def add_product_order(request, slug, action):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        user_cart = CartForAuthenticatedUser(request, slug, action)
        next_page = request.META.get('HTTP_REFERER', 'main')
        return redirect(next_page)


def my_cart_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        order_info =get_cart_data(request)
        order_products = order_info['order_products']
        products = Product.objects.all()[::-1][:8]
        context = {
            'title': 'Ваша корзина',
            'order': order_info['order'],
            'order_products': order_products,
            'products': products
        }

        return render(request, 'loft/my_cart.html', context)


def delete_products_cart(request, pk, order):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        order_product = OrderProduct.objects.get(pk=pk, order=order)
        order_product.delete()
        return redirect('my_cart')


def checkout_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        order_info = get_cart_data(request)
        print(request.META, '====================================')
        if order_info['order_products']:
            regions = Region.objects.all()
            dict_city = {i.pk: [[j.title, j.pk] for j in i.cities.all()] for i in regions}
            print(dict_city)
            context = {
                'title': 'Оформление заказа',
                'order': order_info['order'],
                'items': order_info['order_products'],
                'form': ShippingForm(),
                'dict_city': dict_city
            }

            return render(request, 'loft/checkout.html', context)
        else:
            next_page = request.META.get('HTTP_REFERER', 'main')
            return redirect(next_page)



def create_checkout_session(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        stripe.api_key = STRIPE_SECRET_KEY
        if request.method == 'POST':
            order_info = get_cart_data(request)
            shipping_form = ShippingForm(data=request.POST)
            ship_address = ShippingAddress.objects.all()
            if shipping_form.is_valid():
                shipping = shipping_form.save(commit=False)
                shipping.customer = Customer.objects.get(user=request.user)
                shipping.order = order_info['order']
                print(order_info['order'])
                if order_info['order'] not in [i.order for i in ship_address]:
                    shipping.save()
            else:
                return redirect('checkout')

            order_price = order_info['order_total_price']
            session = stripe.checkout.Session.create(
                line_items=[{
                    'price_data': {
                        'currency': 'rub',
                        'product_data': {'name': 'Товары магазина LOFT'},
                        'unit_amount': int(order_price) * 100
                    },
                    'quantity': 1
                }],
                mode='payment',
                success_url=request.build_absolute_uri(reverse('success')),
                cancel_url=request.build_absolute_uri(reverse('checkout'))
            )

            return redirect(session.url, 303)




def success_payment(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        cart = CartForAuthenticatedUser(request)
        cart.clear_cart()

        context = {
                'title': 'Успешная оплата'
            }

        return render(request, 'loft/success.html', context)










