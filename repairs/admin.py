from django.contrib import admin
from .models import RepairJob, UsedPart

# การตั้งค่าหน้า Admin สำหรับ RepairJob
class UsedPartInline(admin.TabularInline):
    model = UsedPart
    extra = 1
    readonly_fields = ('cost',)

class RepairJobAdmin(admin.ModelAdmin):
    list_display = ('id', 'job_name', 'customer', 'repair_date', 'labor_cost', 'parts_cost', 'total_cost', 'status', 'payment', 'updated_at')
    search_fields = ('customer__name', 'description', 'notes')
    list_filter = ('status', 'payment', 'repair_date', 'updated_at')
    ordering = ('-updated_at',)
    inlines = [UsedPartInline]
    readonly_fields = ('total_cost', 'parts_cost',)

    def save_model(self, request, obj, form, change):
        # คำนวณค่า total_cost ก่อนบันทึก
        obj.total_cost = obj.labor_cost + obj.parts_cost
        super().save_model(request, obj, form, change)

# การตั้งค่าหน้า Admin สำหรับ UsedPart
class UsedPartAdmin(admin.ModelAdmin):
    list_display = ('id', 'repair_job', 'product', 'quantity', 'price', 'cost')  # เปลี่ยนจาก repair_order เป็น repair_job
    search_fields = ('repair_job__job_name', 'product__name')  # เปลี่ยนจาก repair_order เป็น repair_job
    readonly_fields = ('cost',)

# ลงทะเบียนกับหน้า Admin
admin.site.register(RepairJob, RepairJobAdmin)
admin.site.register(UsedPart, UsedPartAdmin)

