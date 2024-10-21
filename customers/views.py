from django.shortcuts import render, get_object_or_404, redirect
from .models import Customer, RepairHistory
from .forms import CustomerForm, RepairHistoryForm
from django.core.paginator import Paginator

# ฟังก์ชันแสดงรายชื่อลูกค้าทั้งหมด
def customer_list(request):
    query = request.GET.get('q')
    customers = Customer.objects.all().order_by('id') # จัดเรียงตามชื่อลูกค้า

    if query:
        customers = customers.filter(name__icontains=query).order_by('id')  # ใช้การค้นหาที่ ignore case sensitive (ใช้ icontains) จัดเรียงตามชื่อเมื่อมีการค้นหา

    paginator = Paginator(customers, 10)  # แบ่งหน้าโดยแสดง 10 รายการต่อหน้า
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'customers/customer_list.html', {'page_obj': page_obj})

# ฟังก์ชันแสดงรายละเอียดลูกค้าแต่ละคน
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    repair_history = RepairHistory.objects.filter(customer=customer)
    return render(request, 'customers/customer_detail.html', {'customer': customer, 'repair_history': repair_history})

# ฟังก์ชันเพิ่มลูกค้าใหม่
def add_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('customer_list')
    else:
        form = CustomerForm()
    return render(request, 'customers/add_customer.html', {'form': form})


# ฟังก์ชันแก้ไขข้อมูลลูกค้า
def edit_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('customer_detail', pk=customer.pk)
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'customers/edit_customer.html', {'form': form, 'customer': customer})

# ฟังก์ชันลบลูกค้า
def delete_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customer.delete()
    return redirect('customer_list')