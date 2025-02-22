"""
URL configuration for store_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path
from store_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('owner_page/', views.owner_page, name='owner_page'),
    path('seller_page/', views.seller_page, name='seller_page'),
    path('user_page/', views.user_page, name='user_page'),
    path('products/', views.product_list, name='product_list'),  # Страница с продуктами
    path('products/upload/', views.upload_product, name='upload_product'),  # Загрузка продукта
   # Редактировать товары
    path('products/redact/', views.product_redact, name='product_redact'),
    path('products/get_colors/', views.get_colors, name='get_colors'),
    path('products/get_product/', views.get_product, name='get_product'),
    path('products/delete/', views.delete_product, name='delete_product'),
    path('debetors_list', views.debetors_list, name='debetors_list'),
    path('debetors/add/', views.add_debtor, name='add_debtor'),
    path('debetors/update/', views.update_debtor, name='update_debtor'),
    path('debetors/delete/', views.delete_debtor, name='delete_debtor'),
    path('orders/', views.orders_list, name='orders_list'),
    path('orders/create/', views.create_order, name='create_order'),
    path('orders/delete/', views.delete_order, name='delete_order'),
    path('orders/edit/<int:order_id>/', views.edit_order, name='edit_order'),
    path('orders/update_status/', views.update_order_status, name='update_order_status'),
    path('analiz/', views.analiz, name='analiz'),
    path('orders/details/<int:order_id>/', views.order_details, name='order_details'),
    path('products/all/', views.get_all_products, name='get_all_products'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
