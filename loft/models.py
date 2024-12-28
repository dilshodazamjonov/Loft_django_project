from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


# Create your models here.

class Category(models.Model):
    title = models.CharField(max_length=150, verbose_name='Название категории')
    icon = models.ImageField(upload_to='icons/', null=True, blank=True, verbose_name='Иконка категории')
    slug = models.SlugField(unique=True, null=True, verbose_name='Слаг категории')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                               related_name='subcategories',
                               verbose_name='Категория')

    def get_absolute_url(self):
        return reverse('category', kwargs={'slug': self.slug})

    def get_icon(self):
        if self.icon:
            return self.icon.url
        else:
            return '😁'

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Категорию'
        verbose_name_plural = 'Категории'


class Product(models.Model):
    title = models.CharField(max_length=250, verbose_name='Название товара')
    description = models.TextField(verbose_name='Описание товара')
    price = models.FloatField(verbose_name='Цена товара')
    quantity = models.IntegerField(default=0, verbose_name='Количество')
    color_name = models.CharField(max_length=100, verbose_name='Название цвета')
    color_code = models.CharField(max_length=10, verbose_name='Код цвета', default='#ffffff')
    width = models.CharField(max_length=10, verbose_name='Ширина')
    depth = models.CharField(max_length=10, verbose_name='Глубина')
    height = models.CharField(max_length=10, verbose_name='Высота')
    discount = models.IntegerField(verbose_name='Скидка', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 related_name='products', verbose_name='Категория')
    model = models.ForeignKey('ProductModel', on_delete=models.CASCADE, blank=True, null=True, verbose_name='Модель')
    slug = models.SlugField(unique=True, null=True, verbose_name='Слаг категории')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name='Дата добавления')
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True, verbose_name='Дата изменения')


    def get_absolute_url(self):
        return reverse('product', kwargs={'slug': self.slug})

    def get_first_photo(self):
        if self.images:
            return self.images.first().image.url
        else:
            return '-'


    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'



class ImageProduct(models.Model):
    image = models.ImageField(upload_to='images/', verbose_name='Фото товара')
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='images', verbose_name='Товар')


    def __str__(self):
        return self.product.title

    class Meta:
        verbose_name = 'Фото товара'
        verbose_name_plural = 'Фото товаров'



class ProductModel(models.Model):
    title = models.CharField(max_length=150, verbose_name='Модель товара')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Модель'
        verbose_name_plural = 'Модели'




class FavoriteProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    def __str__(self):
        return f'Пользоваетль: {self.user.username} Товар: {self.product.title}'

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные товары'



# ========================= Модели для Заказа и сохранения ==============

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, verbose_name='Пользователь')

    def __str__(self):
        return f'Покупатель: {self.user.first_name}'

    class Meta:
        verbose_name = 'Покупателя'
        verbose_name_plural = 'Покупатели'


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, verbose_name='Покупатель')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата заказа')
    is_completed = models.BooleanField(default=False, verbose_name='Статус заказа')
    payment = models.BooleanField(default=False, verbose_name='Статус оплаты')
    shipping = models.BooleanField(default=True, verbose_name='Доставка')

    def __str__(self):
        return f'Номер заказа: {self.pk}, на имя: {self.customer.user.username}'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    # Методы для подсчёта суммы заказа и кол-ва товаров
    @property
    def get_order_total_price(self):
        order_products = self.orderproduct_set.all() # Получаем заказанные товарвы Заказа по оброзу класса привязки
        total_price = sum([i.get_total_price for i in order_products])  # [10 000, 10 0000, 20 0000]
        return total_price


    @property
    def get_order_total_quantity(self):
        order_products = self.orderproduct_set.all()
        total_quantity = sum([i.quantity for i in order_products])  # [2, 1, 1]
        return total_quantity


class OrderProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, verbose_name='Товар')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, verbose_name='Заказ')
    quantity = models.IntegerField(default=0, verbose_name='В количестве')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')

    def __str__(self):
        return f'Товар {self.product.title} по заказу №: {self.order.pk}'


    class Meta:
        verbose_name = 'Заказанный товар'
        verbose_name_plural = 'Заказанные товары'

    # Метод для получения уммы заказа в количестве
    @property
    def get_total_price(self):
        if self.product.discount:
            sun_proc = (self.product.price * self.product.discount) / 100
            self.product.price -= sun_proc

        return self.product.price * self.quantity


    def total_price(self):
        return self.product.price * self.quantity


class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, verbose_name='Покупатель')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, verbose_name='Заказа')
    address = models.CharField(max_length=150, verbose_name='Адрес доставки (улица, дом, кв)')
    phone = models.CharField(max_length=30, verbose_name='Номер телефона')
    comment = models.TextField(verbose_name='Комментарий к заказу', max_length=200)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата оформления доставки')
    region = models.ForeignKey('Region', on_delete=models.SET_NULL, null=True, verbose_name='Регион')
    city = models.ForeignKey('City', on_delete=models.SET_NULL, null=True, verbose_name='Город')

    def __str__(self):
        return f'Доставка для {self.customer.user.first_name} на заказ №{self.order.pk}'


    class Meta:
        verbose_name = 'Адрес доставки'
        verbose_name_plural = 'Адреса доставок'




class Region(models.Model):
    title = models.CharField(max_length=150, verbose_name='Регион')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Регион'
        verbose_name_plural = 'Регионы'


class City(models.Model):
    title = models.CharField(max_length=150, verbose_name='город')
    region = models.ForeignKey(Region, on_delete=models.CASCADE, verbose_name='Регион', related_name='cities')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'







