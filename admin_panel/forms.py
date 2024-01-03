from django import forms
from store.models import *
from django.core.exceptions import ValidationError
from decimal import Decimal
from store.models import ProductImages

class CreateProductForm(forms.ModelForm):
    new_image = forms.ImageField(required=False)  # Add this line for the new image field
    
    class Meta:
        model = Product
        fields = ['title', 'category', 'description','price','old_price', 'new_image']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            
    
    def clean_price(self):
        price = self.cleaned_data.get('price')

        if price is not None and price < Decimal('0'):
            raise forms.ValidationError("Price cannot be negative.")

        return price
    
class ProductVariantForm(forms.ModelForm):
      # Add this line for the new image field
    class Meta:
        model = ProductVariant
        fields = ['product', 'color' ,'price','old_price', 'stock_count','image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

    
    def clean_price(self):
        price = self.cleaned_data.get('price')

        if price is not None and price < Decimal('0'):
            raise forms.ValidationError("Price cannot be negative.")

        return price

class PriceFilterForm(forms.Form):
    min_price = forms.DecimalField(decimal_places=2)
    max_price = forms.DecimalField(decimal_places=2)


class BrandFilterForm(forms.Form):
    brand = forms.ModelChoiceField(queryset=Brand.objects.all(), empty_label="All Brands", required=False)

class CategoryForm(forms.ModelForm):
    class Meta:
       model =  Category
       fields = ["title"]

class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['title']

class ColorForm(forms.ModelForm):
    class Meta:
        model = Color
        fields = ['name']

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = []

from django import forms
class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'description', 'discount', 'expiration_date', 'is_active','minimum_purchase_value','maximum_purchase_value','Usage_count']


        widgets = {
            'expiration_date': forms.DateInput(attrs={'type': 'date'}),
        }

