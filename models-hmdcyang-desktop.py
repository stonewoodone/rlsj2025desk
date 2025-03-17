from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import func

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    short_name = db.Column(db.String(64), unique=True, index=True)
    full_name = db.Column(db.String(128), unique=True)
    supplier_type = db.Column(db.String(64))  # 集团煤、焦煤、地方煤、市场煤
    secondary_unit = db.Column(db.String(64))  # 二级单位
    
    # Relationships
    fuel_contracts = db.relationship('FuelContract', backref='supplier', lazy='dynamic')
    fuel_mine_deliveries = db.relationship('FuelMineDelivery', backref='supplier', lazy='dynamic')

class FuelContract(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contract_date = db.Column(db.Date, index=True)
    contract_name = db.Column(db.String(128), unique=True, index=True)
    contract_type = db.Column(db.String(64))  # 集团煤、焦煤长协、地方长协、焦煤贸易
    mine_calorific_value = db.Column(db.Float)  # 矿发热值
    mine_unit_price = db.Column(db.Float)  # 矿发单价
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))
    
    # Relationships
    fuel_mine_deliveries = db.relationship('FuelMineDelivery', backref='fuel_contract', lazy='dynamic')
    fuel_transportations = db.relationship('FuelTransportation', backref='fuel_contract', lazy='dynamic')
    fuel_arrivals = db.relationship('FuelArrival', backref='fuel_contract', lazy='dynamic')

class FuelMineDelivery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))
    fuel_contract_id = db.Column(db.Integer, db.ForeignKey('fuel_contract.id'))
    mine_quantity = db.Column(db.Float)  # 矿发数量
    mine_calorific_value = db.Column(db.Float)  # 矿发热值
    mine_unit_price = db.Column(db.Float)  # 矿发单价
    coal_payment = db.Column(db.Float)  # 煤款
    
    def calculate_coal_payment(self):
        try:
            if self.mine_quantity is None or self.mine_unit_price is None:
                print(f"警告: 矿发数量或单价为空，无法计算煤款。数量={self.mine_quantity}, 单价={self.mine_unit_price}")
                self.coal_payment = 0
            else:
                self.coal_payment = self.mine_quantity * self.mine_unit_price
                print(f"计算煤款: {self.mine_quantity} * {self.mine_unit_price} = {self.coal_payment}")
        except Exception as e:
            print(f"计算煤款时出错: {str(e)}")
            self.coal_payment = 0

class FuelTransportation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transport_date = db.Column(db.Date, index=True)
    fuel_contract_id = db.Column(db.Integer, db.ForeignKey('fuel_contract.id'))
    transport_type = db.Column(db.String(64))  # 上站短倒、上站站台、铁路运输、下站站台、下站短倒、汽车运输
    transport_unit_price = db.Column(db.Float)  # 拉运单价
    transport_location = db.Column(db.String(128))  # 拉运地点
    transport_contract = db.Column(db.String(128))  # 拉运合同
    transportation_unit_price = db.Column(db.Float)  # 运输单价
    transport_quantity = db.Column(db.Float)  # 拉运数量
    transportation_amount = db.Column(db.Float)  # 运输金额
    
    def calculate_transportation_amount(self):
        self.transportation_amount = self.transport_quantity * self.transportation_unit_price

class FuelArrival(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    arrival_date = db.Column(db.Date, index=True)
    fuel_contract_id = db.Column(db.Integer, db.ForeignKey('fuel_contract.id'))
    arrival_quantity = db.Column(db.Float)  # 到厂数量
    arrival_calorific_value = db.Column(db.Float)  # 到厂热值
    arrival_standard_coal = db.Column(db.Float)  # 到厂标煤量
    transport_type = db.Column(db.String(64))  # 拉运类型：汽运、火车短倒、火车直发
    estimated_mine_quantity = db.Column(db.Float)  # 矿发数量估算
    estimated_mine_unit_price = db.Column(db.Float)  # 矿发单价估算
    arrival_value = db.Column(db.Float)  # 到厂价值
    arrival_standard_unit_price = db.Column(db.Float)  # 入厂标单
    
    def calculate_standard_coal(self):
        self.arrival_standard_coal = self.arrival_quantity * self.arrival_calorific_value / 7000
    
    def calculate_estimated_mine_quantity(self):
        if self.transport_type == '汽运':
            self.estimated_mine_quantity = self.arrival_quantity / 0.99
        elif self.transport_type == '火车短倒':
            self.estimated_mine_quantity = self.arrival_quantity / 0.98
        elif self.transport_type == '火车直发':
            self.estimated_mine_quantity = self.arrival_quantity / 0.985
    
    def calculate_estimated_mine_unit_price(self):
        # 检查fuel_contract是否存在
        if not self.fuel_contract:
            print(f"警告: fuel_contract为空，无法计算矿发单价估算")
            self.estimated_mine_unit_price = 0
            return
            
        # Get the contract type from the associated fuel contract
        contract_type = self.fuel_contract.contract_type
        estimated_calorific_value = self.arrival_calorific_value + 100
        
        if contract_type == '集团煤':
            if estimated_calorific_value >= 4300:
                self.estimated_mine_unit_price = 570 / 5500 * estimated_calorific_value
            elif estimated_calorific_value >= 3800:
                self.estimated_mine_unit_price = 0.0806 * estimated_calorific_value
            elif estimated_calorific_value >= 3300:
                self.estimated_mine_unit_price = 0.0706 * estimated_calorific_value
            elif estimated_calorific_value >= 2500:
                self.estimated_mine_unit_price = 0.0676 * estimated_calorific_value
            else:
                self.estimated_mine_unit_price = 0.02 * estimated_calorific_value
        elif contract_type == '焦煤长协':
            contract_name = self.fuel_contract.contract_name
            if '三交河' in contract_name:
                self.estimated_mine_unit_price = 353
            elif '雪坪' in contract_name:
                self.estimated_mine_unit_price = 211
            elif '金辛达' in contract_name:
                self.estimated_mine_unit_price = 353
            elif '晋牛' in contract_name:
                self.estimated_mine_unit_price = 372
            else:
                # Default to the contract's mine unit price
                self.estimated_mine_unit_price = self.fuel_contract.mine_unit_price
        else:
            # For other contract types, use the contract's mine unit price
            self.estimated_mine_unit_price = self.fuel_contract.mine_unit_price
    
    def calculate_arrival_value(self):
        # 检查fuel_contract_id是否存在
        if not self.fuel_contract_id:
            print(f"警告: fuel_contract_id为空，无法计算到厂价值")
            self.arrival_value = 0
            return
            
        # Get the total transportation amount for this contract
        from app import db
        
        total_transport_amount = db.session.query(func.sum(FuelTransportation.transportation_amount))\
            .filter(FuelTransportation.fuel_contract_id == self.fuel_contract_id)\
            .scalar() or 0
        
        self.arrival_value = (self.estimated_mine_quantity * self.estimated_mine_unit_price / 1.13) + (total_transport_amount / 1.09)
    
    def calculate_arrival_standard_unit_price(self):
        if self.arrival_standard_coal > 0:
            self.arrival_standard_unit_price = self.arrival_value / self.arrival_standard_coal
        else:
            self.arrival_standard_unit_price = 0 