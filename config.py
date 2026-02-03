import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Flask 密钥 - 生产环境请更换为随机字符串
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-in-production'
    
    # SQLite 数据库路径
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 应用配置
    APP_NAME = 'Personal Life OS'
    
    # PushPlus 微信推送配置 (可选)
    # 访问 https://www.pushplus.plus 获取 Token
    PUSHPLUS_TOKEN = os.environ.get('PUSHPLUS_TOKEN') or ''
