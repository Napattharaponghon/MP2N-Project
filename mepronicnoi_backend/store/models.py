from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='ชื่อหมวดหมู่')
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'หมวดหมู่'
        verbose_name_plural = 'หมวดหมู่'

    def __str__(self):
        return self.name


class Product(models.Model):
    SIZE_CHOICES = [
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
        ('XXL', 'XXL'),
    ]

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True,
                                  verbose_name='หมวดหมู่')
    brand = models.CharField(max_length=200, default='ME PRO NID NOI', verbose_name='แบรนด์')
    name = models.CharField(max_length=200, verbose_name='ชื่อสินค้า')
    description = models.TextField(blank=True, verbose_name='รายละเอียด')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='ราคา (฿)')
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name='รูปภาพ')
    image_url = models.URLField(blank=True, verbose_name='URL รูปภาพ (ถ้าไม่อัปโหลด)')
    available_sizes = models.CharField(max_length=50, default='S,M,L,XL', verbose_name='ไซส์ที่มี (คั่นด้วย ,)')
    stock = models.PositiveIntegerField(default=0, verbose_name='จำนวนสต็อก')
    is_active = models.BooleanField(default=True, verbose_name='เปิดขาย')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'สินค้า'
        verbose_name_plural = 'สินค้า'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_image(self):
        if self.image:
            return self.image.url
        return self.image_url or ''

    def get_sizes(self):
        return [s.strip() for s in self.available_sizes.split(',')]

    def formatted_price(self):
        return f"{int(self.price):,} ฿"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'รอดำเนินการ'),
        ('confirmed', 'ยืนยันแล้ว'),
        ('shipped', 'จัดส่งแล้ว'),
        ('delivered', 'ได้รับสินค้าแล้ว'),
        ('cancelled', 'ยกเลิก'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                              verbose_name='ผู้สั่งซื้อ')
    # ข้อมูลลูกค้า (สำหรับ guest หรือ backup)
    full_name = models.CharField(max_length=200, verbose_name='ชื่อ-นามสกุล')
    email = models.EmailField(verbose_name='อีเมล')
    phone = models.CharField(max_length=20, verbose_name='เบอร์โทร')
    address = models.TextField(verbose_name='ที่อยู่จัดส่ง')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending',
                               verbose_name='สถานะ')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='ราคารวม (฿)')
    note = models.TextField(blank=True, verbose_name='หมายเหตุ')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'คำสั่งซื้อ'
        verbose_name_plural = 'คำสั่งซื้อ'
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - {self.full_name}"

    def formatted_total(self):
        return f"{int(self.total_price):,} ฿"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE,
                               verbose_name='คำสั่งซื้อ')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True,
                                 verbose_name='สินค้า')
    product_name = models.CharField(max_length=200, verbose_name='ชื่อสินค้า (snapshot)')
    size = models.CharField(max_length=10, verbose_name='ไซส์')
    quantity = models.PositiveIntegerField(default=1, verbose_name='จำนวน')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='ราคาต่อชิ้น (฿)')

    class Meta:
        verbose_name = 'รายการสินค้า'
        verbose_name_plural = 'รายการสินค้า'

    def __str__(self):
        return f"{self.product_name} x{self.quantity} (Size: {self.size})"

    def subtotal(self):
        return self.price * self.quantity

    def formatted_subtotal(self):
        return f"{int(self.subtotal()):,} ฿"
