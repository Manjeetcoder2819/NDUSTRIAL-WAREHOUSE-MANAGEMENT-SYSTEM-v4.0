#!/bin/bash
echo "🚀 Deploying Industrial Warehouse System v4.0..."

# Install dependencies (minimal - no database needed)
pip install -r requirements.txt

# Start production
streamlit run app.py --server.port 8080 --server.address 0.0.0.0

# Data persists in warehouse_data.json automatically
echo "✅ System deployed on http://0.0.0.0:8080"

