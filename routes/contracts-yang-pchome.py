from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from extensions import db
from models import FuelContract, Supplier
from forms import FuelContractForm
from datetime import datetime

contracts_bp = Blueprint('contracts', __name__, url_prefix='/contracts')

@contracts_bp.route('/')
@login_required
def index():
    contracts = FuelContract.query.all()
    return render_template('contracts/index.html', title='燃料合同管理', contracts=contracts)

@contracts_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = FuelContractForm()
    if form.validate_on_submit():
        try:
            # Calculate mine unit price based on contract type and calorific value
            mine_unit_price = calculate_mine_unit_price(
                form.contract_type.data,
                form.mine_calorific_value.data,
                form.contract_name.data
            )
            
            contract = FuelContract(
                contract_date=form.contract_date.data,
                contract_name=form.contract_name.data,
                contract_type=form.contract_type.data,
                mine_calorific_value=form.mine_calorific_value.data,
                mine_unit_price=mine_unit_price if mine_unit_price else form.mine_unit_price.data,
                supplier_id=form.supplier_id.data
            )
            db.session.add(contract)
            db.session.commit()
            flash('燃料合同添加成功！')
            return redirect(url_for('contracts.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'添加合同时出错：{str(e)}', 'danger')
            print(f"添加合同错误: {str(e)}")
    return render_template('contracts/create.html', title='添加燃料合同', form=form)

@contracts_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    contract = FuelContract.query.get_or_404(id)
    form = FuelContractForm(obj=contract)
    if form.validate_on_submit():
        try:
            # Calculate mine unit price based on contract type and calorific value
            mine_unit_price = calculate_mine_unit_price(
                form.contract_type.data,
                form.mine_calorific_value.data,
                form.contract_name.data
            )
            
            contract.contract_date = form.contract_date.data
            contract.contract_name = form.contract_name.data
            contract.contract_type = form.contract_type.data
            contract.mine_calorific_value = form.mine_calorific_value.data
            contract.mine_unit_price = mine_unit_price if mine_unit_price else form.mine_unit_price.data
            contract.supplier_id = form.supplier_id.data
            db.session.commit()
            flash('燃料合同更新成功！')
            return redirect(url_for('contracts.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新合同时出错：{str(e)}', 'danger')
            print(f"更新合同错误: {str(e)}")
    return render_template('contracts/edit.html', title='编辑燃料合同', form=form, contract=contract)

@contracts_bp.route('/delete/<int:id>')
@login_required
def delete(id):
    contract = FuelContract.query.get_or_404(id)
    db.session.delete(contract)
    db.session.commit()
    flash('燃料合同删除成功！')
    return redirect(url_for('contracts.index'))

@contracts_bp.route('/get_supplier_name/<int:supplier_id>')
@login_required
def get_supplier_name(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    return jsonify({'full_name': supplier.full_name})

@contracts_bp.route('/calculate_price', methods=['POST'])
@login_required
def calculate_price():
    # 添加调试信息
    print("收到计算价格请求")
    print("表单数据:", request.form)
    
    try:
        contract_type = request.form.get('contract_type')
        calorific_value = float(request.form.get('calorific_value', 0))
        contract_name = request.form.get('contract_name', '')
        
        print(f"合同类型: {contract_type}")
        print(f"热值: {calorific_value}")
        print(f"合同名称: {contract_name}")
        
        price = calculate_mine_unit_price(contract_type, calorific_value, contract_name)
        print(f"计算的价格: {price}")
        
        return jsonify({'price': price})
    except Exception as e:
        print(f"计算价格时出错: {str(e)}")
        return jsonify({'error': str(e)}), 400

def calculate_mine_unit_price(contract_type, calorific_value, contract_name=''):
    """Calculate mine unit price based on contract type and calorific value"""
    if contract_type == '集团煤':
        if calorific_value >= 4300:
            return 570 / 5500 * calorific_value
        elif calorific_value >= 3800:
            return 0.0806 * calorific_value
        elif calorific_value >= 3300:
            return 0.0706 * calorific_value
        elif calorific_value >= 2500:
            return 0.0676 * calorific_value
        else:
            return 0.02 * calorific_value
    elif contract_type == '焦煤长协':
        if '三交河' in contract_name:
            return 353
        elif '雪坪' in contract_name:
            return 211
        elif '金辛达' in contract_name:
            return 353
        elif '晋牛' in contract_name:
            return 372
    
    # For other contract types, return None to use manual input
    return None 