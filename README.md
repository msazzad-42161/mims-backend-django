# Pharmacy Management System API

A Django REST API for managing pharmacy inventory, sales, and customer data.

## Features

- Product Management (medicines)
- Customer Management 
- Stock Management
- Transaction Management (Sales & Purchases)
- User Management (Admin & Staff roles)
- Bulk Product Import via CSV
- Payment Tracking
- Draft Transaction Management

## Models

### Product
- Medicine name
- Volume (ml) 
- Price
- Unit price
- Company
- Minimum sale quantity

### Customer
- Name
- Email
- Phone
- Address
- Associated User

### Transaction
- Type (Sale/Purchase)
- Customer
- Total Amount
- Payment Status (Pending/Partial/Completed)
- Payment In
- Due Amount
- Associated Items

### Stock
- Product
- Quantity
- Associated User

### UserProfile
- User Type (Admin/Staff)
- Associated User

### DraftTransaction
- Party
- User
- Total Amount
- Payment In
- Due Amount
- Payment Status
- Type
- Created At
- Updated At

## API Endpoints

### Authentication
- `POST /api/token/` - Obtain JWT token pair
- `POST /api/token/refresh/` - Refresh JWT token
- `POST /api/register/` - Register new user (admin/staff)

### Products
- `GET /api/products/` - List all products
- `POST /api/products/` - Create new product
- `POST /api/products/bulk/` - Bulk create products via JSON
- `POST /api/products/csv-upload/` - Bulk create products via CSV file

### Parties
- `GET /api/parties/` - List all parties (filtered by user)
- `POST /api/parties/` - Create new party

### Stock
- `GET /api/stock/` - List all stock (filtered by user)
- `POST /api/stock/` - Create new stock
- `PUT /api/stock/<id>/` - Update stock quantity

### Transactions
- `GET /api/transactions/` - List all transactions (filtered by user)
- `POST /api/transactions/` - Create new transaction
- `POST /api/transactions/<id>/complete-payment/` - Update payment for transaction

### Draft Transactions
- `GET /api/draft-transactions/` - List all draft transactions (filtered by user)
- `POST /api/draft-transactions/` - Create new draft transaction
- `POST /api/draft-transactions/<id>/execute/` - Execute draft transaction

## Request/Response Examples

### Authentication

#### Login (Obtain Token)
POST /api/token/
```
{
"username": "admin",
"password": "password123"
}
```
### Register
POST /api/register/

**Admin user:**
```
{
    "username": "admin1",
    "email": "admin1@test.com",
    "password": "Admin123!",
    "user_type": "admin"
}
```
```
{
    "username": "admin2",
    "email": "admin2@test.com",
    "password": "Admin123!",
    "user_type": "admin"
}
```
**Staff user(admin1):**
```
{
    "username": "staff1",
    "email": "staff1@test.com",
    "password": "Staff123!",
    "user_type": "staff",
    "admin_id": 1  // admin1's ID
}
```
```
{
    "username": "staff2",
    "email": "staff2@test.com",
    "password": "Staff123!",
    "user_type": "staff",
    "admin_id": 1  // admin1's ID
}
```

**Staff user(admin2):**
```
{
    "username": "staff3",
    "email": "staff3@test.com",
    "password": "Staff123!",
    "user_type": "staff",
    "admin_id": 2  // admin2's ID
}
```
```
{
    "username": "staff4",
    "email": "staff4@test.com",
    "password": "Staff123!",
    "user_type": "staff",
    "admin_id": 2  // admin2's ID
}
```

### Products

#### Create Product
POST /api/products/
```
    {
        "medicine_name": "Paracetamol",
        "ml": "500mg",
        "price": "15.00",
        "unit_price": "1.50",
        "company": "GSK",
        "min_sale": 10
    }
```

#### Create Product Bulk
POST /api/products/bulk/
```
[
    {
        "medicine_name": "Paracetamol",
        "ml": "500mg",
        "price": "15.00",
        "unit_price": "1.50",
        "company": "GSK",
        "min_sale": 10
    },
    {
        "medicine_name": "Amoxicillin",
        "ml": "250mg",
        "price": "25.00",
        "unit_price": "2.50",
        "company": "Pfizer",
        "min_sale": 5
    },
    {
        "medicine_name": "Omeprazole",
        "ml": "20mg",
        "price": "30.00",
        "unit_price": "3.00",
        "company": "AstraZeneca",
        "min_sale": 7
    },
    {
        "medicine_name": "Metformin",
        "ml": "500mg",
        "price": "20.00",
        "unit_price": "2.00",
        "company": "Novartis",
        "min_sale": 10
    },
    {
        "medicine_name": "Lisinopril",
        "ml": "10mg",
        "price": "35.00",
        "unit_price": "3.50",
        "company": "Merck",
        "min_sale": 5
    },
    {
        "medicine_name": "Ibuprofen",
        "ml": "400mg",
        "price": "18.00",
        "unit_price": "1.80",
        "company": "Cipla",
        "min_sale": 8
    },
    {
        "medicine_name": "Cetirizine",
        "ml": "10mg",
        "price": "12.00",
        "unit_price": "1.20",
        "company": "Sun Pharma",
        "min_sale": 6
    },
    {
        "medicine_name": "Azithromycin",
        "ml": "500mg",
        "price": "45.00",
        "unit_price": "4.50",
        "company": "Pfizer",
        "min_sale": 3
    },
    {
        "medicine_name": "Metronidazole",
        "ml": "400mg",
        "price": "22.00",
        "unit_price": "2.20",
        "company": "GSK",
        "min_sale": 5
    },
    {
        "medicine_name": "Amlodipine",
        "ml": "5mg",
        "price": "28.00",
        "unit_price": "2.80",
        "company": "Novartis",
        "min_sale": 7
    },
    {
        "medicine_name": "Pantoprazole",
        "ml": "40mg",
        "price": "32.00",
        "unit_price": "3.20",
        "company": "AstraZeneca",
        "min_sale": 5
    },
    {
        "medicine_name": "Ciprofloxacin",
        "ml": "500mg",
        "price": "38.00",
        "unit_price": "3.80",
        "company": "Cipla",
        "min_sale": 4
    },
    {
        "medicine_name": "Aspirin",
        "ml": "75mg",
        "price": "10.00",
        "unit_price": "1.00",
        "company": "Bayer",
        "min_sale": 10
    },
    {
        "medicine_name": "Montelukast",
        "ml": "10mg",
        "price": "42.00",
        "unit_price": "4.20",
        "company": "Merck",
        "min_sale": 5
    },
    {
        "medicine_name": "Fluconazole",
        "ml": "150mg",
        "price": "35.00",
        "unit_price": "3.50",
        "company": "Sun Pharma",
        "min_sale": 3
    }
]
```

### Stocks

#### Create/Update Stock
POST /api/stocks/
```
    {
        "product": 1,  // ID of the product
        "quantity": 100  // Initial quantity of the stock
    }
```

#### Create Transaction
POST /api/transactions/
```
{
    "party": 1,
    "items": [
        {
            "stock": 1,
            "quantity": 5
        },
        {
            "stock": 2,
            "quantity": 3
        }
    ],
    "total_amount": "150.00",
    "payment_in": "0.00",
    "due_amount": "150.00",
    "payment_status": "pending",
    "type": "sale"
}
```
