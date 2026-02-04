"""
数据库迁移脚本 - 添加 DataVersion 表
在 PythonAnywhere 上运行此脚本来创建新表
"""
import sys
sys.path.insert(0, '/home/你的用户名/Personal-Life-OS')  # 请修改为你的路径

from app import app, db
from models import DataVersion

with app.app_context():
    # 创建所有缺失的表
    db.create_all()
    print("数据库表已更新！")
    
    # 检查 DataVersion 表
    versions = DataVersion.get_all_versions()
    print(f"当前版本号: {versions}")
