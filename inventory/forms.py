from django import forms
from .models import Purchase, ProductSupplier

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['product', 'quantity', 'supplier', 'purchase_date', 'payment', 'status']

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        supplier = cleaned_data.get('supplier')

        if product and supplier:
            product_supplier = ProductSupplier.objects.filter(product=product, supplier=supplier).first()
            if not product_supplier:
                raise forms.ValidationError("ไม่พบราคาสำหรับสินค้านี้จากซัพพลายเออร์ที่เลือก")
        return cleaned_data