from django.shortcuts import render, redirect
from .forms import UserRegisterForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
import random
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.views.decorators.cache import never_cache
from django.views.decorators.cache import cache_control
from django.http import HttpResponseRedirect,HttpResponseBadRequest
from django.urls import reverse
from accounts.models import Account  # Import your custom user model

@never_cache
def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            # user = form.save()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password=form.cleaned_data.get('password1')
            request.session["username"]=username
            request.session["password"]=password
            request.session["email"]=email
            messages.success(request, f'Hey {username}, Your account was created succesfully')
            email=request.POST["email"]
            send_otp(request)
            return render(request,'accounts/otp.html',{"email":email})
            
           
    else:
        form = UserRegisterForm()

    context = {'form': form}
    return render(request, 'accounts/signup.html', context)

#OTP
@never_cache
def send_otp(request):
    s=""
    for x in range(0,4):
        s+=str(random.randint(0,9))
    request.session["otp"]=s
    send_mail("otp for sign up",s,'djangoalerts0011@gmail.com',[request.session['email']],fail_silently=False)
    return render(request,"accounts/otp.html")

@never_cache
def  otp_verification(request):
    if  request.method=='POST':
       
        otp_=request.POST.get("otp")
    if otp_ == request.session["otp"]:
        encryptedpassword=make_password(request.session['password'])
        nameuser=Account(username=request.session['username'],email=request.session['email'],password=encryptedpassword)
        nameuser.save()
        messages.info(request,'signed in successfully...')
        Account.is_active=True
       
        return redirect('store:home')
    else:
        messages.error(request,"otp doesn't match")
        return render(request,'accounts/otp.html')
    

@never_cache
def login_view(request):
  
    if request.user.is_authenticated:
      messages.warning(request,f"Hey You are already logged in")
      return redirect("store:home")
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        request.session["email"]=email
        print(email,password)
        if not Account.objects.filter(email=email).exists():
            messages.error(request, "Invalid Email Adress")
            return redirect('accounts:login')
        
        if not Account.objects.filter(email=email,is_active=True).exists():
            messages.error(request, "Account blocked ! ! !")
            return redirect('accounts:login') 
        try:
          user = Account.objects.get(email=email)
          user = authenticate(email=email, password=password)
        

          if user is not None:
              login(request, user)
           
              messages.success(request, 'Login successful.')
              return redirect("store:home")  # Redirect to the desired page after successful login
          else:
              messages.warning(request, 'Username or Password is incorrect.')

        except:
          messages.warning(request, f'User with {email} doesnot exists')
          
        
    context = {}
    return render(request, 'accounts/login.html', context)
    
@never_cache
def logoutUser(request):
    logout(request)
    request.session.flush()  # Clear all session data
    messages.success(request, 'You logged out')
    return redirect('store:home')

############################################################################


from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
import random
from django.core.mail import send_mail

# Existing code...

@never_cache
def forgot_password(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            associated_users = Account.objects.filter(email=email)
            if associated_users.exists():
                for user in associated_users:
                    otp = ''.join([str(random.randint(0, 9)) for _ in range(4)])  # Generate OTP
                    request.session['reset_email'] = email
                    request.session['reset_otp'] = otp
                    send_mail(
                        "Reset Password OTP",
                        f"Your OTP for resetting the password: {otp}",
                        'djangoalerts0011@gmail.com',
                        [email],
                        fail_silently=False
                    )
                    return redirect('accounts:verify_otp')
                messages.success(request, 'Password reset OTP sent. Please check your email.')
            else:
                messages.error(request, 'No user is associated with this email.')
            return redirect('accounts:reset_password')
    else:
        form = PasswordResetForm()
    return render(request, 'accounts/reset_password.html', {'form': form})

@never_cache
def verify_otp(request):
    if request.method == 'POST':
        otp_entered = request.POST.get("otp")
        if otp_entered == request.session["reset_otp"]:
            return redirect('accounts:reset_password_confirm')
        else:
            messages.error(request, "Invalid OTP entered. Please try again.")
    return render(request, 'accounts/verify_otp.html')

@never_cache
def reset_password_confirm(request):
    if request.method == 'POST':
        new_password = request.POST.get("new_password")
        user = Account.objects.get(email=request.session['reset_email'])
        user.set_password(new_password)
        user.save()
        messages.success(request, 'Password reset successfully. You can now log in with your new password.')
        return redirect('accounts:login')
    return render(request, 'accounts/reset_password_confirm.html')
