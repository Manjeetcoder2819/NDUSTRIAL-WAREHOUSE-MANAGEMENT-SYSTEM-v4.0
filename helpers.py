"""
HELPER UTILITIES - Validation, business logic for v4.0
JSON-based inventory system with peak hour management
Features: Backup, Logging, Search, CSV Export, Error Handling, Authentication, Analytics
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json
import csv
import os
import shutil
import hashlib
from pathlib import Path

class PeakHourManager:
    """Handles 300% order spikes during 2-5PM (14:00-17:00)"""
    
    def __init__(self):
        # Peak hour capacity limits by hour
        self.hourly_limits = {
            14: 50,   # 2-3 PM: 50 units
            15: 75,   # 3-4 PM: 75 units (peak)
            16: 100,  # 4-5 PM: 100 units (peak peak)
            17: 80    # 5-6 PM: 80 units
        }
    
    def get_current_capacity(self) -> int:
        """Returns hourly capacity limit based on current time"""
        hour = datetime.now().hour
        return self.hourly_limits.get(hour, 30)  # Default 30 units outside peak hours
    
    def is_peak_hour(self) -> bool:
        """Check if current time is in peak hours"""
        hour = datetime.now().hour
        return hour in self.hourly_limits
    
    def get_peak_hour_warning(self, current_orders: List[Dict]) -> Tuple[bool, str]:
        """
        Returns (is_near_capacity, warning_message)
        """
        hour = datetime.now().hour
        if hour not in self.hourly_limits:
            return False, ""
        
        capacity = self.hourly_limits[hour]
        total_ordered = sum(o.get('total_qty', 0) for o in current_orders 
                           if o.get('created_date', '').startswith(datetime.now().strftime("%Y-%m-%d")))
        
        if total_ordered >= capacity * 0.8:  # 80% capacity
            return True, f"⏰ PEAK HOUR ALERT: {total_ordered}/{capacity} capacity used ({int(total_ordered/capacity*100)}%)"
        
        return False, ""


def validate_inventory_movement(inventory: List[Dict], item_id: int, qty: int, 
                               direction: str = 'OUT') -> Dict:
    """
    Validates inventory movement before deduction
    
    Returns:
        {
            'valid': bool,
            'error': str or None,
            'new_qty': int or None,
            'item': dict or None
        }
    """
    # Find item
    item = next((i for i in inventory if i['id'] == item_id), None)
    
    if not item:
        return {
            'valid': False,
            'error': '❌ Item not found',
            'new_qty': None,
            'item': None
        }
    
    # Validate quantity
    if qty <= 0:
        return {
            'valid': False,
            'error': '❌ Quantity must be > 0',
            'new_qty': None,
            'item': item
        }
    
    if direction == 'OUT':
        if item['quantity'] < qty:
            return {
                'valid': False,
                'error': f"❌ Insufficient stock: {item['quantity']} available, {qty} requested",
                'new_qty': None,
                'item': item
            }
        
        new_qty = item['quantity'] - qty
        
        # Check low stock warning
        if new_qty < item.get('min_stock', 10):
            return {
                'valid': True,
                'error': f"⚠️ WARNING: Stock will drop below minimum ({item.get('min_stock', 10)})",
                'new_qty': new_qty,
                'item': item
            }
    
    elif direction == 'IN':
        new_qty = item['quantity'] + qty
    else:
        return {
            'valid': False,
            'error': '❌ Invalid direction (use IN or OUT)',
            'new_qty': None,
            'item': item
        }
    
    return {
        'valid': True,
        'error': None,
        'new_qty': new_qty,
        'item': item
    }


def calculate_inventory_metrics(inventory: List[Dict]) -> Dict:
    """Calculate key inventory metrics"""
    if not inventory:
        return {
            'total_items': 0,
            'total_value': 0.0,
            'low_stock_count': 0,
            'avg_stock_value': 0.0
        }
    
    total_value = sum(item['quantity'] * item['price'] for item in inventory)
    low_stock = len([i for i in inventory if i['quantity'] < i.get('min_stock', 10)])
    
    return {
        'total_items': len(inventory),
        'total_value': total_value,
        'low_stock_count': low_stock,
        'avg_stock_value': total_value / len(inventory) if inventory else 0
    }


def validate_employee_data(name: str, age: int, position: str, salary: float) -> Tuple[bool, str]:
    """Validate employee form input"""
    if not name or not name.strip():
        return False, "❌ Name is required"
    
    if age < 18 or age > 70:
        return False, "❌ Age must be between 18 and 70"
    
    valid_positions = ["Worker", "Supervisor", "Manager", "Engineer"]
    if position not in valid_positions:
        return False, f"❌ Position must be one of: {', '.join(valid_positions)}"
    
    if salary < 0 or salary > 500000:
        return False, "❌ Salary must be between 0 and 500,000"
    
    return True, "✅ Valid"


def validate_inventory_item(name: str, quantity: int, price: float, min_stock: int) -> Tuple[bool, str]:
    """Validate inventory item form input"""
    if not name or not name.strip():
        return False, "❌ Item name is required"
    
    if quantity < 0:
        return False, "❌ Quantity cannot be negative"
    
    if price <= 0:
        return False, "❌ Price must be greater than 0"
    
    if min_stock < 0:
        return False, "❌ Minimum stock cannot be negative"
    
    return True, "✅ Valid"


# Initialize manager
peak_manager = PeakHourManager()


# =============================================================================
# FEATURE 1: DATA BACKUP SYSTEM
# =============================================================================
class BackupManager:
    """Handles automatic data backups with timestamped files"""
    
    def __init__(self, backup_dir="backups"):
        self.backup_dir = backup_dir
        Path(self.backup_dir).mkdir(exist_ok=True)
    
    def create_backup(self, data: Dict, filename="warehouse_data.json") -> str:
        """Create timestamped backup of data"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"{self.backup_dir}/{filename.split('.')[0]}_{timestamp}.json"
            
            with open(backup_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            return backup_file
        except Exception as e:
            return f"❌ Backup failed: {str(e)}"
    
    def list_backups(self) -> List[Dict]:
        """List all available backups"""
        try:
            backups = []
            for file in sorted(os.listdir(self.backup_dir), reverse=True):
                if file.endswith('.json'):
                    filepath = os.path.join(self.backup_dir, file)
                    mtime = os.path.getmtime(filepath)
                    backups.append({
                        'filename': file,
                        'path': filepath,
                        'timestamp': datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S"),
                        'size_kb': os.path.getsize(filepath) / 1024
                    })
            return backups
        except Exception as e:
            return []
    
    def restore_backup(self, backup_file: str, target_file="warehouse_data.json") -> Tuple[bool, str]:
        """Restore data from backup file"""
        try:
            if not os.path.exists(backup_file):
                return False, "❌ Backup file not found"
            
            with open(backup_file, 'r') as f:
                data = json.load(f)
            
            # Create safety backup of current file
            if os.path.exists(target_file):
                shutil.copy(target_file, f"{target_file}.safety_backup")
            
            with open(target_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True, f"✅ Restored from {os.path.basename(backup_file)}"
        except json.JSONDecodeError:
            return False, "❌ Backup file is corrupted"
        except Exception as e:
            return False, f"❌ Restore failed: {str(e)}"


# =============================================================================
# FEATURE 2: LOGGING SYSTEM (Audit Trail)
# =============================================================================
class AuditLogger:
    """Tracks all CRUD operations with timestamps"""
    
    def __init__(self, log_file="audit.json"):
        self.log_file = log_file
        self._initialize_log()
    
    def _initialize_log(self):
        """Create audit log file if it doesn't exist"""
        try:
            if not os.path.exists(self.log_file):
                with open(self.log_file, 'w') as f:
                    json.dump([], f)
        except Exception as e:
            print(f"Error initializing log: {e}")
    
    def log_action(self, action: str, module: str, record_id: int, 
                   user: str = "System", details: str = "") -> bool:
        """Log a CRUD operation"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'action': action,  # CREATE, READ, UPDATE, DELETE
                'module': module,   # employees, inventory, orders, shipments
                'record_id': record_id,
                'user': user,
                'details': details
            }
            
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
            
            logs.append(log_entry)
            
            with open(self.log_file, 'w') as f:
                json.dump(logs, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Logging error: {e}")
            return False
    
    def get_audit_trail(self, module: str = None, action: str = None) -> List[Dict]:
        """Retrieve audit logs with optional filtering"""
        try:
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
            
            filtered = logs
            if module:
                filtered = [l for l in filtered if l['module'] == module]
            if action:
                filtered = [l for l in filtered if l['action'] == action]
            
            return sorted(filtered, key=lambda x: x['timestamp'], reverse=True)
        except Exception as e:
            return []
    
    def export_audit_csv(self, filename="audit_report.csv") -> Tuple[bool, str]:
        """Export audit logs to CSV"""
        try:
            logs = self.get_audit_trail()
            if not logs:
                return False, "No logs to export"
            
            with open(filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=logs[0].keys())
                writer.writeheader()
                writer.writerows(logs)
            
            return True, f"✅ Exported to {filename}"
        except Exception as e:
            return False, f"❌ Export failed: {str(e)}"


# =============================================================================
# FEATURE 3: SEARCH & FILTER
# =============================================================================
def search_employees(employees: List[Dict], query: str) -> List[Dict]:
    """Search employees by name, position, or ID"""
    query = query.lower()
    return [
        emp for emp in employees
        if query in str(emp.get('name', '')).lower() or
           query in str(emp.get('position', '')).lower() or
           query in str(emp.get('id', ''))
    ]


def search_inventory(inventory: List[Dict], query: str) -> List[Dict]:
    """Search inventory by name or ID"""
    query = query.lower()
    return [
        item for item in inventory
        if query in str(item.get('name', '')).lower() or
           query in str(item.get('id', ''))
    ]


def search_orders(orders: List[Dict], query: str) -> List[Dict]:
    """Search orders by customer name or order ID"""
    query = query.lower()
    return [
        order for order in orders
        if query in str(order.get('customer', '')).lower() or
           query in str(order.get('id', ''))
    ]


def filter_inventory_by_price(inventory: List[Dict], min_price: float = 0, 
                              max_price: float = float('inf')) -> List[Dict]:
    """Filter inventory by price range"""
    return [
        item for item in inventory
        if min_price <= item.get('price', 0) <= max_price
    ]


def filter_inventory_by_stock_status(inventory: List[Dict], 
                                     status: str = "low") -> List[Dict]:
    """Filter inventory by stock status (low, medium, high)"""
    if status == "low":
        return [i for i in inventory if i.get('quantity', 0) < i.get('min_stock', 10)]
    elif status == "medium":
        return [i for i in inventory 
                if i.get('min_stock', 10) <= i.get('quantity', 0) < i.get('min_stock', 10) * 2]
    elif status == "high":
        return [i for i in inventory if i.get('quantity', 0) >= i.get('min_stock', 10) * 2]
    return inventory


# =============================================================================
# FEATURE 4: CSV EXPORT
# =============================================================================
def export_to_csv(data: List[Dict], filename: str) -> Tuple[bool, str]:
    """Export any data list to CSV"""
    try:
        if not data:
            return False, "No data to export"
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        
        return True, f"✅ Exported to {filename}"
    except Exception as e:
        return False, f"❌ Export failed: {str(e)}"


# =============================================================================
# FEATURE 5: AUTHENTICATION SYSTEM
# =============================================================================
class AuthManager:
    """Handles user authentication with roles"""
    
    ROLES = {
        'admin': ['read', 'create', 'update', 'delete', 'view_reports'],
        'manager': ['read', 'create', 'update', 'view_reports'],
        'worker': ['read']
    }
    
    def __init__(self, users_file="users.json"):
        self.users_file = users_file
        self._initialize_users()
    
    def _initialize_users(self):
        """Create default users if file doesn't exist"""
        try:
            if not os.path.exists(self.users_file):
                default_users = [
                    {
                        'username': 'admin',
                        'password': self._hash_password('admin123'),
                        'role': 'admin',
                        'name': 'Admin User'
                    },
                    {
                        'username': 'manager',
                        'password': self._hash_password('manager123'),
                        'role': 'manager',
                        'name': 'Manager User'
                    },
                    {
                        'username': 'worker',
                        'password': self._hash_password('worker123'),
                        'role': 'worker',
                        'name': 'Worker User'
                    }
                ]
                with open(self.users_file, 'w') as f:
                    json.dump(default_users, f, indent=2)
        except Exception as e:
            print(f"Error initializing users: {e}")
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate(self, username: str, password: str) -> Tuple[bool, str, str]:
        """Authenticate user, returns (success, message, role)"""
        try:
            with open(self.users_file, 'r') as f:
                users = json.load(f)
            
            user = next((u for u in users if u['username'] == username), None)
            if not user:
                return False, "❌ User not found", ""
            
            if user['password'] == self._hash_password(password):
                return True, f"✅ Welcome {user['name']}", user['role']
            else:
                return False, "❌ Incorrect password", ""
        except Exception as e:
            return False, f"❌ Auth error: {str(e)}", ""
    
    def has_permission(self, role: str, action: str) -> bool:
        """Check if role has permission for action"""
        return action in self.ROLES.get(role, [])
    
    def register_user(self, username: str, password: str, role: str, 
                     fullname: str) -> Tuple[bool, str]:
        """Register a new user, returns (success, message)"""
        try:
            with open(self.users_file, 'r') as f:
                users = json.load(f)
            
            # Check if user already exists
            existing = next((u for u in users if u['username'] == username), None)
            if existing:
                return False, f"❌ Username '{username}' already exists"
            
            # Validate role
            if role not in self.ROLES:
                return False, f"❌ Invalid role. Must be one of: {', '.join(self.ROLES.keys())}"
            
            # Create new user
            new_user = {
                'username': username,
                'password': self._hash_password(password),
                'role': role,
                'name': fullname,
                'created_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            users.append(new_user)
            
            with open(self.users_file, 'w') as f:
                json.dump(users, f, indent=2)
            
            return True, f"✅ User '{username}' registered successfully as {role.upper()}"
        except Exception as e:
            return False, f"❌ Registration failed: {str(e)}"
    
    def get_all_users(self) -> List[Dict]:
        """Get all user accounts (without passwords)"""
        try:
            with open(self.users_file, 'r') as f:
                users = json.load(f)
            
            # Return users without passwords
            return [{**u, 'password': '***'} for u in users]
        except Exception as e:
            return []
    
    def delete_user(self, username: str) -> Tuple[bool, str]:
        """Delete a user account"""
        try:
            with open(self.users_file, 'r') as f:
                users = json.load(f)
            
            # Don't allow deleting the last admin
            admin_count = len([u for u in users if u['role'] == 'admin'])
            target_user = next((u for u in users if u['username'] == username), None)
            
            if not target_user:
                return False, f"❌ User '{username}' not found"
            
            if target_user['role'] == 'admin' and admin_count <= 1:
                return False, "❌ Cannot delete the last admin account"
            
            # Remove user
            users = [u for u in users if u['username'] != username]
            
            with open(self.users_file, 'w') as f:
                json.dump(users, f, indent=2)
            
            return True, f"✅ User '{username}' deleted successfully"
        except Exception as e:
            return False, f"❌ Deletion failed: {str(e)}"
    
    def change_password(self, username: str, old_password: str, 
                       new_password: str) -> Tuple[bool, str]:
        """Change user password"""
        try:
            with open(self.users_file, 'r') as f:
                users = json.load(f)
            
            user = next((u for u in users if u['username'] == username), None)
            if not user:
                return False, f"❌ User '{username}' not found"
            
            # Verify old password
            if user['password'] != self._hash_password(old_password):
                return False, "❌ Current password is incorrect"
            
            if len(new_password) < 6:
                return False, "❌ New password must be at least 6 characters"
            
            # Update password
            user['password'] = self._hash_password(new_password)
            
            with open(self.users_file, 'w') as f:
                json.dump(users, f, indent=2)
            
            return True, "✅ Password changed successfully"
        except Exception as e:
            return False, f"❌ Password change failed: {str(e)}"


# =============================================================================
# FEATURE 6: ADVANCED ANALYTICS
# =============================================================================
def calculate_profit_margin(orders: List[Dict], inventory: List[Dict]) -> Dict:
    """Calculate profit margin analysis"""
    try:
        if not orders:
            return {'total_revenue': 0, 'estimated_cost': 0, 'profit': 0, 'margin_percent': 0}
        
        total_revenue = sum(o.get('total', 0) for o in orders)
        
        # Estimate cost (assuming 40% cost ratio for SME)
        estimated_cost = total_revenue * 0.4
        profit = total_revenue - estimated_cost
        margin_percent = (profit / total_revenue * 100) if total_revenue > 0 else 0
        
        return {
            'total_revenue': total_revenue,
            'estimated_cost': estimated_cost,
            'profit': profit,
            'margin_percent': round(margin_percent, 2)
        }
    except Exception as e:
        return {'error': str(e)}


def calculate_inventory_turnover(orders: List[Dict], inventory: List[Dict]) -> Dict:
    """Calculate inventory turnover rate"""
    try:
        total_sold = sum(sum(i.get('quantity', 0) for i in o.get('items', [])) 
                        for o in orders)
        avg_inventory = sum(i.get('quantity', 0) for i in inventory) / max(len(inventory), 1)
        
        turnover_rate = total_sold / avg_inventory if avg_inventory > 0 else 0
        
        return {
            'total_sold': total_sold,
            'avg_inventory': round(avg_inventory, 2),
            'turnover_rate': round(turnover_rate, 2),
            'days_to_sell': round(365 / turnover_rate, 1) if turnover_rate > 0 else float('inf')
        }
    except Exception as e:
        return {'error': str(e)}


def get_revenue_trends(orders: List[Dict], days: int = 30) -> Dict:
    """Calculate revenue trends for last N days"""
    try:
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        daily_revenue = {}
        for order in orders:
            order_date = order.get('created_date', '').split()[0]
            if order_date >= cutoff_date:
                daily_revenue[order_date] = daily_revenue.get(order_date, 0) + order.get('total', 0)
        
        return {
            'period_days': days,
            'daily_revenue': daily_revenue,
            'total_revenue': sum(daily_revenue.values()),
            'avg_daily': round(sum(daily_revenue.values()) / max(len(daily_revenue), 1), 2)
        }
    except Exception as e:
        return {'error': str(e)}


def get_stock_out_frequency(orders: List[Dict], inventory: List[Dict]) -> Dict:
    """Analyze which items are frequently low on stock"""
    try:
        stock_outs = {}
        
        for order in orders:
            for item in order.get('items', []):
                item_id = item.get('item_id')
                if item_id not in stock_outs:
                    stock_outs[item_id] = 0
                stock_outs[item_id] += 1
        
        # Match with inventory names
        item_names = {i['id']: i['name'] for i in inventory}
        
        result = []
        for item_id, count in sorted(stock_outs.items(), key=lambda x: x[1], reverse=True):
            result.append({
                'item_id': item_id,
                'item_name': item_names.get(item_id, 'Unknown'),
                'order_frequency': count
            })
        
        return result[:10]  # Top 10
    except Exception as e:
        return []


# =============================================================================
# FEATURE 7: EMAIL ALERTS (Configuration)
# =============================================================================
class EmailAlertConfig:
    """Email notification configuration"""
    
    def __init__(self, config_file="email_config.json"):
        self.config_file = config_file
        self._initialize_config()
    
    def _initialize_config(self):
        """Create default email config"""
        try:
            if not os.path.exists(self.config_file):
                default_config = {
                    'smtp_server': 'smtp.gmail.com',
                    'smtp_port': 587,
                    'sender_email': 'your_email@gmail.com',
                    'sender_password': 'your_app_password',
                    'enabled': False,
                    'alerts': {
                        'low_stock': True,
                        'payroll_due': True,
                        'peak_hours': False
                    }
                }
                with open(self.config_file, 'w') as f:
                    json.dump(default_config, f, indent=2)
        except Exception as e:
            print(f"Error initializing email config: {e}")
    
    def get_config(self) -> Dict:
        """Get email configuration"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def update_config(self, config: Dict) -> bool:
        """Update email configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            return False


# =============================================================================
# FEATURE 8: INVENTORY FORECASTING
# =============================================================================
def predict_low_stock(orders: List[Dict], inventory: List[Dict], 
                     days_ahead: int = 7) -> List[Dict]:
    """Predict which items will be low on stock in N days"""
    try:
        predictions = []
        
        for item in inventory:
            item_id = item['id']
            # Calculate average daily consumption
            total_sold = sum(
                sum(i.get('quantity', 0) for i in o.get('items', []) 
                    if i.get('item_id') == item_id)
                for o in orders[-30:]  # Last 30 days
            )
            
            daily_consumption = total_sold / 30 if total_sold > 0 else 0
            projected_qty = item['quantity'] - (daily_consumption * days_ahead)
            
            if projected_qty < item.get('min_stock', 10):
                predictions.append({
                    'item_id': item_id,
                    'item_name': item['name'],
                    'current_qty': item['quantity'],
                    'daily_consumption': round(daily_consumption, 2),
                    'projected_qty': round(projected_qty, 2),
                    'min_stock': item.get('min_stock', 10),
                    'days_until_low': round((item['quantity'] - item.get('min_stock', 10)) / max(daily_consumption, 0.1), 1) if daily_consumption > 0 else float('inf'),
                    'reorder_qty': round(item.get('min_stock', 10) * 2 - projected_qty, 0)
                })
        
        return sorted(predictions, key=lambda x: x['days_until_low'])
    except Exception as e:
        return []


# =============================================================================
# FEATURE 9: EMPLOYEE ATTENDANCE TRACKING
# =============================================================================
class AttendanceManager:
    """Track employee attendance"""
    
    def __init__(self, attendance_file="attendance.json"):
        self.attendance_file = attendance_file
        self._initialize_attendance()
    
    def _initialize_attendance(self):
        """Create attendance file if doesn't exist"""
        try:
            if not os.path.exists(self.attendance_file):
                with open(self.attendance_file, 'w') as f:
                    json.dump([], f)
        except Exception as e:
            print(f"Error initializing attendance: {e}")
    
    def check_in(self, employee_id: int) -> Tuple[bool, str]:
        """Record employee check-in"""
        try:
            with open(self.attendance_file, 'r') as f:
                records = json.load(f)
            
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Check if already checked in
            existing = next((r for r in records 
                           if r['employee_id'] == employee_id and r['date'] == today),
                          None)
            if existing and existing['check_in']:
                return False, "Already checked in today"
            
            record = {
                'employee_id': employee_id,
                'date': today,
                'check_in': datetime.now().strftime("%H:%M:%S"),
                'check_out': None
            }
            
            records.append(record)
            with open(self.attendance_file, 'w') as f:
                json.dump(records, f, indent=2)
            
            return True, "✅ Checked in"
        except Exception as e:
            return False, f"❌ Check-in failed: {str(e)}"
    
    def check_out(self, employee_id: int) -> Tuple[bool, str]:
        """Record employee check-out"""
        try:
            with open(self.attendance_file, 'r') as f:
                records = json.load(f)
            
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Find today's check-in
            for record in records:
                if record['employee_id'] == employee_id and record['date'] == today:
                    record['check_out'] = datetime.now().strftime("%H:%M:%S")
                    
                    with open(self.attendance_file, 'w') as f:
                        json.dump(records, f, indent=2)
                    
                    return True, "✅ Checked out"
            
            return False, "No check-in record found today"
        except Exception as e:
            return False, f"❌ Check-out failed: {str(e)}"
    
    def get_attendance_report(self, employee_id: int = None) -> List[Dict]:
        """Get attendance records"""
        try:
            with open(self.attendance_file, 'r') as f:
                records = json.load(f)
            
            if employee_id:
                records = [r for r in records if r['employee_id'] == employee_id]
            
            return records
        except Exception as e:
            return []


# =============================================================================
# FEATURE 10: MULTI-LOCATION WAREHOUSE SUPPORT
# =============================================================================
class MultiWarehouseManager:
    """Manage multiple warehouse locations"""
    
    def __init__(self, warehouse_file="warehouses.json"):
        self.warehouse_file = warehouse_file
        self._initialize_warehouses()
    
    def _initialize_warehouses(self):
        """Create warehouses file"""
        try:
            if not os.path.exists(self.warehouse_file):
                default_warehouse = {
                    'id': 1,
                    'name': 'Main Warehouse',
                    'location': 'Pune',
                    'address': '',
                    'phone': '',
                    'capacity': 10000
                }
                with open(self.warehouse_file, 'w') as f:
                    json.dump([default_warehouse], f, indent=2)
        except Exception as e:
            print(f"Error initializing warehouses: {e}")
    
    def get_all_warehouses(self) -> List[Dict]:
        """Get all warehouse locations"""
        try:
            with open(self.warehouse_file, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def add_warehouse(self, name: str, location: str, address: str = "", 
                     phone: str = "", capacity: int = 5000) -> Tuple[bool, str]:
        """Add new warehouse location"""
        try:
            with open(self.warehouse_file, 'r') as f:
                warehouses = json.load(f)
            
            new_id = max([w['id'] for w in warehouses], default=0) + 1
            warehouse = {
                'id': new_id,
                'name': name,
                'location': location,
                'address': address,
                'phone': phone,
                'capacity': capacity
            }
            
            warehouses.append(warehouse)
            with open(self.warehouse_file, 'w') as f:
                json.dump(warehouses, f, indent=2)
            
            return True, f"✅ Warehouse {name} added"
        except Exception as e:
            return False, f"❌ Failed: {str(e)}"


# Initialize managers
backup_manager = BackupManager()
audit_logger = AuditLogger()
auth_manager = AuthManager()
email_config = EmailAlertConfig()
attendance_manager = AttendanceManager()
warehouse_manager = MultiWarehouseManager()
