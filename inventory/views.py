# inventory/views.py
from decimal import Decimal
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .models import Product, Party, Transaction,Stock, UserProfile, DraftTransaction,TransactionItem
from django.db import transaction
from .serializers import ProductSerializer, PartySerializer, TransactionSerializer, RegisterSerializer,StockSerializer, DraftTransactionSerializer,UserProfileSerializer
from .permissions import IsAdminOrStaffPermission
from rest_framework.parsers import MultiPartParser, FormParser
import csv
import io
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from django.db import transaction as db_transaction
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import logout

User = get_user_model()

# Product View: Handles product listing and creation
class ProductListCreate(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrStaffPermission]
    queryset = Product.objects.all()

    def get_queryset(self):
        try:
            if self.request.user.userprofile.user_type == 'admin':
                return Product.objects.all()
            return Product.objects.filter(stock__user=self.request.user)
        except UserProfile.DoesNotExist:
            return Product.objects.none()

    def perform_create(self, serializer):
        serializer.save()  # Simply create the product without creating stock

# Party View: Handles customer listing and creation

class PartyListCreate(generics.ListCreateAPIView):
    serializer_class = PartySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        try:
            user = self.request.user
            if user.userprofile.user_type == 'admin':
                if self.request.path.endswith('/me/parties/'):
                    return Party.objects.filter(user=user)
                return Party.objects.filter(user=user)
            # For staff users
            return Party.objects.filter(user=user.userprofile.admin)
        except UserProfile.DoesNotExist:
            return Party.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.userprofile.user_type == 'staff':
            user = user.userprofile.admin  # Use the admin user for staff
        serializer.save(user=user)

# Transaction View: Handles transaction listing and creation
class TransactionListCreate(generics.ListCreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        try:
            user = self.request.user
            if user.userprofile.user_type == 'admin':
                if self.request.path.endswith('/me/transactions/'):
                    return Transaction.objects.filter(user=user)
                return Transaction.objects.filter(user=user)
            # For staff users
            if self.request.path.endswith('/me/transactions/'):
                return Transaction.objects.filter(created_by=user)
            return Transaction.objects.filter(user=user.userprofile.admin)
        except UserProfile.DoesNotExist:
            return Transaction.objects.none()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_create(self, serializer):
        try:
            with transaction.atomic():
                user = self.request.user
                if user.userprofile.user_type == 'staff':
                    user = user.userprofile.admin
                serializer.save(user=user)
        except Exception as e:
            raise ValidationError(str(e))

    def _validate_stock(self, items):
        """Validate stock availability before processing sale"""
        for item in items:
            stock = item['stock']
            quantity = item['quantity']
            
            if quantity < stock.product.min_sale:
                raise ValidationError(
                    f"Minimum sale quantity for {stock.product.medicine_name} is {stock.product.min_sale}"
                )
            
            if stock.quantity < quantity:
                raise ValidationError(
                    f"Insufficient stock for {stock.product.medicine_name}. Available: {stock.quantity}"
                )

# Complete Payment View: Handles updating the payment information for a transaction
class CompletePayment(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, transaction_id):
        try:
            # Retrieve the transaction and update the payment details
            transaction = Transaction.objects.get(id=transaction_id, user=request.user)
            additional_payment = Decimal(request.data.get('additional_payment', 0))
            transaction.payment_in += additional_payment
            transaction.update_balance()
            serializer = TransactionSerializer(transaction)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Transaction.DoesNotExist:
            return Response({"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND)



class StockListCreate(generics.ListCreateAPIView):
    serializer_class = StockSerializer
    permission_classes = [IsAdminOrStaffPermission]

    def get_queryset(self):
        try:
            user = self.request.user
            if user.userprofile.user_type == 'admin':
                return Stock.objects.filter(user=user)
            # For staff, get stocks associated with their admin
            return Stock.objects.filter(user=user.userprofile.admin)
        except UserProfile.DoesNotExist:
            return Stock.objects.none()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        product = serializer.validated_data['product']
        new_quantity = serializer.validated_data['quantity']

        # Get the appropriate user (admin's ID for staff)
        user = request.user
        if user.userprofile.user_type == 'staff':
            user = user.userprofile.admin

        existing_stock = Stock.objects.filter(
            product=product,
            user=user
        ).first()

        if existing_stock:
            existing_stock.quantity += new_quantity
            existing_stock.save()
            response_data = {
                'message': 'Stock updated successfully',
                'stock': self.get_serializer(existing_stock).data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            # Create new stock with admin's user ID for staff
            stock = serializer.save(user=user)
            response_data = {
                'message': 'Stock created successfully',
                'stock': self.get_serializer(stock).data
            }
            return Response(response_data, status=status.HTTP_201_CREATED)

class StockUpdateView(generics.UpdateAPIView):
    serializer_class = StockSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        try:
            if self.request.user.userprofile.user_type == 'admin':
                return Stock.objects.all()
            return Stock.objects.filter(user=self.request.user)
        except UserProfile.DoesNotExist:
            return Stock.objects.none()

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)




# Register View: Handles user registration
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user_type = request.data.get('user_type', 'staff')
            
            if user_type not in ['admin', 'staff']:
                return Response({'error': 'Invalid user type'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            try:
                with transaction.atomic():
                    user, is_premium = serializer.save()
                    
                    if user_type == 'staff':
                        admin_id = request.data.get('admin_id')
                        if not admin_id:
                            return Response({'error': 'Staff must be assigned to an admin'}, 
                                          status=status.HTTP_400_BAD_REQUEST)
                        try:
                            admin = User.objects.get(id=admin_id)
                            admin_profile = UserProfile.objects.get(user=admin, user_type='admin')
                            # Staff inherits premium status from admin
                            is_premium = admin_profile.is_premium
                        except (User.DoesNotExist, UserProfile.DoesNotExist):
                            return Response({'error': 'Invalid admin ID'}, 
                                          status=status.HTTP_400_BAD_REQUEST)
                    
                    # Create user profile
                    profile = UserProfile.objects.create(
                        user=user,
                        user_type=user_type,
                        is_premium=is_premium
                    )
                    
                    # If staff, associate with admin
                    if user_type == 'staff':
                        profile.admin = admin
                        profile.save()
                    
                    return Response({
                        'message': f'User registered successfully as {user_type}',
                        'user': {
                            'id': user.id,
                            'username': user.username,
                            'email': user.email,
                            'user_type': user_type,
                            'is_premium': profile.is_premium
                        }
                    }, status=status.HTTP_201_CREATED)
                    
            except Exception as e:
                return Response({'error': str(e)}, 
                              status=status.HTTP_400_BAD_REQUEST)
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductBulkCreateView(generics.CreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrStaffPermission]

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True
        return super().get_serializer(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            products = serializer.save()
            
            return Response({
                'message': f'Successfully created {len(products)} products',
                'products': ProductSerializer(products, many=True).data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class ProductCSVUploadView(generics.CreateAPIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAdminOrStaffPermission]

    def post(self, request, *args, **kwargs):
        try:
            csv_file = request.FILES.get('file')
            if not csv_file:
                return Response({
                    'error': 'No file uploaded'
                }, status=status.HTTP_400_BAD_REQUEST)

            if not csv_file.name.endswith('.csv'):
                return Response({
                    'error': 'File must be a CSV'
                }, status=status.HTTP_400_BAD_REQUEST)

            decoded_file = csv_file.read().decode('utf-8')
            csv_data = csv.DictReader(io.StringIO(decoded_file))
            products_data = []

            for row in csv_data:
                product_data = {
                    'medicine_name': row['medicine_name'],
                    'ml': row.get('ml', None),
                    'price': float(row['price']),
                    'unit_price': float(row['unit_price']),
                    'company': row['company'],
                    'min_sale': int(row['min_sale'])
                }
                products_data.append(product_data)

            serializer = ProductSerializer(data=products_data, many=True)
            serializer.is_valid(raise_exception=True)
            products = serializer.save()

            return Response({
                'message': f'Successfully created {len(products)} products',
                'products': ProductSerializer(products, many=True).data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class DraftTransactionListCreate(generics.ListCreateAPIView):
    serializer_class = DraftTransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DraftTransaction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save()  # Just save the serializer, user is handled in the serializer


class ExecuteDraftTransaction(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, draft_id):
        try:
            # Retrieve the draft transaction
            if request.user.userprofile.user_type == 'staff':
                draft_transaction = DraftTransaction.objects.get(id=draft_id, user=request.user.userprofile.admin)
            else:
                draft_transaction = DraftTransaction.objects.get(id=draft_id, user=request.user)
            # Create a new transaction from the draft
            transaction = Transaction.objects.create(
                user=draft_transaction.user,  # Set the user to the admin
                party=draft_transaction.party,
                total_amount=draft_transaction.total_amount,
                payment_in=draft_transaction.payment_in,
                due_amount=draft_transaction.due_amount,
                payment_status=draft_transaction.payment_status,
                type=draft_transaction.type,
            )

            # Create transaction items from the draft
            for item in draft_transaction.items.all():
                TransactionItem.objects.create(
                    transaction=transaction,
                    stock=item.stock,
                    quantity=item.quantity,
                    price=item.price,
                    subtotal=item.subtotal
                )

            # Update stock quantities using the existing logic
            transaction.update_stock()

            # Optionally, delete the draft after execution
            draft_transaction.delete()

            return Response({"message": "Draft transaction executed successfully.", "transaction_id": transaction.id}, status=status.HTTP_201_CREATED)
        except DraftTransaction.DoesNotExist:
            return Response({"error": "Draft transaction not found."}, status=status.HTTP_404_NOT_FOUND)

class TransactionDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.userprofile.user_type == 'admin':
            return Transaction.objects.filter(user=user)
        return Transaction.objects.filter(user=user.userprofile.admin)

    def perform_update(self, serializer):
        with db_transaction.atomic():
            old_transaction = self.get_object()
            
            for item in old_transaction.items.all():
                if old_transaction.type == 'sale':
                    item.stock.quantity += item.quantity
                else:  # purchase
                    item.stock.quantity -= item.quantity
                item.stock.save()
            
            transaction = serializer.save()
            transaction.update_stock()

    def get_serializer(self, *args, **kwargs):
        kwargs['partial'] = True
        return super().get_serializer(*args, **kwargs)

    def perform_destroy(self, instance):
        with db_transaction.atomic():
            # Reverse the stock changes before deleting
            for item in instance.items.all():
                if instance.type == 'sale':
                    item.stock.quantity += item.quantity
                else:  # purchase
                    item.stock.quantity -= item.quantity
                item.stock.save()
            
            instance.delete()

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.userprofile

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        profile = self.get_object()
        serializer = self.get_serializer(profile)
        data = serializer.data
        
        if profile.user_type == 'admin':
            data['statistics'] = {
                'total_products': Product.objects.count(),
                'total_parties': Party.objects.filter(user=request.user).count(),
                'total_transactions': Transaction.objects.filter(user=request.user).count(),
                'total_staff': UserProfile.objects.filter(admin=request.user).count()
            }
            # Add staff list if requested
            if request.path.endswith('/me/staff/'):
                staff_serializer = UserProfileSerializer(
                    UserProfile.objects.filter(admin=request.user),
                    many=True
                )
                data['staff'] = staff_serializer.data
        else:  # staff
            data['statistics'] = {
                'transactions_created': Transaction.objects.filter(
                    user=profile.admin,
                    created_by=request.user
                ).count()
            }
        
        return Response(data)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            logout(request)
            return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            old_password = request.data.get('old_password')
            new_password = request.data.get('new_password')

            # Verify old password
            if not user.check_password(old_password):
                return Response(
                    {"error": "Old password is incorrect"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Set new password
            user.set_password(new_password)
            user.save()

            # Logout user from all sessions
            RefreshToken.for_user(user)

            return Response(
                {"message": "Password successfully changed. Please login again with your new password."}, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PartyDetailView(generics.RetrieveAPIView):
    serializer_class = PartySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        try:
            user = self.request.user
            if user.userprofile.user_type == 'admin':
                return Party.objects.filter(user=user)
            # For staff users
            return Party.objects.filter(user=user.userprofile.admin)
        except UserProfile.DoesNotExist:
            return Party.objects.none()
