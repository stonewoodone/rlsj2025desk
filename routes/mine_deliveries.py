from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from app import db
from models import FuelMineDelivery, FuelContract, Supplier
from forms import FuelMineDeliveryForm

mine_deliveries_bp = Blueprint('mine_deliveries', __name__, url_prefix='/mine_deliveries')

@mine_deliveries_bp.route('/')
@login_required
def index():
    deliveries = FuelMineDelivery.query.all()
    return render_template('mine_deliveries/index.html', title='燃料矿发管理', deliveries=deliveries)

@mine_deliveries_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = FuelMineDeliveryForm()
    
    # 如果是POST请求，在验证前动态更新合同选项
    if request.method == 'POST':
        # 获取提交的供应商ID和合同ID
        supplier_id = request.form.get('supplier_id')
        contract_id = request.form.get('fuel_contract_id')
        print(f"表单提交数据 - 供应商ID: {supplier_id}, 合同ID: {contract_id}")
        
        # 如果有合同ID，将其添加到表单的合同选项中
        if contract_id:
            from models import FuelContract
            contract = FuelContract.query.get(int(contract_id))
            if contract:
                # 动态更新合同选项
                form.fuel_contract_id.choices.append((str(contract.id), contract.contract_name))
                print(f"已将合同 {contract_id} 添加到表单选项中")
        
        print("表单提交数据:", request.form)
        print("表单验证结果:", form.validate())
        if form.errors:
            print("表单错误:", form.errors)
    
    if form.validate_on_submit():
        try:
            print("表单验证通过，准备保存记录")
            # 确保供应商ID和合同ID是整数
            supplier_id = int(form.supplier_id.data)
            fuel_contract_id = int(form.fuel_contract_id.data)
            print(f"供应商ID: {supplier_id}, 合同ID: {fuel_contract_id}")
            
            # 获取其他表单数据
            mine_quantity = form.mine_quantity.data
            mine_calorific_value = form.mine_calorific_value.data
            mine_unit_price = form.mine_unit_price.data
            print(f"矿发数量: {mine_quantity}, 热值: {mine_calorific_value}, 单价: {mine_unit_price}")
            
            # 创建记录
            delivery = FuelMineDelivery(
                supplier_id=supplier_id,
                fuel_contract_id=fuel_contract_id,
                mine_quantity=mine_quantity,
                mine_calorific_value=mine_calorific_value,
                mine_unit_price=mine_unit_price
            )
            delivery.calculate_coal_payment()
            print(f"计算的煤款: {delivery.coal_payment}")
            
            # 保存记录
            db.session.add(delivery)
            db.session.commit()
            print("记录保存成功")
            
            flash('燃料矿发记录添加成功！')
            return redirect(url_for('mine_deliveries.index'))
        except Exception as e:
            db.session.rollback()
            print("保存记录时出错:", str(e))
            flash(f'保存记录时出错: {str(e)}', 'danger')
    else:
        print("表单验证失败")
    
    return render_template('mine_deliveries/create.html', title='添加燃料矿发记录', form=form)

@mine_deliveries_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    delivery = FuelMineDelivery.query.get_or_404(id)
    form = FuelMineDeliveryForm(obj=delivery)
    
    # 如果是POST请求，在验证前动态更新合同选项
    if request.method == 'POST':
        # 获取提交的供应商ID和合同ID
        supplier_id = request.form.get('supplier_id')
        contract_id = request.form.get('fuel_contract_id')
        print(f"编辑表单提交数据 - 供应商ID: {supplier_id}, 合同ID: {contract_id}")
        
        # 如果有合同ID，将其添加到表单的合同选项中
        if contract_id:
            from models import FuelContract
            contract = FuelContract.query.get(int(contract_id))
            if contract:
                # 检查是否已经在选项中
                contract_ids = [c[0] for c in form.fuel_contract_id.choices]
                if str(contract.id) not in contract_ids:
                    # 动态更新合同选项
                    form.fuel_contract_id.choices.append((str(contract.id), contract.contract_name))
                    print(f"已将合同 {contract_id} 添加到编辑表单选项中")
    
    if form.validate_on_submit():
        try:
            # 确保供应商ID和合同ID是整数
            supplier_id = int(form.supplier_id.data)
            fuel_contract_id = int(form.fuel_contract_id.data)
            delivery.supplier_id = supplier_id
            delivery.fuel_contract_id = fuel_contract_id
            delivery.mine_quantity = form.mine_quantity.data
            delivery.mine_calorific_value = form.mine_calorific_value.data
            delivery.mine_unit_price = form.mine_unit_price.data
            delivery.calculate_coal_payment()
            db.session.commit()
            flash('燃料矿发记录更新成功！')
            return redirect(url_for('mine_deliveries.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新记录时出错: {str(e)}', 'danger')
    return render_template('mine_deliveries/edit.html', title='编辑燃料矿发记录', form=form, delivery=delivery)

@mine_deliveries_bp.route('/delete/<int:id>')
@login_required
def delete(id):
    delivery = FuelMineDelivery.query.get_or_404(id)
    db.session.delete(delivery)
    db.session.commit()
    flash('燃料矿发记录删除成功！')
    return redirect(url_for('mine_deliveries.index'))

@mine_deliveries_bp.route('/get_contract_details/<int:contract_id>')
@login_required
def get_contract_details(contract_id):
    try:
        contract = FuelContract.query.get_or_404(contract_id)
        print(f"获取合同 {contract_id} 的详情: 热值={contract.mine_calorific_value}, 单价={contract.mine_unit_price}")
        return jsonify({
            'mine_calorific_value': contract.mine_calorific_value,
            'mine_unit_price': contract.mine_unit_price
        })
    except Exception as e:
        print(f"获取合同详情时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500

@mine_deliveries_bp.route('/get_supplier_contracts/<int:supplier_id>')
@login_required
def get_supplier_contracts(supplier_id):
    try:
        contracts = FuelContract.query.filter_by(supplier_id=supplier_id).all()
        print(f"找到供应商 {supplier_id} 的合同数量: {len(contracts)}")
        result = [{
            'id': str(c.id),
            'name': c.contract_name
        } for c in contracts]
        print("返回的合同列表:", result)
        return jsonify(result)
    except Exception as e:
        print(f"获取供应商合同时出错: {str(e)}")
        return jsonify([]), 500 