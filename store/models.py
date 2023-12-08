from django.db import models
from shortuuidfield import ShortUUIDField
from accounts.models import Account
from django.utils.html import mark_safe

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

class Category(models.Model):
  cid = ShortUUIDField(unique=True, max_length=20)
  title = models.CharField(max_length=100, default="Unisex watches")
  image = models.ImageField(upload_to='category', default="category.jpg", blank=True, null=True)
  is_blocked =models.BooleanField(default=False)

  class Meta:
    verbose_name_plural = "Categories"

  def category_image(self):
    return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

  def __str__(self):
    return self.title



class Product(models.Model):
  pid = ShortUUIDField(unique =True, max_length = 20)
  user = models.ForeignKey(Account, on_delete = models.SET_NULL,null =True)

  brand = models.ForeignKey(Brand, on_delete = models.SET_NULL,null = True, related_name ="brand")
  category = models.ForeignKey(Category, on_delete = models.SET_NULL,null = True, related_name ="category")

  title = models.CharField(max_length = 100,default = "Fresh pear")
  image = models.ImageField(upload_to=user_directory_path, default = "product.jpg", null=True,blank=True)
  description = models.TextField(null =True, blank =True, default = "This is the product")

  price = models.DecimalField(max_digits =10, decimal_places =2, default = 1.99 )
  # old_price = models.DecimalField(max_digits =10, decimal_places =2, default = 2.99)

  tags = models.CharField(max_length = 100,default = "Classic",null=True, blank=True)
  stock_count = models.CharField(max_length = 100,default = "10",null=True, blank=True)

  specifications = models.TextField(null =True, blank =True)
  status = models.BooleanField(default=True)
  in_stock = models.BooleanField(default=True)
  featured = models.BooleanField(default=False)
  digital = models.BooleanField(default=False)
  featured = models.BooleanField(default=False)
  sku = ShortUUIDField(unique =True,max_length = 20)

  date = models.DateTimeField(auto_now_add =True)
  updated = models.DateTimeField(null=True, blank=True)
  mfd=models.DateTimeField(auto_now_add=False,null=True, blank=True)
  return_policy= models.CharField(max_length = 100,default = "10", null=True, blank=True)
  warrenty = models.CharField(max_length = 100,default = "1", null=True, blank=True)

  class Meta:
    verbose_name_plural = "Products"
    
  def product_image(self):
    return mark_safe('<img src= "%s" width="50" height= "50" />' % (self.image.url))
  
  def __str__(self):
      return self.title
    
  def get_percentage(self):
    new_price = (self.price /self.old_price) * 100
    return new_price
  
class Color(models.Model):
    name = models.CharField(max_length=100)
    # price = models.IntegerField(default=0)
    def __str__(self)->str:
        return self.name
    
class Material(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name
  
class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    color=models.ForeignKey(Color,on_delete=models.CASCADE)
    material=models.ForeignKey(Material,on_delete=models.CASCADE)
    price = models.DecimalField(max_digits =10, decimal_places =2, default = 1.99 )
    # old_price = models.DecimalField(max_digits =10, decimal_places =2, default = 2.99)
    stock_count = models.IntegerField(default=0)

    @property
    def quantity(self):
        return self.stock_count

    def __str__(self):
        return f"{self.product.title} - {self.color}"

    

class ProductImages(models.Model):
  Images = models.ImageField(upload_to="products-images", default = "product.jpg")
  product = models.ForeignKey(Product, related_name='p_images',on_delete = models.SET_NULL,null =True)
  date = models.DateField(auto_now_add =True)
  
  class Meta:
    verbose_name_plural = "Product Images"

##################cart, order, orderitems and Address######################################


class CartOrder(models.Model):
  user = models.ForeignKey(Account, on_delete=models.CASCADE)
  price = models.DecimalField(max_digits =10, decimal_places =2, default = 1.99 )
  paid_status = models.BooleanField(default=False)
  order_date = models.DateTimeField(auto_now_add=True)
  product_status = models.CharField(choices=STATUS_CHOICE, max_length=10, default='processing')

  class Meta:
     verbose_name_plural = 'Cart Order'


class CartOderItems(models.Model):
  order = models.ForeignKey(CartOrder, on_delete=models.CASCADE)
  product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
  invoice_no = models.CharField(max_length=200, default='invoice number')
  product_status = models.CharField(max_length=200)
  item = models.CharField(max_length=200)
  image = models.CharField(max_length=200)
  qty = models.IntegerField(default=0)
  price = models.DecimalField(max_digits =10, decimal_places =2, default = 1.99)
  total = models.DecimalField(max_digits =10, decimal_places =2, default = 1.99)

  def order_img(self):
    return mark_safe('<img src= "/media/%s" width="50" height= "50" />' % (self.image))
  
##############################Product Review, wishlist and Address###########################################

class ProductReview(models.Model):
   user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
   product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
   review = models.TextField()
   rating = models.IntegerField(choices=RATING, default=None)
   date = models.DateTimeField(auto_now_add=True)

   class Meta:
    verbose_name_plural = "Product Reviews"
    
   def product_image(self):
      return mark_safe('<img src= "%s" width="50" height= "50" />' % (self.image.url))
  
   def __str__(self):
      return self.product.title
   
   def get_rating(self):
      return self.rating
   
class wishlist(models.Model):
   user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
   product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
   date = models.DateTimeField(auto_now_add=True)

   class Meta:
    verbose_name_plural = "Wishlists"
    
   def product_image(self):
      return mark_safe('<img src= "%s" width="50" height= "50" />' % (self.image.url))
  
   def __str__(self):
      return self.product.title
   
class Address(models.Model):
   user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
   address = models.CharField(max_length=100, null=True)
   status = models.BooleanField(default=False)
   










