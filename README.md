# Pharmacy Management System API

A Django REST API for managing pharmacy inventory, sales, and customer data.

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

## Features

- Product Management (medicines)
- Customer Management 
- Stock Management
- Transaction Management (Sales & Purchases)
- User Management (Admin & Staff roles)
- Bulk Product Import via CSV
- Payment Tracking
- Draft Transaction Management
- User Profile Management with Statistics
- Session Management
- Password Reset Functionality

## API Endpoints

### Authentication
- `POST /api/token/` - Obtain JWT token pair
- `POST /api/token/refresh/` - Refresh JWT token
- `POST /api/register/` - Register new user (admin/staff)
- `POST /api/me/logout/` - Logout user
- `POST /api/me/change-password/` - Change password

### User Profile
- `GET /api/me/` - Get current user profile with statistics
- `PUT /api/me/` - Update user profile
- `GET /api/me/staff/` - Get admin's staff list (admin only)
- `GET /api/me/transactions/` - List user's transactions
- `GET /api/me/parties/` - List user's parties

### Products
- `GET /api/products/` - List all products
- `POST /api/products/` - Create new product
- `POST /api/products/bulk/` - Bulk create products via JSON
- `POST /api/products/csv-upload/` - Bulk create products via CSV file

### Parties
- `GET /api/parties/` - List all parties (filtered by user)
- `POST /api/parties/` - Create new party
- `GET /api/me/parties/` - List user's parties

### Stock
- `GET /api/stock/` - List all stock (filtered by user)
- `POST /api/stock/` - Create new stock
- `PUT /api/stock/<id>/` - Update stock quantity

### Transactions
- `GET /api/transactions/` - List all transactions (filtered by user)
- `POST /api/transactions/` - Create new transaction
- `GET /api/transactions/<id>/` - Get specific transaction
- `PUT /api/transactions/<id>/` - Update transaction
- `DELETE /api/transactions/<id>/` - Delete transaction
- `POST /api/transactions/<id>/complete-payment/` - Update payment for transaction
- `GET /api/me/transactions/` - List user's transactions

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

### User Profile

#### Get Profile
GET /api/me/
```json
Response:
{
    "username": "admin1",
    "email": "admin1@test.com",
    "user_type": "admin",
    "is_premium": true,
    "statistics": {
        "total_products": 15,
        "total_parties": 5,
        "total_transactions": 25,
        "total_staff": 2
    }
}
```

#### Change Password
POST /api/me/change-password/
```json
{
    "old_password": "current-password",
    "new_password": "new-password"
}
```

#### Logout
POST /api/me/logout/
```json
{
    "refresh_token": "your-refresh-token"
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

### Update Transaction
PUT /api/transactions/1/
```json
{
    "payment_in": 150.00,
    "items": [
        {
            "stock": 1,
            "quantity": 3
        }
    ]
}
```

## Error Handling

The API returns appropriate HTTP status codes:

- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Server Error

Error responses include a message explaining the error:
```json
{
    "error": "Detailed error message"
}
```

## Installation and Setup

1. Clone the repository
2. Create a virtual environment
3. Install dependencies: `pip install -r requirements.txt`
4. Run migrations: `python manage.py migrate`
5. Create superuser: `python manage.py createsuperuser`
6. Run server: `python manage.py runserver`

## Environment Variables

Create a `.env` file with:
```
SECRET_KEY=your_secret_key
DEBUG=True
DATABASE_URL=your_database_url
```

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

### User Profile

#### Get Profile
GET /api/me/
```json
Response:
{
    "username": "admin1",
    "email": "admin1@test.com",
    "user_type": "admin",
    "is_premium": true,
    "statistics": {
        "total_products": 15,
        "total_parties": 5,
        "total_transactions": 25,
        "total_staff": 2
    }
}
```

#### Change Password
POST /api/me/change-password/
```json
{
    "old_password": "current-password",
    "new_password": "new-password"
}
```

#### Logout
POST /api/me/logout/
```json
{
    "refresh_token": "your-refresh-token"
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
        "id": 1,
        "name": "City Hospital",
        "email": "contact@cityhospital.com",
        "phone": "555-444-5555",
        "address": "123 Health St",
        "associated_user": null,
        "user": 2,
        "balance": 900  // Positive balance means party owes money
    },
    {
        "id": 2,
        "name": "Pharma Solutions",
        "email": "info@pharmasolutions.com",
        "phone": "555-888-9999",
        "address": "456 Care St",
        "associated_user": null,
        "user": 2,
        "balance": -200  // Negative balance means we owe money
    }
]
```

#### Get Single Party Details
GET /api/me/parties/<id>/
```json
Response:
{
    "id": 1,
    "name": "City Hospital",
    "email": "contact@cityhospital.com",
    "phone": "555-444-5555",
    "address": "123 Health St",
    "associated_user": null,
    "user": 2,
    "balance": 900
}
```

Note: Balance calculation is based on all transactions with the party:
- For sales: balance += (total_amount - payment_in)
- For purchases: balance -= (total_amount - payment_in)