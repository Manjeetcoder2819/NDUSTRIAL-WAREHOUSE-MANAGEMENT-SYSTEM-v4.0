# 🏭 Industrial Warehouse Management System v4.0 - AI Agent Instructions

## Project Purpose
Production-grade inventory management system for Pune SMEs. Solves ₹47L/year in operational losses. **v4.0 Design**: Zero dependencies (except Streamlit), instant deployment with local JSON file storage.

## Architecture Overview
z
### Why v4.0 (JSON-Based)?
- **Zero complexity**: No database setup, no Supabase credentials required
- **Instant deployment**: Works immediately after `streamlit run app.py`
- **Data persistence**: warehouse_data.json auto-saves on all changes
- **Multi-module UI**: 6 main modules (Dashboard, Employees, Inventory, Orders, Shipments, Reports)

### Core Components

1. **app.py** (366 lines) - Complete Streamlit application
   - 6-module sidebar navigation with state management
   - Local JSON file handling (load_data/save_data functions)
   - Form-based CRUD for Employees, Inventory, Orders
   - Real-time metrics and status displays
   - Peak hour warnings for order capacity

2. **helpers.py** - Business logic & validation layer
   - `PeakHourManager`: Peak hour capacity {14:50, 15:75, 16:100, 17:80} units
   - `validate_inventory_movement()`: Prevents stock going negative
   - `validate_employee_data()` / `validate_inventory_item()`: Form input validation
   - `calculate_inventory_metrics()`: KPI calculations

3. **warehouse_data.json** - Local persistent storage
   ```json
   {
     "employees": [{id, name, age, position, salary, shift, hire_date}],
     "inventory": [{id, name, quantity, price, min_stock, added_date}],
     "orders": [{id, customer, items, total, status, created_date}],
     "shipments": []
   }
   ```

## Critical Data Flows

### Employee Hiring Flow
```
User fills "Hire Employee" form 
→ Validate with validate_employee_data()
→ Generate emp_id = len(employees) + 1
→ Append to warehouse_data['employees']
→ save_data() → JSON persisted
→ st.rerun() → UI updates
```

### Inventory Add Flow
```
User submits "Add Stock" form
→ Validate item name/price/qty with validate_inventory_item()
→ item_id = len(inventory) + 1
→ Create item dict with added_date timestamp
→ Append to warehouse_data['inventory']
→ save_data() → JSON file updated
→ st.success() confirmation
```

### Order Creation Flow
```
User selects items and quantity
→ FoManual sequential**: `new_id = len(warehouse_data[table]) + 1`
- Not auto-incrementing, but sufficient for single warehouse
- Order same as insertion order (deterministic)

### File Persistence
- `load_data()` called once at startup: `warehouse_data = load_data()`
- `save_data(warehouse_data)` after EVERY create/update/delete
- **Critical**: Always save after mutations, else data is lost on page reload
- JSON format allows git-friendly diffs for audit trails

### Form Handling (Production Pattern)
```python
with st.form("form_name", clear_on_submit=True):
    # Input widgets here
    submitted = st.form_submit_button("Button Text")
    if submitted and validation:
        # Mutate warehouse_data
        save_data(warehouse_data)
        st.success("Message")
        st.rerun()  # Refresh UI
```

### Data Lookup Pattern
```python
# Finding items by ID
item = next((i for i in warehouse_data['inventory'] if i['id'] == item_id), None)

# Filtering
low_Local Development
```bash
pip install -r requirements.txt     # Only streamlit + pandas
streamlit run app.py               # Runs on http://localhost:8501
# Edit app.py → Auto-reloads in browser
# warehouse_data.json updates in real-time
```

### Testing Data
- Delete or edit `warehouse_data.json` to reset data
- Commit clean JSON structure to git for team testing
- No database schema to manage

### Deployment
```bash
pip install -r requirements.txt
streamlit run app.py --server.port 8080 --server.address 0.0.0.0
# Data persists in warehouse_data.json (upload to server beforehand if needed)
```

if result['valid']:
    # Safe to update
    result['item']['quantity'] = result['new_qty']
else:
    st.error(result['error'])
```

### Streamlit-Specific Patterns
- **Session state for persistence**: `st.session_state.user` (not used in v4.0, but available)
- **Container layout**: `st.columns(4)`, `st.tabs()` for UI sections
- **Data display**: `st.dataframe()` for tables, `st.json()` for nested structures
- **Metrics**: `st.metric("Label", value, delta="+X")` for KPIs
- **Charts**: Native `st.bar_chart(dict)` for simple charts (no Plotly needed
- EVERY create/update/delete calls `log_audit(action, table, record_id, user, details)`
- User context comes from `st.session_state.user` (defaulted to "Manager")
- Timestamps use `.isoformat()` format for ISO 8601 compliance
- Audit logs prevent ₹2L compliance fines

### Stock Validation Pattern
- **Python Libraries
- **streamlit** (1.38.0): UI framework, forms, metrics
- **pandas** (2.2.2): Optional, imported but currently unused (for future aggregations)

### External Services
- **None required** - Entirely self-contained
- Optional: Git for backup, file sync for multi-instance deployments
- Use `db.fetch_all(table_name)` to get latest data (no client-side caching)
- Always check existence before updates: `next((r for r in data if r['id'] == x), None)`
- Use `item['id']` for updates (database PK), not emp_id/item_id (business keys)

## Development Workflows

### Setup
```bash
cp .env.example .env        # Add SUPABASE_URL, SUPABASE_KEY
piAdd employee with validation
if name and age:
    emp_id = len(warehouse_data['employees']) + 1
    employee = {
        'id': emp_id,
        'name': name,
        'age': int(age),
        'position': position,
        'salary': float(salary),
        'hire_date': datetime.now().strftime("%Y-%m-%d")
    }
    warehouse_data['employees'].append(employee)
    save_data(warehouse_data)
    st.success("✅ Employee added")

# Update inventory after validation
result = validate_inventory_movement(warehouse_data['inventory'], 3, 25, 'OUT')
if result['valid']:
    item = result['item']
    item['quantity'] = result['new_qty']
    save_data(warehouse_data)
```

### ❌ INCORRECT
```python - Complete UI, all 6 modules, forms, state management
- [helpers.py](helpers.py) - Validation functions, peak hour logic, metrics
- [warehouse_data.json](warehouse_data.json) - Persistent data store
- [requirements.txt](requirements.txt) - Only streamlit + pandas (2 dependencies)
- [.env.example](.env.example) - Currently empty, for future use

## Performance & Scalability Notes
- `warehouse_data` loaded fresh on startup, mutations in-memory
- JSON re-written on every save (OK for <10k records, currently ~100s)
- Form submission flow: create object → append → save → rerun
- No caching layer needed (Streamlit handles view caching)
- **Scale limit**: ~50k records before JSON load/save becomes noticeable (~500ms)

## Data Integrity & Consistency
- **Single-file storage**: No race conditions (JSON writes are atomic)
- **Audit trail**: Timestamp every create/update with `.strftime("%Y-%m-%d %H:%M:%S")`
- **Soft references**: Orders contain item names, not item_ids (snapshot approach)
- **Stock validation**: Always call `validate_inventory_movement()` before reduction

## Testing Patterns
- Modify `warehouse_data` manually in Python console
- Inspect JSON file directly: `cat warehouse_data.json | jq .`
- Test peak hour logic by changing system time or mocking `datetime.now()`
- Forms auto-reset after submit (`clear_on_submit=True`) → good UX for testing
# Modifying stale copy from memory
old_item = warehouse_data['inventory'][0]
old_item['quantity'] = 50
# But list reference broken if data reloaded elsewhere
### Python Libraries
- **streamlit**: UI framework, session_state is key to multi-user experience
- **pandas**: DataFrame for tabular display + `.sort_values('price')`
- **plotly**: Interactive charts (imported but usage minimal in current code)
- **beautifulsoup4 + requests**: Web scraping for market prices
- **python-dotenv**: Load .env credentials at startup

## Common Coding Patterns & Gotchas

### ✅ CORRECT
```python
# Create with audit
emp_id = db.get_next_id('employees')
emp = Employee(emp_id, name, age, position, salary)
db.create('employees', emp.to_dict(), st.session_state.user)

# Update with validation
inventory = db.fetch_all('inventory')
item = next((i for i in inventory if i['item_id'] == item_id), None)
db.update('inventory', item['id'], {'quantity': new_qty})
```

### ❌ INCORRECT
```python
# Direct Supabase without audit
db.supabase.table('employees').insert(emp.to_dict()).execute()

# Using business key as update identifier
db.update('inventory', item_id=item_id, data={...})  # Wrong! Use id field

# Skipping validation
db.update('inventory', item_id, {'quantity': qty - 50})  # Could go negative!
```

## Key Files & Responsibilities
- [app.py](app.py): Streamlit UI + module routing
- [database.py](database.py): Supabase ORM + audit layer (most critical)
- [scraper.py](scraper.py): External API integration
- [utils.py](utils.py): Business rule enforcement
- [requirements.txt](requirements.txt): Python 3.9+ dependencies
- [.env.example](.env.example): Credential templates

## Performance & Scalability Notes
- Supabase PostgreSQL handles concurrent writes
- `db.fetch_all()` returns full table (OK for <10k records)
- Peak hour limits prevent overload during 2-5PM spike
- Audit trail grows unbounded (consider archival strategy for >1M logs)
