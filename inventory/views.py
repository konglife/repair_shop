from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Supplier, Stock, Purchase, ProductSupplier
from .forms import SupplierForm, PurchaseForm
from django.http import JsonResponse
from .models import Product

def product_list(request):
    products = Product.objects.all()  # ดึงสินค้าทั้งหมดจากฐานข้อมูล
    return render(request, 'inventory/product_list.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)  # ดึงสินค้าตาม Primary Key (id)
    stock = product.stock  # ดึงข้อมูลสต็อกของสินค้า
    return render(request, 'inventory/product_detail.html', {'product': product, 'stock': stock})

def add_supplier(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()  # บันทึกซัพพลายเออร์ใหม่
            return redirect('supplier_list')  # กลับไปที่หน้าแสดงซัพพลายเออร์
    else:
        form = SupplierForm()
    return render(request, 'inventory/add_supplier.html', {'form': form})

def purchase_list(request):
    purchases = Purchase.objects.all()  # ดึงคำสั่งซื้อทั้งหมดจากฐานข้อมูล
    return render(request, 'inventory/purchase_list.html', {'purchases': purchases})

def add_purchase(request):
    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        if form.is_valid():
            purchase = form.save(commit=False)

            # ดึงราคาอัตโนมัติจาก ProductSupplier
            product_supplier = ProductSupplier.objects.filter(
                product=purchase.product, supplier=purchase.supplier
            ).first()

            if product_supplier:
                purchase.price = product_supplier.price
            else:
                purchase.price = 0  # กำหนดค่า default หากไม่พบ ProductSupplier ที่ตรงกัน

            purchase.save()
            return redirect('purchase_list')
    else:
        form = PurchaseForm()

    return render(request, 'inventory/add_purchase.html', {'form': form})