from django.contrib import admin
from .models import Account

# Register your models here.
class AccountAdmin(admin.ModelAdmin):
  list_display = ['username', 'email',]
admin.site.register(Account,AccountAdmin)
