import os
import markdown
from datetime import datetime, timezone, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from models import db, User, Memo, Bookmark, Reminder

# 创建 Flask 应用
app = Flask(__name__)
app.config.from_object(Config)

# 初始化扩展
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = '请先登录'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ==================== 认证路由 ====================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('用户名或密码错误', 'error')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# ==================== 主页路由 ====================

@app.route('/')
@login_required
def index():
    return redirect(url_for('memos'))


# ==================== 速记模块 ====================

@app.route('/memos')
@login_required
def memos():
    all_memos = Memo.query.order_by(Memo.created_at.desc()).all()
    return render_template('memos.html', memos=all_memos)


@app.route('/memos/tag/<tag>')
@login_required
def memos_by_tag(tag):
    """按标签筛选速记"""
    all_memos = Memo.query.filter(Memo.tags.contains(tag)).order_by(Memo.created_at.desc()).all()
    return render_template('memos.html', memos=all_memos, current_tag=tag)


@app.route('/memos/add', methods=['POST'])
@login_required
def add_memo():
    content = request.form.get('content', '').strip()
    tags = request.form.get('tags', '').strip()
    
    if content:
        memo = Memo(content=content, tags=tags)
        db.session.add(memo)
        db.session.commit()
    
    # HTMX 请求返回新增的单条记录 HTML
    if request.headers.get('HX-Request'):
        return render_template('partials/memo_item.html', memo=memo)
    
    return redirect(url_for('memos'))


@app.route('/memos/delete/<int:id>', methods=['DELETE'])
@login_required
def delete_memo(id):
    memo = Memo.query.get_or_404(id)
    db.session.delete(memo)
    db.session.commit()
    return '', 200


@app.route('/memos/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_memo(id):
    memo = Memo.query.get_or_404(id)
    
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        tags = request.form.get('tags', '').strip()
        
        if content:
            memo.content = content
            memo.tags = tags
            db.session.commit()
        
        if request.headers.get('HX-Request'):
            return render_template('partials/memo_item.html', memo=memo)
        
        return redirect(url_for('memos'))
    
    # GET 请求返回编辑表单
    if request.headers.get('HX-Request'):
        return render_template('partials/memo_edit.html', memo=memo)
    
    return redirect(url_for('memos'))


# ==================== 稍后读模块 ====================

@app.route('/bookmarks')
@login_required
def bookmarks():
    status_filter = request.args.get('status', 'all')
    if status_filter == 'all':
        all_bookmarks = Bookmark.query.order_by(Bookmark.created_at.desc()).all()
    else:
        all_bookmarks = Bookmark.query.filter_by(status=status_filter).order_by(Bookmark.created_at.desc()).all()
    return render_template('bookmarks.html', bookmarks=all_bookmarks, current_status=status_filter)


@app.route('/bookmarks/add', methods=['POST'])
@login_required
def add_bookmark():
    url = request.form.get('url', '').strip()
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    
    if url:
        # 如果没有标题，尝试自动抓取
        if not title:
            title = fetch_page_title(url) or url
        
        bookmark = Bookmark(url=url, title=title, description=description)
        db.session.add(bookmark)
        db.session.commit()
        
        if request.headers.get('HX-Request'):
            return render_template('partials/bookmark_item.html', bookmark=bookmark)
    
    return redirect(url_for('bookmarks'))


@app.route('/bookmarks/status/<int:id>', methods=['POST'])
@login_required
def update_bookmark_status(id):
    bookmark = Bookmark.query.get_or_404(id)
    new_status = request.form.get('status', 'unread')
    bookmark.status = new_status
    db.session.commit()
    
    if request.headers.get('HX-Request'):
        return render_template('partials/bookmark_item.html', bookmark=bookmark)
    
    return redirect(url_for('bookmarks'))


@app.route('/bookmarks/delete/<int:id>', methods=['DELETE'])
@login_required
def delete_bookmark(id):
    bookmark = Bookmark.query.get_or_404(id)
    db.session.delete(bookmark)
    db.session.commit()
    return '', 200


@app.route('/bookmarks/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_bookmark(id):
    bookmark = Bookmark.query.get_or_404(id)
    
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        
        if url:
            bookmark.url = url
            bookmark.title = title or url
            bookmark.description = description
            db.session.commit()
        
        if request.headers.get('HX-Request'):
            return render_template('partials/bookmark_item.html', bookmark=bookmark)
        
        return redirect(url_for('bookmarks'))
    
    if request.headers.get('HX-Request'):
        return render_template('partials/bookmark_edit.html', bookmark=bookmark)
    
    return redirect(url_for('bookmarks'))


@app.route('/api/fetch-title')
@login_required
def api_fetch_title():
    """AJAX 接口：获取 URL 的标题"""
    url = request.args.get('url', '')
    title = fetch_page_title(url)
    return jsonify({'title': title or ''})


def fetch_page_title(url):
    """从 URL 抓取网页标题"""
    try:
        import requests
        from bs4 import BeautifulSoup
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=5)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'html.parser')
        
        if soup.title:
            return soup.title.string.strip()
    except Exception as e:
        print(f"抓取标题失败: {e}")
    return None


# ==================== 提醒模块 ====================

@app.route('/reminders')
@login_required
def reminders():
    show_done = request.args.get('show_done', 'false') == 'true'
    if show_done:
        all_reminders = Reminder.query.order_by(Reminder.target_datetime.asc()).all()
    else:
        all_reminders = Reminder.query.filter_by(is_done=False).order_by(Reminder.target_datetime.asc()).all()
    return render_template('reminders.html', reminders=all_reminders, show_done=show_done)


@app.route('/reminders/add', methods=['POST'])
@login_required
def add_reminder():
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    target_datetime_str = request.form.get('target_datetime', '')
    
    if title and target_datetime_str:
        target_datetime = datetime.fromisoformat(target_datetime_str)
        reminder = Reminder(title=title, description=description, target_datetime=target_datetime)
        db.session.add(reminder)
        db.session.commit()
        
        if request.headers.get('HX-Request'):
            return render_template('partials/reminder_item.html', reminder=reminder)
    
    return redirect(url_for('reminders'))


@app.route('/reminders/toggle/<int:id>', methods=['POST'])
@login_required
def toggle_reminder(id):
    reminder = Reminder.query.get_or_404(id)
    reminder.is_done = not reminder.is_done
    db.session.commit()
    
    if request.headers.get('HX-Request'):
        return render_template('partials/reminder_item.html', reminder=reminder)
    
    return redirect(url_for('reminders'))


@app.route('/reminders/delete/<int:id>', methods=['DELETE'])
@login_required
def delete_reminder(id):
    reminder = Reminder.query.get_or_404(id)
    db.session.delete(reminder)
    db.session.commit()
    return '', 200


@app.route('/reminders/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_reminder(id):
    reminder = Reminder.query.get_or_404(id)
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        target_datetime_str = request.form.get('target_datetime', '')
        
        if title and target_datetime_str:
            reminder.title = title
            reminder.description = description
            reminder.target_datetime = datetime.fromisoformat(target_datetime_str)
            # 修改时间后重置通知状态，这样可以重新触发通知
            reminder.notified = False
            db.session.commit()
        
        if request.headers.get('HX-Request'):
            return render_template('partials/reminder_item.html', reminder=reminder)
        
        return redirect(url_for('reminders'))
    
    if request.headers.get('HX-Request'):
        return render_template('partials/reminder_edit.html', reminder=reminder)
    
    return redirect(url_for('reminders'))


@app.route('/api/pending-reminders')
@login_required
def api_pending_reminders():
    """检查是否有到期的提醒 (用于浏览器通知)"""
    # 使用北京时间 (UTC+8)
    beijing_tz = timezone(timedelta(hours=8))
    now = datetime.now(beijing_tz).replace(tzinfo=None)  # 转为naive datetime进行比较
    
    pending = Reminder.query.filter(
        Reminder.target_datetime <= now,
        Reminder.is_done == False,
        Reminder.notified == False
    ).all()
    
    result = []
    for r in pending:
        result.append({'id': r.id, 'title': r.title, 'description': r.description or ''})
        # 发送微信推送
        send_pushplus_notification(r.title, r.description or '提醒时间已到')
        r.notified = True
    
    db.session.commit()
    return jsonify(result)


@app.route('/api/test-notification')
@login_required
def api_test_notification():
    """测试通知功能"""
    # 测试 PushPlus
    pushplus_ok = send_pushplus_notification('测试通知', '如果你收到这条消息，说明微信推送配置成功！')
    return jsonify({
        'pushplus_configured': bool(app.config.get('PUSHPLUS_TOKEN')),
        'pushplus_sent': pushplus_ok
    })


@app.route('/api/debug-reminders')
@login_required
def api_debug_reminders():
    """调试：查看所有提醒状态"""
    beijing_tz = timezone(timedelta(hours=8))
    now = datetime.now(beijing_tz).replace(tzinfo=None)
    
    reminders = Reminder.query.order_by(Reminder.target_datetime.desc()).limit(10).all()
    
    result = []
    for r in reminders:
        result.append({
            'id': r.id,
            'title': r.title,
            'target': r.target_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            'is_done': r.is_done,
            'notified': r.notified,
            'is_overdue': r.target_datetime <= now
        })
    
    return jsonify({
        'server_time': now.strftime('%Y-%m-%d %H:%M:%S'),
        'reminders': result
    })


def send_pushplus_notification(title, content):
    """发送 PushPlus 微信推送"""
    token = app.config.get('PUSHPLUS_TOKEN')
    if not token:
        return False
    
    try:
        import requests
        url = 'http://www.pushplus.plus/send'
        data = {
            'token': token,
            'title': f'⏰ {title}',
            'content': content,
            'template': 'html'
        }
        response = requests.post(url, json=data, timeout=10)
        result = response.json()
        if result.get('code') == 200:
            print(f'PushPlus 推送成功: {title}')
            return True
        else:
            print(f'PushPlus 推送失败: {result}')
            return False
    except Exception as e:
        print(f'PushPlus 推送异常: {e}')
        return False


# ==================== 搜索模块 ====================

@app.route('/search')
@login_required
def search():
    query = request.args.get('q', '').strip()
    results = {'memos': [], 'bookmarks': []}
    
    if query:
        # 搜索速记：同时搜索内容和标签
        results['memos'] = Memo.query.filter(
            (Memo.content.contains(query)) | (Memo.tags.contains(query))
        ).order_by(Memo.created_at.desc()).all()
        # 搜索书签：搜索标题和描述
        results['bookmarks'] = Bookmark.query.filter(
            (Bookmark.title.contains(query)) | (Bookmark.description.contains(query))
        ).order_by(Bookmark.created_at.desc()).all()
    
    return render_template('search.html', query=query, results=results)


# ==================== Markdown 过滤器 ====================

@app.template_filter('markdown')
def markdown_filter(text):
    """Jinja2 过滤器：渲染 Markdown"""
    return markdown.markdown(text, extensions=['nl2br', 'fenced_code'])


@app.context_processor
def utility_processor():
    """注入模板全局函数"""
    def now():
        # 使用北京时间 (UTC+8)
        beijing_tz = timezone(timedelta(hours=8))
        return datetime.now(beijing_tz).replace(tzinfo=None)
    return dict(now=now)


# ==================== 初始化数据库 ====================

def init_db():
    """初始化数据库和默认用户"""
    with app.app_context():
        # 确保 instance 目录存在
        instance_path = os.path.join(os.path.dirname(__file__), 'instance')
        if not os.path.exists(instance_path):
            os.makedirs(instance_path)
        
        db.create_all()
        
        # 创建默认用户 (如果不存在)
        if not User.query.filter_by(username='admin').first():
            user = User(username='edikkgizc')
            user.set_password('edikkgizc')  # 请修改默认密码
            db.session.add(user)
            db.session.commit()
            # print('已创建默认用户: admin / admin123')


if __name__ == '__main__':
    init_db()
    # 本地开发使用 debug=True，生产环境会通过 wsgi 启动，不走这里
    app.run(debug=True, host='0.0.0.0', port=5000)
