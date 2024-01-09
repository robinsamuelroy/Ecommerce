from django.contrib import admin
from store.models import *
class ProductImagesAdmin(admin.TabularInline):
   model = ProductImages

class VariantImagesAdmin(admin.TabularInline):
   model = VariantImages

class ProductAdmin(admin.ModelAdmin):
  inlines = [ProductImagesAdmin]
  list_display = ['user','title','product_image','price','category','old_price','featured','product_status','pid']

class CategoryAdmin(admin.ModelAdmin):
  list_display = ['cid','title','category_image']

class CartAdmin(admin.ModelAdmin):
  list_display = ['cart_id','date_added']

class CartItemAdmin(admin.ModelAdmin):
  list_display = ['user','product','cart','quantity','is_active', 'variations']

class ProductVariantAdmin(admin.ModelAdmin):
    inlines = [VariantImagesAdmin]
    list_display = ['product', 'color', 'stock_count' ,'price','old_price','image']

class ColorAdmin(admin.ModelAdmin):
    list_display = ['name']

class BrandAdmin(admin.ModelAdmin):
    list_display = ['title']

class AddressAdmin(admin.ModelAdmin):
   list_display = ['user', 'address_type', 'is_active']


class OrderAdmin(admin.ModelAdmin):
   list_display = ['user', 'order_number', 'order_total','is_ordered']

class OrderProductAdmin(admin.ModelAdmin):
   list_display = ['order', 'payment', 'user','color']

class  CouponAdmin(admin.ModelAdmin):
   list_display = ['code', 'description', 'discount', 'is_active']

class RedeemedCouponAdmin(admin.ModelAdmin):
   list_display = ['coupon', 'user', 'redeemed_date', 'is_redeemed']

class PaymentAdmin(admin.ModelAdmin):
   list_display = ['user', 'payment_id', 'amount_paid', 'status']

class WalletAdmin(admin.ModelAdmin):
   list_display = ['user', 'wallet_amount', 'wishlist']

class BannerImageAdmin(admin.TabularInline):
   model = BannerImage

class BannerAdmin(admin.ModelAdmin):
   inlines = [BannerImageAdmin]
   list_display = ['banner_name', 'is_active', 'set']



admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(ProductVariant,ProductVariantAdmin)
admin.site.register(Color,ColorAdmin)
admin.site.register(Brand,BrandAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Banner, BannerAdmin)

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct, OrderProductAdmin)
admin.site.register(Coupon, CouponAdmin)
admin.site.register(RedeemedCoupon, RedeemedCouponAdmin)
admin.site.register(Payment, PaymentAdmin)
