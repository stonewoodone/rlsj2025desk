from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from app import db
from models import FuelArrival, FuelContract, FuelTransportation
from forms import FuelArrivalForm
from sqlalchemy import func

arrivals_bp = Blueprint('arrivals', __name__, url_prefix='/arrivals')

@arrivals_bp.route('/')
@login_required
def index():
    arrivals = FuelArrival.query.all()
    return render_template('arrivals/index.html', title='燃料到厂管理', arrivals=arrivals)

@arrivals_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = FuelArrivalForm()
    # 填充合同选择下拉框
    form.fuel_contract_id.choices = [(c.id, c.contract_name) for c in FuelContract.query.all()]
    
    if form.validate_on_submit():
        # 确保日期格式正确
        arrival_date = form.arrival_date.data
        
        # 验证合同是否存在
        fuel_contract = FuelContract.query.get(form.fuel_contract_id.data)
        if not fuel_contract:
            flash('选择的燃料合同不存在！', 'error')
            return render_template('arrivals/create.html', title='添加燃料到厂记录', form=form)
        
        arrival = FuelArrival(
            arrival_date=arrival_date,
            fuel_contract_id=form.fuel_contract_id.data,
            arrival_quantity=form.arrival_quantity.data,
            arrival_calorific_value=form.arrival_calorific_value.data,
            transport_type=form.transport_type.data
        )
        
        try:
            # 先保存到数据库以建立关联
            db.session.add(arrival)
            db.session.flush()  # 刷新会话，但不提交
            
            # 确保fuel_contract已正确关联
            if not arrival.fuel_contract:
                db.session.rollback()
                flash('无法关联燃料合同，请重试！', 'error')
                return render_template('arrivals/create.html', title='添加燃料到厂记录', form=form)
            
            # 现在可以安全地调用计算方法
            arrival.calculate_standard_coal()
            arrival.calculate_estimated_mine_quantity()
            arrival.calculate_estimated_mine_unit_price()
            arrival.calculate_arrival_value()
            arrival.calculate_arrival_standard_unit_price()
            
            # 最终提交
            db.session.commit()
            flash('燃料到厂记录已添加成功！')
            return redirect(url_for('arrivals.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'添加记录时出错：{str(e)}', 'error')
            print(f"错误详情：{str(e)}")
            return render_template('arrivals/create.html', title='添加燃料到厂记录', form=form)
    
    return render_template('arrivals/create.html', title='添加燃料到厂记录', form=form)

@arrivals_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    arrival = FuelArrival.query.get_or_404(id)
    form = FuelArrivalForm(obj=arrival)
    
    if form.validate_on_submit():
        try:
            # 验证合同是否存在
            fuel_contract = FuelContract.query.get(form.fuel_contract_id.data)
            if not fuel_contract:
                flash('选择的燃料合同不存在！', 'error')
                return render_template('arrivals/edit.html', title='编辑燃料到厂记录', form=form, arrival=arrival)
            
            # 更新字段
            arrival.arrival_date = form.arrival_date.data
            arrival.fuel_contract_id = form.fuel_contract_id.data
            arrival.arrival_quantity = form.arrival_quantity.data
            arrival.arrival_calorific_value = form.arrival_calorific_value.data
            arrival.transport_type = form.transport_type.data
            
            # 刷新会话以确保关联已更新
            db.session.flush()
            
            # 确保fuel_contract已正确关联
            if not arrival.fuel_contract:
                db.session.rollback()
                flash('无法关联燃料合同，请重试！', 'error')
                return render_template('arrivals/edit.html', title='编辑燃料到厂记录', form=form, arrival=arrival)
            
            # 重新计算所有值
            arrival.calculate_standard_coal()
            arrival.calculate_estimated_mine_quantity()
            arrival.calculate_estimated_mine_unit_price()
            arrival.calculate_arrival_value()
            arrival.calculate_arrival_standard_unit_price()
            
            db.session.commit()
            flash('燃料到厂记录更新成功！')
            return redirect(url_for('arrivals.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新记录时出错：{str(e)}', 'error')
            print(f"错误详情：{str(e)}")
            return render_template('arrivals/edit.html', title='编辑燃料到厂记录', form=form, arrival=arrival)
    
    return render_template('arrivals/edit.html', title='编辑燃料到厂记录', form=form, arrival=arrival)

@arrivals_bp.route('/delete/<int:id>')
@login_required
def delete(id):
    arrival = FuelArrival.query.get_or_404(id)
    db.session.delete(arrival)
    db.session.commit()
    flash('燃料到厂记录删除成功！')
    return redirect(url_for('arrivals.index'))

@arrivals_bp.route('/get_contract_details/<int:contract_id>')
@login_required
def get_contract_details(contract_id):
    contract = FuelContract.query.get_or_404(contract_id)
    
    # Get the total transportation amount for this contract
    total_transport_amount = db.session.query(func.sum(FuelTransportation.transportation_amount))\
        .filter(FuelTransportation.fuel_contract_id == contract_id)\
        .scalar() or 0
    
    return jsonify({
        'contract_type': contract.contract_type,
        'total_transport_amount': total_transport_amount
    }) 