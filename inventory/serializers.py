# inventory/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Product, Party, Transaction,Stock, TransactionItem, DraftTransaction, DraftTransactionItem,UserProfile
from django.contrib.auth.password_validation import validate_password
from decimal import Decimal
from django.db import transaction

class BulkProductSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        products = [Product(**item) for item in validated_data]
        return Product.objects.bulk_create(products)

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'medicine_name', 'ml', 'price', 'unit_price', 'company', 'min_sale']
        list_serializer_class = BulkProductSerializer

from rest_framework import serializers
from .models import Party
from django.contrib.auth.models import User

class PartySerializer(serializers.ModelSerializer):
    associated_user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Party
        fields = ['id', 'name', 'email', 'phone', 'address', 'associated_user', 'user']
        read_only_fields = ('user',)

    def validate(self, data):
        user = self.context['request'].user

        # If the user is a staff member and associated_user is provided, override it with their admin
        if user.userprofile.user_type == 'staff':
            admin_user = user.userprofile.admin
            if not admin_user:
                raise serializers.ValidationError("Staff user does not have an associated admin.")
            data['associated_user'] = admin_user
        else:
            # If the user is an admin and associated_user is not provided, it's a regular party
            # If associated_user is provided, it will be a user-associated party
            data['associated_user'] = data.get('associated_user')

        return data
class TransactionItemSerializer(serializers.ModelSerializer):
    stock = serializers.PrimaryKeyRelatedField(queryset=Stock.objects.all())
    
    class Meta:
        model = TransactionItem
        fields = ['stock', 'quantity']

class TransactionSerializer(serializers.ModelSerializer):
    items = TransactionItemSerializer(many=True)
    
    class Meta:
        model = Transaction
        fields = ['id', 'party', 'type', 'payment_in', 'items', 'total_amount', 'due_amount', 
                 'payment_status', 'created_by', 'user', 'date_at']
        read_only_fields = ('payment_status', 'due_amount', 'total_amount', 'date_at', 
                          'created_by', 'user')
        extra_kwargs = {
            'party': {'required': False},
            'type': {'required': False},
            'payment_in': {'required': False}
        }

    def validate(self, data):
        # Get the current user
        user = self.context['request'].user
        
        # If user is staff, get their admin
        if user.userprofile.user_type == 'staff':
            user = user.userprofile.admin

        # Validate party belongs to user
        if data['party'].user != user:
            raise serializers.ValidationError(
                {"party": "You can only create transactions for your own partys"}
            )

        # Validate stock ownership for each item
        for item in data['items']:
            stock = item['stock']
            if stock.user != user:
                raise serializers.ValidationError(
                    {"items": f"Stock {stock.product.medicine_name} does not belong to you"}
                )

        return data

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        
        # Calculate total amount from items using product prices
        total_amount = sum(
            item['stock'].product.price * item['quantity']
            for item in items_data
        )

        validated_data['total_amount'] = total_amount
        validated_data['due_amount'] = total_amount - validated_data.get('payment_in', 0)

        with transaction.atomic():
            # Create transaction
            transaction_instance = Transaction.objects.create(**validated_data)
            
            # Create transaction items
            for item in items_data:
                TransactionItem.objects.create(
                    transaction=transaction_instance,
                    stock=item['stock'],
                    quantity=item['quantity'],
                    price=item['stock'].product.price,
                    subtotal=item['stock'].product.price * item['quantity']
                )
            
            # Call update_stock() after creating all items
            transaction_instance.update_stock()
            
            return transaction_instance

    def update(self, instance, validated_data):
        # Only process items if they're in the payload
        if 'items' in validated_data:
            items_data = validated_data.pop('items')
            
            # Calculate new total amount
            total_amount = sum(
                item['stock'].product.price * item['quantity']
                for item in items_data
            )
            
            instance.total_amount = total_amount
            instance.due_amount = total_amount - instance.payment_in
            
            # Delete existing items
            instance.items.all().delete()
            
            # Create new items
            for item in items_data:
                TransactionItem.objects.create(
                    transaction=instance,
                    stock=item['stock'],
                    quantity=item['quantity'],
                    price=item['stock'].product.price,
                    subtotal=item['stock'].product.price * item['quantity']
                )
        
        # Update any other fields if they're in the payload
        for field in validated_data:
            setattr(instance, field, validated_data[field])
        
        instance.save()
        return instance

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = '__all__'
        read_only_fields = ('user',)

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    email = serializers.EmailField(required=True)
    is_premium = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'is_premium')

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        is_premium = validated_data.pop('is_premium', False)
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user, is_premium

class DraftTransactionItemSerializer(serializers.ModelSerializer):
    stock = serializers.PrimaryKeyRelatedField(queryset=Stock.objects.all())
    
    class Meta:
        model = DraftTransactionItem
        fields = ['stock', 'quantity']

class DraftTransactionSerializer(serializers.ModelSerializer):
    items = DraftTransactionItemSerializer(many=True)

    class Meta:
        model = DraftTransaction
        fields = ['id', 'party', 'items', 'total_amount', 'payment_in', 'due_amount', 
                 'payment_status', 'type', 'created_at', 'updated_at', 'created_by', 'user']
        read_only_fields = ('created_at', 'updated_at', 'total_amount', 'due_amount', 
                          'payment_status', 'created_by', 'user')

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        
        # Use the user from the request context
        user = self.context['request'].user
        
        if user.userprofile.user_type == 'staff':
            user = user.userprofile.admin

        # Calculate total_amount based on items
        total_amount = sum(item['quantity'] * item['stock'].product.price for item in items_data)
        validated_data['total_amount'] = total_amount
        
        # Create the draft transaction
        draft_transaction = DraftTransaction.objects.create(user=user, **validated_data)
        
        # Create draft transaction items
        for item in items_data:
            DraftTransactionItem.objects.create(
                draft_transaction=draft_transaction,
                stock=item['stock'],
                quantity=item['quantity'],
                price=item['stock'].product.price,
                subtotal=item['stock'].product.price * item['quantity']
            )
        
        return draft_transaction

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    email = serializers.CharField(source='user.email')
    admin_email = serializers.CharField(source='admin.email', read_only=True)
    admin_username = serializers.CharField(source='admin.username', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'user_type', 'is_premium', 
                 'admin_email', 'admin_username']
        read_only_fields = ['user_type', 'is_premium']