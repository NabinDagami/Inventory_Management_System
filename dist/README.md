# 📦 Inventory Pro - Professional Inventory Management System

A modern, feature-rich inventory management application built with Python and CustomTkinter, designed for Windows desktop environments.

## ✨ Features

### 🏠 Dashboard
- **KPI Cards**: Real-time metrics for sales, products, low stock, and customers
- **Interactive Charts**: Sales trends, product categories, and monthly comparisons
- **Quick Actions**: Fast access to common tasks
- **Recent Activity**: Live feed of system activities

### 📦 Inventory Management
- **Product Management**: Add, edit, and organize products
- **Categories & Brands**: Hierarchical organization
- **Stock Tracking**: Real-time inventory levels
- **Low Stock Alerts**: Automated reorder notifications
- **Barcode Support**: Product identification

### 💰 Sales Management
- **Dynamic Pricing**: Normal and Workshop customer rates
- **Payment Methods**: Cash and credit transactions
- **Invoice Generation**: Professional PDF invoices
- **Customer Selection**: Integrated customer database
- **Sales History**: Complete transaction records

### 🛒 Purchase Management
- **Purchase Orders**: Create and manage POs
- **Supplier Integration**: Linked supplier database
- **Goods Receipt**: Stock level updates
- **Payment Tracking**: Cash and credit purchases
- **Purchase History**: Complete procurement records

### 👥 Customer Management
- **Customer Types**: Normal and Workshop classifications
- **Contact Information**: Complete customer profiles
- **Credit Limits**: Account management
- **Balance Tracking**: Outstanding amounts
- **Search & Filter**: Advanced customer lookup

### 🏭 Supplier Management
- **Supplier Profiles**: Complete vendor information
- **Contact Management**: Multiple contact methods
- **Payment Terms**: Flexible payment arrangements
- **Purchase History**: Vendor transaction records
- **Performance Tracking**: Supplier analytics

### 📊 Reports & Analytics
- **Sales Reports**: Comprehensive sales analysis
- **Purchase Reports**: Procurement analytics
- **Profit Analysis**: Financial performance metrics
- **Stock Reports**: Inventory level summaries
- **PDF Export**: Professional report generation
- **Excel Export**: Data analysis capabilities

## 🎨 User Interface

### Modern Design
- **Dark/Light Mode**: Adaptive theme system
- **Professional Layout**: Clean, intuitive interface
- **Responsive Design**: Optimized for various screen sizes
- **Sidebar Navigation**: Easy module switching
- **Modal Dialogs**: Streamlined data entry

### Performance Optimized
- **SQLite Database**: Efficient local storage
- **Caching System**: Fast data retrieval
- **Memory Management**: Optimized resource usage
- **Smooth Animations**: Fluid user interactions

## 🔧 Technical Specifications

### Requirements
- **Operating System**: Windows 10/11
- **Python**: 3.8+ (for development)
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 100MB application + database space
- **Display**: 1200x800 minimum resolution

### Dependencies
```
customtkinter >= 5.2.0    # Modern UI framework
matplotlib >= 3.7.0       # Charts and graphs
reportlab >= 4.0.0        # PDF generation
openpyxl >= 3.1.0         # Excel file handling
python-dateutil >= 2.8.0  # Date utilities
tkcalendar >= 1.6.0       # Date picker widgets
Pillow >= 9.5.0           # Image processing
```

## 🚀 Installation

### Option 1: Pre-built Executable (Recommended)
1. Download the latest release
2. Run `install.bat` as administrator
3. Launch from desktop shortcut or Start menu

### Option 2: From Source
1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd "Inventory Management"
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Application**
   ```bash
   python main.py
   ```

## 🔨 Building from Source

### Create Executable
```bash
# Activate virtual environment
venv\Scripts\activate

# Run build script
python build.py
```

This creates:
- `dist/InventoryPro.exe` - Main executable
- `dist/install.bat` - Installation script
- `dist/assets/` - Application resources

## 📁 Project Structure

```
Inventory Management/
├── main.py                 # Application entry point
├── build.py               # Build script for executable
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── create_icon.py        # Icon generation script
├── assets/               # Application assets
│   ├── logo.svg         # SVG logo
│   └── icons/           # Icon files
├── src/                 # Source code
│   ├── main_app.py      # Main application class
│   ├── models/          # Data models
│   │   └── database.py  # Database management
│   ├── views/           # UI views
│   │   ├── dashboard.py # Dashboard view
│   │   ├── inventory.py # Inventory management
│   │   ├── sales.py     # Sales management
│   │   ├── purchases.py # Purchase management
│   │   ├── customers.py # Customer management
│   │   ├── suppliers.py # Supplier management
│   │   └── reports.py   # Reports and analytics
│   └── utils/           # Utility modules
├── data/                # Database files
└── reports/             # Generated reports
```

## 💾 Database Schema

### Core Tables
- **products**: Product catalog with pricing and stock
- **categories**: Product categorization
- **brands**: Brand management
- **customers**: Customer profiles and balances
- **suppliers**: Supplier information
- **sales**: Sales transactions
- **purchases**: Purchase transactions
- **stock_movements**: Inventory tracking

### Key Features
- **Foreign Key Relationships**: Data integrity
- **Indexes**: Performance optimization
- **Triggers**: Automated stock updates
- **Views**: Complex query simplification

## 🔐 Security Features

- **Data Validation**: Input sanitization
- **SQL Injection Prevention**: Parameterized queries
- **Backup Support**: Database export/import
- **User Authentication**: Optional login system
- **Audit Trail**: Transaction logging

## 🎯 Usage Guide

### Getting Started
1. **First Launch**: Application creates database automatically
2. **Setup Categories**: Organize your products
3. **Add Suppliers**: Set up vendor relationships
4. **Create Products**: Build your inventory catalog
5. **Add Customers**: Set up customer base
6. **Start Selling**: Process your first sale

### Daily Operations
1. **Check Dashboard**: Monitor KPIs and alerts
2. **Process Sales**: Handle customer transactions
3. **Receive Goods**: Update stock from purchases
4. **Monitor Stock**: Address low stock alerts
5. **Generate Reports**: Analyze performance

## 📈 Performance Tips

- **Regular Backups**: Export database periodically
- **Database Cleanup**: Archive old transactions
- **Index Maintenance**: Keep database optimized
- **Memory Management**: Close unused views
- **Update Regularly**: Install application updates

## 🐛 Troubleshooting

### Common Issues

**Application Won't Start**
- Check system requirements
- Verify Python installation (development mode)
- Review error logs

**Database Errors**
- Ensure write permissions
- Check disk space
- Verify database integrity

**Performance Issues**
- Monitor memory usage
- Check hard drive space
- Close unnecessary applications

**UI Display Issues**
- Update graphics drivers
- Check display scaling settings
- Verify minimum resolution

## 🤝 Support

### Documentation
- User manual included in installation
- Video tutorials available
- FAQ section covers common questions

### Technical Support
- GitHub Issues for bug reports
- Community forum for discussions
- Email support for critical issues

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **CustomTkinter**: Modern UI framework
- **Matplotlib**: Data visualization
- **ReportLab**: PDF generation
- **SQLite**: Reliable database engine

## 📊 Version History

### v1.0.0 (Current)
- Initial release
- Complete inventory management
- Sales and purchase tracking
- Customer and supplier management
- Dashboard with analytics
- PDF report generation
- Dark/light theme support

---

**Inventory Pro** - Professional inventory management made simple. 📦✨
