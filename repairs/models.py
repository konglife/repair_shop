from django.db import models
from customers.models import Customer
from inventory.models import Product

# งานซ่อมหลัก
class RepairJob(models.Model):
    STATUS_CHOICES = [
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
    ]
    PAYMENT_CHOICES = [
        ('PAID', 'Paid'),
        ('UNPAID', 'Unpaid'),
    ]

    job_name = models.CharField(max_length=255)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='repair_jobs')
    repair_date = models.DateTimeField()
    description = models.TextField()
    labor_cost = models.DecimalField(max_digits=10, decimal_places=2)
    parts_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='IN_PROGRESS')
    notes = models.TextField(blank=True, null=True)
    payment = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='UNPAID')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def update_parts_cost(self):
        # คำนวณค่าอะไหล่ทั้งหมดจาก UsedPart ที่เกี่ยวข้อง
        total_parts_cost = sum(part.cost for part in self.used_parts.all())
        self.parts_cost = total_parts_cost
        self.save()

    def save(self, *args, **kwargs):
        # ตรวจสอบสถานะก่อนหน้า
        old_status = None
        if self.pk:
            old_repair = RepairJob.objects.get(pk=self.pk)
            old_status = old_repair.status

        self.total_cost = self.labor_cost + self.parts_cost
        super(RepairJob, self).save(*args, **kwargs)

        # ถ้าสถานะเปลี่ยนเป็น Completed ให้ลดจำนวนอะไหล่ในสต็อก
        if old_status != 'COMPLETED' and self.status == 'COMPLETED':
            for part in self.used_parts.all():
                stock = part.product.stocks.first()  # ค้นหา Stock ที่เกี่ยวข้องกับ Product นี้
                if stock:
                    stock.current_stock -= part.quantity
                    stock.save()

        # ถ้าสถานะเปลี่ยนจาก Completed ไปเป็น In Progress ให้คืนสต็อกอะไหล่
        elif old_status == 'COMPLETED' and self.status != 'COMPLETED':
            for part in self.used_parts.all():
                stock = part.product.stocks.first()  # ค้นหา Stock ที่เกี่ยวข้องกับ Product นี้
                if stock:
                    stock.current_stock += part.quantity
                    stock.save()

    def __str__(self):
        return f"Repair Job for {self.customer.name} on {self.repair_date}"

    class Meta:
        verbose_name = "Repair Job"
        verbose_name_plural = "Repair Jobs"


# อะไหล่ที่ใช้ในงานซ่อม
class UsedPart(models.Model):
    repair_job = models.ForeignKey(RepairJob, on_delete=models.CASCADE, related_name='used_parts')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='used_in_repairs')
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    cost = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        # ดึงราคาจาก Product
        self.price = self.product.selling_price
        old_quantity = 0

        if self.pk:
            # ดึงข้อมูลเก่าเพื่อคำนวณความแตกต่างในจำนวนที่เปลี่ยนแปลง
            old_part = UsedPart.objects.get(pk=self.pk)
            old_quantity = old_part.quantity

        # คำนวณราคารวมของอะไหล่
        self.cost = self.quantity * self.price
        super(UsedPart, self).save(*args, **kwargs)

        # อัปเดตค่าอะไหล่ทั้งหมดใน RepairJob
        self.repair_job.update_parts_cost()

        # ตรวจสอบสถานะงานซ่อมและอัปเดตสต็อกอะไหล่
        if self.repair_job.status == 'COMPLETED':
            # อัปเดตสต็อกใน Stock ที่เกี่ยวข้องกับ Product
            stock = self.product.stocks.first()  # ค้นหา Stock ที่เกี่ยวข้องกับ Product นี้
            if stock:
                quantity_difference = self.quantity - old_quantity
                stock.current_stock -= quantity_difference
                stock.save()

    def delete(self, *args, **kwargs):
        # ก่อนลบ UsedPart ให้คืนสต็อกอะไหล่ถ้า RepairJob เป็น Completed
        if self.repair_job.status == 'COMPLETED':
            stock = self.product.stocks.first()  # ค้นหา Stock ที่เกี่ยวข้องกับ Product นี้
            if stock:
                stock.current_stock += self.quantity
                stock.save()
        
        super(UsedPart, self).delete(*args, **kwargs)
        # อัปเดตค่าอะไหล่ทั้งหมดใน RepairJob หลังจากลบ UsedPart
        self.repair_job.update_parts_cost()

    def __str__(self):
        return f"{self.quantity} x {self.product.name} for {self.repair_job.job_name}"
