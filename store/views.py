import datetime
import re
from django.shortcuts import redirect, render
from django.db.models import Count
from django.db import transaction
from django.urls import reverse
from admin_panel.forms import CreateProductForm, OrderForm
from store.models import *
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.contrib import auth
from django.views.decorators.cache import cache_control
from django.db.models import F

#for profile validation

def is_valid_phone(phone):
    # Phone number should be exactly 10 digits
    phone_pattern = "^\d{10}$"
    return re.match(phone_pattern, str(phone)) is not None

def is_valid_postal_code(postal_code):
    # Postal code should be a valid format based on your requirement
    postal_code_pattern = "^[0-9]{6}$"
    return re.match(postal_code_pattern, postal_code) is not None

def is_not_empty_or_whitespace(value):
    # Check if the value is not empty or contains only whitespace
    return bool(value.strip())

#home, shop, product detail,  view
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def home(request):
    blocked_categories =Category.objects.filter(is_blocked =True)
    products = Product.objects.filter(featured = True, status =True).exclude(category__in=blocked_categories)
    latest = Product.objects.filter(status=True).order_by("-id")[:10]
    categories =Category.objects.filter(is_blocked =False)
    print(categories)
   
    context = {
        "products":products,
        "latest":latest,
        "categories":categories
    }
    return render(request, 'store/home.html',context)


def product_list(request):
    blocked_categories =Category.objects.filter(is_blocked =True)
    products = Product.objects.filter(status =True).exclude(category__in=blocked_categories)
    categories =Category.objects.filter(is_blocked =False)
    p=Paginator(Product.objects.filter(status =True).exclude(category__in=blocked_categories),10)
    page=request.GET.get('page')
    productss=p.get_page(page)

    #Filtering out cases where price and old price are the same
    latest = products.filter(price__lt=F('old_price'))
    
    context = {
        "products":products,
        "categories":categories,
        "productss":productss,
        "latest": latest,
    }
    
    return render(request,'store/product-list.html', context)


def category_list(request):
    category = Category.objects.filter(is_blocked=False)
    context ={
        "category":category,
       
    }
    return render(request,'store/category-list.html', context )

# def catagory_list(request):
    
#     search_query = request.GET.get('search')

#     if search_query:
#         categories = Category.objects.filter(Q(category_name__icontains=search_query))
#     else:
#      categories = Category.objects.filter(is_active=True)

#     context={

#         'categories': categories
#       }

#     return render(request,'admin_panel/category.html',context)



def category_product_list(request, cid):
    category = Category.objects.get(cid=cid)
    product = Product.objects.filter(category=category,status =True)
    
    
    context ={
        "category":category,
        "product":product
    }
    
    return render(request,'store/category-product-list.html', context)


def product_detail(request, pid):
 try:
    product = Product.objects.get(pid=pid)
    p_image = product.p_images.all()
    variant = ProductVariant.objects.filter(product=product)
    distinct_colors = variant.values_list('color__name', flat=True).distinct()
    print(distinct_colors)

    selected_color = request.GET.get('selected_color', None)
    selected_variants = None
    if selected_color:
     sel=Color.objects.get(name=selected_color)
    print(selected_color)
    if selected_color:
        selected_variants = ProductVariant.objects.filter(product=product, color=sel)
    
        print(selected_color)

 except Product.DoesNotExist:
        return HttpResponse("Product not found", status=404)

 context = {
        "product" : product,
        "p_image" : p_image,
         "distinct_colors": distinct_colors,
        "variant" : variant,
        'selected_color': selected_color,
        'selected_variants': selected_variants,
    }
 return render(request, 'store/product-detail.html', context)

###################################################################################

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
     cart = request.session.create()
    return cart

@login_required(login_url='accounts:login')
def cart(request, total=0, quantity=0, cart_items=None):
    try:
        tax=0
        grand_total=0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.variations.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total)/100
        grand_total = total+tax
    except ObjectDoesNotExist:
        pass 

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total
    }

    return render(request, 'store/cart.html', context)

@login_required(login_url='accounts:login')
def add_cart(request, pid):
   
   
   color = request.GET.get('color')
   if color is None or color.lower() == 'none':
       messages.error(request, 'Please choose a color', extra_tags='danger')
   
       return HttpResponseRedirect(reverse('store:product-detail', args=(pid,)))
   
   else:
    print("hsabfhsabbsvjncjxzncja") 
    sel=Color.objects.get(name=color)
    print(sel)
    print(color)
    
    product = Product.objects.get(pid=pid)

    try:
        variant = ProductVariant.objects.get(product=product, color=sel.id)
    except ProductVariant.DoesNotExist:
        messages.warning(request, 'Variation not available, please select another variation')
        return HttpResponseRedirect(reverse('store:product_detail', args=(pid)))

    if variant.stock_count >= 1:
        if request.user.is_authenticated:
            try:
                is_cart_item_exists = CartItem.objects.filter(
                    user=request.user, product=product, variations=variant).exists()
            except CartItem.DoesNotExist:
                is_cart_item_exists = False

            if is_cart_item_exists:
                to_cart = CartItem.objects.get(user=request.user, product=product, variations=variant)
                variation = to_cart.variations
                if to_cart.quantity < variation.stock_count:
                    to_cart.quantity += 1
                    to_cart.save()
                else:
                    messages.success(request, "Product out of stock")
            else:
                try:
                    cart = Cart.objects.get(cart_id=_cart_id(request))
                except Cart.MultipleObjectsReturned:
                    # If multiple records exist, choose the first one
                    cart = Cart.objects.filter(cart_id=_cart_id(request)).first()
                except Cart.DoesNotExist:
                    cart = Cart.objects.create(cart_id=_cart_id(request))
                to_cart = CartItem.objects.create(
                    user=request.user,
                    product=product,
                    variations=variant,
                    quantity=1,
                    is_active=True,
                    cart=cart  # Associate the CartItem with the Cart
                )
            return redirect('store:shopping_cart')
        else:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
            except Cart.MultipleObjectsReturned:
                # If multiple records exist, choose the first one
                cart = Cart.objects.filter(cart_id=_cart_id(request)).first()
            except Cart.DoesNotExist:
                cart = Cart.objects.create(cart_id=_cart_id(request))
            is_cart_item_exists = CartItem.objects.filter(cart=cart, product=product, variations=variant).exists()
            if is_cart_item_exists:
                to_cart = CartItem.objects.get(cart=cart, product=product, variations=variant)
                to_cart.quantity += 1
            else:
                to_cart = CartItem(cart=cart, product=product, variations=variant, quantity=1)
            to_cart.save()
            return redirect('cart:shopping_cart')
    else:
        messages.warning(request, 'This item is out of stock.')
        return redirect('store:product-detail', pid)

    messages.warning(request, 'Variant not found.')  # Add an error message for debugging
    return redirect('store:product-detail', pid)




def remove_cart(request, pid, cart_item_id):
    
    product = get_object_or_404(Product, pid=pid)

    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            variant = cart_item.variations
            variant.stock_count += 1
            cart_item.quantity -= 1

            variant.save()
            cart_item.save()    
        else:
            cart_item.delete()
    except:
        pass
    return redirect('store:shopping_cart')



def remove_cart_item(request, pid, cart_item_id):
    product = get_object_or_404(Product, pid=pid)

    try:
        if request.user.is_authenticated:
            # If the user is authenticated, remove the cart item associated with the user
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            # If the user is not authenticated, remove the cart item associated with the session cart
            cart_item = CartItem.objects.get(product=product, cart__cart_id=_cart_id(request), id=cart_item_id)
        
        # Delete the cart item
        cart_item.delete()
    except CartItem.DoesNotExist:
        pass  # Handle the case where the cart item doesn't exist

    # Redirect back to the shopping cart page
    return redirect('store:shopping_cart')


def newcart_update(request):
    new_quantity = 0
    total = 0
    tax = 0
    grand_total = 0
    quantity=0
    counter=0

    if request.method == 'POST' and request.user.is_authenticated:
        prod_id = request.POST.get('product_id')
        print(prod_id)
        cart_item_id = int(request.POST.get('cart_id'))
        qty=int(request.POST.get('qty'))
        counter=int(request.POST.get('counter'))
        print(qty)
        product = get_object_or_404(Product, pid=prod_id)
        print(product)

        try:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
            cart_items = CartItem.objects.filter(user=request.user)
        except CartItem.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Cart item not found'})
        
        if cart_item.variations:
            print('hjsgfgfhghjfg')
            print(cart_item.variations)
            variation = cart_item.variations  # Access the variation associated with the cart item
            if cart_item.quantity < variation.stock_count:
                cart_item.quantity += 1
                cart_item.save()
               
                sub_total=cart_item.quantity * variation.price
                new_quantity = cart_item.quantity
            else:
                message = "out of stock"
                return JsonResponse({'status': 'error', 'message': message})      
        for cart_item in cart_items:
            total += (cart_item.variations.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total) / 100
        grand_total = total + tax
        print(new_quantity,total,tax,grand_total,sub_total)       
        
        

    if new_quantity ==0:
        message = "out of stock"
        return JsonResponse({'status': 'error', 'message': message})
    else:
        return JsonResponse({
            'status': "success",
            'new_quantity': new_quantity,
            "total": total,
            "tax": tax,
            'counter':counter,
            "grand_total": grand_total,
            "sub_total":sub_total,
            
        })
    
def remove_cart_item_fully(request):
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            counter = int(request.POST.get('counter'))
            product_id = request.POST.get('product_id')
            cart_item_id = int(request.POST.get('cart_id'))

            # Get the product and cart item
            product = get_object_or_404(Product, pid=product_id)
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
            cart_items = CartItem.objects.filter(user=request.user)

            # Check if the cart item exists and belongs to the logged-in user
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
                sub_total = cart_item.quantity * cart_item.variations.price

                total = 0
                quantity = 0

                for cart_item in cart_items:
                    total += (cart_item.variations.price * cart_item.quantity)
                    quantity += cart_item.quantity

                tax = (2 * total) / 100
                grand_total = total + tax
                current_quantity = cart_item.quantity

                return JsonResponse({
                    'status': 'success',
                    'tax': tax,
                    'total': total,
                    'grand_total': grand_total,
                    'counter': counter,
                    'new_quantity': current_quantity,
                    'sub_total': sub_total,  # Updated quantity
                })
            else:
                cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
                cart_item.delete()
                message = "the cart item has bee deleted"
                return JsonResponse({'status': 'error', 'message': message}) 

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return HttpResponseBadRequest('Invalid request')

###########################################################################################################

@login_required(login_url='accounts:login')
def checkout(request,total=0, quantity=0, cart_items=None):
        
    if not request.user.is_authenticated:
        return redirect('store:home')
    if 'coupon_discount' in request.session:
                del request.session['coupon_discount']
    try:
        tax = 0
        grand_total = 0
        coupon_discount = 0

        if request.user.is_authenticated:
           cart_items = CartItem.objects.filter(user=request.user, is_active=True)
           addresses = Address.objects.filter(user=request.user,is_active=True)
           coupons = Coupon.objects.filter(is_active=True)
           
           coupons = [coupon for coupon in coupons if coupon.validate_usage_count(request.user)]
           print(coupons)
          
        else:
            addresses = []

        for cart_item in cart_items:
            total += (cart_item.variations.price * cart_item.quantity)
            quantity += cart_item.quantity

            try:
                variant = cart_item.variations
                if variant.stock_count <= 0:
                    print("Not enough stock!")
            except ObjectDoesNotExist:
                pass

        tax = (2 * total) / 100
        grand_total = total + tax  

    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'addresses':addresses,
        'tax': tax,
        'grand_total': grand_total,
        'coupons'  : coupons,
    }

    return render(request,'store/checkout.html',context)




from django.http import JsonResponse
def add_addresss(request):
    if request.method == 'POST':
        # Handle the form submission to add a new address
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address_line_1 = request.POST.get('address_line_1')
        address_line_2 = request.POST.get('address_line_2')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
        country = request.POST.get('country')

        if not is_not_empty_or_whitespace(first_name) or not re.match("^[a-zA-Z]+$", first_name):
            return JsonResponse({'error': 'Invalid or empty first name. Use only letters.'})
        elif not is_not_empty_or_whitespace(last_name) or not re.match("^[a-zA-Z]+$", last_name):
            return JsonResponse({'error': 'Invalid or empty last name. Use only letters.'})
        elif not is_not_empty_or_whitespace(email) or not re.match("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
            return JsonResponse({'error': 'Invalid or empty email address.'})
        elif not is_not_empty_or_whitespace(phone) or not is_valid_phone(phone):
            return JsonResponse({'error': 'Invalid or empty phone number. It should be exactly 10 digits.'})
        elif not is_not_empty_or_whitespace(address_line_1):
            return JsonResponse({'error': 'Address line 1 cannot be empty.'})
        elif not is_not_empty_or_whitespace(city):
            return JsonResponse({'error': 'City cannot be empty.'})
        elif not is_not_empty_or_whitespace(state):
            return JsonResponse({'error': 'State cannot be empty.'})
        elif not is_valid_postal_code(postal_code):
            return JsonResponse({'error': 'Invalid postal code.'})
        elif not is_not_empty_or_whitespace(country):
            return JsonResponse({'error': 'Country cannot be empty.'})
        else:
            address = Address(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                address_line_1=address_line_1,
                address_line_2=address_line_2,
                city=city,
                state=state,
                postal_code=postal_code,
                country=country,
                user=request.user
            )
            address.save()
            return JsonResponse({'success': 'Address added successfully.','redirect_url': reverse('store:checkout')}) 
            
    return JsonResponse({'error': 'Invalid request method.'})



def place_order(request, total=0, quantity=0):
    current_user = request.user
    
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store:home')
    
    final_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.variations.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total) / 100

    coupon_discount = request.session.get('coupon_discount', 0)
    final_total = (total + tax)-coupon_discount

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            
            
            data = form.save(commit=False)
            data.user = current_user
            data.discount=coupon_discount
            data.order_total = final_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            
        
            selected_address_id = request.session.get('selected_address_id')
            
            if selected_address_id is not None:
                selected_address = Address.objects.get(pk=selected_address_id)
                data.selected_address = selected_address
                del request.session['selected_address_id']
            else:
                selected_address_id = request.POST.get('selected_address')
                if selected_address_id is None:
                    messages.error(request,'choose an address or add address')  
                    return redirect('store:checkout')
                else:

                 selected_address = Address.objects.get(pk=selected_address_id)
                
                 data.selected_address = selected_address

            
            data.save()
            
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            #Remove the coupon_discount from the session
            if 'coupon_discount' in request.session:
                
                cp=request.session.get('coupon_code')
                ns=Coupon.objects.get(code=cp)

                reddemcoupon= RedeemedCoupon(
                    coupon=ns,
                    user=request.user,
                    redeemed_date=current_date,
                    is_redeemed=False,
                )  
                 
                reddemcoupon.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            selected_address = order.selected_address
            context = {
                'order' : order,
                'cart_items' : cart_items,
                'total' : total,
                'tax' : tax,
                'final_total' : final_total,
                'selected_address': selected_address,
            }
            return render(request, 'store/payment.html', context)
        else:
            return redirect('store:checkout')
        
from datetime import date

def apply_coupon(request):
   
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
        grand_total_str = request.POST.get('grand_total', '0')  
        grand_total = float(grand_total_str)

        try:
            coupon = Coupon.objects.get(code=coupon_code)
            min=coupon.minimum_purchase_value
            max=coupon.maximum_purchase_value
            minimum=float(min)
            maximum=float(max)
           
             
           
        except Coupon.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Coupon not found'})

        if not coupon.is_active:
            return JsonResponse({'status': 'error', 'message': 'Coupon is not active'})
        if grand_total < minimum or grand_total > maximum:
                print(f'grand_total: {grand_total}, minimum: {minimum}, maximum: {maximum}')  # Print values for debugging
                return JsonResponse({'status': 'error', 'message': 'Not in between price range'})
 

        if coupon.expiration_date < date.today():
            return JsonResponse({'status': 'error', 'message': 'Coupon has expired'})
        

       
        coupon_discount = (coupon.discount / 100) * grand_total
        final_total = grand_total - int(coupon_discount)

        # Store the coupon_discount in the session
        request.session['coupon_discount'] = int(coupon_discount)
        request.session['coupon_code'] = coupon_code

        response_data = {
            'status': 'success',
            'coupon_discount': coupon_discount,
            'final_total': final_total,
        }
        return JsonResponse(response_data)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

@require_POST
@csrf_exempt
def remove_coupon(request):
    if 'coupon_discount' in request.session:
        # Remove coupon data from the session
        del request.session['coupon_discount']
        del request.session['coupon_code']
        grand_total = float(request.POST.get('grand_total', '0'))
        response_data = {
            'status': 'success',
            'coupon_discount': 0,
            'final_total':  grand_total, 
        }
        return JsonResponse(response_data)
    else:
        return JsonResponse({'status': 'error', 'message': 'No coupon applied'})

def paytment(request):
   if request.method == 'POST':
        print(request.POST)
        action = request.POST.get('action')
        selected_address_id = request.POST.get('selected_address')
        grand_total = request.POST.get('grand_total')
        print(grand_total)
        order_number = request.POST.get('order_number')
        print(order_number)  
        
        try:
            order = Order.objects.get(order_number=order_number, is_ordered=False)
        except Order.DoesNotExist:
            
            return HttpResponse("Order not found")

        if action == "Cash on Delivery":
            print('action is done')
            payment = Payment.objects.create(
                user=request.user,
                payment_method="Cash on Delivery",  
                amount_paid=grand_total,  
                status="Pending",  
            )

            
            order.payment = payment
            order.save()
            
            

            cp=request.session.get('coupon_code')
            if cp is not None:
             ns=Coupon.objects.get(code=cp)
             reddemcoupon= RedeemedCoupon.objects.filter(user=request.user,coupon=ns,is_redeemed=False)
             reddemcoupon.is_redeemed=True
             reddemcoupon.update(is_redeemed=True)
             del request.session['coupon_code']
            
             
             

            
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
            
      # Access the related varients instance
     # Update the stock for the varients
        
            for item in cart_items:
                orderproduct = OrderProduct()
                item.variations.stock_count-=item.quantity
                item.variations.save()
                orderproduct.order = order
                orderproduct.payment = payment
                orderproduct.user = request.user
                orderproduct.product = item.product
                orderproduct.quantity = item.quantity
                orderproduct.product_price = item.variations.price
                orderproduct.ordered = True
                orderproduct.color = item.variations.color
                orderproduct.save()


                    # Update the product's quantity or perform any other necessary updates
            cart_items.delete()
            
            
            return redirect("store:order_success", id=order.id) 
        else:
            return render(request, 'store/payment.html')
        
     
def order_success(request, id):
     try:
        order = get_object_or_404(Order, id=id)
        order_products = OrderProduct.objects.filter(order=order)
        
        order.status = 'New'
        #order.payment.status = "Completed"
        order.is_ordered=True
        order.save()
        
        print(f"Order {order.order_number} status updated to 'Completed'")
     except Exception as e:
        # Log any exceptions that occur during the update
        print(f"Error updating order status: {str(e)}")
     context = {
        'order': order,
        'order_products': order_products,
     }
     return render(request, 'store/order_sucess.html', context)


################################################################################################profile page##############################

@login_required(login_url='accounts:login')
def profile(request):
    user = request.user
    context = {
        'user': user
    }
    return render(request, 'store/profile.html', context)


@login_required(login_url='accounts:login')
def user_orders(request,):
    orders = Order.objects.filter(is_ordered=True, user=request.user).order_by('-created_at')
    print(orders)
   
    context = {
        'orders': orders,
       

    }
    return render(request, 'store/my_orders.html', context)



@login_required(login_url='base:login')
def cancel_order_product(request, order_id):
    print(order_id)
    order = get_object_or_404(Order, id=order_id)
    
    if order.status != 'Cancelled':
        order.status = 'Cancelled'
        order.save()
        print("CHECK")
        order_products = OrderProduct.objects.filter(order=order)
        for order_product in order_products:
            products = order_product.product.pid
            product=Product.objects.get(pid=products)
            print(product)

            
            product_variants = ProductVariant.objects.filter(product=product)
                        
            for variant in product_variants:
             variant.stock_count += order_product.quantity
             variant.save()
            
    return redirect('store:user_dashboard') 

def return_order(request, order_id):
    order = Order.objects.get(id=order_id)
    order_method=order.payment.payment_method
    if  order_method!='Cash on Delivery'and order.status == 'Completed':
        user_profile = request.user
        wallets,create = wallet.objects.get_or_create(user=user_profile)

        
        wallets.wallet_amount += order.order_total
        wallets.wallet_amount = round(wallets.wallet_amount, 2)
        wallets.save()
       
      
        order.status = 'Rejected'
        order.save()
        order_products = OrderProduct.objects.filter(order=order)
        for order_product in order_products:
            products = order_product.product.pid
            product=Product.objects.get(pid=products)
            print(product)

            
            product_variants = ProductVariant.objects.filter(product=product)
                        
            for variant in product_variants:
             variant.stock_count += order_product.quantity
             variant.save()
        messages.warning(request, 'return request has been send. amount sucessfully returned to your wallet')

    elif order_method=='Cash on Delivery' and order.status == 'Completed':
        order.status = 'Rejected'
        order.save()
        messages.warning(request, 'return request has been send.')

    elif order_method=='Cash on Delivery' and order.status != 'Completed' :
        order.status = 'Cancelled'
        order.save()
        messages.warning(request, 'return request has been send.')
    else:
        user_profile = request.user
        wallets,create = wallet.objects.get_or_create(user=user_profile)

        # Credit the purchased amount back to the wallet
        wallets.wallet_amount += order.order_total
        wallets.wallet_amount = round(wallets.wallet_amount, 2)
        wallets.save()
       
        # Update the order status to 'Returned'
        order.status = 'Cancelled'
        order.save()
        order_products = OrderProduct.objects.filter(order=order)
        for order_product in order_products:
            products = order_product.product.pid
            product=Product.objects.get(pid=products)
            print(product)

            
            product_variants = ProductVariant.objects.filter(product=product)
                        
            for variant in product_variants:
             variant.stock_count += order_product.quantity
             variant.save()
        messages.warning(request, 'cancel request has been send. amount sucessfully returned to your wallet')
    return redirect('store:user_dashboard') 
            
       
        

@login_required(login_url='accounts:login')
def order_details(request, order_id):
    order_products = OrderProduct.objects.filter(order__user=request.user, order__id=order_id)
    orders = Order.objects.filter(is_ordered=True, id=order_id)
    
    payments = Payment.objects.filter(order__id=order_id,user=request.user)

    for order_product in order_products:
        order_product.total = order_product.quantity * order_product.product_price

    context = {
        'order_products': order_products,
        'orders': orders,
        'payments': payments,
    }

    return render(request,'store/order_detail.html',context)
     
import re
@login_required(login_url='accounts:login')
def edit_profile(request):
    #user = request.user  # Get the currently logged-in user
    user = Account.objects.get(pk=request.user.pk)
    print("User ID:", user.id)
   
    context={
            'user':user
        }

        
    if request.method == 'POST':
        first_name=request.POST.get('first_name')
        last_name=request.POST.get('last_name')
        username=request.POST.get('user_name')


        username_pattern = "^[a-zA-Z0-9_]+$"
        name_pattern = "^[a-zA-Z]+$"

        if not username or not re.match(username_pattern, username):
            messages.error(request, 'Invalid or empty username. Use only letters, numbers, and underscores.')
        elif not first_name or not re.match(name_pattern, first_name):
            messages.error(request, 'Invalid or empty first name. Use only letters.')
        elif not last_name or not re.match(name_pattern, last_name):
            messages.error(request, 'Invalid or empty last name. Use only letters.')
        else:
         user.first_name=first_name
         user.last_name=last_name
         user.username=username
         user.save()
         return redirect('store:profile')
        
    return render(request, 'store/edit_profile.html',context)
@login_required(login_url='accounts:login')
def user_addres(request):
    addresses = Address.objects.filter(user=request.user,is_active=True)
    context = {
        'addresses': addresses
    }
    return render(request, 'store/user_address.html', context)


@login_required(login_url='accounts:login')
def add_address(request):
    if request.method == 'POST':
        # Handle the form submission to add a new address
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address_line_1 = request.POST.get('address_line_1')
        address_line_2 = request.POST.get('address_line_2')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
        country = request.POST.get('country')
        print(first_name, postal_code)

        if not is_not_empty_or_whitespace(first_name) or not re.match("^[a-zA-Z]+$", first_name):
            messages.error(request, 'Invalid or empty first name. Use only letters.')
        elif not is_not_empty_or_whitespace(last_name) or not re.match("^[a-zA-Z]+$", last_name):
            messages.error(request, 'Invalid or empty last name. Use only letters.')
        elif not is_not_empty_or_whitespace(email) or not re.match("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
            messages.error(request, 'Invalid or empty email address.')
        elif not is_not_empty_or_whitespace(phone) or not is_valid_phone(phone):
            messages.error(request, 'Invalid or empty phone number. It should be exactly 10 digits.')
        elif not is_not_empty_or_whitespace(address_line_1):
            messages.error(request, 'Address line 1 cannot be empty.')
        elif not is_not_empty_or_whitespace(city):
            messages.error(request, 'City cannot be empty.')
        elif not is_not_empty_or_whitespace(state):
            messages.error(request, 'State cannot be empty.')
        elif not is_valid_postal_code(postal_code):
            messages.error(request, 'Invalid postal code.')
        elif not is_not_empty_or_whitespace(country):
            messages.error(request, 'Country cannot be empty.')
        else:
            address = Address(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                address_line_1=address_line_1,
                address_line_2=address_line_2,
                city=city,
                state=state,
                postal_code=postal_code,
                country=country,
                user=request.user
            )
            address.save()
            messages.success(request, 'Address added successfully.')
            # Redirect to the manage addresses page after adding the new address
            return redirect('store:user_address')

    # Add this return statement for the else block
    return render(request, 'store/add_address.html')

from django.http import JsonResponse
def add_addresss(request):
    if request.method == 'POST':
        # Handle the form submission to add a new address
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address_line_1 = request.POST.get('address_line_1')
        address_line_2 = request.POST.get('address_line_2')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
        country = request.POST.get('country')

        if not is_not_empty_or_whitespace(first_name) or not re.match("^[a-zA-Z]+$", first_name):
            return JsonResponse({'error': 'Invalid or empty first name. Use only letters.'})
        elif not is_not_empty_or_whitespace(last_name) or not re.match("^[a-zA-Z]+$", last_name):
            return JsonResponse({'error': 'Invalid or empty last name. Use only letters.'})
        elif not is_not_empty_or_whitespace(email) or not re.match("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
            return JsonResponse({'error': 'Invalid or empty email address.'})
        elif not is_not_empty_or_whitespace(phone) or not is_valid_phone(phone):
            return JsonResponse({'error': 'Invalid or empty phone number. It should be exactly 10 digits.'})
        elif not is_not_empty_or_whitespace(address_line_1):
            return JsonResponse({'error': 'Address line 1 cannot be empty.'})
        elif not is_not_empty_or_whitespace(city):
            return JsonResponse({'error': 'City cannot be empty.'})
        elif not is_not_empty_or_whitespace(state):
            return JsonResponse({'error': 'State cannot be empty.'})
        elif not is_valid_postal_code(postal_code):
            return JsonResponse({'error': 'Invalid postal code.'})
        elif not is_not_empty_or_whitespace(country):
            return JsonResponse({'error': 'Country cannot be empty.'})
        else:
            address = Address(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                address_line_1=address_line_1,
                address_line_2=address_line_2,
                city=city,
                state=state,
                postal_code=postal_code,
                country=country,
                user=request.user
            )
            address.save()
            return JsonResponse({'success': 'Address added successfully.','redirect_url': reverse('store:checkout')}) 
            

    return JsonResponse({'error': 'Invalid request method.'})




@login_required(login_url='base:login')
def edit_address(request,id):
    try:
        address = Address.objects.get(pk=id)
    except Address.DoesNotExist:
        messages.error(request, 'Address not found.')
        return redirect('user:user_address')

    if request.method == 'POST':
        # Handle the form submission to edit the address
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address_line_1 = request.POST.get('address_line_1')
        address_line_2 = request.POST.get('address_line_2')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
        country = request.POST.get('country')

        # Perform validation on the fields
        if not is_not_empty_or_whitespace(first_name) or not re.match("^[a-zA-Z]+$", first_name):
            messages.error(request, 'Invalid or empty first name. Use only letters.')
        elif not is_not_empty_or_whitespace(last_name) or not re.match("^[a-zA-Z]+$", last_name):
            messages.error(request, 'Invalid or empty last name. Use only letters.')
        elif not is_not_empty_or_whitespace(email) or not re.match("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
            messages.error(request, 'Invalid or empty email address.')
        elif not is_not_empty_or_whitespace(phone) or not is_valid_phone(phone):
            messages.error(request, 'Invalid or empty phone number. It should be exactly 10 digits.')
        elif not is_not_empty_or_whitespace(address_line_1):
            messages.error(request, 'Address line 1 cannot be empty.')
        elif not is_not_empty_or_whitespace(city):
            messages.error(request, 'City cannot be empty.')
        elif not is_not_empty_or_whitespace(state):
            messages.error(request, 'State cannot be empty.')
        elif not is_valid_postal_code(postal_code):
            messages.error(request, 'Invalid postal code.')
        elif not is_not_empty_or_whitespace(country):
            messages.error(request, 'Country cannot be empty.')
        else:
            # All fields are valid, update the address
            address.first_name = first_name
            address.last_name = last_name
            address.email = email
            address.phone = phone
            address.address_line_1 = address_line_1
            address.address_line_2 = address_line_2
            address.city = city
            address.state = state
            address.postal_code = postal_code
            address.country = country

            address.save()
            messages.success(request, 'Address updated successfully.')
            return redirect('store:user_address')

    context = {'address': address}
    return render(request, 'store/edit_address.html', context)

@login_required(login_url='accounts:login')
def delete_address(request, id):
    try:
        address = Address.objects.get(id=id)
        address.isactive=False
        address.save()
       
    except Address.DoesNotExist:
     
        pass
    return redirect('store:user_address')


@login_required(login_url='accounts:login')
def change_password(request):
    if request.method=='POST':
        old_password=request.POST.get('old_password')
        new_password1=request.POST.get('new_password1')
        new_password2=request.POST.get('new_password2')
        user=request.user
        password_pattern = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
        if not user.check_password(old_password):
            messages.error(request,'Old password is incorect')


            
        elif new_password1!=new_password2 :
           messages.error(request,'newpassword desnot match ')
        elif not new_password1 or not re.match(password_pattern,new_password1):
             messages.error(request, 'Invalid or weak password. It should have at least 8 characters, including at least one uppercase letter, one lowercase letter, one digit, and one special character.')
        else:
            user.set_password(new_password1)
            user.save()
            auth.update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully.')
            return redirect('store:profile')  
    return render(request,'store/change_password.html')  

###################################################################################################

@login_required(login_url='accounts:login')
def add_wishList(request,pid):
    product = get_object_or_404(Product, pid=pid)
    print(product)

    try:
        vs = WishList.objects.get(user=request.user, product=product)
    except WishList.DoesNotExist:
        vs = None

    if vs is not None:
        messages.error(request, 'Product Already in wishlist')
    else:
        wishlist = WishList.objects.create(user=request.user, product=product)
        messages.success(request, 'Added Product to wishlist')
        
    return redirect('store:home')

@login_required(login_url='accounts:login')
def wishlist(request):
    wishlist=WishList.objects.filter(user=request.user)
    print(wishlist)
    context={
        'wishlist':wishlist
    }
    return render(request,'store/wishlist.html',context)


@login_required(login_url='accounts:login')
def remove_from_wishlist(request, pid):
    print(pid,'hai')
    if request.method == 'POST' or request.method == 'DELETE':
        product = get_object_or_404(Product, pid=pid)
        wishlist_item = get_object_or_404(WishList, user=request.user, product=product)

        # Assuming you have a method to remove the item from the wishlist
        wishlist_item.delete()

        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

########################################################################################

# def wallet_details(request):
    
#     try:
#        wallets=wallet.objects.get(user=request.user)
#     except wallet.DoesNotExist:
#         wallets=wallet.objects.create(user=request.user, wallet_amount=0)
#     wallet_amount=round(wallets.wallet_amount, 2)
#     user=request.user

#     context={
#         'wallet_amount':wallet_amount,
#         'user':user,
        
#     } 
#     return render(request,'store/wallet.html',context)
    

from .models import wallet  # Import models as needed
from django.contrib.auth.decorators import login_required
from django.db.models import Case, When, Value, CharField

@login_required
def wallet_details(request):
    try:
        wallet_instance = wallet.objects.get(user=request.user)
    except wallet.DoesNotExist:
        wallet_instance = wallet.objects.create(user=request.user, wallet_amount=0)

    wallet_amount = round(wallet_instance.wallet_amount, 2)
    user = request.user

    # Fetch 'Debit' transactions related to wallet payments
    wallet_transactions = user.payment_set.filter(
        payment_method="Wallet Payment",  # Filter by wallet payments
        status="Paid",                    # Filter only paid transactions
        amount_paid__lt=0                 # Assuming 'Debit' amounts are negative
    ).order_by('-created_at')            # Sort by date, descending order

    # Fetch related products for each 'Debit' transaction
    for transaction in wallet_transactions:
        transaction.products_purchased = OrderProduct.objects.filter(
            payment=transaction, user=request.user
        ).values_list('product__name', flat=True)

    context = {
        'wallet_amount': wallet_amount,
        'user': user,
        'wallet_transactions': wallet_transactions,
    }

    return render(request, 'store/wallet.html', context)




def pay_wallet_details(request, order_number, order_total):
    grand_total = order_total
    order_number = order_number

    if request.method == 'POST':
        action = request.POST.get('action')
        grand_total = request.POST.get('grand_total')
        order_number = request.POST.get('order_number')
        print(order_number)

        try:
            wallets = wallet.objects.get(user=request.user)
        except wallet.DoesNotExist:
            wallets = wallet.objects.create(user=request.user, wallet_amount=0)
            wallets.save()

        if wallets.wallet_amount <= float(grand_total):
            print("error")
            messages.error(request, "Wallet out of balance")
            print("tgtfvfvbbh")
            try:
                order = Order.objects.get(order_number=order_number, is_ordered=False)
            except Order.DoesNotExist:
                return HttpResponse("Order not found")

            cart_items = CartItem.objects.filter(user=request.user)
            selected_address_id = request.session.get('selected_address_id')

            if selected_address_id is not None:
                selected_address = Address.objects.get(pk=selected_address_id)
                del request.session['selected_address_id']
            else:
                selected_address_id = request.POST.get('selected_address')
                if selected_address_id is None:
                    messages.error(request, 'Choose an address or add address')
                    return redirect('store:checkout')
                else:
                    selected_address = Address.objects.get(pk=selected_address_id)
                    coupon_discount = request.session.get('coupon_discount', 0)
                    final_total = 0
                    quantity = 0
                    total = 0
                    tax = 0
                    for cart_item in cart_items:
                        total += (cart_item.product.price * cart_item.quantity)
                        quantity += cart_item.quantity
                    tax = (2 * total) / 100
                
                    print(coupon_discount,'fg')
                    final_total = (total + tax) - coupon_discount
                    context = {
                        'order': order,
                        'cart_items': cart_items,
                        'total': total,
                        'tax': tax,
                        'coupon_discount':coupon_discount,
                        'final_total': final_total,
                        'selected_address': selected_address,
                    }
                    return render(request, 'store/payment.html', context)

        else:
                
                print('action is done')
                try:
                    order = Order.objects.get(order_number=order_number, is_ordered=False)
                except Order.DoesNotExist:
                    return HttpResponse("Order not found")

                print('action is done')
                payment = Payment.objects.create(
                    user=request.user,
                    payment_method="Wallet Payment",
                    amount_paid=grand_total,
                    status="Paid",)

                order.payment = payment
                order.save()
                
                
                cp = request.session.get('coupon_code')
                if cp is not None:
                    ns = Coupon.objects.get(code=cp)
                    reddemcoupon = RedeemedCoupon.objects.filter(user=request.user, coupon=ns, is_redeemed=False)
                    reddemcoupon.is_redeemed = True
                    reddemcoupon.update(is_redeemed=True)
                    del request.session['coupon_code']
                    
                   

                cart_items = CartItem.objects.filter(user=request.user, is_active=True)

                # Access the related variants instance
                # Update the stock for the variants
                for item in cart_items:
                    orderproduct = OrderProduct()
                    item.variations.stock_count -= item.quantity
                    item.variations.save()
                    orderproduct.order = order
                    orderproduct.payment = payment
                    orderproduct.user = request.user
                    orderproduct.product = item.product
                    orderproduct.quantity = item.quantity
                    orderproduct.product_price = item.variations.price
                    orderproduct.ordered = True
                    orderproduct.color = item.variations.color
                    orderproduct.save()

                # Update the product's quantity or perform any other necessary updates
                cart_items.delete()    
                wallets.wallet_amount -= float(grand_total)
                wallets.save()
                return redirect("store:order_success", id=order.id)