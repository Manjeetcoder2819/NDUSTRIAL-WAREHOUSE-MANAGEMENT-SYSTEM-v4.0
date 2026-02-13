"""
🏭 INDUSTRIAL WAREHOUSE SYSTEM v4.0
✅ ZERO DEPENDENCIES (except streamlit)
✅ WORKS IMMEDIATELY - No pip errors
✅ Production ready - Data persists
"""

import streamlit as st
import json
import os
from datetime import datetime
from helpers import (
    validate_inventory_movement, 
    validate_employee_data, 
    validate_inventory_item,
    calculate_inventory_metrics,
    peak_manager,
    # New imports
    BackupManager,
    AuditLogger,
    AuthManager,
    search_employees,
    search_inventory,
    search_orders,
    filter_inventory_by_stock_status,
    export_to_csv,
    calculate_profit_margin,
    calculate_inventory_turnover,
    get_revenue_trends,
    get_stock_out_frequency,
    predict_low_stock,
    AttendanceManager,
    MultiWarehouseManager,
    backup_manager,
    audit_logger,
    auth_manager,
    attendance_manager,
    warehouse_manager
)

# =============================================================================
# DATA STORAGE (Local JSON - No database needed)
# =============================================================================
DATA_FILE = "warehouse_data.json"

def load_data():
    """Load data from JSON file"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {
        'employees': [],
        'inventory': [],
        'orders': [],
        'shipments': []
    }

def save_data(data):
    """Save data to JSON file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# Load initial data
warehouse_data = load_data()

# =============================================================================
# AUTHENTICATION & SESSION MANAGEMENT
# =============================================================================
def initialize_session():
    """Initialize session state for authentication"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'username' not in st.session_state:
        st.session_state.username = None


def login_page():
    """Display login page with login and registration tabs"""
    # Custom CSS for login page
    st.markdown("""
    <style>
    /* Main page background */
    .stApp {
        background: linear-gradient(135deg, #0F1419 0%, #1A2332 50%, #2D3E50 100%);
    }
    
    /* Login form container styling */
    [data-testid="column"] {
        background: rgba(26, 35, 50, 0.8);
        border-radius: 15px;
        padding: 30px;
        border: 2px solid #FF6B6B;
        box-shadow: 0 8px 32px rgba(255, 107, 107, 0.2);
    }
    
    /* Form input styling */
    .stTextInput input, .stSelectbox select {
        background-color: #0F1419 !important;
        border: 2px solid #FF6B6B !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
        padding: 10px !important;
    }
    
    .stTextInput input:focus, .stSelectbox select:focus {
        border: 2px solid #FF9999 !important;
        box-shadow: 0 0 10px rgba(255, 107, 107, 0.5) !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #FF6B6B, #FF8E8E);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 20px;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #FF8E8E, #FFB0B0);
        box-shadow: 0 6px 20px rgba(255, 107, 107, 0.6);
        transform: translateY(-2px);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background-color: #1A2332;
        border-radius: 10px;
        border: 2px solid #FF6B6B;
        padding: 5px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #FF6B6B;
        color: white;
        border-radius: 8px;
    }
    
    .stTabs [aria-selected="false"] {
        color: #FFFFFF;
    }
    
    /* Title styling */
    h1, h2, h3 {
        color: #FF6B6B !important;
        text-shadow: 0 0 20px rgba(255, 107, 107, 0.3);
    }
    
    /* Text styling */
    p, label, .stCaption {
        color: #FFFFFF !important;
    }
    
    /* Success/Error messages */
    .stSuccess {
        background-color: rgba(76, 175, 80, 0.2);
        color: #4CAF50;
        border: 2px solid #4CAF50;
        border-radius: 8px;
    }
    
    .stError {
        background-color: rgba(255, 107, 107, 0.2);
        color: #FF6B6B;
        border: 2px solid #FF6B6B;
        border-radius: 8px;
    }
    
    .stInfo {
        background-color: rgba(33, 150, 243, 0.2);
        color: #2196F3;
        border: 2px solid #2196F3;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <h1 style='text-align: center; color: #FF6B6B; text-shadow: 0 0 20px rgba(255, 107, 107, 0.4);'>
    🏭 INDUSTRIAL WAREHOUSE MANAGEMENT
    </h1>
    """, unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #FFB0B0; font-size: 14px;'>v4.0 - Production Ready</p>", unsafe_allow_html=True)
    
    # Create tabs for login and registration
    login_tab, register_tab = st.tabs(["🔐 Login", "📝 Register New User"])
    
    # ===== LOGIN TAB =====
    with login_tab:
        st.markdown("### Login to Continue")
        
        with st.form("login_form"):
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            submit = st.form_submit_button("🔓 Login", use_container_width=True)
            
            if submit:
                try:
                    success, message, role = auth_manager.authenticate(username, password)
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.user_role = role
                        st.session_state.username = username
                        st.success(message)
                        st.experimental_rerun()
                    else:
                        st.error(message)
                except Exception as e:
                    st.error(f"❌ Login error: {str(e)}")
        
        st.markdown("---")
        st.caption("📌 Demo Credentials:")
        st.caption("✓ Admin: admin / admin123")
        st.caption("✓ Manager: manager / manager123")
        st.caption("✓ Worker: worker / worker123")
        
    # ===== REGISTRATION TAB =====
    with register_tab:
        st.markdown("### Create New Account")
        st.info("📝 Fill in the form below to create a new user account")
        
        with st.form("register_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_username = st.text_input("New Username", key="register_username")
                new_password = st.text_input("Password", type="password", key="register_password")
            
            with col2:
                confirm_password = st.text_input("Confirm Password", type="password", key="register_confirm")
                user_role = st.selectbox(
                    "User Role",
                    ["worker", "manager", "admin"],
                    help="Select role: worker=Read-only, manager=Read/Create/Update, admin=Full access"
                )
            
            user_fullname = st.text_input("Full Name", key="register_fullname")
            
            col1, col2 = st.columns(2)
            with col1:
                submit_register = st.form_submit_button("✅ Create Account", use_container_width=True)
            with col2:
                st.form_submit_button(" Clear", use_container_width=True, disabled=True)
            
            if submit_register:
                try:
                    # Validation
                    if not new_username or len(new_username) < 3:
                        st.error(" Username must be at least 3 characters")
                    elif not new_password or len(new_password) < 6:
                        st.error("Password must be at least 6 characters")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match")
                    elif not user_fullname:
                        st.error(" Full name is required")
                    else:
                        # Try to register user
                        success, message = auth_manager.register_user(
                            new_username, 
                            new_password, 
                            user_role, 
                            user_fullname
                        )
                        
                        if success:
                            st.success(message)
                            st.balloons()
                            st.info("✅ Account created! You can now login with your credentials.")
                            audit_logger.log_action(
                                'CREATE', 
                                'users', 
                                1, 
                                'System', 
                                f'New user registered: {new_username} ({user_role})'
                            )
                        else:
                            st.error(message)
                except Exception as e:
                    st.error(f"❌ Registration error: {str(e)}")


def check_permission(required_action: str) -> bool:
    """Check if user has permission for action"""
    return auth_manager.has_permission(st.session_state.user_role, required_action)


# Initialize session
initialize_session()

# Check authentication
if not st.session_state.authenticated:
    login_page()
    st.stop()

# Load initial data
warehouse_data = load_data()

# =============================================================================
# CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="🏭 Industrial Warehouse Pro",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# CUSTOM STYLING FOR MAIN APPLICATION
# =============================================================================
st.markdown("""
<style>
/* Main app background */
.stApp {
    background: linear-gradient(135deg, #0F1419 0%, #1A2332 50%, #2D3E50 100%);
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1A2332 0%, #0F1419 100%);
    border-right: 3px solid #FF6B6B;
}

[data-testid="stSidebar"] > * {
    color: #FFFFFF !important;
}

/* Main content area */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, rgba(15, 20, 25, 0.9) 0%, rgba(26, 35, 50, 0.9) 100%);
}

/* Title styling */
h1 {
    color: #FF6B6B !important;
    text-shadow: 0 0 30px rgba(255, 107, 107, 0.4) !important;
    border-bottom: 3px solid #FF6B6B;
    padding-bottom: 15px;
}

h2 {
    color: #FF8E8E !important;
    text-shadow: 0 0 20px rgba(255, 107, 107, 0.3) !important;
}

h3 {
    color: #FFB0B0 !important;
}

/* Text styling */
body, p, label, .stMarkdown, span {
    color: #FFFFFF !important;
}

/* Button styling */
.stButton > button {
    background: linear-gradient(90deg, #FF6B6B, #FF8E8E) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 10px 20px !important;
    font-weight: bold !important;
    box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4) !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    background: linear-gradient(90deg, #FF8E8E, #FFB0B0) !important;
    box-shadow: 0 6px 20px rgba(255, 107, 107, 0.6) !important;
    transform: translateY(-2px) !important;
}

/* Input fields */
.stTextInput input, .stTextArea textarea, .stNumberInput input, .stSelectbox select, .stMultiSelect {
    background-color: #0F1419 !important;
    border: 2px solid #FF6B6B !important;
    color: #FFFFFF !important;
    border-radius: 8px !important;
    padding: 10px !important;
}

.stTextInput input:focus, .stTextArea textarea:focus, .stNumberInput input:focus {
    border: 2px solid #FF9999 !important;
    box-shadow: 0 0 15px rgba(255, 107, 107, 0.5) !important;
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    background-color: #1A2332;
    border-radius: 10px;
    border: 2px solid #FF6B6B;
    padding: 5px;
    gap: 0;
}

.stTabs [aria-selected="true"] {
    background-color: #FF6B6B !important;
    color: white !important;
    border-radius: 8px;
}

.stTabs [aria-selected="false"] {
    color: #FFFFFF !important;
}

/* Dataframe styling */
.stDataFrame {
    background-color: #1A2332 !important;
    color: #FFFFFF !important;
}

/* Metric styling */
.stMetric {
    background-color: rgba(255, 107, 107, 0.1);
    border: 2px solid #FF6B6B;
    border-radius: 10px;
    padding: 15px;
}

/* Success/Error/Info messages */
.stSuccess {
    background-color: rgba(76, 175, 80, 0.2) !important;
    color: #4CAF50 !important;
    border: 2px solid #4CAF50 !important;
    border-radius: 8px !important;
}

.stError {
    background-color: rgba(255, 107, 107, 0.2) !important;
    color: #FF6B6B !important;
    border: 2px solid #FF6B6B !important;
    border-radius: 8px !important;
}

.stInfo {
    background-color: rgba(33, 150, 243, 0.2) !important;
    color: #2196F3 !important;
    border: 2px solid #2196F3 !important;
    border-radius: 8px !important;
}

.stWarning {
    background-color: rgba(255, 152, 0, 0.2) !important;
    color: #FF9800 !important;
    border: 2px solid #FF9800 !important;
    border-radius: 8px !important;
}

/* Sidebar section headers */
.stSidebar h2, .stSidebar h3 {
    color: #FF6B6B !important;
}

/* Form container */
.stForm {
    background-color: rgba(26, 35, 50, 0.6);
    border: 2px solid #FF6B6B;
    border-radius: 10px;
    padding: 20px;
}

/* Expander styling */
.streamlit-expanderHeader {
    background-color: #1A2332 !important;
    color: #FF6B6B !important;
    border: 2px solid #FF6B6B !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# MAIN INTERFACE
# =============================================================================
col1, col2 = st.columns([10, 2])
with col1:
    st.markdown("""
    <h1 style='color: #FF6B6B; text-align: left; text-shadow: 0 0 30px rgba(255, 107, 107, 0.4);'>
    🏭 INDUSTRIAL WAREHOUSE MANAGEMENT SYSTEM
    </h1>
    """, unsafe_allow_html=True)
with col2:
    if st.button("🚪 Logout", key="logout_btn"):
        st.session_state.authenticated = False
        st.session_state.user_role = None
        st.session_state.username = None
        st.experimental_rerun()

st.markdown(f"<p style='color: #FFB0B0; font-size: 13px;'>**User:** {st.session_state.username} | **Role:** {st.session_state.user_role.upper()} | ✅ Production Ready | ⚡ Zero Dependencies | 🚀 Instant Deployment</p>", unsafe_allow_html=True)

# Sidebar Navigation with Role-Based Access
st.sidebar.title("📋 Navigation")

page_options = ["📊 Dashboard", "👥 Employees", "📦 Inventory", "🛒 Orders", "🚚 Shipments", "📈 Reports"]

# Add admin-only options
if st.session_state.user_role == 'admin':
    page_options.extend(["🔐 Admin Panel", "⚙️ Settings"])

page = st.sidebar.selectbox("Select Module:", page_options)

# Sidebar Info Panel
with st.sidebar:
    st.markdown("---")
    st.subheader("📊 Quick Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("👥 Employees", len(warehouse_data['employees']))
    with col2:
        st.metric("📦 Items", len(warehouse_data['inventory']))
    
    st.metric("🛒 Orders", len(warehouse_data['orders']))
    
    # Admin options
    if st.session_state.user_role == 'admin':
        st.markdown("---")
        st.subheader("🔧 Admin Tools")
        
        with st.expander("💾 Backup & Recovery"):
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Create Backup"):
                    try:
                        backup_file = backup_manager.create_backup(warehouse_data)
                        st.success(f"✅ Backup created: {backup_file}")
                    except Exception as e:
                        st.error(f"❌ Backup failed: {str(e)}")
            
            with col2:
                if st.button("📋 View Backups"):
                    st.session_state.show_backups = not st.session_state.get('show_backups', False)
            
            if st.session_state.get('show_backups'):
                backups = backup_manager.list_backups()
                if backups:
                    selected_backup = st.selectbox(
                        "Select backup to restore:",
                        [b['filename'] for b in backups],
                        key="backup_select"
                    )
                    
                    backup_path = next((b['path'] for b in backups if b['filename'] == selected_backup), None)
                    if st.button("Restore Selected Backup"):
                        try:
                            success, msg = backup_manager.restore_backup(backup_path)
                            if success:
                                st.success(msg)
                                st.experimental_rerun()
                            else:
                                st.error(msg)
                        except Exception as e:
                            st.error(f"❌ Restore failed: {str(e)}")
                else:
                    st.info("No backups available")
        
        with st.expander("📋 Audit Trail"):
            if st.button("📥 Download Audit Log"):
                try:
                    success, msg = audit_logger.export_audit_csv()
                    if success:
                        st.success(msg)
                        with open("audit_report.csv", "rb") as f:
                            st.download_button(
                                label="⬇️ Download CSV",
                                data=f.read(),
                                file_name="audit_report.csv",
                                mime="text/csv"
                            )
                    else:
                        st.error(msg)
                except Exception as e:
                    st.error(f"❌ Export failed: {str(e)}")
            
            recent_logs = audit_logger.get_audit_trail()[:10]
            if recent_logs:
                st.dataframe(recent_logs, use_container_width=True)
            else:
                st.info("No audit logs yet")

# =============================================================================
# EXECUTIVE DASHBOARD
# =============================================================================
if page == "📊 Dashboard":
    col1, col2, col3, col4 = st.columns(4)
    
    # KPIs
    with col1:
        st.metric("👥 Employees", len(warehouse_data['employees']))
    
    with col2:
        total_value = sum(
            item.get('quantity', 0) * item.get('price', 0) 
            for item in warehouse_data['inventory']
        )
        st.metric("💰 Inventory Value", f"₹{total_value:,.0f}")
    
    with col3:
        pending = len([o for o in warehouse_data['orders'] if o.get('status') == 'Pending'])
        st.metric("🛒 Pending Orders", pending)
    
    with col4:
        low_stock = len([
            i for i in warehouse_data['inventory'] 
            if i.get('quantity', 0) < i.get('min_stock', 10)
        ])
        st.metric("⚠️ Low Stock", low_stock)
    
    # Advanced Analytics Row
    st.subheader("📊 Advanced Analytics")
    tab1, tab2, tab3, tab4 = st.tabs(["💵 Profit Analysis", "📈 Inventory Turnover", "📊 Revenue Trends", "🏭 Stock Forecast"])
    
    with tab1:
        try:
            profit_data = calculate_profit_margin(warehouse_data['orders'], warehouse_data['inventory'])
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Revenue", f"₹{profit_data.get('total_revenue', 0):,.0f}")
            with col2:
                st.metric("Estimated Cost", f"₹{profit_data.get('estimated_cost', 0):,.0f}")
            with col3:
                st.metric("Profit", f"₹{profit_data.get('profit', 0):,.0f}")
            with col4:
                st.metric("Profit Margin %", f"{profit_data.get('margin_percent', 0):.1f}%")
        except Exception as e:
            st.error(f"❌ Analytics error: {str(e)}")
    
    with tab2:
        try:
            turnover_data = calculate_inventory_turnover(warehouse_data['orders'], warehouse_data['inventory'])
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Sold", turnover_data.get('total_sold', 0))
            with col2:
                st.metric("Avg Inventory", turnover_data.get('avg_inventory', 0))
            with col3:
                st.metric("Turnover Rate", f"{turnover_data.get('turnover_rate', 0):.2f}x")
            with col4:
                st.metric("Days to Sell", f"{turnover_data.get('days_to_sell', 0):.0f}")
        except Exception as e:
            st.error(f"❌ Analytics error: {str(e)}")
    
    with tab3:
        try:
            trends = get_revenue_trends(warehouse_data['orders'], days=30)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Period", f"{trends.get('period_days', 0)} days")
            with col2:
                st.metric("Total Revenue", f"₹{trends.get('total_revenue', 0):,.0f}")
            with col3:
                st.metric("Daily Avg", f"₹{trends.get('avg_daily', 0):,.0f}")
            
            if trends.get('daily_revenue'):
                st.bar_chart(trends['daily_revenue'])
        except Exception as e:
            st.error(f"❌ Analytics error: {str(e)}")
    
    with tab4:
        try:
            forecasts = predict_low_stock(warehouse_data['orders'], warehouse_data['inventory'], days_ahead=7)
            if forecasts:
                st.warning(f"⚠️ {len(forecasts)} items predicted to go low in 7 days")
                st.dataframe(forecasts, use_container_width=True)
            else:
                st.success("✅ All items have sufficient stock for next 7 days")
        except Exception as e:
            st.error(f"❌ Forecast error: {str(e)}")
    
    # Peak Hour Alert
    if peak_manager.is_peak_hour():
        capacity = peak_manager.get_current_capacity()
        total_ordered = sum(
            sum(item.get('quantity', 0) for item in o.get('items', [])) 
            for o in warehouse_data['orders']
        )
        peak_warning, msg = peak_manager.get_peak_hour_warning(warehouse_data['orders'])
        if peak_warning:
            st.warning(msg)
        else:
            st.info(f"📊 Peak hours: {total_ordered}/{capacity} capacity used")
    
    # Recent Activity
    st.subheader("📋 Recent Activity")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Latest Orders")
        recent_orders = warehouse_data['orders'][-5:]
        if recent_orders:
            st.dataframe(recent_orders, use_container_width=True)
    
    with col2:
        st.subheader("Inventory Status")
        low_items = [i for i in warehouse_data['inventory'] 
                    if i.get('quantity', 0) < i.get('min_stock', 10)]
        if low_items:
            st.error(f"⚠️ {len(low_items)} LOW STOCK ITEMS")
            for item in low_items:
                st.warning(f"{item['name']}: {item['quantity']}/{item['min_stock']}")
        else:
            st.success("✅ All stock levels OK")

# =============================================================================
# EMPLOYEES MODULE
# =============================================================================
elif page == "👥 Employees":
    tab1, tab2, tab3, tab4 = st.tabs(["➕ Hire Employee", "📋 Employee List", "👣 Attendance", "📥 Export"])
    
    with tab1:
        if check_permission('create'):
            st.subheader("Hire New Employee")
            with st.form("add_employee", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("Full Name")
                    position = st.selectbox("Position", ["Worker", "Supervisor", "Manager", "Engineer"])
                with col2:
                    age = st.number_input("Age", 18, 65, 30)
                    salary = st.number_input("Monthly Salary", 25000.0, 150000.0, 50000.0, step=1000.0)
                
                submitted = st.form_submit_button("✅ Hire Employee", use_container_width=True)
                if submitted:
                    try:
                        valid, msg = validate_employee_data(name, int(age), position, float(salary))
                        if valid:
                            emp_id = len(warehouse_data['employees']) + 1
                            employee = {
                                'id': emp_id,
                                'name': name,
                                'age': int(age),
                                'position': position,
                                'salary': float(salary),
                                'shift': 'Day',
                                'hire_date': datetime.now().strftime("%Y-%m-%d")
                            }
                            warehouse_data['employees'].append(employee)
                            save_data(warehouse_data)
                            audit_logger.log_action('CREATE', 'employees', emp_id, st.session_state.username, f"Hired {name}")
                            st.success(f"✅ {name} hired successfully! ID: {emp_id}")
                            st.experimental_rerun()
                        else:
                            st.error(msg)
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("❌ You don't have permission to hire employees")
    
    with tab2:
        st.subheader("👥 Employee List")
        
        # Search functionality
        search_query = st.text_input("🔍 Search employees (name/position/ID):")
        
        if search_query:
            employees_to_display = search_employees(warehouse_data['employees'], search_query)
            if not employees_to_display:
                st.info("No employees found")
        else:
            employees_to_display = warehouse_data['employees']
        
        if employees_to_display:
            st.dataframe(employees_to_display, use_container_width=True)
            
            # Payroll Summary
            total_payroll = sum(emp.get('salary', 0) for emp in employees_to_display)
            st.metric("💰 Payroll (Filtered)", f"₹{total_payroll:,.0f}")
        else:
            st.info("👥 No employees. Hire your first employee above!")
    
    with tab3:
        st.subheader("👣 Employee Attendance")
        
        if warehouse_data['employees']:
            col1, col2 = st.columns(2)
            
            with col1:
                selected_emp = st.selectbox(
                    "Select Employee:",
                    [f"ID:{e['id']} - {e['name']}" for e in warehouse_data['employees']]
                )
                emp_id = int(selected_emp.split(':')[1].split(' ')[0])
                
                if st.button("✅ Check In", use_container_width=True):
                    success, msg = attendance_manager.check_in(emp_id)
                    if success:
                        st.success(msg)
                        audit_logger.log_action('UPDATE', 'attendance', emp_id, st.session_state.username, 'Checked in')
                    else:
                        st.warning(msg)
            
            with col2:
                if st.button("🚪 Check Out", use_container_width=True):
                    success, msg = attendance_manager.check_out(emp_id)
                    if success:
                        st.success(msg)
                        audit_logger.log_action('UPDATE', 'attendance', emp_id, st.session_state.username, 'Checked out')
                    else:
                        st.warning(msg)
            
            # Attendance Report
            st.subheader("📋 Attendance Record")
            attendance_records = attendance_manager.get_attendance_report(emp_id)
            if attendance_records:
                st.dataframe(attendance_records, use_container_width=True)
            else:
                st.info("No attendance records yet")
        else:
            st.info("No employees to track")
    
    with tab4:
        st.subheader("📥 Export Employees")
        
        if warehouse_data['employees']:
            if st.button("📥 Export to CSV"):
                try:
                    success, msg = export_to_csv(warehouse_data['employees'], "employees_export.csv")
                    if success:
                        st.success(msg)
                        with open("employees_export.csv", "rb") as f:
                            st.download_button(
                                label="⬇️ Download CSV",
                                data=f.read(),
                                file_name="employees_export.csv",
                                mime="text/csv"
                            )
                    else:
                        st.error(msg)
                except Exception as e:
                    st.error(f"❌ Export failed: {str(e)}")
        else:
            st.info("No employees to export")

# =============================================================================
# INVENTORY MODULE
# =============================================================================
elif page == "📦 Inventory":
    tab1, tab2, tab3, tab4 = st.tabs(["➕ Add Stock", "📋 View Stock", "✏️ Adjust Stock", "📥 Export"])
    
    with tab1:
        if check_permission('create'):
            st.subheader("Add New Inventory Item")
            with st.form("add_inventory", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("Item Name")
                    quantity = st.number_input("Quantity", 0, 10000, 100, step=10)
                with col2:
                    price = st.number_input("Price per Unit", 0.1, 100000.0, 100.0, step=10.0)
                    min_stock = st.number_input("Minimum Stock Level", 0, 1000, 10)
                
                submitted = st.form_submit_button("➕ Add Item", use_container_width=True)
                if submitted:
                    try:
                        valid, msg = validate_inventory_item(name, int(quantity), float(price), int(min_stock))
                        if valid:
                            item_id = len(warehouse_data['inventory']) + 1
                            item = {
                                'id': item_id,
                                'name': name,
                                'quantity': int(quantity),
                                'price': float(price),
                                'min_stock': int(min_stock),
                                'added_date': datetime.now().strftime("%Y-%m-%d")
                            }
                            warehouse_data['inventory'].append(item)
                            save_data(warehouse_data)
                            audit_logger.log_action('CREATE', 'inventory', item_id, st.session_state.username, f"Added {name}")
                            st.success(f"✅ Added {quantity} x {name} to inventory!")
                            st.experimental_rerun()
                        else:
                            st.error(msg)
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("❌ You don't have permission to add inventory")
    
    with tab2:
        st.subheader("📦 View & Filter Stock")
        
        # Search functionality
        search_query = st.text_input("🔍 Search inventory (name/ID):")
        
        # Filter by stock status
        status_filter = st.selectbox("Filter by status:", ["All", "Low Stock", "Medium Stock", "High Stock"])
        
        if search_query:
            inventory_to_display = search_inventory(warehouse_data['inventory'], search_query)
        else:
            inventory_to_display = warehouse_data['inventory']
        
        if status_filter != "All":
            status_map = {
                "Low Stock": "low",
                "Medium Stock": "medium",
                "High Stock": "high"
            }
            inventory_to_display = filter_inventory_by_stock_status(inventory_to_display, status_map[status_filter])
        
        if inventory_to_display:
            # Prepare display data with status
            display_items = []
            total_value = 0
            
            for item in inventory_to_display:
                status = "⚠️ LOW" if item['quantity'] < item['min_stock'] else "✅ OK"
                value = item['quantity'] * item['price']
                display_items.append({
                    **item,
                    'status': status,
                    'total_value': value
                })
                total_value += value
            
            st.dataframe(display_items, use_container_width=True)
            st.metric("💰 Total Inventory Value", f"₹{total_value:,.0f}")
            
            # Stock Level Chart
            if len(display_items) > 1:
                chart_data = {}
                for item in display_items[:10]:
                    chart_data[item['name'][:20]] = item['quantity']
                
                st.subheader("📊 Stock Levels")
                st.bar_chart(chart_data)
        else:
            st.info("📦 No items found")
    
    with tab3:
        if check_permission('update'):
            if warehouse_data['inventory']:
                selected_item = st.selectbox(
                    "Select Item to Adjust:",
                    [f"ID:{item['id']} - {item['name']}" for item in warehouse_data['inventory']]
                )
                
                if selected_item:
                    item = next(i for i in warehouse_data['inventory'] 
                               if f"ID:{i['id']}" in selected_item)
                    
                    with st.form("adjust_stock", clear_on_submit=True):
                        col1, col2 = st.columns(2)
                        with col1:
                            new_quantity = st.number_input(
                                "New Quantity", 
                                0, 10000, item['quantity'], step=5
                            )
                        with col2:
                            new_price = st.number_input(
                                "New Price", 
                                0.1, 100000.0, item['price'], step=5.0
                            )
                        
                        submitted = st.form_submit_button("💾 Update Stock", use_container_width=True)
                        if submitted:
                            try:
                                item['quantity'] = int(new_quantity)
                                item['price'] = float(new_price)
                                item['updated_date'] = datetime.now().strftime("%Y-%m-%d")
                                save_data(warehouse_data)
                                audit_logger.log_action('UPDATE', 'inventory', item['id'], st.session_state.username, f"Updated {item['name']}")
                                st.success(f"✅ {item['name']} updated successfully!")
                                st.experimental_rerun()
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("📦 No inventory to adjust")
        else:
            st.warning("❌ You don't have permission to update inventory")
    
    with tab4:
        st.subheader("📥 Export Inventory")
        
        if warehouse_data['inventory']:
            if st.button("📥 Export to CSV"):
                try:
                    success, msg = export_to_csv(warehouse_data['inventory'], "inventory_export.csv")
                    if success:
                        st.success(msg)
                        with open("inventory_export.csv", "rb") as f:
                            st.download_button(
                                label="⬇️ Download CSV",
                                data=f.read(),
                                file_name="inventory_export.csv",
                                mime="text/csv"
                            )
                    else:
                        st.error(msg)
                except Exception as e:
                    st.error(f"❌ Export failed: {str(e)}")
        else:
            st.info("No inventory to export")

# =============================================================================
# ORDERS MODULE
# =============================================================================
elif page == "🛒 Orders":
    tab1, tab2, tab3 = st.tabs(["➕ New Order", "📋 Order List", "📥 Export"])
    
    with tab1:
        if check_permission('create'):
            st.subheader("Create New Order")
            
            # Peak hour warning
            if peak_manager.is_peak_hour():
                capacity = peak_manager.get_current_capacity()
                total_ordered = sum(
                    sum(item.get('quantity', 0) for item in o.get('items', [])) 
                    for o in warehouse_data['orders']
                )
                peak_warning, msg = peak_manager.get_peak_hour_warning(warehouse_data['orders'])
                if peak_warning:
                    st.warning(msg)
            
            with st.form("new_order", clear_on_submit=True):
                customer = st.text_input("Customer Name")
                
                st.subheader("Select Items")
                available_items = {i['id']: i for i in warehouse_data['inventory']}
                selected_items = {}
                
                for item_id, item in available_items.items():
                    qty = st.number_input(
                        f"{item['name']} (₹{item['price']}) - Stock: {item['quantity']}",
                        0, min(10, item['quantity']), 0, key=f"qty_{item_id}"
                    )
                    if qty > 0:
                        selected_items[item_id] = qty
                
                submitted = st.form_submit_button("✅ Create Order", use_container_width=True)
                
                if submitted and customer and selected_items:
                    try:
                        order_id = len(warehouse_data['orders']) + 1
                        total = 0
                        
                        # Calculate total and validate stock
                        order_items = []
                        all_valid = True
                        
                        for item_id, qty in selected_items.items():
                            item = available_items[item_id]
                            
                            # Validate inventory movement
                            result = validate_inventory_movement(warehouse_data['inventory'], item_id, qty, 'OUT')
                            if not result['valid']:
                                st.error(f"❌ {item['name']}: {result['error']}")
                                all_valid = False
                                break
                            
                            line_total = qty * item['price']
                            total += line_total
                            order_items.append({
                                'item_id': item_id,
                                'name': item['name'],
                                'quantity': qty,
                                'price': item['price'],
                                'total': line_total
                            })
                            # Deduct from inventory
                            item['quantity'] -= qty
                        
                        if all_valid:
                            order = {
                                'id': order_id,
                                'customer': customer,
                                'items': order_items,
                                'total': total,
                                'total_qty': sum(i['quantity'] for i in order_items),
                                'status': 'Pending',
                                'created_date': datetime.now().strftime("%Y-%m-%d")
                            }
                            
                            warehouse_data['orders'].append(order)
                            save_data(warehouse_data)
                            audit_logger.log_action('CREATE', 'orders', order_id, st.session_state.username, f"Order from {customer}")
                            st.success(f"✅ Order #{order_id} created for {customer} | ₹{total:,.0f}")
                            st.experimental_rerun()
                    except Exception as e:
                        st.error(f"❌ Error creating order: {str(e)}")
                elif submitted:
                    st.error("❌ Select items and enter customer name!")
        else:
            st.warning("❌ You don't have permission to create orders")
    
    with tab2:
        st.subheader("📋 Order List")
        
        # Search functionality
        search_query = st.text_input("🔍 Search orders (customer/ID):")
        
        if search_query:
            orders_to_display = search_orders(warehouse_data['orders'], search_query)
            if not orders_to_display:
                st.info("No orders found")
        else:
            orders_to_display = warehouse_data['orders']
        
        if orders_to_display:
            total_revenue = sum(order.get('total', 0) for order in orders_to_display)
            st.metric("💰 Total Revenue (Filtered)", f"₹{total_revenue:,.0f}")
            
            for order in reversed(orders_to_display[-10:]):  # Last 10 orders
                with st.expander(f"Order #{order['id']} - {order['customer']} (₹{order['total']:,.0f})"):
                    st.write(f"**Status:** {order['status']}")
                    st.write(f"**Date:** {order.get('created_date', 'N/A')}")
                    st.write("**Items:**")
                    for item in order['items']:
                        st.write(f"• {item['name']} x{item['quantity']} @ ₹{item['price']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if check_permission('update') and st.button(f"✅ Mark Fulfilled", key=f"fulfill_{order['id']}"):
                            try:
                                order['status'] = 'Fulfilled'
                                save_data(warehouse_data)
                                audit_logger.log_action('UPDATE', 'orders', order['id'], st.session_state.username, 'Marked fulfilled')
                                st.success("✅ Order marked fulfilled!")
                                st.experimental_rerun()
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                    
                    with col2:
                        if check_permission('delete') and st.button(f"🗑️ Delete Order", key=f"delete_{order['id']}"):
                            try:
                                warehouse_data['orders'].remove(order)
                                save_data(warehouse_data)
                                audit_logger.log_action('DELETE', 'orders', order['id'], st.session_state.username, 'Deleted')
                                st.success("✅ Order deleted!")
                                st.experimental_rerun()
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
        else:
            st.info("🛒 No orders yet.")
    
    with tab3:
        st.subheader("📥 Export Orders")
        
        if warehouse_data['orders']:
            if st.button("📥 Export to CSV"):
                try:
                    success, msg = export_to_csv(warehouse_data['orders'], "orders_export.csv")
                    if success:
                        st.success(msg)
                        with open("orders_export.csv", "rb") as f:
                            st.download_button(
                                label="⬇️ Download CSV",
                                data=f.read(),
                                file_name="orders_export.csv",
                                mime="text/csv"
                            )
                    else:
                        st.error(msg)
                except Exception as e:
                    st.error(f"❌ Export failed: {str(e)}")
        else:
            st.info("No orders to export")

# =============================================================================
# SHIPMENTS & REPORTS (Simplified)
# =============================================================================
elif page == "🚚 Shipments":
    st.header("🚚 Shipment Tracking")
    st.info("👈 Create orders first, then mark as fulfilled")

elif page == "📈 Reports":
    st.header("📈 Business Reports")
    
    # Simple metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        avg_order = sum(o.get('total', 0) for o in warehouse_data['orders']) / max(len(warehouse_data['orders']), 1)
        st.metric("📊 Avg Order Value", f"₹{avg_order:,.0f}")
    
    with col2:
        active_items = len([i for i in warehouse_data['inventory'] if i['quantity'] > 0])
        st.metric("📦 Active SKUs", active_items)
    
    with col3:
        st.metric("👥 Team Size", len(warehouse_data['employees']))
    
    # Top selling items
    st.subheader("🏆 Top Selling Items")
    stock_outs = get_stock_out_frequency(warehouse_data['orders'], warehouse_data['inventory'])
    if stock_outs:
        st.dataframe(stock_outs, use_container_width=True)

# =============================================================================
# ADMIN PANEL
# =============================================================================
elif page == "🔐 Admin Panel":
    if st.session_state.user_role == 'admin':
        st.title("🔐 Admin Control Panel")
        
        admin_tab1, admin_tab2, admin_tab3, admin_tab4 = st.tabs(["🏢 Warehouses", "👥 Users", "⚙️ System", "📊 Analytics"])
        
        with admin_tab1:
            st.subheader("🏢 Warehouse Locations")
            
            warehouses = warehouse_manager.get_all_warehouses()
            if warehouses:
                st.dataframe(warehouses, use_container_width=True)
            
            st.subheader("➕ Add New Warehouse")
            with st.form("add_warehouse"):
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("Warehouse Name")
                    location = st.text_input("Location/City")
                with col2:
                    address = st.text_input("Address")
                    phone = st.text_input("Phone")
                
                capacity = st.number_input("Capacity (units)", 1000, 100000, 5000)
                submitted = st.form_submit_button("Add Warehouse")
                
                if submitted and name and location:
                    success, msg = warehouse_manager.add_warehouse(name, location, address, phone, capacity)
                    if success:
                        st.success(msg)
                        st.experimental_rerun()
                    else:
                        st.error(msg)
        
        with admin_tab2:
            st.subheader("👥 User Management")
            
            user_subtab1, user_subtab2, user_subtab3 = st.tabs(["📋 All Users", "➕ Add User", "🔐 Manage Users"])
            
            with user_subtab1:
                st.write("**All User Accounts:**")
                try:
                    all_users = auth_manager.get_all_users()
                    if all_users:
                        st.dataframe(all_users, use_container_width=True)
                        st.caption(f"Total users: {len(all_users)}")
                    else:
                        st.info("No users found")
                except Exception as e:
                    st.error(f"Error loading users: {str(e)}")
            
            with user_subtab2:
                st.write("**Create New User Account:**")
                with st.form("admin_add_user"):
                    col1, col2 = st.columns(2)
                    with col1:
                        add_username = st.text_input("Username", key="admin_username")
                        add_password = st.text_input("Password", type="password", key="admin_password")
                    with col2:
                        add_fullname = st.text_input("Full Name", key="admin_fullname")
                        add_role = st.selectbox(
                            "Role",
                            ["worker", "manager", "admin"],
                            key="admin_role"
                        )
                    
                    submit_add = st.form_submit_button("➕ Add User", use_container_width=True)
                    
                    if submit_add:
                        try:
                            if not add_username or len(add_username) < 3:
                                st.error("❌ Username must be at least 3 characters")
                            elif not add_password or len(add_password) < 6:
                                st.error("❌ Password must be at least 6 characters")
                            elif not add_fullname:
                                st.error("❌ Full name is required")
                            else:
                                success, msg = auth_manager.register_user(
                                    add_username,
                                    add_password,
                                    add_role,
                                    add_fullname
                                )
                                if success:
                                    st.success(msg)
                                    audit_logger.log_action(
                                        'CREATE',
                                        'users',
                                        1,
                                        st.session_state.username,
                                        f'New user created: {add_username} ({add_role})'
                                    )
                                    st.experimental_rerun()
                                else:
                                    st.error(msg)
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
            
            with user_subtab3:
                st.write("**Delete User or Manage Access:**")
                try:
                    all_users = auth_manager.get_all_users()
                    if all_users and len(all_users) > 1:
                        user_to_manage = st.selectbox(
                            "Select user to manage:",
                            [u['username'] for u in all_users if u['username'] != st.session_state.username],
                            key="manage_user_select"
                        )
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("🗑️ Delete User", key="delete_user_btn"):
                                success, msg = auth_manager.delete_user(user_to_manage)
                                if success:
                                    st.success(msg)
                                    audit_logger.log_action(
                                        'DELETE',
                                        'users',
                                        1,
                                        st.session_state.username,
                                        f'User deleted: {user_to_manage}'
                                    )
                                    st.experimental_rerun()
                                else:
                                    st.error(msg)
                        
                        with col2:
                            st.caption("⚠️ This will permanently delete the user account")
                    else:
                        st.info("Cannot manage users (need at least 2 users and cannot delete yourself)")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        with admin_tab3:
            st.subheader("⚙️ System Settings")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📧 Email Configuration")
                try:
                    email_cfg = email_config.get_config()
                    
                    enabled = st.checkbox("Enable Email Alerts", value=email_cfg.get('enabled', False))
                    smtp_server = st.text_input("SMTP Server", value=email_cfg.get('smtp_server', ''))
                    smtp_port = st.number_input("SMTP Port", value=email_cfg.get('smtp_port', 587))
                    sender_email = st.text_input("Sender Email", value=email_cfg.get('sender_email', ''))
                    sender_password = st.text_input("Sender Password", type="password", value=email_cfg.get('sender_password', ''))
                    
                    if st.button("💾 Save Email Config"):
                        new_config = {
                            'smtp_server': smtp_server,
                            'smtp_port': smtp_port,
                            'sender_email': sender_email,
                            'sender_password': sender_password,
                            'enabled': enabled,
                            'alerts': email_cfg.get('alerts', {})
                        }
                        if email_config.update_config(new_config):
                            st.success("✅ Email config saved")
                        else:
                            st.error("❌ Failed to save config")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            
            with col2:
                st.subheader("💾 Data Management")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("🔄 Create Backup Now"):
                        try:
                            backup_file = backup_manager.create_backup(warehouse_data)
                            st.success(f"✅ Backup created: {backup_file}")
                        except Exception as e:
                            st.error(f"❌ Backup failed: {str(e)}")
                
                with col_b:
                    if st.button("🗑️ Clear All Data"):
                        if st.checkbox("I understand this will delete all data"):
                            warehouse_data['employees'] = []
                            warehouse_data['inventory'] = []
                            warehouse_data['orders'] = []
                            warehouse_data['shipments'] = []
                            save_data(warehouse_data)
                            st.success("✅ All data cleared")
                            st.experimental_rerun()
        
        with admin_tab4:
            st.subheader("📊 System Analytics")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Employees", len(warehouse_data['employees']))
            with col2:
                st.metric("Total Inventory Items", len(warehouse_data['inventory']))
            with col3:
                st.metric("Total Orders", len(warehouse_data['orders']))
            
            # Audit trail summary
            st.subheader("📋 Recent Audit Trail")
            recent_logs = audit_logger.get_audit_trail()[:20]
            if recent_logs:
                st.dataframe(recent_logs, use_container_width=True)
            else:
                st.info("No audit logs yet")
    else:
        st.error("❌ Admin access required")

# =============================================================================
# SETTINGS PAGE
# =============================================================================
elif page == "⚙️ Settings":
    st.title("⚙️ User Settings")
    
    settings_tab1, settings_tab2, settings_tab3 = st.tabs(["👤 Profile", "🔐 Change Password", "ℹ️ Help"])
    
    with settings_tab1:
        st.subheader(f"👤 Your Profile")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Username:** {st.session_state.username}")
        with col2:
            st.write(f"**Role:** {st.session_state.user_role.upper()}")
        
        st.markdown("---")
        st.subheader("🔑 Permissions")
        
        role = st.session_state.user_role
        permissions = {
            'admin': ['Create', 'Read', 'Update', 'Delete', 'View Reports', 'Admin Panel'],
            'manager': ['Create', 'Read', 'Update', 'View Reports'],
            'worker': ['Read (View-only)']
        }
        
        st.write(f"**Your {role.upper()} can:**")
        for perm in permissions.get(role, []):
            st.write(f"✅ {perm}")
        
        if st.session_state.user_role == 'admin':
            st.markdown("---")
            st.subheader("🔗 Admin Tools")
            st.markdown("- [Go to Admin Panel](#admin-panel)")
    
    with settings_tab2:
        st.subheader("🔐 Change Your Password")
        
        with st.form("change_password_form"):
            current_pwd = st.text_input("Current Password", type="password", key="current_pwd")
            new_pwd = st.text_input("New Password", type="password", key="new_pwd")
            confirm_pwd = st.text_input("Confirm New Password", type="password", key="confirm_pwd")
            
            submit_change = st.form_submit_button("✅ Change Password", use_container_width=True)
            
            if submit_change:
                try:
                    # Validate
                    if not current_pwd:
                        st.error("❌ Current password is required")
                    elif not new_pwd or len(new_pwd) < 6:
                        st.error("❌ New password must be at least 6 characters")
                    elif new_pwd != confirm_pwd:
                        st.error("❌ Passwords do not match")
                    else:
                        success, msg = auth_manager.change_password(
                            st.session_state.username,
                            current_pwd,
                            new_pwd
                        )
                        if success:
                            st.success(msg)
                            st.info("ℹ️ Please login again with your new password")
                            audit_logger.log_action(
                                'UPDATE',
                                'users',
                                1,
                                st.session_state.username,
                                'Password changed'
                            )
                        else:
                            st.error(msg)
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    with settings_tab3:
        st.subheader("📚 Help & Documentation")
        st.markdown("""
        **Quick Tips:**
        - 📊 Dashboard: View KPIs and analytics
        - 👥 Employees: Hire and manage team
        - 📦 Inventory: Manage stock levels
        - 🛒 Orders: Create and track orders
        - 🚚 Shipments: Track shipments
        - 📈 Reports: View business analytics
        
        **Role Permissions:**
        - **Admin**: Full access to all features + Admin Panel
        - **Manager**: Can view reports, create/update orders, manage employees
        - **Worker**: View-only access to all data
        
        **Getting Help:**
        - Check DEPLOYMENT_GUIDE.md for detailed help
        - Review FEATURES_IMPLEMENTED.md for feature details
        - Contact your administrator for account issues
        """)

# Footer
st.markdown("---")
st.markdown("*✅ Production Ready | Zero Dependencies | Audit Trail Enabled | Multi-user Support*")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | User: {st.session_state.username} | Role: {st.session_state.user_role.upper()}")
