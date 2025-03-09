import os
from flask import Flask, render_template, redirect, url_for, flash, request, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from datetime import datetime
from sqlalchemy import func, distinct
from sqlalchemy.sql import text
import csv
from io import StringIO

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-testing')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///fuel_settlement.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

# Import models after initializing db to avoid circular imports
from models_simple import User, Supplier, FuelContract, FuelMineDelivery, FuelTransportation, FuelArrival

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    # Get counts for dashboard
    supplier_count = Supplier.query.count()
    contract_count = FuelContract.query.count()
    mine_delivery_count = FuelMineDelivery.query.count()
    transportation_count = FuelTransportation.query.count()
    
    # Get count of unique combinations of transport_date and contract_name for summary
    # Using a SQLite compatible approach
    transportation_summary_count = db.session.query(
        FuelTransportation.transport_date, 
        FuelTransportation.fuel_contract_id
    ).distinct().count()
    
    arrival_count = FuelArrival.query.count()
    
    return render_template('index.html', 
                          supplier_count=supplier_count,
                          contract_count=contract_count,
                          mine_delivery_count=mine_delivery_count,
                          transportation_count=transportation_count,
                          transportation_summary_count=transportation_summary_count,
                          arrival_count=arrival_count)

# Export route using CSV instead of Excel
@app.route('/export')
def export_data():
    # Create a CSV file for each model
    suppliers = Supplier.query.all()
    contracts = FuelContract.query.all()
    deliveries = FuelMineDelivery.query.all()
    transportations = FuelTransportation.query.all()
    arrivals = FuelArrival.query.all()
    
    # Create a zip file with all CSV files
    import zipfile
    from io import BytesIO
    
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        # Suppliers CSV
        suppliers_csv = StringIO()
        csv_writer = csv.writer(suppliers_csv)
        csv_writer.writerow(['供应商简称', '供应商全称', '所属类型', '二级单位'])
        for s in suppliers:
            csv_writer.writerow([s.short_name, s.full_name, s.supplier_type, s.secondary_unit])
        zf.writestr('供应商.csv', suppliers_csv.getvalue())
        
        # Contracts CSV
        contracts_csv = StringIO()
        csv_writer = csv.writer(contracts_csv)
        csv_writer.writerow(['合同日期', '燃料合同名称', '合同类型', '矿发热值', '矿发单价'])
        for c in contracts:
            csv_writer.writerow([
                c.contract_date.strftime('%Y-%m'),
                c.contract_name,
                c.contract_type,
                c.mine_calorific_value,
                c.mine_unit_price
            ])
        zf.writestr('燃料合同.csv', contracts_csv.getvalue())
        
        # Deliveries CSV
        deliveries_csv = StringIO()
        csv_writer = csv.writer(deliveries_csv)
        csv_writer.writerow(['供应商', '燃料合同名称', '矿发数量', '矿发热值', '矿发单价', '煤款'])
        for d in deliveries:
            csv_writer.writerow([
                d.supplier.short_name,
                d.fuel_contract.contract_name,
                d.mine_quantity,
                d.mine_calorific_value,
                d.mine_unit_price,
                d.coal_payment
            ])
        zf.writestr('燃料矿发.csv', deliveries_csv.getvalue())
        
        # Transportations CSV
        transportations_csv = StringIO()
        csv_writer = csv.writer(transportations_csv)
        csv_writer.writerow([
            '承运日期', '燃料合同名称', '拉运类型', '拉运单价', 
            '拉运地点', '拉运合同', '运输单价', '拉运数量', '运输金额'
        ])
        for t in transportations:
            csv_writer.writerow([
                t.transport_date.strftime('%Y-%m'),
                t.fuel_contract.contract_name,
                t.transport_type,
                t.transport_unit_price,
                t.transport_location,
                t.transport_contract,
                t.transportation_unit_price,
                t.transport_quantity,
                t.transportation_amount
            ])
        zf.writestr('燃料拉运.csv', transportations_csv.getvalue())
        
        # Transportation Summary CSV
        transport_summary = {}
        for t in transportations:
            key = (t.transport_date.strftime('%Y-%m'), t.fuel_contract.contract_name)
            if key not in transport_summary:
                transport_summary[key] = {
                    '承运日期': t.transport_date.strftime('%Y-%m'),
                    '燃料合同名称': t.fuel_contract.contract_name,
                    '运输单价': 0,
                    '运输金额': 0
                }
            transport_summary[key]['运输单价'] += t.transportation_unit_price
            transport_summary[key]['运输金额'] += t.transportation_amount
        
        summary_csv = StringIO()
        csv_writer = csv.writer(summary_csv)
        csv_writer.writerow(['承运日期', '燃料合同名称', '运输单价', '运输金额'])
        for summary in transport_summary.values():
            csv_writer.writerow([
                summary['承运日期'],
                summary['燃料合同名称'],
                summary['运输单价'],
                summary['运输金额']
            ])
        zf.writestr('燃料拉运汇总.csv', summary_csv.getvalue())
        
        # Arrivals CSV
        arrivals_csv = StringIO()
        csv_writer = csv.writer(arrivals_csv)
        csv_writer.writerow([
            '到厂日期', '燃料合同名称', '到厂数量', '到厂热值', '到厂标煤量',
            '拉运类型', '矿发数量估算', '矿发单价估算', '到厂价值', '入厂标单'
        ])
        for a in arrivals:
            csv_writer.writerow([
                a.arrival_date.strftime('%Y-%m'),
                a.fuel_contract.contract_name,
                a.arrival_quantity,
                a.arrival_calorific_value,
                a.arrival_standard_coal,
                a.transport_type,
                a.estimated_mine_quantity,
                a.estimated_mine_unit_price,
                a.arrival_value,
                a.arrival_standard_unit_price
            ])
        zf.writestr('燃料到厂.csv', arrivals_csv.getvalue())
    
    memory_file.seek(0)
    return send_file(
        memory_file,
        as_attachment=True,
        download_name='燃料结算系统数据.zip',
        mimetype='application/zip'
    )

# Register blueprints after all models are imported
def register_blueprints(app):
    # Authentication routes
    try:
        from routes.auth_simple import auth_bp
        app.register_blueprint(auth_bp)
    except ImportError:
        print("Warning: auth_simple.py not found, authentication routes will not be available.")

# Only register auth blueprint for now
register_blueprints(app)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 