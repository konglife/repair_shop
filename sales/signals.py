from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import SaleItem

@receiver(post_delete, sender=SaleItem)
def update_stock_on_delete(sender, instance, **kwargs):
    # เมื่อ SaleItem ถูกลบ จะคืนจำนวนสินค้าในสต็อก
    stock = instance.product.stocks.first()
    if stock:
        stock.current_stock += instance.quantity
        stock.save()
