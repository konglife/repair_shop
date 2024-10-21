from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .models import Purchase, Stock
from django.utils import timezone

@receiver(post_save, sender=Purchase)
def update_stock_after_purchase(sender, instance, created, **kwargs):
    product = instance.product

    # อัปเดต Stock เมื่อมีการสร้าง Purchase ใหม่และสถานะเป็น RECEIVED
    if created and instance.status == 'RECEIVED':
        stock, created = Stock.objects.get_or_create(product=product)
        if created:
            stock.min_stock = 0
            stock.current_stock = instance.quantity
        else:
            stock.current_stock += instance.quantity

        stock.last_updated_at = timezone.now()
        update_stock_status(stock)
        stock.save()

@receiver(post_delete, sender=Purchase)
def update_stock_after_purchase_delete(sender, instance, **kwargs):
    # ปรับสต็อกเมื่อมีการลบ Purchase ที่เคยถูกเพิ่มเข้าไป
    if instance.status == 'RECEIVED':
        product = instance.product
        try:
            stock = Stock.objects.get(product=product)
            stock.current_stock -= instance.quantity
            stock.last_updated_at = timezone.now()
            update_stock_status(stock)
            stock.save()
        except Stock.DoesNotExist:
            pass

@receiver(pre_save, sender=Purchase)
def update_stock_before_purchase_update(sender, instance, **kwargs):
    if instance.pk:  # ตรวจสอบว่าเป็นการอัปเดต (มี pk อยู่แล้ว)
        old_purchase = Purchase.objects.get(pk=instance.pk)
        stock, created = Stock.objects.get_or_create(product=instance.product)

        # กรณีที่เปลี่ยนจาก RECEIVED เป็น PENDING หรือ CANCELLED
        if old_purchase.status == 'RECEIVED' and instance.status != 'RECEIVED':
            stock.current_stock -= old_purchase.quantity

        # กรณีที่เปลี่ยนจาก PENDING หรือ CANCELLED เป็น RECEIVED
        elif old_purchase.status != 'RECEIVED' and instance.status == 'RECEIVED':
            stock.current_stock += instance.quantity

        # กรณีที่อัปเดตจำนวนสินค้า (เฉพาะสถานะ RECEIVED)
        elif old_purchase.status == 'RECEIVED' and instance.status == 'RECEIVED' and old_purchase.quantity != instance.quantity:
            stock.current_stock -= old_purchase.quantity
            stock.current_stock += instance.quantity

        stock.last_updated_at = timezone.now()
        update_stock_status(stock)
        stock.save()

def update_stock_status(stock):
    """ฟังก์ชันช่วยในการอัปเดตสถานะของสต็อก"""
    if stock.current_stock == 0:
        stock.status = 'OUT_OF_STOCK'
    elif stock.current_stock < stock.min_stock:
        stock.status = 'LOW'
    else:
        stock.status = 'AVAILABLE'
