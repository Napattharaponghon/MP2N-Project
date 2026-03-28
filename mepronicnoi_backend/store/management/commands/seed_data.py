"""
คำสั่ง: python manage.py seed_data
ใส่ข้อมูลตัวอย่าง (Category + Product) เพื่อทดสอบเว็บไซต์
"""
from django.core.management.base import BaseCommand
from store.models import Category, Product


PRODUCTS = [
    {
        'brand': 'ME PRO NID NOI',
        'name': 'Derrick Rose II Basketball',
        'category': 'footwear',
        'description': 'รองเท้าบาสเก็ตบอลรุ่นคลาสสิกที่นำมาตีความใหม่ในแบบมินิมอล ออกแบบเพื่อประสิทธิภาพสูงสุดบนสนาม',
        'price': 6299,
        'stock': 50,
        'image_url': 'https://images.unsplash.com/photo-1608231387042-66d1773070a5?q=80&w=1000&auto=format&fit=crop',
        'available_sizes': 'S,M,L,XL',
    },
    {
        'brand': 'ME PRO NID NOI',
        'name': 'Oversized Linen Shirt',
        'category': 'tops',
        'description': 'เสื้อเชิ้ต Oversized ผ้าลินินธรรมชาติ ใส่สบาย ระบายอากาศดี เหมาะกับอากาศร้อน',
        'price': 3890,
        'stock': 30,
        'image_url': 'https://images.unsplash.com/photo-1512436991641-6745cdb1723f?q=80&w=1000&auto=format&fit=crop',
        'available_sizes': 'S,M,L,XL,XXL',
    },
    {
        'brand': 'ME PRO NID NOI',
        'name': 'Relaxed Track Pants',
        'category': 'bottoms',
        'description': 'กางเกง Track Pants ทรง Relaxed เนื้อผ้าเบา นุ่ม ใส่ได้ทั้ง Casual และ Sport',
        'price': 4590,
        'stock': 25,
        'image_url': 'https://images.unsplash.com/photo-1506152983158-b4a74a01c721?q=80&w=1000&auto=format&fit=crop',
        'available_sizes': 'S,M,L,XL',
    },
    {
        'brand': 'ME PRO NID NOI',
        'name': 'Merino Wool Hoodie',
        'category': 'tops',
        'description': 'Hoodie ผ้า Merino Wool คุณภาพสูง อบอุ่น ไม่คัน เหมาะกับอากาศเย็น',
        'price': 7990,
        'stock': 20,
        'image_url': 'https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?q=80&w=1000&auto=format&fit=crop',
        'available_sizes': 'S,M,L,XL',
    },
    {
        'brand': 'ME PRO NID NOI',
        'name': 'Leather Tote Bag',
        'category': 'accessories',
        'description': 'กระเป๋า Tote หนังแท้ ดีไซน์มินิมอล จุของได้เยอะ ทนทาน',
        'price': 12500,
        'stock': 15,
        'image_url': 'https://images.unsplash.com/photo-1549298916-b41d501d3772?q=80&w=1000&auto=format&fit=crop',
        'available_sizes': 'S,M,L',
    },
    {
        'brand': 'ME PRO NID NOI',
        'name': 'Essential Cotton Tee',
        'category': 'tops',
        'description': 'เสื้อยืด Cotton 100% น้ำหนักกลาง ทรง Boxy ใส่ได้ทุกวัน',
        'price': 1890,
        'stock': 100,
        'image_url': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?q=80&w=1000&auto=format&fit=crop',
        'available_sizes': 'S,M,L,XL,XXL',
    },
]

CATEGORIES = [
    ('Footwear', 'footwear'),
    ('Tops', 'tops'),
    ('Bottoms', 'bottoms'),
    ('Accessories', 'accessories'),
]


class Command(BaseCommand):
    help = 'ใส่ข้อมูลตัวอย่างสินค้าและหมวดหมู่'

    def handle(self, *args, **kwargs):
        self.stdout.write('📦 กำลังสร้างหมวดหมู่...')
        cat_map = {}
        for name, slug in CATEGORIES:
            cat, created = Category.objects.get_or_create(slug=slug, defaults={'name': name})
            cat_map[slug] = cat
            status = '✅ สร้าง' if created else '⏭️  มีอยู่แล้ว'
            self.stdout.write(f'  {status}: {name}')

        self.stdout.write('\n🛍️  กำลังสร้างสินค้า...')
        for data in PRODUCTS:
            cat_slug = data.pop('category')
            product, created = Product.objects.get_or_create(
                name=data['name'],
                defaults={**data, 'category': cat_map.get(cat_slug)}
            )
            status = '✅ สร้าง' if created else '⏭️  มีอยู่แล้ว'
            self.stdout.write(f'  {status}: {product.name} ({product.formatted_price()})')

        self.stdout.write(self.style.SUCCESS('\n🎉 เสร็จสิ้น! เว็บพร้อมใช้งานแล้ว'))
        self.stdout.write(self.style.SUCCESS('   → รันด้วย: python manage.py runserver'))
        self.stdout.write(self.style.SUCCESS('   → Admin:   http://127.0.0.1:8000/admin/'))
