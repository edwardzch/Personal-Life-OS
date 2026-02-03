from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """用户表 - 单用户系统"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Memo(db.Model):
    """速记条目表"""
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    tags = db.Column(db.String(200))  # 逗号分隔的标签
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Memo {self.id}>'


class Bookmark(db.Model):
    """稍后读书签表"""
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='unread')  # unread, read, archived
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Bookmark {self.title}>'


class Reminder(db.Model):
    """提醒任务表"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    target_datetime = db.Column(db.DateTime, nullable=False)
    is_done = db.Column(db.Boolean, default=False)
    notified = db.Column(db.Boolean, default=False)  # 是否已发送通知
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Reminder {self.title}>'
