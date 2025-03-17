from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from extensions import db
from models import Supplier
from forms import SupplierForm

suppliers_bp = Blueprint('suppliers', __name__, url_prefix='/suppliers')

@suppliers_bp.route('/')
@login_required
def index():
    suppliers = Supplier.query.all()
    return render_template('suppliers/index.html', title='供应商管理', suppliers=suppliers)

@suppliers_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = SupplierForm()
    if form.validate_on_submit():
        supplier = Supplier(
            short_name=form.short_name.data,
            full_name=form.full_name.data,
            supplier_type=form.supplier_type.data,
            secondary_unit=form.secondary_unit.data
        )
        db.session.add(supplier)
        db.session.commit()
        flash('供应商添加成功！')
        return redirect(url_for('suppliers.index'))
    return render_template('suppliers/create.html', title='添加供应商', form=form)

@suppliers_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    supplier = Supplier.query.get_or_404(id)
    form = SupplierForm(obj=supplier)
    if form.validate_on_submit():
        supplier.short_name = form.short_name.data
        supplier.full_name = form.full_name.data
        supplier.supplier_type = form.supplier_type.data
        supplier.secondary_unit = form.secondary_unit.data
        db.session.commit()
        flash('供应商更新成功！')
        return redirect(url_for('suppliers.index'))
    return render_template('suppliers/edit.html', title='编辑供应商', form=form, supplier=supplier)

@suppliers_bp.route('/delete/<int:id>')
@login_required
def delete(id):
    supplier = Supplier.query.get_or_404(id)
    db.session.delete(supplier)
    db.session.commit()
    flash('供应商删除成功！')
    return redirect(url_for('suppliers.index')) 