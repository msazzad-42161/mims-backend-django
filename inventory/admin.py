# inventory/admin.py
from django.contrib import admin
from .models import Product, Party, Transaction, UserProfile, Stock, DraftTransaction

admin.site.site_header = 'Medicine Inventory Management System'
admin.site.site_title = 'MIMS'
admin.site.index_title = 'Admin Panel'

# admin.site.register(Product)    
# admin.site.register(Party)
# admin.site.register(Transaction)
# admin.site.register(UserProfile)
# admin.site.register(Stock)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'medicine_name', 'company', 'price', 'unit_price')
    search_fields = ('medicine_name', 'company')
    list_filter = ('company',)

@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone', 'user','associated_user')
    search_fields = ('name', 'email', 'phone', 'user__username')
    list_filter = ('name', 'user')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'party', 'user', 'date_at', 'total_amount', 'payment_in', 'due_amount', 'payment_status', 'type')
    search_fields = ('party__name', 'type', 'user__username')
    list_filter = ('payment_status', 'type', 'user')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'user', 'user_type', 'get_admin_username', 'is_premium', 'get_email')
    search_fields = (
        'user__username', 
        'user__email',
        'user_type', 
        'admin__username'
    )
    list_filter = (
        'is_premium',
        'user_type', 
        'admin',
    )
    ordering = ('-is_premium', 'user_type', 'user__username')
    list_editable = ('is_premium',)  # Allow editing premium status directly from list view
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'  # Column header in admin
    get_email.admin_order_field = 'user__email'  # Make column sortable

    def get_admin_username(self, obj):
        return obj.admin.username if obj.admin else 'No Admin'
    get_admin_username.short_description = 'Admin Username'  # Column header in admin
    get_admin_username.admin_order_field = 'admin__username'  # Make column sortable

    def user_id(self, obj):
        return obj.user.id  # Return the ID of the associated User
    user_id.short_description = 'User ID'  # Column header in admin
    user_id.admin_order_field = 'user__id'  # Make column sortable

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'admin')

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'quantity', 'user')
    search_fields = ('product__medicine_name', 'user__username')
    list_filter = ('product__company', 'user')

@admin.register(DraftTransaction)
class DraftTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'party', 'user', 'total_amount', 'created_at', 'updated_at')
    search_fields = ('party__name', 'user__username')
    list_filter = ('user',)