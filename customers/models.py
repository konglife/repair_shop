from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=100)  # ชื่อและนามสกุล
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)  # รูปภาพ
    phone = models.CharField(max_length=15)  # เบอร์โทรศัพท์
    email = models.EmailField(unique=True)  # อีเมล
    address = models.TextField()  # ที่อยู่
    created_at = models.DateTimeField(auto_now_add=True)  # วันเวลาที่สร้าง
    updated_at = models.DateTimeField(auto_now=True)  # วันเวลาที่แก้ไขล่าสุด

    def __str__(self):
        return f"{self.name}"

class RepairHistory(models.Model):
    customer = models.ForeignKey(Customer, related_name='repair_history', on_delete=models.CASCADE)  # ลูกค้าที่เกี่ยวของงานซ่อม
    description = models.TextField()  # รายละเอียดงานซ่อม
    date = models.DateTimeField()  # วันที่ซ่อม
    cost = models.DecimalField(max_digits=10, decimal_places=2)  # ค่าใช้

    def __str__(self):
        return f"Repair on {self.date} for {self.customer.name}"

