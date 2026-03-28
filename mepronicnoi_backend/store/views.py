import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .models import Product, Order, OrderItem, Category
from .forms import OrderForm, RegisterForm


# ─── หน้าหลัก ─────────────────────────────────────────────────────────────────
def home(request):
    featured = Product.objects.filter(is_active=True)[:6]
    categories = Category.objects.all()
    return render(request, 'store/home.html', {
        'featured_products': featured,
        'categories': categories,
    })


# ─── หน้าสินค้า ───────────────────────────────────────────────────────────────
def products(request):
    qs = Product.objects.filter(is_active=True)
    category_slug = request.GET.get('category')
    search_q = request.GET.get('q', '')

    if category_slug:
        qs = qs.filter(category__slug=category_slug)
    if search_q:
        qs = qs.filter(name__icontains=search_q) | qs.filter(brand__icontains=search_q)

    categories = Category.objects.all()
    return render(request, 'store/products.html', {
        'products': qs,
        'categories': categories,
        'selected_category': category_slug,
        'search_q': search_q,
    })


# ─── API: ดึงข้อมูลสินค้าทั้งหมด (JSON) ──────────────────────────────────────
def api_products(request):
    qs = Product.objects.filter(is_active=True)
    data = []
    for p in qs:
        data.append({
            'id': p.id,
            'brand': p.brand,
            'name': p.name,
            'price': str(p.price),
            'formatted_price': p.formatted_price(),
            'description': p.description,
            'image': p.get_image(),
            'sizes': p.get_sizes(),
            'stock': p.stock,
        })
    return JsonResponse({'products': data})


# ─── API: ข้อมูลสินค้าชิ้นเดียว (JSON) ──────────────────────────────────────
def api_product_detail(request, pk):
    p = get_object_or_404(Product, pk=pk, is_active=True)
    return JsonResponse({
        'id': p.id,
        'brand': p.brand,
        'name': p.name,
        'price': str(p.price),
        'formatted_price': p.formatted_price(),
        'description': p.description,
        'image': p.get_image(),
        'sizes': p.get_sizes(),
        'stock': p.stock,
    })


# ─── API: ค้นหาสินค้า (JSON) ─────────────────────────────────────────────────
def api_search(request):
    q = request.GET.get('q', '')
    if not q:
        return JsonResponse({'products': []})
    qs = Product.objects.filter(is_active=True).filter(
        name__icontains=q
    ) | Product.objects.filter(is_active=True).filter(brand__icontains=q)
    data = [{'id': p.id, 'brand': p.brand, 'name': p.name,
              'formatted_price': p.formatted_price(), 'image': p.get_image()} for p in qs]
    return JsonResponse({'products': data})


# ─── หน้า Checkout ────────────────────────────────────────────────────────────
def checkout(request):
    cart_data = request.session.get('cart', [])
    if not cart_data:
        messages.warning(request, 'ตะกร้าของคุณว่างเปล่า')
        return redirect('products')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            total = sum(item['price'] * item['qty'] for item in cart_data)
            order.total_price = total
            order.save()

            for item in cart_data:
                product = Product.objects.filter(id=item.get('product_id')).first()
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=item['name'],
                    size=item['size'],
                    quantity=item['qty'],
                    price=item['price'],
                )

            request.session['cart'] = []
            messages.success(request, f'สั่งซื้อสำเร็จ! หมายเลขออร์เดอร์: #{order.id}')
            return redirect('order_success', pk=order.id)
    else:
        initial = {}
        if request.user.is_authenticated:
            initial = {
                'full_name': request.user.get_full_name() or request.user.username,
                'email': request.user.email,
            }
        form = OrderForm(initial=initial)

    cart_total = sum(item['price'] * item['qty'] for item in cart_data)
    return render(request, 'store/checkout.html', {
        'form': form,
        'cart': cart_data,
        'cart_total': cart_total,
    })


# ─── หน้าสั่งซื้อสำเร็จ ───────────────────────────────────────────────────────
def order_success(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'store/order_success.html', {'order': order})


# ─── API: เพิ่มสินค้าเข้าตะกร้า (Session) ───────────────────────────────────
@require_POST
def api_add_to_cart(request):
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        size = data.get('size', 'L')
        qty = int(data.get('qty', 1))

        product = get_object_or_404(Product, pk=product_id, is_active=True)
        cart = request.session.get('cart', [])

        # ตรวจสอบสินค้าซ้ำ
        found = False
        for item in cart:
            if item['product_id'] == product_id and item['size'] == size:
                item['qty'] += qty
                found = True
                break
        if not found:
            cart.append({
                'product_id': product_id,
                'name': product.name,
                'brand': product.brand,
                'price': float(product.price),
                'size': size,
                'qty': qty,
                'image': product.get_image(),
            })

        request.session['cart'] = cart
        request.session.modified = True
        total_items = sum(i['qty'] for i in cart)
        return JsonResponse({'success': True, 'cart_count': total_items})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


# ─── API: ดูตะกร้า ────────────────────────────────────────────────────────────
def api_cart(request):
    cart = request.session.get('cart', [])
    total = sum(item['price'] * item['qty'] for item in cart)
    return JsonResponse({
        'cart': cart,
        'total': total,
        'formatted_total': f"{int(total):,} ฿",
        'cart_count': sum(i['qty'] for i in cart),
    })


# ─── API: ลบสินค้าออกจากตะกร้า ───────────────────────────────────────────────
@require_POST
def api_remove_from_cart(request):
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        size = data.get('size')
        cart = request.session.get('cart', [])
        cart = [i for i in cart if not (i['product_id'] == product_id and i['size'] == size)]
        request.session['cart'] = cart
        request.session.modified = True
        total = sum(i['price'] * i['qty'] for i in cart)
        return JsonResponse({'success': True, 'cart_count': sum(i['qty'] for i in cart),
                             'formatted_total': f"{int(total):,} ฿"})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


# ─── Auth: สมัครสมาชิก ───────────────────────────────────────────────────────
def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'สมัครสมาชิกสำเร็จ! ยินดีต้อนรับ 🎉')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'store/register.html', {'form': form})


# ─── Auth: เข้าสู่ระบบ ───────────────────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'ยินดีต้อนรับกลับมา, {user.username}!')
            return redirect(request.GET.get('next', 'home'))
    else:
        form = AuthenticationForm()
    return render(request, 'store/login.html', {'form': form})


# ─── Auth: ออกจากระบบ ────────────────────────────────────────────────────────
def logout_view(request):
    logout(request)
    messages.info(request, 'ออกจากระบบแล้ว')
    return redirect('home')


# ─── ประวัติการสั่งซื้อ ───────────────────────────────────────────────────────
@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/my_orders.html', {'orders': orders})
