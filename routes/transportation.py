from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from extensions import db
from models import FuelTransportation, FuelContract, FuelMineDelivery, FuelArrival
from forms import FuelTransportationForm
from sqlalchemy import func

transportation_bp = Blueprint('transportation', __name__, url_prefix='/transportation')

@transportation_bp.route('/')
@login_required
def index():
    transportations = FuelTransportation.query.all()
    return render_template('transportation/index.html', title='燃料拉运管理', transportations=transportations)

@transportation_bp.route('/summary')
@login_required
def summary():
    # Group by contract and date
    transport_summary = db.session.query(
        FuelTransportation.transport_date,
        FuelContract.contract_name,
        func.sum(FuelTransportation.transportation_unit_price).label('total_unit_price'),
        func.sum(FuelTransportation.transportation_amount).label('total_amount')
    ).join(FuelContract).group_by(
        FuelTransportation.transport_date,
        FuelContract.contract_name
    ).all()
    
    return render_template('transportation/summary.html', title='燃料拉运汇总', summary=transport_summary)

@transportation_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = FuelTransportationForm()
    if form.validate_on_submit():
        try:
            # 确保合同ID是整数
            fuel_contract_id = int(form.fuel_contract_id.data)
            transportation = FuelTransportation(
                transport_date=form.transport_date.data,
                fuel_contract_id=fuel_contract_id,
                transport_type=form.transport_type.data,
                transport_unit_price=form.transport_unit_price.data,
                transport_location=form.transport_location.data,
                transport_contract=form.transport_contract.data,
                transportation_unit_price=form.transportation_unit_price.data,
                transport_quantity=form.transport_quantity.data
            )
            transportation.calculate_transportation_amount()
            db.session.add(transportation)
            db.session.commit()
            flash('燃料拉运记录添加成功！')
            return redirect(url_for('transportation.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'保存记录时出错: {str(e)}', 'danger')
    return render_template('transportation/create.html', title='添加燃料拉运记录', form=form)

@transportation_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    transportation = FuelTransportation.query.get_or_404(id)
    form = FuelTransportationForm(obj=transportation)
    if form.validate_on_submit():
        try:
            # 确保合同ID是整数
            fuel_contract_id = int(form.fuel_contract_id.data)
            transportation.transport_date = form.transport_date.data
            transportation.fuel_contract_id = fuel_contract_id
            transportation.transport_type = form.transport_type.data
            transportation.transport_unit_price = form.transport_unit_price.data
            transportation.transport_location = form.transport_location.data
            transportation.transport_contract = form.transport_contract.data
            transportation.transportation_unit_price = form.transportation_unit_price.data
            transportation.transport_quantity = form.transport_quantity.data
            transportation.calculate_transportation_amount()
            db.session.commit()
            flash('燃料拉运记录更新成功！')
            return redirect(url_for('transportation.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新记录时出错: {str(e)}', 'danger')
    return render_template('transportation/edit.html', title='编辑燃料拉运记录', form=form, transportation=transportation)

@transportation_bp.route('/delete/<int:id>')
@login_required
def delete(id):
    transportation = FuelTransportation.query.get_or_404(id)
    db.session.delete(transportation)
    db.session.commit()
    flash('燃料拉运记录删除成功！')
    return redirect(url_for('transportation.index'))

@transportation_bp.route('/get_transport_quantity/<int:contract_id>/<string:transport_type>')
@login_required
def get_transport_quantity(contract_id, transport_type):
    quantity = 0
    
    # For upper station, railway, and upper station platform types, use mine delivery quantity
    if transport_type in ['上站短倒', '上站站台', '铁路运输', '下站站台']:
        # Get the total mine delivery quantity for this contract
        mine_delivery = db.session.query(func.sum(FuelMineDelivery.mine_quantity))\
            .filter(FuelMineDelivery.fuel_contract_id == contract_id)\
            .scalar()
        quantity = mine_delivery if mine_delivery else 0
    
    # For lower station and car transportation types, use arrival quantity
    elif transport_type in ['下站短倒', '汽车运输']:
        # Get the total arrival quantity for this contract
        arrival = db.session.query(func.sum(FuelArrival.arrival_quantity))\
            .filter(FuelArrival.fuel_contract_id == contract_id)\
            .scalar()
        quantity = arrival if arrival else 0
    
    return jsonify({'quantity': quantity}) 