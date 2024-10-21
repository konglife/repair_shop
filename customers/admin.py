from django.contrib import admin
from .models import Customer, RepairHistory
from django.utils.html import format_html

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone', 'created_at', 'profile_thumbnail')  # ฟิลด์ที่จะแสดงในหน้า List
    search_fields = ('name', 'email', 'phone')  # เพิ่มฟังก์ชันการค้นหาตามชื่อ อีเมล และเบอร์โทรศัพท์
    list_filter = ('created_at',)  # เพิ่มตัวกรองตามวันที่สร้าง
    ordering = ('-created_at',)  # เรียงตามวันที่สร้างใหม่ล่าสุดก่อน
    fields = ('name', 'profile_image', 'phone', 'email', 'address')  # ฟิลด์ที่จะแสดงเมื่อเพิ่มหรือแก้ไขข้อมูลลูกค้า
    def profile_thumbnail(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" width="50" height="50" />', obj.profile_image.url)
        return "-"
    profile_thumbnail.short_description = 'Profile Image'

class RepairHistoryAdmin(admin.ModelAdmin):
    list_display = ('customer', 'description', 'date', 'cost')
    search_fields = ('customer__name', 'description')
    list_filter = ('date',)
    ordering = ('-date',)

admin.site.register(Customer, CustomerAdmin)
admin.site.register(RepairHistory, RepairHistoryAdmin)