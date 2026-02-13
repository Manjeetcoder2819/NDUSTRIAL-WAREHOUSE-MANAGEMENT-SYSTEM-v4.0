# 🚀 IWM v4.0 - Deployment & User Guide

## ⚡ Quick Start (2 Minutes)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the application
streamlit run app.py

# 3. Open browser at http://localhost:8501
# 4. Login with: admin / admin123
```

---

## 🔐 Default Login Credentials

| Role | Username | Password | Permissions |
|------|----------|----------|-------------|
| **Admin** | `admin` | `admin123` | Full access to all features |
| **Manager** | `manager` | `manager123` | View reports, manage orders |
| **Worker** | `worker` | `worker123` | View-only access |

---

## 📊 Features Overview

### Dashboard
- **Real-time KPIs**: Employee count, inventory value, pending orders, low stock alerts
- **Advanced Analytics**:
  - 💵 **Profit Analysis**: Revenue, Cost, Profit, Margin %
  - 📈 **Inventory Turnover**: Turnover rate, Days to sell
  - 📊 **Revenue Trends**: 30-day revenue chart
  - 🏭 **Stock Forecast**: Items going low in 7 days
- **Peak Hour Alert**: Warning when capacity is near 80%

### 👥 Employees Module
- **Hire Employees**: Add new team members with salary management
- **Employee List**: View all employees with search functionality
- **Attendance Tracking**: Daily check-in/check-out with timestamps
- **Payroll Summary**: Calculate total payroll costs
- **CSV Export**: Download employee list to spreadsheet

### 📦 Inventory Module
- **Add Stock**: Add new inventory items with minimum stock levels
- **View & Filter**: 
  - Search by name or ID
  - Filter by stock status (Low/Medium/High)
  - Stock level charts
- **Adjust Stock**: Update quantities and prices
- **Inventory Value**: Calculate total inventory worth
- **CSV Export**: Download inventory to spreadsheet

### 🛒 Orders Module
- **Create Orders**: 
  - Select items and quantities
  - Automatic stock validation
  - Peak hour capacity checking
- **Order Management**:
  - Search orders by customer or ID
  - Mark as fulfilled
  - Delete orders (admin only)
- **Revenue Tracking**: Total revenue calculation
- **CSV Export**: Download order list to spreadsheet

### 🏢 Admin Panel (Admin Only)
- **Warehouse Management**: Manage multiple warehouse locations
- **User Management**: View and manage user accounts
- **System Settings**: 
  - Email configuration (SMTP)
  - Data backup/restore
  - Clear all data option
- **System Analytics**: Overview of all records

### 🔧 Sidebar Admin Tools (Admin Only)
- **Backup & Recovery**: 
  - Create backups automatically
  - View all backup files
  - Restore from any backup
- **Audit Trail**: View recent actions, download audit log

---

## 📁 Data Files Structure

```
warehouse_data.json       (Main inventory, employees, orders)
audit.json               (All system actions logged)
users.json               (User accounts & encrypted passwords)
email_config.json        (Email SMTP settings)
attendance.json          (Employee check-in/out records)
warehouses.json          (Warehouse locations)
backups/                 (Timestamped backup files)
  warehouse_data_20260208_153045.json
  warehouse_data_20260208_100230.json
  ...
```

---

## 🔄 Workflow Examples

### Example 1: New Order from Customer

```
1. Go to Orders → New Order
2. Enter Customer Name: "ABC Enterprises"
3. Select Items:
   - Widget A: 10 units
   - Gadget B: 5 units
4. Click "✅ Create Order"
5. System automatically:
   - Validates stock availability
   - Deducts from inventory
   - Creates order record
   - Logs audit trail
   - Shows confirmation
```

### Example 2: Low Stock Alert & Reorder

```
1. Dashboard → Stock Forecast Tab
2. See: "Widget A: Days until low: 2.5 days"
3. Recommendation: "Reorder 30 units"
4. Go to Inventory → Adjust Stock
5. Select Widget A, increase quantity
6. System logs the update in audit trail
```

### Example 3: Employee Attendance

```
1. Go to Employees → Attendance Tab
2. Select Employee: "Raj Kumar"
3. Click "✅ Check In" (morning)
4. Later, Click "🚪 Check Out" (evening)
5. View attendance record with timestamps
6. Admin can see daily attendance report
```

### Example 4: Data Backup & Recovery

```
1. Go to Sidebar → Admin Tools → Backup & Recovery
2. Click "🔄 Create Backup"
3. System creates: warehouse_data_20260208_153045.json
4. If data gets corrupted:
   - Click "📋 View Backups"
   - Select backup file
   - Click "Restore Selected Backup"
   - Confirm recovery
```

---

## 🛡️ Security Features

### Authentication
- Username/password login
- SHA256 password hashing
- Session-based access control
- Automatic logout on window close

### Role-Based Access Control
```
Admin:   Can CREATE, UPDATE, DELETE, VIEW REPORTS
Manager: Can READ, CREATE, UPDATE, VIEW REPORTS
Worker:  READ-ONLY access (view all data)
```

### Audit Trail
- Every action logged: CREATE, UPDATE, DELETE
- Timestamp for each action
- User who performed action recorded
- Exportable for compliance

### Data Safety
- Automatic backups in `backups/` folder
- Safety backup created before restore
- JSON format allows easy recovery
- No data loss on app crash

---

## ⚙️ Configuration Guide

### Email Alerts Setup

1. **Go to Admin Panel → System Settings → Email Configuration**
2. **Enable Email Alerts**: Check the box
3. **Configure SMTP**:
   - **Gmail**: 
     - SMTP Server: `smtp.gmail.com`
     - Port: `587`
     - Email: Your Gmail address
     - Password: Your Gmail app password
   - **Office365**:
     - SMTP Server: `smtp.office365.com`
     - Port: `587`
     - Email: Your Office365 email
     - Password: Your Office365 password
4. **Click "💾 Save Email Config"**

### Warehouse Setup

1. **Go to Admin Panel → Warehouses**
2. **Click "Add Warehouse"** in the form
3. **Fill in**:
   - Warehouse Name
   - Location/City
   - Full Address
   - Contact Phone
   - Storage Capacity (units)
4. **Click "Add Warehouse"**
5. System stores in `warehouses.json`

---

## 📈 Reports & Analytics

### Available Reports

1. **Profit Analysis** (Dashboard → Profit Analysis)
   - Total Revenue
   - Estimated Cost
   - Profit Amount
   - Profit Margin %

2. **Inventory Turnover** (Dashboard → Inventory Turnover)
   - Total Sold Units
   - Average Inventory
   - Turnover Rate
   - Days to Sell

3. **Revenue Trends** (Dashboard → Revenue Trends)
   - 30-day revenue chart
   - Daily breakdown
   - Total & Average

4. **Top Selling Items** (Reports Page)
   - Item with highest order frequency
   - Stock out patterns

5. **Audit Trail** (Admin Panel → System Analytics)
   - All actions taken
   - User who performed action
   - Exact timestamp
   - Exportable to CSV

---

## 🔧 Troubleshooting

### Problem: Application won't start
```bash
# Check Python version (3.7+)
python --version

# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Run with verbose mode
streamlit run app.py --logger.level=debug
```

### Problem: JSON file corruption
```bash
# Restore from backup
1. Go to Sidebar → Admin Tools → Backup & Recovery
2. Select backup file
3. Click "Restore Selected Backup"

# Or manually restore
cp backups/warehouse_data_[latest].json warehouse_data.json
```

### Problem: Login fails
```bash
# Check users.json exists
# Edit users.json to reset credentials
# Default admin password: admin123
```

### Problem: Audit logs not appearing
```bash
# Check audit.json was created
# If missing, admin can create fresh logs
# System will auto-create on next action
```

---

## 🚀 Deployment Options

### Option 1: Local Development
```bash
streamlit run app.py
# Accessible at: http://localhost:8501
```

### Option 2: Cloud Deployment (Streamlit Cloud)
```bash
# 1. Push code to GitHub
git push origin main

# 2. Go to share.streamlit.io
# 3. Connect GitHub repo
# 4. Deploy main branch
# 5. Get public URL
```

### Option 3: VPS/Server Deployment
```bash
# On your server:
pip install -r requirements.txt
streamlit run app.py --server.port 8080 --server.address 0.0.0.0

# Access at: http://your_server_ip:8080
```

### Option 4: Docker Container
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

```bash
docker build -t iwm-warehouse .
docker run -p 8501:8501 iwm-warehouse
```

---

## 📊 Data Backup Strategy

### Automatic Backups
- Create backup before every major operation
- Admin panel → "Create Backup Now"
- Stored with timestamp: `warehouse_data_YYYYMMDD_HHMMSS.json`

### Manual Backups
```bash
# Copy main file
cp warehouse_data.json warehouse_data_backup_$(date +%s).json

# Compress for cloud storage
tar -czf warehouse_backup_$(date +%Y%m%d).tar.gz warehouse_data.json audit.json
```

### Cloud Backup (Optional)
```bash
# AWS S3
aws s3 cp warehouse_data.json s3://your-bucket/backups/

# Google Drive
# Manual upload of backup files

# Dropbox
# Use rclone: rclone copy warehouse_data.json dropbox:backups/
```

---

## 📱 Mobile App Integration (Future)

When ready to build mobile apps:

```bash
# Install FastAPI
pip install fastapi uvicorn

# Create api.py
# Expose REST endpoints:
# GET /api/inventory
# POST /api/orders
# GET /api/employees
# etc.

# Run API server
uvicorn api:app --host 0.0.0.0 --port 8000

# Connect mobile app to: http://server_ip:8000/api/
```

---

## 🎯 Best Practices

### Daily Operations
1. ✅ Check dashboard KPIs every morning
2. ✅ Review low stock alerts
3. ✅ Process pending orders
4. ✅ Update attendance for employees
5. ✅ Monitor peak hour capacity

### Weekly Operations
1. ✅ Review revenue trends
2. ✅ Check top selling items
3. ✅ Forecast low stock for next 7 days
4. ✅ Verify employee attendance
5. ✅ Create weekly backup

### Monthly Operations
1. ✅ Generate profitability report
2. ✅ Calculate inventory turnover
3. ✅ Review audit trail for compliance
4. ✅ Analyze customer patterns
5. ✅ Archive old backup files

### Security
- ✅ Change default passwords immediately
- ✅ Don't share login credentials
- ✅ Review audit trail monthly
- ✅ Keep backups in safe location
- ✅ Update data regularly

---

## 📞 Support

**For Issues:**
1. Check FEATURES_IMPLEMENTED.md
2. Review audit.json for error patterns
3. Check backups/ folder for recovery options
4. Reinstall dependencies: `pip install -r requirements.txt`

**Documentation Files:**
- [CODE_ANALYSIS.md](CODE_ANALYSIS.md) - Code structure and improvements
- [FEATURES_IMPLEMENTED.md](FEATURES_IMPLEMENTED.md) - Complete feature list
- [README.md](README.md) - Project overview

---

## 📋 Checklist Before Production

- [ ] Change all default passwords
- [ ] Configure email SMTP if using alerts
- [ ] Set up backup strategy
- [ ] Create admin account
- [ ] Test with sample data
- [ ] Review audit trail settings
- [ ] Set up multi-warehouse if needed
- [ ] Document custom workflows
- [ ] Train users on features
- [ ] Deploy to production

---

**Version:** 4.0 (JSON-based with 15 features)
**Last Updated:** February 8, 2026
**Status:** 🟢 Production Ready
