from django.contrib import admin
from .models import Category, Product, Order, OrderItem

admin.site.site_header = 'ME PRO NID NOI - Admin'
admin.site.site_title = 'ME PRO NID NOI'
admin.site.index_title = 'จัดการร้านค้า'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'category', 'price', 'stock', 'is_active', 'created_at']
    list_filter = ['is_active', 'category', 'brand']
    search_fields = ['name', 'brand', 'description']
    list_editable = ['price', 'stock', 'is_active']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('ข้อมูลสินค้า', {
            'fields': ('brand', 'name', 'category', 'description')
        }),
        ('ราคาและสต็อก', {
            'fields': ('price', 'stock', 'available_sizes', 'is_active')
        }),
        ('รูปภาพ', {
            'fields': ('image', 'image_url'),
            'description': 'อัปโหลดรูปภาพ หรือใส่ URL รูปภาพ (เลือกอย่างใดอย่างหนึ่ง)'
        }),
        ('เวลา', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'product_name', 'size', 'quantity', 'price', 'formatted_subtotal']
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'email', 'phone', 'status', 'formatted_total', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['full_name', 'email', 'phone']
    list_editable = ['status']
    readonly_fields = ['created_at', 'updated_at', 'total_price', 'user']
    inlines = [OrderItemInline]
    fieldsets = (
        ('ข้อมูลลูกค้า', {
            'fields': ('user', 'full_name', 'email', 'phone', 'address')
        }),
        ('สถานะ & ราคา', {
            'fields': ('status', 'total_price', 'note')
        }),
        ('เวลา', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
