# inventory/urls.py
from django.urls import path
from .views import ProductListCreate, PartyListCreate, TransactionListCreate, CompletePayment, StockListCreate, StockUpdateView, ProductBulkCreateView, ProductCSVUploadView, DraftTransactionListCreate, ExecuteDraftTransaction, TransactionDetailView, UserProfileView, LogoutView, ChangePasswordView

urlpatterns = [
    path('products/', ProductListCreate.as_view(), name='product-list-create'),
    path('parties/', PartyListCreate.as_view(), name='party-list-create'),
    path('transactions/', TransactionListCreate.as_view(), name='transaction-list-create'),
    path('transactions/<int:transaction_id>/complete-payment/', CompletePayment.as_view(), name='complete-payment'),
    path('stock/', StockListCreate.as_view(), name='stock-list-create'),
    path('stock/<int:pk>/', StockUpdateView.as_view(), name='stock-update'),
    path('products/bulk/', ProductBulkCreateView.as_view(), name='product-bulk-create'),
    path('products/csv-upload/', ProductCSVUploadView.as_view(), name='product-csv-upload'),
    path('draft-transactions/', DraftTransactionListCreate.as_view(), name='draft-transaction-list-create'),
    path('draft-transactions/<int:draft_id>/execute/', ExecuteDraftTransaction.as_view(), name='execute-draft-transaction'),
    path('transactions/<int:pk>/', TransactionDetailView.as_view(), name='transaction-detail'),
    path('me/', UserProfileView.as_view(), name='user-profile'),
    path('me/logout/', LogoutView.as_view(), name='logout'),
    path('me/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('me/transactions/', TransactionListCreate.as_view(), name='user-transactions'),
    path('me/parties/', PartyListCreate.as_view(), name='user-parties'),
    path('me/staff/', UserProfileView.as_view(), name='admin-staff'),
]
