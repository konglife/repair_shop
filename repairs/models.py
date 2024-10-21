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
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='repair_jobs')  # ลูกค้าที่เกี่ยวข้อง
    repair_date = models.DateTimeField()  # วันที่เริ่มงานซ่อม
    description = models.TextField()  # คำอธิบายงานซ่อม
    labor_cost = models.DecimalField(max_digits=10, decimal_places=2)  # ค่าแรง
    parts_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # ค่าอะไหล่ทั้งหมด
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, editable=False)  # ค่าใช้จ่ายทั้งหมด (ค่าแรง + ค่าอะไหล่)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='IN_PROGRESS')  # สถานะงานซ่อม
    notes = models.TextField(blank=True, null=True)  # หมายเหตุเพิ่มเติม
    payment = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='UNPAID')  # สถานะการชำระเงิน
    created_at = models.DateTimeField(auto_now_add=True)  # วันที่สร้าง
    updated_at = models.DateTimeField(auto_now=True)  # วันที่แก้ไขล่าสุด

    def save(self, *args, **kwargs):
        self.total_cost = self.labor_cost + self.parts_cost
        super(RepairJob, self).save(*args, **kwargs)

    def __str__(self):
        return f"Repair Job for {self.customer.name} on {self.repair_date}"
    
    class Meta:
        verbose_name = "Repair Job"
        verbose_name_plural = "Repair Jobs"

# อะไหล่ที่ใช้ในงานซ่อม
class UsedPart(models.Model):
    repair_job = models.ForeignKey(RepairJob, on_delete=models.CASCADE, related_name='used_parts', default=1)  # งานซ่อมที่เกี่ยวข้อง
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='used_in_repairs')  # อะไหล่ที่ใช้
    quantity = models.PositiveIntegerField()  # จำนวนอะไหล่ที่ใช้
    price = models.DecimalField(max_digits=10, decimal_places=2)  # ราคาต่อหน่วยของอะไหล่
    cost = models.DecimalField(max_digits=10, decimal_places=2, editable=False)  # ราคารวมของอะไหล่ (quantity * price)

    def save(self, *args, **kwargs):
        # ถ้า price ยังไม่มีค่า ให้ดึงจากราคาขายของสินค้า
        if not self.price:
            self.price = self.product.selling_price  # ดึงราคาขายจาก Product (สินค้านั้นๆ)
        
        # คำนวณราคารวมของอะไหล่
        self.cost = self.quantity * self.price
        
        # อัปเดต parts_cost ใน RepairJob
        self.repair_job.parts_cost += self.cost
        self.repair_job.save()
        
        super(UsedPart, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} for {self.repair_job.job_name}"


