# BillO - Instant Billing System
*A complete retail management solution with Telegram bot interface*


## ✨ Features

### 💰 Billing System
- Create and manage customer bills
- Add multiple items with quantities
- Apply discounts
- Generate printable receipts
- Bill history tracking

### 📦 Inventory Management
- Real-time stock tracking
- Low stock alerts
- Bulk stock updates
- Product categorization
- Barcode scanning support

### 👥 Customer Management
- Customer database
- Purchase history
- Loyalty tracking
- Contact management

### 📊 Reporting
- Sales reports
- Inventory reports
- Customer spending analytics
- Export to Excel/PDF

## 🛠 Technology Stack

- Python 3.7+
- pyTelegramBotAPI (async version)
- MySQL 8.0

## Project Structure
```
BillO - Instant Billing/
├── .env                      # Environment variables (SECURE)
├── .gitignore
├── requirements.txt
├── README.md

├── config/                   # Configuration management
│   ├── __init__.py
│   ├── settings.py           # Loads .env and provides config
│   └── constants.py          # Business constants

├── database/                 # Database layer
│   ├── __init__.py
│   ├── connection.py         # DB connection handler
│   ├── operations.py         # CRUD operations
│   ├── backup.py             # Automated backups
│   └── models.py             # DB table schemas

├── bot/                      # Core bot logic
│   ├── __init__.py
│   ├── main.py               # Bot entry point
│   ├── keyboards.py          # All menu layouts
│   └── handlers/             # Feature-wise bot handlers
│       ├── __init__.py
│       ├── billing.py
│       ├── inventory.py
│       └── customer.py

├── utils/                    # Utility functions
│   ├── __init__.py
│   ├── helpers.py            # FormatNum, etc.
│   ├── logger.py             # Logging config
│   └── validators.py         # Input validation

├── data/                     # Static & runtime data
│   └── products.xlsx         # Sample product catalog
```


## 🚀 Setup Guide

### Prerequisites
1. Python 3.7 or later
2. MySQL Server 8.0+
3. Telegram Bot Token from [@BotFather](https://t.me/BotFather)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/HelloYug/billo-instant-billing.git
   cd billo-instant-billing
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file with your credentials.

## ⚙ Configuration

### Essential Settings (`.env`)
Intialise `.env` with your data


## 🗃 Database Setup

1. Create MySQL database and tables:
   ```bash
   python -m database.models
   ```
2. Setup your products in data/products.xlsx

3. Import initial products:
   ```bash
   python -m utils.import_products data/products.xlsx
   ```

## 🤖 Running the Bot

```bash
python -m bot.main
```

## 🎮 Usage Guide

### Main Menu

- 💰 **Generate Bill** - Create new customer bill
- 📦 **Inventory**   - Manage product stock
- 👥 **Customers**   - View customer details
- 📊 **Reports**     - Generate sales reports
- ⚙️ **Settings**    - Configure system

### Bill Creation Flow
1. Select "Generate Bill"
2. Enter customer name
3. Enter phone number (optional)
4. Add products:
   - Select category
   - Choose product
   - Enter quantity
5. Apply discount (if any)
6. Confirm and save bill

### Inventory Management
- Add stock: `📥 Add Stock > Select Product > Enter Quantity`
- Remove stock: `📤 Remove Stock > Select Product > Enter Quantity`
- View low stock: `🔍 View Stock`

## 🎨 Customization

### Business Branding
1. Edit `config/constants.py` for custom messages:
   ```python
   class Messages:
       WELCOME = "Welcome to {COMPANY_NAME} Retail System!"
       # ... other messages
   ```

2. Update references in `bot/keyboards.py`

### Product Categories
Modify the category structure in:
```python
# database/models.py
DEFAULT_CATEGORIES = [
    "Groceries",
    "Electronics",
    "Clothing",
    # Add more categories
]
```

## 🐛 Troubleshooting

### Common Issues
1. **Bot not responding**:
   - Verify bot token in `.env`

2. **Database connection errors**:
   - Confirm MySQL service is running
   - Verify credentials in `.env`
   - Check firewall settings


## 🔮 Future Enhancements

- 🧾 PDF invoice generation
- 📥 Telegram file exports (Excel/PDF)
- 💳 Payment gateway integration
- 👥 Multi-user access controls


## 👨‍💻 Author

**Yug Agarwal**
- 📧 [yugagarwal704@gmail.com](mailto:yugagarwal704@gmail.com)
- 🔗 GitHub – [@HelloYug](https://github.com/HelloYug)
