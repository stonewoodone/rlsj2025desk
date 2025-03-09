# 燃料结算系统

这是一个用于电厂燃料结算管理的系统，包括供应商管理、燃料合同管理、燃料矿发管理、燃料拉运管理和燃料到厂管理等功能。

## 系统功能

- **供应商管理**：添加、编辑、删除供应商信息，支持筛选和排序
- **燃料合同管理**：添加、编辑、删除燃料合同信息，支持筛选和排序
- **燃料矿发管理**：记录燃料矿发数据，自动计算煤款
- **燃料拉运管理**：记录燃料拉运数据，并提供拉运汇总功能
- **燃料到厂管理**：记录燃料到厂数据，自动计算标煤量和入厂标单
- **数据导出**：将系统数据导出为Excel文件

## 系统要求

- Python 3.8+
- Flask 2.0+
- SQLite 3
- 现代浏览器（Chrome、Firefox、Edge等）

## 安装和运行说明

### 方法一：使用 Flask 命令运行（推荐）

1. 克隆或下载项目代码到本地

2. 创建并激活虚拟环境：
   ```bash
   # 创建虚拟环境
   python -m venv new_venv
   
   # 激活虚拟环境（Windows）
   new_venv\Scripts\activate
   
   # 激活虚拟环境（macOS/Linux）
   source new_venv/bin/activate
   ```

3. 安装依赖包：
   ```bash
   pip install -r requirements.txt
   ```

4. 初始化数据库（如果是首次运行）：
   ```bash
   flask shell
   ```
   
   在打开的Python shell中执行：
   ```python
   from app import db
   from models import User
   
   db.create_all()
   
   # 创建管理员用户
   if not User.query.filter_by(username='admin').first():
       user = User(username='admin', email='admin@example.com')
       user.set_password('admin')
       db.session.add(user)
       db.session.commit()
   
   exit()
   ```

5. 运行应用：
   ```bash
   flask run -p 5003
   ```

6. 在浏览器中访问：
   ```
   http://127.0.0.1:5003
   ```

### 方法二：使用 Python 直接运行

1. 完成上述步骤1-4

2. 运行应用：
   ```bash
   python app.py
   ```

3. 在浏览器中访问：
   ```
   http://127.0.0.1:5003
   ```

## 登录信息

默认管理员账号：
- 用户名：`admin`
- 密码：`admin`

## 常见问题解决

### 登录问题

如果无法登录，请尝试以下步骤：

1. 确保输入正确的用户名和密码（区分大小写）
2. 清除浏览器缓存和Cookie
3. 重新启动Flask应用
4. 如果仍然无法登录，可以重新创建管理员用户：
   ```bash
   flask shell
   ```
   
   在Python shell中执行：
   ```python
   from app import db
   from models import User
   
   # 删除现有管理员用户
   admin = User.query.filter_by(username='admin').first()
   if admin:
       db.session.delete(admin)
       db.session.commit()
   
   # 创建新管理员用户
   user = User(username='admin', email='admin@example.com')
   user.set_password('admin')
   db.session.add(user)
   db.session.commit()
   
   exit()
   ```

### 数据库问题

如果遇到数据库相关错误，可以尝试重新初始化数据库：

1. 停止Flask应用
2. 删除`instance`目录下的`fuel_settlement.db`文件
3. 重新执行初始化数据库的步骤
4. 重启Flask应用

### 依赖包问题

如果安装依赖包时遇到问题，可以尝试：

```bash
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

## 使用说明

### 供应商管理

1. 登录系统后，点击导航栏中的"供应商管理"
2. 点击"添加供应商"按钮创建新供应商
3. 填写供应商信息（简称、全称、类型、二级单位）
4. 点击"提交"按钮保存
5. 可以使用筛选和排序功能快速查找供应商

### 燃料合同管理

1. 点击导航栏中的"燃料合同管理"
2. 点击"添加燃料合同"按钮创建新合同
3. 填写合同信息（日期、名称、类型、热值、单价等）
4. 选择关联的供应商
5. 点击"提交"按钮保存
6. 可以使用筛选和排序功能快速查找合同

### 燃料矿发管理

1. 点击导航栏中的"燃料矿发管理"
2. 点击"添加燃料矿发记录"按钮创建新矿发记录
3. 选择供应商，系统会自动加载该供应商的合同列表
4. 选择合同后，系统会自动填充矿发热值和单价
5. 填写矿发数量，系统会自动计算煤款
6. 点击"提交"按钮保存
7. 可以使用筛选和排序功能快速查找矿发记录

### 燃料拉运管理

1. 点击导航栏中的"燃料拉运管理"
2. 点击"添加燃料拉运记录"按钮创建新拉运记录
3. 选择合同，填写拉运日期、类型、单价、数量等信息
4. 系统会自动计算运输金额
5. 点击"提交"按钮保存
6. 可以使用筛选和排序功能快速查找拉运记录

### 燃料到厂管理

1. 点击导航栏中的"燃料到厂管理"
2. 点击"添加燃料到厂记录"按钮创建新到厂记录
3. 选择合同，填写到厂日期、数量、热值和拉运类型
4. 系统会自动计算到厂标煤量、矿发数量估算、矿发单价估算和入厂标单
5. 点击"提交"按钮保存
6. 可以使用筛选和排序功能快速查找到厂记录

### 数据导出

1. 在各管理页面中点击"导出数据"按钮
2. 系统将生成包含所有模块数据的Excel文件并下载

## 开发者信息

如需进一步开发或定制系统，请参考以下文件结构：

- `app.py`：应用程序主文件
- `models.py`：数据库模型定义
- `forms.py`：表单类定义
- `routes/`：路由文件目录
- `templates/`：HTML模板文件目录
- `static/`：静态资源文件目录

## 许可证

本项目采用MIT许可证。详情请参阅LICENSE文件。 