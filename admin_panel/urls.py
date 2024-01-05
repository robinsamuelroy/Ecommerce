from django.contrib import admin
from django.urls import include, path
from .import views


app_name='admin_panel'
urlpatterns = [
  
    path('dashboard/', views.dashboard, name='dashboard'),
    path('chart/',views.charts,name='charts'),
    path('reports/',views.reports,name='reports'),
    path('sales-report/', views.sales_report, name='sales_report'),
    path('filtered_sales/', views.filtered_sales, name='filtered_sales'),

    path('add_banner/', views.add_banners, name='add_banner'),
    path('display/',views.display,name='display'),
    path('delete_banner/<int:banner_id>',views.delete_banner,name='delete_banner'),

    path('admin_products_list',views.admin_products_list,name='admin_products_list'),
    path('admin_products_details/<str:pid>/',views.admin_products_details,name='admin_products_details'),

    path('block_unblock_products/<str:pid>/',views.block_unblock_products,name='block_unblock_products'),
    path('admin_add_product/',views.add_product,name='admin_add_product'),
    path('admin_delete_product/<str:pid>',views.delete_product,name='admin_delete_product'),


    path('admin_category_list',views.admin_category_list,name='admin_category_list'),
    path('admin_add_category',views.admin_add_category,name='admin_add_category'),
    path('admin_category_edit/<str:cid>/',views.admin_category_edit,name='admin_category_edit'),
    
    path('admin_delete_category/<str:cid>/',views.delete_category,name='admin_delete_category'),
    path('block_unblock_category/<str:cid>/',views.available_category,name='block_unblock_category'),

    path('add-variant',views.add_variant,name='add-variant'),
    path('variant-list',views.variant_list,name='variant-list'),
    path('edit-variant/<str:id>',views.edit_variant,name='edit-variant'),
    path('delete-variant/<str:id>/', views.delete_variant, name='delete-variant'),

    path('brand', views.brand,name="brand"),
    path('edit-brand/<int:id>/', views.edit_brand,name="edit-brand"),
    path('del-brand/<int:id>/', views.del_brand,name="del-brand"),
    path('add-brand', views.add_brand,name="add-brand"),

    path('color', views.color,name="color"),
    path('edit_color/<int:id>/', views.edit_color,name="edit_color"),
    path('del_color/<int:id>/', views.del_color,name="del_color"),
    path('add_color', views.add_color,name="add_color"),

    path('order_list',views.order_list,name='order_list'),
    path('ordered_product_details/<int:order_id>', views.ordered_product_details, name='ordered_product_details'),
    path('update_order_status/<str:order_id>/', views.update_order_status, name='update_order_status'),

    path('add_coupon',views.add_coupon,name='add_coupon'),
    path('list_coupons',views.list_coupons,name='list_coupons'),
    path('edit_coupon/<int:id>/', views.edit_coupon, name="edit_coupon"),
    path('delete_coupon/<int:id>/', views.delete_coupon, name="delete_coupon"),

]