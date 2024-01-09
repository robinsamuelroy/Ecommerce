from datetime import timezone
from django.db import models
from shortuuidfield import ShortUUIDField
from accounts.models import Account
from django.utils.html import mark_safe
from django.utils import timezone


# Create your models here.

STATUS_CHOICE = (
  ("process", "Processing"),
  ("shipped", "Shipped"),
  ("delivered", "Delivered")
) 

RATING = (
  (1,"⭐☆☆☆☆"),
  (2,"⭐⭐☆☆☆"),
  (3,"⭐⭐⭐☆☆"),
  (4,"⭐⭐⭐⭐☆"),
  (5,"⭐⭐⭐⭐⭐")
)

def user_directory_path(instance, filename):
    if instance.user and instance.user.id:
        return 'user_{0}/{1}'.format(instance.user.id, filename)
    else:
        return 'user_unknown/{0}'.format(filename)
    
class Brand(models.Model):
  bid = ShortUUIDField(unique=True, max_length=20)
  title = models.CharField(max_length=100, default="Casio")
  image = models.ImageField(upload_to='brand', default="brand.jpg", blank=True, null=True)
  is_blocked =models.BooleanField(default=False)

  class Meta:
    verbose_name_plural = "Brands"

  def brand_image(self):
    return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

  def __str__(self):
    return self.title
############################################
class Category(models.Model):
  cid = ShortUUIDField(unique=True, max_length=20)
  title = models.CharField(max_length=100, default="Unisex watches")
  image = models.ImageField(upload_to='brand', default="brand.jpg", blank=True, null=True)
  is_blocked =models.BooleanField(default=False)

  class Meta:
    verbose_name_plural = "Categories"

  def category_image(self):
    return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

  def __str__(self):
    return self.title
  ###################################################################################

class Color(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self)->str:
        return self.name


###################################################################################
class Product(models.Model):
  pid = ShortUUIDField(unique =True, max_length = 20)
  user = models.ForeignKey(Account, on_delete = models.SET_NULL,null =True)

  brand = models.ForeignKey(Brand, on_delete = models.SET_NULL,null = True, related_name ="brand")
  category = models.ForeignKey(Category, on_delete = models.SET_NULL,null = True, related_name ="category")

  title = models.CharField(max_length = 100,default = "Fresh pear")
  image = models.ImageField(upload_to=user_directory_path, default = "product.jpg", null=True,blank=True)
  description = models.TextField(null =True, blank =True, default = "This is the product")

  price = models.DecimalField(max_digits =10, decimal_places =2, default = 1.99 )
  old_price = models.DecimalField(max_digits =10, decimal_places =2, default = 2.99)

  specifications = models.TextField(null =True, blank =True)
  tags = models.CharField(max_length = 100,default = "Classic",null=True, blank=True)
  stock_count = models.CharField(max_length = 100,default = "10",null=True, blank=True)

  
  product_status = models.CharField(choices=STATUS_CHOICE, max_length=10, default='in_review')
  status = models.BooleanField(default=True)
  in_stock = models.BooleanField(default=True)

  featured = models.BooleanField(default=False)
  digital = models.BooleanField(default=False)
  featured = models.BooleanField(default=False)
  sku = ShortUUIDField(unique =True, max_length=20)

  date = models.DateTimeField(auto_now_add =True)
  updated = models.DateTimeField(null=True, blank=True)
  mfd=models.DateTimeField(auto_now_add=False,null=True, blank=True)
  return_policy= models.CharField(max_length = 100,default = "10", null=True, blank=True)
  warrenty = models.CharField(max_length = 100,default = "1", null=True, blank=True)
  is_active = models.BooleanField(default=True)

  class Meta:
      verbose_name_plural = 'Products'

  def product_image(self):
      return mark_safe("<img src='%s' width ='50' height='50' />" % (self.image.url))
   
  def __str__(self):
      return self.title
  
  def get_percentage(self):
    new_price = (self.price / self.old_price) * 100
    return new_price

  ############################################################################################   
   
class ProductImages(models.Model):
    images = models.ImageField(upload_to='product_images',default='product.jpg')
    product = models.ForeignKey(Product,related_name='p_images', on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
      verbose_name_plural = 'Product Images'

########################################################################################################################
  
class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variant')
    color = models.ForeignKey(Color,on_delete=models.CASCADE)
    price = models.DecimalField(max_digits =10, decimal_places =2, default = 1.99 )
    old_price = models.DecimalField(max_digits =10, decimal_places =2, default = 2.99)
    stock_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='variant_images/', null=True, blank=True)

    class Meta:
      verbose_name_plural = 'Product variants'

    def variant_image(self):
      return mark_safe("<img src='%s' width ='50' height='50' />" % (self.image.url))
   
    def __str__(self):
      return self.product.title
  
    def get_percentage(self):
      new_price = (self.price / self.old_price) * 100
      return new_price
    
###########################################################################################################
   
class VariantImages(models.Model):
    images = models.ImageField(upload_to='variant_images',default='variant.jpg')
    productvariant = models.ForeignKey(ProductVariant,related_name='v_images', on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Product Variants'

    def Variant_image(self):
        return mark_safe("<img src='%s' width ='50' height='50' />" % (self.images.url))

    # def __str__(self):
    #     return str(self.product)
    def __str__(self):
        return f"Variant Image: {self.pk}"  # Changed the __str__ method to display image ID or any other identifier


#################cart, order, orderitems and Address######################################

    
class Cart(models.Model):
    cart_id=models.CharField(max_length=250,blank=True)
    date_added=models.DateField(auto_now_add=True)

    def __str__(self):
        return self.cart_id

class CartItem(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE)
    quantity=models.IntegerField()
    is_active=models.BooleanField(default=True)
    variations = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True)

    def sub_total(self):
        return self.variations.price * self.quantity

    def __str__(self):
        return self.product.title
    
   
class Address(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, default='Robin')
    address_type = models.CharField(max_length=10, choices=[('HOME', 'Home'), ('WORK', 'Work')],default='HOME' )
    first_name = models.CharField(max_length=100, default=None)
    last_name = models.CharField(max_length=100, default=None)
    email = models.CharField(max_length=100, default=None)
    phone = models.CharField(max_length=10, default=None)
    address_line_1 = models.CharField(max_length=100,default='Royal house')
    address_line_2 = models.CharField(max_length=100, blank=True,)
    city = models.CharField(max_length=50, default='kollam')
    state = models.CharField(max_length=50, default='kerala')
    postal_code = models.CharField(max_length=10, default='690522')
    country = models.CharField(max_length=50, default='India')
    is_active=models.BooleanField(default=True)

    def __str__(self):
        return f"{self.address_type} - {self.first_name} - {self.address_line_1}"



class Payment(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)
    amount_paid = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.payment_id



class orderAddress(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, default='Robin')
    address_type = models.CharField(max_length=10, choices=[('HOME', 'Home'), ('WORK', 'Work')],default='HOME' )
    first_name = models.CharField(max_length=100, default=None)
    last_name = models.CharField(max_length=100, default=None)
    email = models.CharField(max_length=100, default=None)
    phone = models.CharField(max_length=10, default=None)
    address_line_1 = models.CharField(max_length=100,default='Royal house')
    address_line_2 = models.CharField(max_length=100, blank=True,)
    city = models.CharField(max_length=50, default='kollam')
    state = models.CharField(max_length=50, default='kerala')
    postal_code = models.CharField(max_length=10, default='690522')
    country = models.CharField(max_length=50, default='India')
    is_active=models.BooleanField(default=True)

    def __str__(self):
        return f"{self.address_type} - {self.first_name} - {self.address_line_1}"

    
class Order(models.Model):
    
    STATUS =(
        ('New','New'),
        ('Accepted','Accepted'),
        ('Completed','Completed'),
        ('Cancelled','Cancelled'),
        ('Rejected','Rejected'),
    )
    user=models.ForeignKey(Account,on_delete=models.SET_NULL,null=True)
    payment=models.ForeignKey(Payment,on_delete=models.SET_NULL,blank=True,null=True)
    order_number = models.CharField(max_length=20)
    order_total = models.FloatField()
    tax=models.FloatField(null=True)
    status=models.CharField(max_length=10, choices=STATUS, default='New')
    ip =  models.CharField(blank=True,max_length=20)
    is_ordered=models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    selected_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    discount=models.FloatField(null=True)
    paymenttype=models.CharField(max_length=100,null=True)
    address=models.ForeignKey(orderAddress, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return self.user.first_name
    
class OrderProduct(models.Model):
    order=models.ForeignKey(Order,on_delete=models.SET_NULL, null=True,)
    payment = models.ForeignKey(Payment,on_delete=models.SET_NULL,blank=True,null=True)
    user=models.ForeignKey(Account,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    product_type=models.CharField(max_length=20)
    quantity=models.IntegerField()
    product_price=models.FloatField()
    ordered=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    color = models.CharField(max_length=50,null=True)
    

    def __str__(self):
        return self.product.title
    
###########################################################################################################
    



class wallet(models.Model):
    user=models.ForeignKey(Account, on_delete=models.CASCADE)
    wallet_amount=models.FloatField(default=100)
    created_on=models.DateField(auto_now=True)


    def __str__(self):
        return(self.user.username,self.wallet_amount)
    
class WalletTransaction(models.Model):
    user=models.ForeignKey(Account, on_delete=models.CASCADE)
    Wallet=models.ForeignKey(wallet, on_delete=models.CASCADE)
    status=models.CharField(max_length=10, null=True)
    amount=models.FloatField(default=100)
    created_at=models.DateTimeField(auto_now_add=True)


class WishList(models.Model):
	user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
	product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
	date_added = models.DateField(default=timezone.now)
    

############################################################################################################
   
class Coupon(models.Model):
    code = models.CharField(max_length=10, unique=True)
    description = models.CharField(max_length=50, blank=True)
    discount = models.PositiveIntegerField(help_text="Discount percentage")
    expiration_date = models.DateField()
    minimum_purchase_value = models.PositiveIntegerField(blank=False,default=1000)
    maximum_purchase_value = models.PositiveIntegerField(blank=False,default=10000)
    Usage_count=models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    def RedeemedCoupon(self, user):
        redeemed_details = RedeemedCoupon.objects.filter(coupon=self, user=user, is_redeemed=True)
        return redeemed_details.exists()
    def validate_usage_count(self, user):
        if self.Usage_count is not None:
            redeemed_count = RedeemedCoupon.objects.filter(coupon=self, user=user, is_redeemed=True).count()
            return redeemed_count < self.Usage_count
        return True
    
class RedeemedCoupon(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    redeemed_date = models.DateTimeField(auto_now_add=True)
    is_redeemed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.coupon.code} redeemed by {self.user.username} on {self.redeemed_date}"
    
class Banner(models.Model):
    banner_name = models.CharField(max_length=50, blank=True)
 
    is_active = models.BooleanField(default=True)
    set=models.BooleanField(default=False)

    def __str__(self):
        return self.banner_name
    
class BannerImage(models.Model):
    banner=models.ForeignKey(Banner,on_delete=models.CASCADE,related_name='images')  
    images = models.ImageField(upload_to='banneer_images/', blank=True) 
    
    def __str__(self):
        return self.banner.banner_name