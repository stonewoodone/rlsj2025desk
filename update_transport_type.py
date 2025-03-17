from flask import Flask
import os
from extensions import db
from models import FuelContract, Supplier

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-testing')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///fuel_settlement.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def update_transport_types():
    """为现有的燃料合同记录设置默认的transport_type值"""
    with app.app_context():
        # 获取所有没有transport_type的合同
        contracts = FuelContract.query.filter(FuelContract.transport_type.is_(None)).all()
        print(f"找到{len(contracts)}个没有设置拉运类型的合同")
        
        for contract in contracts:
            # 获取供应商
            supplier = Supplier.query.get(contract.supplier_id)
            if not supplier:
                print(f"警告: 合同ID {contract.id} 没有关联的供应商，设置默认拉运类型为'汽运'")
                contract.transport_type = '汽运'
                continue
                
            supplier_name = supplier.short_name
            
            # 根据供应商设置默认的拉运类型
            if supplier_name in ['富康源', '华泓', '焦煤物流', '金辛达', '晋牛', '三交河', '山凹', '四明山', '雪坪', '野川']:
                contract.transport_type = '汽运'
                print(f"合同 '{contract.contract_name}' (供应商: {supplier_name}) 设置为汽运")
            elif supplier_name in ['小峪', '龙泉', '炉峪口']:
                contract.transport_type = '火车直发'
                print(f"合同 '{contract.contract_name}' (供应商: {supplier_name}) 设置为火车直发")
            elif supplier_name in ['北辛窑', '莲盛']:
                contract.transport_type = '火车短倒'
                print(f"合同 '{contract.contract_name}' (供应商: {supplier_name}) 设置为火车短倒")
            else:
                # 默认设置为汽运
                contract.transport_type = '汽运'
                print(f"合同 '{contract.contract_name}' (供应商: {supplier_name}) 设置为默认值汽运")
        
        # 提交更改
        db.session.commit()
        print("所有合同的拉运类型已更新完成")

if __name__ == '__main__':
    update_transport_types()
    print("脚本执行完成") 