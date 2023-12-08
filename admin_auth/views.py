from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from accounts.models import Account
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
# Create your views here.


def admin_login(request):
  if request.user.is_authenticated and request.user.is_superadmin:
    return redirect('admin_panel:dashboard')
  
  if request.method == 'POST':
    email = request.POST['email']
    password = request.POST['password']
    print(email,password)
    user = authenticate(request, email=email, password=password)
    print(user)
    if user:
      if user.is_superadmin:
        login(request,user)
        return redirect('admin_panel:dashboard')
  
      messages.error(request, "Invalid admin credentials!")
  return render(request, 'admin_panel/admin_login.html')

#####################################################################

def admin_logout(request):
    logout(request)

    return redirect('admin_auth:admin_login')


################################ujijiojoijiojopijiop######################

@login_required(login_url='admin_auth:admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def users_list(request):
    if not request.user.is_authenticated:
        return redirect('admin_auth:admin_login')
    
    search_query=request.GET.get('query')

    if search_query:
         users = Account.objects.filter(username__icontains=search_query)
    else:
         users = Account.objects.all().order_by('id')
         print("the users are :", users)
    context = {
        'users': users
    }
      
    return render(request,'admin_panel/users_list.html',context)
  
  
  
  
@login_required(login_url='admin_auth:admin_login')
def block_unblock_user(request,user_id):
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)
    
    user = get_object_or_404(Account, id=user_id)
    
    if user.is_active:
        
        user.is_active=False
        
    else:
        user.is_active=True
        
    user.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))