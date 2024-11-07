from django.db import models
from django.contrib.auth.models import User  # Import the User model

class Product(models.Model):
    medicine_name = models.CharField(max_length=255)
    ml = models.CharField(max_length=50, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    company = models.CharField(max_length=255)
    min_sale = models.IntegerField()

    def __str__(self):
        return self.medicine_name


class Party(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_parties'
    )  # The user (Admin or Staff) who manages this party
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    associated_user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='as_party'
    )  # The authenticated user who is also a party, if applicable

    def __str__(self):
        return self.name


class BaseTransaction(models.Model):
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=[('sale', 'Sale'), ('purchase', 'Purchase')])
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_in = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    due_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(
        max_length=10,
        choices=[('pending', 'Pending'), ('partial', 'Partial'), ('completed', 'Completed')],
        default='pending'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='%(class)s_transactions')
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='%(class)s_created'
    )

    class Meta:
        abstract = True

class Transaction(BaseTransaction):
    date_at = models.DateField(auto_now_add=True)

    # def save(self, *args, **kwargs):
    #     self.due_amount = self.total_amount - self.payment_in
    #     if self.due_amount <= 0:
    #         self.payment_status = 'completed'
    #     elif self.payment_in > 0:
    #         self.payment_status = 'partial'
    #     else:
    #         self.payment_status = 'pending'
    #     super().save(*args, **kwargs)

    def update_stock(self):
        for item in self.items.all():
            if self.type == 'sale':
                item.stock.quantity -= item.quantity
            else:  # purchase
                item.stock.quantity += item.quantity
            item.stock.save()

    def __str__(self):
        return f"Transaction {self.id} - {self.type}"

class DraftTransaction(BaseTransaction):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Draft Transaction {self.id} - {self.party.name}"

class Stock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['product', 'user']

    def __str__(self):
        return f"{self.product.medicine_name} - Stock: {self.quantity}"

    def save(self, *args, **kwargs):
        if self.quantity < 0:
            self.quantity = 0
        super().save(*args, **kwargs)

class UserProfile(models.Model):
    USER_TYPE_CHOICES = [
        ('admin', 'Admin'),
        ('staff', 'Staff'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='staff')
    admin = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='staff_members'
    )
    is_premium = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # If this is a staff profile and their admin is premium,
        # automatically set this user as premium
        if self.user_type == 'staff' and self.admin:
            try:
                admin_profile = UserProfile.objects.get(user=self.admin)
                self.is_premium = admin_profile.is_premium
            except UserProfile.DoesNotExist:
                pass
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.user_type}"

class TransactionItem(models.Model):
    transaction = models.ForeignKey(
        Transaction, 
        related_name='items',  # Changed from 'transaction_items' to 'items'
        on_delete=models.CASCADE
    )
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.price
        super().save(*args, **kwargs)

class DraftTransactionItem(models.Model):
    draft_transaction = models.ForeignKey(
        'DraftTransaction',
        related_name='items',  # Use 'items' to access related items from DraftTransaction
        on_delete=models.CASCADE
    )
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.price
        super().save(*args, **kwargs)
