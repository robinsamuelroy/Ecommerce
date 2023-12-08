from django.shortcuts import render,redirect,get_object_or_404
from store.models import Product,Category,ProductImages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from admin_panel.forms import CreateProductForm
from django.http import HttpResponse,HttpResponseRedirect
from django.forms import inlineformset_factory
from django.contrib import messages
from django.core.paginator import Paginator


# Create your views here.
@login_required(login_url='admin_auth:admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def dashboard(request):
  if request.user.is_authenticated and not request.user.is_superadmin:
    return redirect('admin_auth:admin_login')
  
  product_count = Product.objects.count()
  category_count = Category.objects.count()

  context={
        'product_count':product_count,
        'category_count':category_count
    }
  
  return render(request,'admin_panel/dashboard.html',context)

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
            product_stock_count = int(product_stock_count)
            if product_stock_count < 0:
                validation_errors.append("Stock Count must be a non-negative integer.")

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
                ProductImages.objects.create(product=product, Images=image)

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
        
        
        # cat_data = Category(title=cat_title,
        #                     image=request.FILES.get('category_image'))
    
        # cat_data.save()
    else:
        return render(request, 'admin_panel/admin_category_list.html')
    
    return render(request, 'admin_panel/admin_category_list.html')

    
#######################################################################################



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

    
    # cat_list=Category.objects.filter(parent_id=category_id)
    # for i in cat_list.values():
    #     print(i)
    
    # for category in cat_list:
    #     if category.is_available:
    #         category.is_available=False
    #     else:
    #         category.is_available=True
    #     category.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))