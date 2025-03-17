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
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
   .\venv1\Scripts\Activate.ps1
   ```

3. 安装依赖包：
   ```bash
   pip install -r requirements.txt
   ```


4. 运行应用：
   ```bash
   python run.py
   ```

3. 在浏览器中访问：
   ```
   http://127.0.0.1:5003
   ```

