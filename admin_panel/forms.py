from django import forms
from store.models import Product,ProductVariant
from django.core.exceptions import ValidationError
from decimal import Decimal
from store.models import ProductImages

class CreateProductForm(forms.ModelForm):
    new_image = forms.ImageField(required=False)  # Add this line for the new image field
    
    class Meta:
        model = Product
        fields = ['title', 'category', 'description','price', 'new_image']
        
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
    class Meta:
        model = ProductVariant
        fields = ['product', 'color', 'material', 'price', 'stock_count']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

    
    def clean_price(self):
        price = self.cleaned_data.get('price')

        if price is not None and price < Decimal('0'):
            raise forms.ValidationError("Price cannot be negative.")

        return price




# class ProductImagesForm(forms.ModelForm):
#     class Meta:
#         model = ProductImages
#         fields = ['Images']