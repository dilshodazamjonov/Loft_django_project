from django.contrib import admin
from django.utils.safestring import mark_safe
from .forms import CategoryForm
from .models import *

# Register your models here.

# admin.site.register(Category)
# admin.site.register(Product)
admin.site.register(ImageProduct)
admin.site.register(ProductModel)
admin.site.register(FavoriteProduct)

# Модельки заказа
admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(OrderProduct)
admin.site.register(ShippingAddress)
admin.site.register(Region)
admin.site.register(City)



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'parent', 'get_icon_category')
    list_display_links = ('pk', 'title')
    prepopulated_fields = {'slug': ('title',)}
    form = CategoryForm

    # Метод для получения иконки
    def get_icon_category(self, obj):
        if obj.icon:
            try:
                return mark_safe(f'<img src="{obj.icon.url}" width="30" >')
            except:
                return '-'
        else:
            return '-'



class ImageProductInline(admin.TabularInline):
    fk_name = 'product'
    model = ImageProduct
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'quantity', 'price', 'color_name', 'category', 'model', 'discount', 'created_at', 'get_photo')
    list_display_links = ('pk', 'title')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ImageProductInline]
    list_editable = ['quantity', 'price', 'discount', 'model']
    list_filter = ['category', 'color_name', 'price']

    def get_photo(self, obj):
        if obj.images:
            try:
                return mark_safe(f'<img src="{obj.images.first().image.url}" width="60" >')
            except:
                return '-'
        else:
            return '-'







