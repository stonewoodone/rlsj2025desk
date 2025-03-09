import os
from flask import Flask, render_template, redirect, url_for, flash, request, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from datetime import datetime
from sqlalchemy import func
import pandas as pd
from io import BytesIO

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
from models import User, Supplier, FuelContract, FuelMineDelivery, FuelTransportation, FuelArrival

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

# Export route
@app.route('/export')
def export_data():
    # Create a Pandas Excel writer using BytesIO
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    
    # Export Suppliers
    suppliers = Supplier.query.all()
    suppliers_data = [{
        '供应商简称': s.short_name,
        '供应商全称': s.full_name,
        '所属类型': s.supplier_type,
        '二级单位': s.secondary_unit
    } for s in suppliers]
    pd.DataFrame(suppliers_data).to_excel(writer, sheet_name='供应商', index=False)
    
    # Export Fuel Contracts
    contracts = FuelContract.query.all()
    contracts_data = [{
        '合同日期': c.contract_date.strftime('%Y-%m'),
        '燃料合同名称': c.contract_name,
        '合同类型': c.contract_type,
        '矿发热值': c.mine_calorific_value,
        '矿发单价': round(c.mine_unit_price, 2)
    } for c in contracts]
    pd.DataFrame(contracts_data).to_excel(writer, sheet_name='燃料合同', index=False)
    
    # Export Fuel Mine Deliveries
    deliveries = FuelMineDelivery.query.all()
    deliveries_data = [{
        '供应商': d.supplier.short_name,
        '燃料合同名称': d.fuel_contract.contract_name,
        '矿发数量': d.mine_quantity,
        '矿发热值': d.mine_calorific_value,
        '矿发单价': round(d.mine_unit_price, 2),
        '煤款': round(d.coal_payment, 2)
    } for d in deliveries]
    pd.DataFrame(deliveries_data).to_excel(writer, sheet_name='燃料矿发', index=False)
    
    # Export Fuel Transportation
    transportations = FuelTransportation.query.all()
    transportations_data = [{
        '承运日期': t.transport_date.strftime('%Y-%m'),
        '燃料合同名称': t.fuel_contract.contract_name,
        '拉运类型': t.transport_type,
        '拉运单价': round(t.transport_unit_price, 2),
        '拉运地点': t.transport_location,
        '拉运合同': t.transport_contract,
        '运输单价': round(t.transportation_unit_price, 2),
        '拉运数量': t.transport_quantity,
        '运输金额': round(t.transportation_amount, 2)
    } for t in transportations]
    pd.DataFrame(transportations_data).to_excel(writer, sheet_name='燃料拉运', index=False)
    
    # Export Fuel Transportation Summary
    # Group by contract and date
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
    
    # 对汇总数据进行四舍五入处理
    for key in transport_summary:
        transport_summary[key]['运输单价'] = round(transport_summary[key]['运输单价'], 2)
        transport_summary[key]['运输金额'] = round(transport_summary[key]['运输金额'], 2)
    
    pd.DataFrame(list(transport_summary.values())).to_excel(writer, sheet_name='燃料拉运汇总', index=False)
    
    # Export Fuel Arrivals
    arrivals = FuelArrival.query.all()
    arrivals_data = [{
        '到厂日期': a.arrival_date.strftime('%Y-%m'),
        '燃料合同名称': a.fuel_contract.contract_name,
        '到厂数量': a.arrival_quantity,
        '到厂热值': a.arrival_calorific_value,
        '到厂标煤量': round(a.arrival_standard_coal, 2),
        '拉运类型': a.transport_type,
        '矿发数量估算': round(a.estimated_mine_quantity, 2),
        '矿发单价估算': round(a.estimated_mine_unit_price, 2),
        '到厂价值': round(a.arrival_value, 2),
        '入厂标单': round(a.arrival_standard_unit_price, 2)
    } for a in arrivals]
    pd.DataFrame(arrivals_data).to_excel(writer, sheet_name='燃料到厂', index=False)
    
    # Save the Excel file
    writer.close()
    output.seek(0)
    
    return send_file(
        output,
        as_attachment=True,
        download_name='燃料结算系统数据.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

# Register blueprints after all models are imported
def register_blueprints(app):
    # Authentication routes
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Supplier routes
    from routes.suppliers import suppliers_bp
    app.register_blueprint(suppliers_bp)

    # Fuel Contract routes
    from routes.contracts import contracts_bp
    app.register_blueprint(contracts_bp)

    # Fuel Mine Delivery routes
    from routes.mine_deliveries import mine_deliveries_bp
    app.register_blueprint(mine_deliveries_bp)

    # Fuel Transportation routes
    from routes.transportation import transportation_bp
    app.register_blueprint(transportation_bp)

    # Fuel Arrival routes
    from routes.arrivals import arrivals_bp
    app.register_blueprint(arrivals_bp)

register_blueprints(app)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 