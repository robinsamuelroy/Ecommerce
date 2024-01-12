from collections import defaultdict
import datetime
from io import BytesIO
import os
from django.shortcuts import render,redirect,get_object_or_404
from store.models import *
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from admin_panel.forms import BrandForm, ColorForm, CreateProductForm, ProductVariantForm
from django.http import HttpResponse, HttpResponseBadRequest,HttpResponseRedirect
from django.forms import inlineformset_factory
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from admin_panel.forms import CouponForm
from admin_auth import views
from django.db.models import Count, Sum
from datetime import datetime
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile

from django.http import JsonResponse
from django.http import HttpResponse
from store.models import *


# Create your views here.
# @login_required(login_url='admin_auth:admin_login')
# @cache_control(no_cache=True, must_revalidate=True, no_store=True)
# def dashboard(request):
#   if request.user.is_authenticated and not request.user.is_superadmin:
#     return redirect('admin_auth:admin_login')
  
#   product_count = Product.objects.count()
#   category_count = Category.objects.count()

#   context={
#         'product_count':product_count,
#         'category_count':category_count
#     }
  
#   return render(request,'admin_panel/dashboard.html',context)

from PIL import Image

from django.core.files.uploadedfile import SimpleUploadedFile

def resize_image(image, output_width=1200, output_height=400):
    original_image = Image.open(image)
    if original_image.mode == 'RGBA':
        original_image = original_image.convert('RGB')

    resized_image = original_image.resize((output_width, output_height), resample=Image.BICUBIC)

    temp_directory = "path/to/temporary/"
    os.makedirs(temp_directory, exist_ok=True)

    temp_file_path = os.path.join(temp_directory, "resized_image.jpg")
    resized_image.save(temp_file_path)

    return temp_file_path

def add_banners(request):
    if request.method == 'POST':
        banner_name = request.POST.get('banner_name')
        images = request.FILES.getlist('images[]')

        if not banner_name or not images:
            messages.error(request, 'Provide Proper banner name and images')
            return redirect('admin_panel:add_banner')  # Redirect back to the form page, or adjust the URL as needed
        
        else:
            banner = Banner.objects.create(banner_name=banner_name)
            for image in images:
                resized_image_path = resize_image(image)
                banner_image = BannerImage(banner=banner, images=SimpleUploadedFile("resized_image.jpg", open(resized_image_path, "rb").read()))
                banner_image.save()

                # Clean up temporary files
                os.remove(resized_image_path)
            
            messages.success(request, 'Banner added successfully')
            print('hai')
            return redirect('admin_panel:display')  # Redirect to the desired page after successfully adding the banner

    return render(request, 'admin_panel/add_banner.html')




def display(request):
    banners = Banner.objects.all()
    return render(request, 'admin_panel/list_banner.html', {'banners': banners})

  

def delete_banner(request,banner_id):
    banner=Banner.objects.get(pk=banner_id)
    if banner.set==True:
       messages.error(request,'This banner is set as default banner,Set another one')
    else:
        banner.delete()   
    return redirect('admin_panel:display')

#####################################################################################################


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def dashboard(request):
    
    if not request.user.is_authenticated:
        return redirect('admin_auth:admin_login')

    total_users_count = int(Account.objects.count())
    product_count = Product.objects.count()
    user_order = Order.objects.filter(is_ordered=True).count()
    # for i in monthly_order_totals:
    completed_orders = Order.objects.filter(is_ordered=True)

    monthly_totals_dict = defaultdict(float)

    # Iterate over completed orders and calculate monthly totals
    for order in completed_orders:
        order_month = order.created_at.strftime('%m-%Y')
        monthly_totals_dict[order_month] += float(order.order_total)

    print(monthly_totals_dict)
    months = list(monthly_totals_dict.keys())
    totals = list(monthly_totals_dict.values())

    variants = ProductVariant.objects.all()

    context = {
        'total_users_count': total_users_count,
        'product_count': product_count,
        'order': user_order,
        'variants': variants,
        'months': months,
        'totals': totals,


    }
    return render(request, 'admin_panel/charts.html', context)



@login_required(login_url='admin_auth:admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def charts(request):
    if not request.user.is_authenticated:
        return redirect('admin_auth:admin_login')
    
    return render(request, 'admin_panel/charts.html')


@login_required(login_url='admin_auth:admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def reports(request):
     if not request.user.is_authenticated:
        return redirect('admin_auth:admin_login')
    
     return render(request, 'admin_panel/report.html')


@login_required(login_url='admin_auth:admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def filtered_sales(request):
    if not request.user.is_authenticated:
        return redirect('admin_auth:admin_login')
    # Get the minimum and maximum price values from the request parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    from_date = f'{start_date}+00:00'
    to_date = f'{end_date} 23:59:59+00:00'
    orders = Order.objects.filter(
        created_at__gte=from_date, created_at__lte=to_date,is_ordered=True )

    context = {
        "sales": orders,
        "start_date": start_date,
        "end_date": end_date

    }

    return render(request, 'admin_panel/report.html', context)

from django.db.models.functions import TruncDate, TruncWeek, TruncMonth, TruncYear
@login_required(login_url='admin_auth:admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def sales_report(request):
    if not request.user.is_authenticated:
        return redirect('admin_auth:admin_login')
    
    if request.method == 'POST':
        fromd=request.POST.get('fromDate')
        tod=request.POST.get('toDate')
        from_date = request.POST.get('fromDate')
        to_date = request.POST.get('toDate')
        time_period = request.POST.get('timePeriod')
        print(time_period)

  
        if not from_date or not to_date:
            
            messages.error(request,"Please provide valid date values.")
            return redirect('admin_panel:sales_report')

    
        try:
            from_date = datetime.strptime(from_date, '%Y-%m-%d')
            to_date = datetime.strptime(to_date, '%Y-%m-%d')
        except ValueError:
            return HttpResponseBadRequest("Invalid date format.")

        
        if time_period == 'all':
            sales_data = Order.objects.filter(created_at__range=[from_date, to_date], is_ordered=True) \
                .annotate(truncated_date=TruncDate('created_at')) \
                .values('truncated_date') \
                .annotate(total_orders=Count('id'), total_revenue=Sum('order_total'))
        elif time_period == 'daily':
            sales_data = Order.objects.filter(created_at__date__range=[from_date, to_date], is_ordered=True) \
                .annotate(truncated_date=TruncDate('created_at')) \
                .values('truncated_date') \
                .annotate(total_orders=Count('id'), total_revenue=Sum('order_total'))
        elif time_period == 'weekly':
            sales_data = Order.objects.filter(created_at__range=[from_date, to_date], is_ordered=True) \
                .annotate(truncated_date=TruncWeek('created_at')) \
                .values('truncated_date') \
                .annotate(total_orders=Count('id'), total_revenue=Sum('order_total'))
        elif time_period == 'monthly':
            sales_data = Order.objects.filter(created_at__range=[from_date, to_date], is_ordered=True) \
                .annotate(truncated_date=TruncMonth('created_at')) \
                .values('truncated_date') \
                .annotate(total_orders=Count('id'), total_revenue=Sum('order_total'))
        elif time_period == 'yearly':
            sales_data = Order.objects.filter(created_at__range=[from_date, to_date], is_ordered=True) \
                .annotate(truncated_date=TruncYear('created_at')) \
                .values('truncated_date') \
                .annotate(total_orders=Count('id'), total_revenue=Sum('order_total'))


        # Define the dateWise queryset for daily sales data
        dateWise = Order.objects.filter(created_at__date__range=[from_date, to_date],is_ordered=True) \
        .values('created_at__date') \
        .annotate(total_orders=Count('id'), total_revenue=Sum('order_total'))
        
        

        # Calculate Total Users
        total_users = Order.objects.filter(is_ordered=True).values('user').distinct().count()

        # Calculate Total Products
        total_products = OrderProduct.objects.filter(order__is_ordered=True).values('product').distinct().count()

        # Calculate Total Orders
        total_orders = Order.objects.filter(is_ordered=True).count()

        # Calculate Total Revenue
        total_revenue = Order.objects.filter(is_ordered=True).aggregate(total_revenue=Sum('order_total'))['total_revenue']
        
        context = {
            'sales_data': sales_data,
            'from_date': from_date,
            'to_date': to_date,
            'report_type': time_period,
            'total_users': total_users,
            'total_products': total_products,
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'dateWise': dateWise,
            'fromd':fromd,
            'tod':tod, 
        }

        return render(request, 'admin_panel/sales_report.html', context)

    return render(request, 'admin_panel/sales_report.html')


################################################################################

def admin_products_list(request):
  products = Product.objects.all()
  p=Paginator(Product.objects.all(),10)
  page=request.GET.get('page')
  productss=p.get_page(page)
  
  context ={
    "products":products ,
    "productss":productss
  }
  return render(request, 'admin_panel/admin_products_list.html',context)

################################################################################

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_products_details(request, pid):
    if not request.user.is_authenticated:
        return redirect('admin_auth:admin_login')

    try:
        product = Product.objects.get(pid=pid)
        product_images = ProductImages.objects.filter(product=product)
    except Product.DoesNotExist:
        return HttpResponse("Product not found", status=404)

    if request.method == 'POST':
        form = CreateProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            # Save the form including the image
            product = form.save(commit=False)
            product_image = form.cleaned_data['new_image']
            if product_image is not None:
                product.image = product_image
            product.save()

            # Update or create additional images
            for i in product_images:
                image_field_name = f'product_image{i.id}'
                image = request.FILES.get(image_field_name)

                if image:
                    i.Images = image
                    i.save()

            return redirect('admin_panel:admin_products_list')
        else:
            print(form.errors)
            context = {
                'form': form,
                'product': product,
                'product_images': product_images,
            }
            return render(request, 'admin_panel/admin_products_details.html', context)
    else:
        initial_data = {'new_image': product.image.url if product.image else ''}
        form = CreateProductForm(instance=product, initial=initial_data)

    context = {
        'form': form,
        'product': product,
        'product_images': product_images,
    }
    return render(request, 'admin_panel/admin_products_details.html', context)

###########################################################################

@login_required(login_url='admin_auth:admin_login')
def block_unblock_products(request, pid):
  if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)
  product = get_object_or_404(Product, pid=pid)
  if product.status:
    product.status=False
  else:
      product.status=True
  product.save()
  return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
  
    
    
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_product(request):
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)

    categories = Category.objects.all()

    if request.method == 'POST':
        product_name = request.POST.get('title')
        product_stock_count = request.POST.get('stock_count')
        description = request.POST.get('description')
        max_price = request.POST.get('old_price')
        sale_price = request.POST.get('price')
        category_name = request.POST.get('category')
        # validations
        validation_errors = []

        try:
            # product_stock_count = int(product_stock_count)
            # if product_stock_count < 0:
            #     validation_errors.append("Stock Count must be a non-negative integer.")

            max_price = float(max_price)
            if max_price < 0:
                validation_errors.append("Max Price must be a non-negative number.")

            sale_price = float(sale_price)
            if sale_price < 0:
                validation_errors.append("Sale Price must be a non-negative number.")
        except ValueError as e:
            validation_errors.append(str(e))

        if validation_errors:
            form = CreateProductForm()
            content = {
                'categories': categories,
                'form': form,
                'additional_image_count': range(1, 4),
                'error_messages': validation_errors,
            }
            return render(request, 'admin_panel/admin_add_product.html', content)
        
        # till here
        

        category = get_object_or_404(Category, title=category_name)

        product = Product(
            title=product_name,
            stock_count=product_stock_count,
            category=category,
            description=description,
            old_price=max_price,
            price=sale_price,
            image=request.FILES['image_feild']
        )
        product.save()

        # Handling additional images
        additional_image_count = 5  # Change this to the desired count of additional images
        for i in range(1, additional_image_count + 1):
            image_field_name = f'product_image{i}'
            image = request.FILES.get(image_field_name)
            if image:
                ProductImages.objects.create(product=product,images=image)

        return redirect('admin_panel:admin_products_list')
    else:
        form = CreateProductForm()

    content = {
        'categories': categories,
        'form': form,
         'additional_image_count': range(1, 4), 
    }
    return render(request, 'admin_panel/admin_add_product.html', content)


#ends here


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_product(request,pid):
    if not request.user.is_authenticated:
        return redirect('admin_auth:admin_login')
    try:
        product = Product.objects.get(pid=pid)
        product.delete()
        return redirect('admin_panel:admin_products_list')
    except Product.DoesNotExist:
        return HttpResponse("Product not found", status=404)
    
    
  ###################################################################################################  
    
def admin_category_list(request):
    if not request.user.is_authenticated:
        return redirect('admin_auth:admin_login')
    
    categories = Category.objects.all()
    
    context = {
        'categories':categories
    }
    
    return render(request,'admin_panel/admin_category_list.html',context)




def admin_add_category(request):
    if request.method == 'POST':
        cat_title = request.POST.get('category_name')
        if Category.objects.filter(title=cat_title).exists():
            messages.error(request, 'Category with this title already exists.')
        else:
            cat_data = Category(title=cat_title, image=request.FILES.get('category_image'))
            cat_data.save()
            messages.success(request, 'Category added successfully.')
            return redirect('admin_panel:admin_add_category')  # Replace 'your_redirect_url_name' with your desired URL
        
    return render(request, 'admin_panel/admin_add_category.html')



def admin_category_edit(request, cid):
    if not request.user.is_authenticated:
        return redirect('admin_auth:admin_login')

    # Using get_object_or_404 to get the Category or return a 404 response if it doesn't exist
    categories = get_object_or_404(Category, cid=cid)

    if request.method == 'POST':
        # Update the fields of the existing category object
        cat_title = request.POST.get("category_name")
        cat_image = request.FILES.get('category_image')

        # Update the category object with the new title and image
        categories.title = cat_title
        if cat_image is not None:
            categories.image = cat_image

        
        # Save the changes to the database
        categories.save()

        # Redirect to the category list page after successful update
        return redirect('admin_panel:admin_category_list')

    # If the request method is GET, render the template with the category details
    context = {
        "categories_title": categories.title,
        "categories_image": categories.image,
    }

    return render(request, 'admin_panel/admin_category_edit.html', context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_category(request,cid):
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)
    try:
        category=Category.objects.get(cid=cid)
    except ValueError:
        return redirect('admin_panel:admin_category_list')
    category.delete()

    return redirect('admin_panel:admin_category_list')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def available_category(request,cid):
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)
    
    category = get_object_or_404(Category, cid=cid)
    
    if category.is_blocked:
        category.is_blocked=False
       
    else:
        category.is_blocked=True
    category.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


# variants adding

#################################################################################################
def variant_list(request):
    product_variations = ProductVariant.objects.all()
    form = ProductVariantForm()
    context = {
        'product_variant': product_variations,
        'form':form
        }
    return render(request, 'admin_panel/listvariants.html', context)



# def add_variant(request):
#     if request.method == "POST":
#         variant_form = ProductVariantForm(request.POST,request.FILES)
#         if variant_form.is_valid():
#             variant_form.save()
#             return redirect("admin_panel:variant-list")
#     else:
#         variant_form = ProductVariantForm()
#     context = {
#         'variant_form': variant_form
#         }
      
#     return render(request, 'admin_panel/addvariants.html', context)


# def add_variant(request):
#     additional_image_count = 3  # Define the count of additional images here

#     if request.method == 'POST':
#         variant_form = ProductVariantForm(request.POST, request.FILES)
#         if variant_form.is_valid():
#             variant_instance = variant_form.save(commit=False)
#             variant_instance.save()

#             # Handling additional images
#             for i in range(1, additional_image_count + 1):
#                 image_field_name = f'additional_image_{i}'
#                 image = request.FILES.get(image_field_name)
#                 if image:
#                     VariantImages.objects.create(productvariant=variant_instance, images=image)

#             return redirect('admin_panel:variant-list')  # Adjust the redirect URL as needed
#     else:
#         variant_form = ProductVariantForm()

#     context = {
#         'variant_form': variant_form,
#         'additional_image_count': range(1, additional_image_count + 1),
#     }

#     return render(request, 'admin_panel/addvariants.html', context)

# views.py


def add_variant(request):
    additional_image_count = 3  # Define the count of additional images here

    if request.method == 'POST':
        variant_form = ProductVariantForm(request.POST, request.FILES)
        if variant_form.is_valid():
            variant_instance = variant_form.save(commit=False)
            variant_instance.save()

            # Handling additional images
            for i in range(1, additional_image_count + 1):
                image_field_name = f'additional_image_{i}'
                image = request.FILES.get(image_field_name)
                if image:
                    VariantImages.objects.create(productvariant=variant_instance, images=image)

            return redirect('admin_panel:variant-list')  # Adjust the redirect URL as needed
    else:
        variant_form = ProductVariantForm()

    context = {
        'variant_form': variant_form,
        'additional_image_count': range(1, additional_image_count + 1),
    }

    return render(request, 'admin_panel/addvariants.html', context)





def edit_variant(request, id):
    product = get_object_or_404(ProductVariant, pk=id)
    if request.method == "POST":
        variant_form = ProductVariantForm(request.POST, request.FILES, instance=product)
        if variant_form.is_valid():
            variant_form.save()
            return redirect('admin_panel:variant-list')
    else:
        variant_form = ProductVariantForm(instance=product)

    context = {
        "variant_form": variant_form
    }
    return render(request, 'admin_panel/edit_variants.html', context)

def delete_variant(request, id):
    if request.method == "POST":
        prod = ProductVariant.objects.get(id=id)
        prod.delete()
        return redirect('admin_panel:variant-list')

###############################################################################################

@login_required(login_url="ad_login")
def brand(request):
    pro = Brand.objects.all()
    context = {
      'pro': pro
    }
    return render(request,"admin_panel/brand-info.html",context)

def del_brand(request,id):
    if request.method == "POST":
        pro = Brand.objects.get(pk=id)
        pro.delete()
        return redirect('admin_panel:brand')
    
def edit_brand(request,id):
    brand = get_object_or_404(Brand,pk=id)
    if request.method == "POST":
        brand_form = BrandForm(request.POST,instance=brand)
        if brand_form.is_valid():
            brand_form.save()
            return redirect('admin_panel:brand')
    else:
        brand_form = BrandForm(instance=brand)
    context = {
        'brand_form':brand_form
    }
    return render(request,"admin_panel/edit-brand.html",context)

def add_brand(request):
    if request.method == "POST":
        brand_form = BrandForm(request.POST,request.FILES)
        # image_form = ProductImageFormSet(request.POST, request.FILES, instance=product())
        if brand_form.is_valid():
            # myproduct = product_form.save(commit=False)
            brand_form.save()
            # image_form.instance = myproduct
            # image_form.save()
            # return redirect('products')
            return redirect("admin_panel:brand")
    else:
        brand_form = BrandForm()
        # image_form = ProductImageFormSet(instance=product())
    context = {'brand_form': brand_form}
    return render(request,'admin_panel/add-brand.html',context)


@login_required(login_url="ad_login")
        
def color(request):
    prod = Color.objects.all()
    context = {
      'prod': prod
    }
    return render(request,"admin_panel/color-info.html",context)

def del_color(request,id):
    if request.method == "POST":
        prod = Color.objects.get(pk=id)
        prod.delete()
        return redirect('admin_panel:color')
    
def edit_color(request,id):
    product = get_object_or_404(Color,pk=id)
    if request.method == "POST":
        color_form = ColorForm(request.POST,request.FILES,instance=product)
        if color_form.is_valid():
            color_form.save()
            return redirect('admin_panel:color')
    else:
        color_form = ColorForm(instance=product)
    context = {
        'color_form':color_form
    }
    return render(request,"admin_panel/edit-color.html",context)
    
def add_color(request):
    if request.method == "POST":
        color_form = ColorForm(request.POST,request.FILES)
        if color_form.is_valid():
            color_form.save()
            return redirect("admin_panel:color")
    else:
        color_form = ColorForm()
    context = {'color_form': color_form}
    return render(request, 'admin_panel/add-color.html', context)

##########################################################################################################


@login_required(login_url='admin_auth:admin_login')
def order_list(request):
    if not request.user.is_authenticated:
        return redirect('admin_panel:dashboard')
    
    orders = Order.objects.filter(is_ordered=True).order_by('-created_at')  # Fetch all orders from the Order model
    context = {'orders': orders}
    return render(request, 'admin_panel/orderlist.html', context)

@login_required(login_url='admin_auth:admin_login')
def ordered_product_details(request, order_id):
    if not request.user.is_authenticated:
        return redirect('admin_panel:dashboard')
    
    orders = Order.objects.get(id=order_id)
    print(orders)
    order_instance = Order.objects.get(id=order_id)

# Retrieving related OrderProduct instances using the default reverse relation
    ordered_products = order_instance.orderproduct_set.all()


    print(ordered_products)
    for i in ordered_products:
        total=+(i.product_price*i.quantity)
    payments = Payment.objects.filter(order__id=order_id,user=orders.user)    

    context = {
        'total':total,
        'order': orders,
        'ordered_products': ordered_products,
        'payments':payments
    }
    return render(request, 'admin_panel/ordered_product_details.html', context)

@login_required(login_url='admin_auth:admin_login')
def update_order_status(request, order_id):
    if not request.user.is_authenticated:
        return redirect('admin_panel:dashboard')
    
    if request.method == 'POST':
        order = get_object_or_404(Order, id=int(order_id))
        status = request.POST['status']
        order.status = status
        order.save()
        if status=='Completed':
            payment=Payment.objects.get(order__id=order_id,user=order.user)
            if payment.payment_method=='Cash on Delivery':
                payment.status='Paid'
                payment.save()
        return redirect('admin_panel:order_list')
    else:
        return HttpResponseBadRequest("Bad request.")
    

###################################################################################################


def add_coupon(request):
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_panel:list_coupons')  # Redirect to the list of coupons or another page
    else:
        form = CouponForm()
    
    return render(request, 'admin_panel/add coupons.html', {'form': form})


# from cart.models import *
def list_coupons(request):
    coupons=Coupon.objects.filter(is_active=True)
    return render(request,'admin_panel/list_coupon.html',{"coupons":coupons})

@login_required(login_url='admin_auth:admin_login')
def delete_coupon(request, id):
    if not request.user.is_authenticated:
        return redirect('admin_auth:admin_login')

    try:
        coupon = Coupon.objects.get(id=id)
        coupon.is_active=False
        coupon.save()
    except Coupon.DoesNotExist:
        # Handle the case where the coupon with the given ID doesn't exist
        pass

    return redirect('admin_panel:list_coupons')


@login_required(login_url='admin_auth:admin_login')
def edit_coupon(request, id):
    coupon = get_object_or_404(Coupon, pk=id)
    if not request.user.is_authenticated:
        return redirect('admin_auth:admin_login')

    if request.method == 'POST':
        form = CouponForm(request.POST,instance=coupon)
        if form.is_valid():
            form.save()
            return redirect('admin_panel:list_coupons')
    else:
        form = CouponForm(instance=coupon)
    return render(request, 'admin_panel/edit_coupon.html', {'form': form})

##################################################################################
