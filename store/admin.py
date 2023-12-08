from django.contrib import admin
from store.models import Category, Product, Brand, ProductVariant, Color, ProductImages, CartOrder, CartOderItems, ProductReview, wishlist, Address
# Register your models here.

class ProductImagesAdmin(admin.TabularInline):
   model = ProductImages

class ProductAdmin(admin.ModelAdmin):
  inlines = [ProductImagesAdmin]
  list_display = ['user','title','product_image','price','featured','status']

class CategoryAdmin(admin.ModelAdmin):
  list_display = ['title','category_image']

class CartOrderAdmin(admin.ModelAdmin):
  list_display = ['user','price','paid_status','order_date','product_status']

class CartOderItemsAdmin(admin.ModelAdmin):
  list_display = ['order','invoice_no','item','image','qty', 'price','total']

class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'color','material', 'stock_count', 'price']

class ColorAdmin(admin.ModelAdmin):
    list_display = ['name']

class BrandAdmin(admin.ModelAdmin):
    list_display = ['title']

class ProductReviewAdmin(admin.ModelAdmin):
   list_display = ['user', 'product', 'review', 'rating']

class wishlistAdmin(admin.ModelAdmin):
   list_display = ['user', 'product', 'date']

class AddressAdmin(admin.ModelAdmin):
   list_display = ['user', 'address', 'status']

admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(CartOrder, CartOrderAdmin)
admin.site.register(CartOderItems, CartOderItemsAdmin)
admin.site.register(ProductReview, ProductReviewAdmin)
admin.site.register(ProductVariant,ProductVariantAdmin)
admin.site.register(Color,ColorAdmin)
admin.site.register(Brand,BrandAdmin)
admin.site.register(wishlist, wishlistAdmin)
admin.site.register(Address, AddressAdmin)