from django.contrib import admin
from django.urls import include, path
from .import views


app_name='admin_panel'
urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin_products_list',views.admin_products_list,name='admin_products_list'),
    path('admin_products_details/<str:pid>/',views.admin_products_details,name='admin_products_details'),

    path('block_unblock_products/<str:pid>/',views.block_unblock_products,name='block_unblock_products'),
    path('admin_add_product/',views.add_product,name='admin_add_product'),
    path('admin_delete_product/<str:pid>',views.delete_product,name='admin_delete_product'),
    path('admin_category_list',views.admin_category_list,name='admin_category_list'),
    path('admin_add_category',views.admin_add_category,name='admin_add_category'),
    path('admin_category_edit/<str:cid>/',views.admin_category_edit,name='admin_category_edit'),
    
    path('admin_delete_category/<str:cid>/',views.delete_category,name='admin_delete_category'),
    path('block_unblock_category/<str:cid>/',views.available_category,name='block_unblock_category')
]