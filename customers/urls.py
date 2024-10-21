from django.urls import path
from . import views

urlpatterns = [
    path('', views.customer_list, name='customer_list'),  # แสดงรายการลูกค้า
    path('<int:pk>/', views.customer_detail, name='customer_detail'),  # แสดงรายละเอียดลูกค้าแต่ละคน
    path('add/', views.add_customer, name='add_customer'),  # เพิ่มลูกค้าใหม่
    path('<int:pk>/edit/', views.edit_customer, name='edit_customer'),  # แก้ไขข้อมูลลูกค้า
    path('<int:pk>/delete/', views.delete_customer, name='delete_customer')  # ลบลูกค้า
]
