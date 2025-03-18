from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, FloatField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Optional
from datetime import datetime

class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('登录')

class RegistrationForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    password2 = PasswordField('确认密码', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('注册')
    
    def validate_username(self, username):
        from models import User
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('该用户名已被使用，请使用其他用户名。')
    
    def validate_email(self, email):
        from models import User
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('该邮箱已被注册，请使用其他邮箱。')

class SupplierForm(FlaskForm):
    short_name = StringField('供应商简称', validators=[DataRequired()])
    full_name = StringField('供应商全称', validators=[DataRequired()])
    supplier_type = SelectField('所属类型', choices=[
        ('集团煤', '集团煤'),
        ('焦煤', '焦煤'),
        ('地方煤', '地方煤'),
        ('市场煤', '市场煤')
    ], validators=[DataRequired()])
    secondary_unit = SelectField('二级单位', choices=[
        ('煤业公司', '煤业公司'),
        ('朔州公司', '朔州公司'),
        ('煤气化', '煤气化'),
        ('晋城公司', '晋城公司'),
        ('装备公司', '装备公司'),
        ('朔州煤电', '朔州煤电'),
        ('焦煤长协', '焦煤长协'),
        ('焦煤贸易', '焦煤贸易'),
        ('地方长协', '地方长协')
    ], validators=[DataRequired()])
    submit = SubmitField('提交')

class FuelContractForm(FlaskForm):
    contract_date = DateField('合同日期', format='%Y-%m', validators=[DataRequired()], render_kw={"placeholder": "YYYY-MM"})
    contract_name = StringField('燃料合同名称', validators=[DataRequired()])
    contract_type = SelectField('合同类型', choices=[
        ('集团煤', '集团煤'),
        ('焦煤长协', '焦煤长协'),
        ('地方长协', '地方长协'),
        ('焦煤贸易', '焦煤贸易')
    ], validators=[DataRequired()])
    supplier_id = SelectField('供应商', coerce=int, validators=[DataRequired()])
    mine_calorific_value = FloatField('矿发热值', validators=[DataRequired()])
    mine_unit_price = FloatField('矿发单价', validators=[DataRequired()])
    transport_type = SelectField('拉运类型', choices=[
        ('汽运', '汽运'),
        ('火车短倒', '火车短倒'),
        ('火车直发', '火车直发')
    ], validators=[DataRequired()])
    submit = SubmitField('提交')
    
    def __init__(self, *args, **kwargs):
        super(FuelContractForm, self).__init__(*args, **kwargs)
        from models import Supplier
        self.supplier_id.choices = [(s.id, s.short_name) for s in Supplier.query.all()]

class FuelMineDeliveryForm(FlaskForm):
    supplier_id = SelectField('供应商', validators=[DataRequired()])
    fuel_contract_id = SelectField('燃料合同名称', validators=[DataRequired()])
    mine_quantity = FloatField('矿发数量', validators=[DataRequired()])
    mine_calorific_value = FloatField('矿发热值', validators=[Optional()])
    mine_unit_price = FloatField('矿发单价', validators=[Optional()])
    submit = SubmitField('提交')
    
    def __init__(self, *args, **kwargs):
        super(FuelMineDeliveryForm, self).__init__(*args, **kwargs)
        from models import Supplier, FuelContract
        self.supplier_id.choices = [('', '-- 请选择供应商 --')] + [(str(s.id), s.short_name) for s in Supplier.query.all()]
        
        # 初始化时只设置一个空选项，实际选项将通过AJAX动态加载
        self.fuel_contract_id.choices = [('', '-- 请选择合同 --')]
        
        # 如果是编辑表单，预加载所有合同作为可能的选项，以通过验证
        if 'obj' in kwargs and kwargs['obj'] is not None:
            all_contracts = [(str(c.id), c.contract_name) for c in FuelContract.query.all()]
            self.fuel_contract_id.choices.extend(all_contracts)
        
    def validate_supplier_id(self, field):
        if field.data == '':
            raise ValidationError('请选择供应商')
            
    def validate_fuel_contract_id(self, field):
        if field.data == '':
            raise ValidationError('请选择燃料合同')
        
        # 验证时动态检查合同ID是否有效
        from models import FuelContract
        if not FuelContract.query.get(int(field.data)):
            raise ValidationError('无效的合同选择')

class FuelTransportationForm(FlaskForm):
    transport_date = DateField('承运日期', format='%Y-%m', validators=[DataRequired()])
    fuel_contract_id = SelectField('燃料合同名称', validators=[DataRequired()])
    transport_type = SelectField('拉运类型', choices=[
        ('上站短倒', '上站短倒'),
        ('上站站台', '上站站台'),
        ('铁路运输', '铁路运输'),
        ('下站站台', '下站站台'),
        ('下站短倒', '下站短倒'),
        ('汽车运输', '汽车运输')
    ], validators=[DataRequired()])
    transport_unit_price = FloatField('拉运单价', validators=[DataRequired()])
    transport_location = StringField('拉运地点', validators=[DataRequired()])
    transport_contract = StringField('拉运合同', validators=[DataRequired()])
    transport_company = StringField('拉运单位', validators=[DataRequired()])
    transportation_unit_price = FloatField('运输单价', validators=[DataRequired()])
    transport_quantity = FloatField('拉运数量', validators=[DataRequired()])
    submit = SubmitField('提交')
    
    def __init__(self, *args, **kwargs):
        super(FuelTransportationForm, self).__init__(*args, **kwargs)
        from models import FuelContract
        self.fuel_contract_id.choices = [(str(c.id), c.contract_name) for c in FuelContract.query.all()]
        
    def validate_fuel_contract_id(self, field):
        if field.data == '':
            raise ValidationError('请选择燃料合同')

class FuelArrivalForm(FlaskForm):
    arrival_date = DateField('到厂日期', format='%Y-%m', validators=[DataRequired()], render_kw={"placeholder": "YYYY-MM"})
    fuel_contract_id = SelectField('燃料合同', coerce=int, validators=[DataRequired()])
    arrival_quantity = FloatField('到厂数量', validators=[DataRequired()])
    arrival_calorific_value = FloatField('到厂热值', validators=[DataRequired()])
    transport_type = SelectField('拉运类型', 
                                choices=[('汽运', '汽运'), ('火车短倒', '火车短倒'), ('火车直发', '火车直发')],
                                validators=[DataRequired()])
    submit = SubmitField('提交')
    
    def __init__(self, *args, **kwargs):
        super(FuelArrivalForm, self).__init__(*args, **kwargs)
        from models import FuelContract
        self.fuel_contract_id.choices = [(c.id, c.contract_name) for c in FuelContract.query.all()] 