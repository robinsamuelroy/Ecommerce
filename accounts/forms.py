from django import forms
from django.contrib.auth.forms import UserCreationForm
from accounts.models import Account

class UserRegisterForm(UserCreationForm):
  first_name = forms.CharField(max_length=30,widget=forms.TextInput(attrs= {"placeholder":"First Name"}), required=True, help_text='Required. 30 characters or fewer.')
  last_name = forms.CharField(max_length=30,widget=forms.TextInput(attrs= {"placeholder":"Last Name"}), required=True, help_text='Required. 30 characters or fewer.')
  email = forms.EmailField(max_length=254,widget=forms.EmailInput(attrs= {"placeholder":"Email"}), required=True, help_text='Required. Enter a valid email address.')
  password1 = forms.CharField(max_length=30,widget=forms.PasswordInput(attrs= {"placeholder":"Password"}), required=True, help_text='Required. 30 characters or fewer.')
  password2 = forms.CharField(max_length=30,widget=forms.PasswordInput(attrs= {"placeholder":"Confirm Password"}), required=True, help_text='Required. 30 characters or fewer.')
  username = forms.CharField(max_length=30,widget=forms.TextInput(attrs= {"placeholder":"Username"}), required=True, help_text='Required. 30 characters or fewer.')

  class Meta:
    model = Account
    fields = ['username', 'first_name', 'last_name', 'email','password1','password2']

