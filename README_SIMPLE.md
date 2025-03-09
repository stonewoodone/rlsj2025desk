# 燃料结算系统（简化版）

这是燃料结算系统的简化版本，不依赖 Pandas 和 NumPy，避免了版本兼容性问题。

## 系统功能

- **用户认证**：用户登录和注销
- **个人资料**：查看和编辑个人资料
- **数据导出**：将系统数据导出为CSV文件

## 安装步骤

1. 创建虚拟环境：
   ```
   python -m venv venv_simple
   ```

2. 激活虚拟环境：
   - Windows:
   ```
   venv_simple\Scripts\activate
   ```
   - macOS/Linux:
   ```
   source venv_simple/bin/activate
   ```

3. 安装依赖：
   ```
   pip install -r requirements_simple.txt
   ```

4. 初始化数据库：
   ```
   python init_db_simple.py
   ```

5. 运行应用程序：
   ```
   python run_simple.py
   ```

6. 在浏览器中访问：
   ```
   http://localhost:5002
   ```

## 登录信息

默认管理员账号：
- 用户名：admin
- 密码：admin

## 文件说明

- `app_simple.py`：应用程序主文件
- `models.py`：数据库模型
- `init_db_simple.py`：数据库初始化脚本
- `run_simple.py`：应用程序运行脚本
- `auth_simple.py`：认证路由

## 使用说明

### 登录系统

1. 访问 http://localhost:5002
2. 点击"登录"按钮
3. 输入用户名和密码（admin/admin）
4. 点击"登录"按钮

### 查看个人资料

1. 登录系统后，点击导航栏中的"个人资料"
2. 查看个人资料信息

### 数据导出

1. 登录系统后，点击导航栏中的"导出数据"
2. 系统将生成包含数据的CSV文件并下载

## 注意事项

- 这是一个简化版本的应用程序，只包含基本功能
- 完整版本需要安装Pandas和NumPy，可能会遇到版本兼容性问题
- 如果需要完整功能，请参考主README.md文件中的说明使用完整版本
- 建议使用Chrome、Firefox或Edge浏览器访问系统 