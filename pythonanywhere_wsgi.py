# PythonAnywhere WSGI 配置文件
# 此文件告诉 PythonAnywhere 如何启动你的 Flask 应用

import sys
import os

# 添加你的项目路径 (需要替换为你的 PythonAnywhere 用户名)
# 例如: /home/你的用户名/personal-life-os
project_home = '/home/YOUR_USERNAME/personal-life-os'

if project_home not in sys.path:
    sys.path.insert(0, project_home)

# 设置环境变量
os.environ['FLASK_ENV'] = 'production'

# 导入 Flask 应用
from app import app as application  # noqa
