from django.db import models
from customers.models import Customer
from inventory.models import Product

# รายการสินค้าที่ขาย
class SaleItem(models.Model):
    sale = models.ForeignKey('Sale', on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sold_items')
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    @property
    def total_price(self):
        return self.quantity * self.price

    def save(self, *args, **kwargs):
        # ดึงราคาจาก Product อัตโนมัติ
        self.price = self.product.selling_price

        # ดึงข้อมูลเก่าเพื่อคำนวณความแตกต่างในจำนวนที่เปลี่ยนแปลง
        old_quantity = 0
        if self.pk:
            old_item = SaleItem.objects.get(pk=self.pk)
            old_quantity = old_item.quantity

        super(SaleItem, self).save(*args, **kwargs)

        # อัปเดตสต็อกใน Stock ที่เกี่ยวข้องกับ Product
        stock = self.product.stocks.first()
        if stock:
            quantity_difference = self.quantity - old_quantity
            stock.current_stock -= quantity_difference
            stock.save()

        # อัปเดตยอดรวมใน Sale
        self.sale.calculate_total_amount()
        self.sale.save()

    def delete(self, *args, **kwargs):
        # ค้นหา Stock ที่เกี่ยวข้องกับ Product และคืนจำนวนสินค้า

        super(SaleItem, self).delete(*args, **kwargs)

        # อัปเดตยอดรวมใน Sale หลังจากลบ SaleItem
        self.sale.calculate_total_amount()
        self.sale.save()

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Sale ID: {self.sale.id})"


# การขาย
class Sale(models.Model):
    PAYMENT_CHOICES = [
        ('PAID', 'Paid'),
        ('UNPAID', 'Unpaid'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, related_name='sales')
    sale_date = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)
    payment = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='UNPAID')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_total_amount(self):
        # คำนวณยอดรวมจาก SaleItem ทั้งหมดที่เชื่อมโยงกับการขายนี้
        total = sum(item.total_price for item in self.items.all())
        self.total_amount = total
        return total

    def save(self, *args, **kwargs):
        # เรียก super().save() เพื่อสร้าง Primary Key ให้กับ Sale ก่อน
        super(Sale, self).save(*args, **kwargs)
        # หลังจากสร้าง Primary Key แล้ว ให้คำนวณและบันทึกยอดรวมใหม่
        self.calculate_total_amount()
        super(Sale, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # คืนจำนวนสินค้าในสต็อกก่อนที่จะลบการขาย
        for item in self.items.all(): item.delete()

        # ลบการขายหลังจากคืนสต็อกแล้ว
        super(Sale, self).delete(*args, **kwargs)

    def __str__(self):
        return f"Sale ID: {self.id} to {self.customer.name if self.customer else 'Unknown Customer'}"
