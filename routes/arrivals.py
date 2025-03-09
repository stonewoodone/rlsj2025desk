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
    if form.validate_on_submit():
        arrival = FuelArrival(
            arrival_date=form.arrival_date.data,
            fuel_contract_id=form.fuel_contract_id.data,
            arrival_quantity=form.arrival_quantity.data,
            arrival_calorific_value=form.arrival_calorific_value.data,
            transport_type=form.transport_type.data
        )
        
        # Calculate standard coal
        arrival.calculate_standard_coal()
        
        # Calculate estimated mine quantity
        arrival.calculate_estimated_mine_quantity()
        
        # Calculate estimated mine unit price
        arrival.calculate_estimated_mine_unit_price()
        
        # Calculate arrival value
        arrival.calculate_arrival_value()
        
        # Calculate arrival standard unit price
        arrival.calculate_arrival_standard_unit_price()
        
        db.session.add(arrival)
        db.session.commit()
        flash('燃料到厂记录添加成功！')
        return redirect(url_for('arrivals.index'))
    return render_template('arrivals/create.html', title='添加燃料到厂记录', form=form)

@arrivals_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    arrival = FuelArrival.query.get_or_404(id)
    form = FuelArrivalForm(obj=arrival)
    if form.validate_on_submit():
        arrival.arrival_date = form.arrival_date.data
        arrival.fuel_contract_id = form.fuel_contract_id.data
        arrival.arrival_quantity = form.arrival_quantity.data
        arrival.arrival_calorific_value = form.arrival_calorific_value.data
        arrival.transport_type = form.transport_type.data
        
        # Recalculate all values
        arrival.calculate_standard_coal()
        arrival.calculate_estimated_mine_quantity()
        arrival.calculate_estimated_mine_unit_price()
        arrival.calculate_arrival_value()
        arrival.calculate_arrival_standard_unit_price()
        
        db.session.commit()
        flash('燃料到厂记录更新成功！')
        return redirect(url_for('arrivals.index'))
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