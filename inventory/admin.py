from django.contrib import admin
from .models import Supplier, Category, Product, ProductSupplier, Stock, Purchase, Unit
from .forms import PurchaseForm

# ซัพพลายเออร์
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'contact_info', 'url', 'created_at', 'updated_at')  # แสดงฟิลด์ในหน้า List
    search_fields = ('name', 'contact_info')  # เพิ่มการค้นหาตามชื่อและข้อมูลติดต่อ
    list_filter = ('created_at',)  # เพิ่มตัวกรองตามวันที่สร้าง
    ordering = ('-created_at',)  # เรียงลำดับตามวันที่สร้างใหม่ล่าสุดก่อน

# หมวดหมู่สินค้า
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

# หน่วยสินค้า
class UnitAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

# สินค้า
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'unit', 'selling_price', 'created_at')  # ลบ cost_price ออก
    search_fields = ('name', 'category__name', 'unit__name')  # เพิ่มการค้นหาตามชื่อสินค้า หมวดหมู่ และหน่วย
    list_filter = ('category', 'created_at')  # กรองตามหมวดหมู่และวันที่สร้าง
    ordering = ('-created_at',)  # เรียงลำดับตามวันที่สร้างใหม่ล่าสุดก่อน

# ความสัมพันธ์ระหว่างสินค้ากับซัพพลายเออร์
class ProductSupplierAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'supplier', 'price')  # แสดงฟิลด์ id, product, supplier, และ price
    search_fields = ('product__name', 'supplier__name')  # เพิ่มการค้นหาตามชื่อสินค้าและซัพพลายเออร์
    list_filter = ('supplier',)  # กรองตามซัพพลายเออร์

# สต็อกสินค้า
class StockAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'current_stock', 'min_stock', 'get_status', 'last_updated_at')
    search_fields = ('product__name',)
    list_filter = ('last_updated_at',)
    ordering = ('-last_updated_at',)
    readonly_fields = ('product', 'current_stock', 'last_updated_at')  # ลบ status ออกจาก readonly_fields

    def get_status(self, obj):
        return obj.get_status()  # เรียกใช้ฟังก์ชัน get_status() จาก Model
    get_status.short_description = 'Stock Status'

# การสั่งซื้อสินค้า
class PurchaseAdmin(admin.ModelAdmin):
    form = PurchaseForm
    list_display = ('id', 'product', 'quantity', 'price', 'supplier', 'purchase_date', 'status', 'payment', 'total_price')
    search_fields = ('product__name', 'supplier__name',)
    list_filter = ('status', 'payment', 'purchase_date')
    ordering = ('-purchase_date',)
    readonly_fields = ('total_price',)  # เพิ่ม readonly_fields ที่เกี่ยวข้องกับ Purchase

    # Override save_model เพื่อกำหนด price ก่อนบันทึกลงฐานข้อมูล
    def save_model(self, request, obj, form, change):
        if not obj.price:  # ตรวจสอบว่ามีการกำหนด price หรือยัง
            product_supplier = ProductSupplier.objects.filter(
                product=obj.product, supplier=obj.supplier
            ).first()

            if product_supplier:
                obj.price = product_supplier.price
            else:
                obj.price = 0  # ตั้งค่า default เป็น 0 ในกรณีที่ไม่พบ ProductSupplier ที่ตรงกัน

        super().save_model(request, obj, form, change)

# ลงทะเบียน Model กับ Django Admin
admin.site.register(Supplier, SupplierAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Unit, UnitAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductSupplier, ProductSupplierAdmin)
admin.site.register(Stock, StockAdmin)
admin.site.register(Purchase, PurchaseAdmin)
