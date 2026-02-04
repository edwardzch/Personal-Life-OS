# PythonAnywhere 部署指南

将 Personal Life OS 部署到 PythonAnywhere 免费账户。

---

## 第一步：注册账号

1. 访问 [www.pythonanywhere.com](https://www.pythonanywhere.com)
2. 点击 **"Start running Python online"** 注册免费账户
3. 用户名将成为你的网址：`用户名.pythonanywhere.com`

---

## 第二步：上传代码

在 **Consoles** 页面打开 **Bash**，运行：

```bash
git clone https://github.com/你的用户名/Personal-Life-OS.git
```

---

## 第三步：创建虚拟环境

```bash
mkvirtualenv --python=/usr/bin/python3.12 personal-life-os-venv
cd ~/Personal-Life-OS
pip install -r requirements.txt
python -c "from app import init_db; init_db()"
```

---

## 第四步：配置 Web 应用

1. 进入 **Web** 页面 → **"Add a new web app"**
2. 选择 **Manual configuration** → **Python 3.12**

### 配置项

| 配置项 | 值 |
|--------|-----|
| **Source code** | `/home/你的用户名/Personal-Life-OS` |
| **Working directory** | `/home/你的用户名/Personal-Life-OS` |
| **Virtualenv** | `/home/你的用户名/.virtualenvs/personal-life-os-venv` |

### 编辑 WSGI 配置文件

点击 **WSGI configuration file**，替换全部内容为：

```python
import sys
import os

project_home = '/home/你的用户名/Personal-Life-OS'  # 修改为你的用户名

if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ['FLASK_ENV'] = 'production'

from app import app as application
```

---

## 第五步：启动应用

1. 点击绿色 **Reload** 按钮
2. 访问 `https://你的用户名.pythonanywhere.com`
3. 使用默认账号登录

---

## 代码更新流程

### 1. 本地推送

```bash
git add .
git commit -m "更新描述"
git push
```

### 2. 服务器拉取

在 PythonAnywhere Bash 中：

```bash
cd ~/Personal-Life-OS
git pull
```

### 3. 重新加载

点击 **Web** → **Reload**

---

## 数据库迁移

添加新的数据模型后，需要创建表：

```bash
cd ~/Personal-Life-OS
workon personal-life-os-venv
python3 -c "from app import app, db; app.app_context().push(); db.create_all(); print('OK')"
```

---

## 常用命令速查

| 场景 | 命令 |
|------|------|
| 更新代码 | `cd ~/Personal-Life-OS && git pull` |
| 进入虚拟环境 | `workon personal-life-os-venv` |
| 安装新依赖 | `pip install 包名` |
| 创建数据库表 | `python3 -c "from app import app, db; app.app_context().push(); db.create_all()"` |
| 备份数据库 | `cp ~/Personal-Life-OS/instance/app.db ~/app.db.bak` |
| 查看错误日志 | Web 页面 → Error log |

---

## 常见问题

### Q: 502 错误？
查看 **Web** 页面的 **Error log** 获取详细错误信息。

### Q: 缺少模块？
```bash
workon personal-life-os-venv
pip install 模块名
```

### Q: 免费账户限制？
- 每天 100 秒 CPU 时间（个人使用够用）
- 512MB 存储空间
- 3 个月不活跃会暂停（登录续期）

---

## 安全建议

部署后请修改默认密码：

1. 编辑 `app.py` 中的 `user.set_password('新密码')`
2. 删除数据库：`rm ~/Personal-Life-OS/instance/app.db`
3. 重新初始化：
   ```bash
   cd ~/Personal-Life-OS
   workon personal-life-os-venv
   python -c "from app import init_db; init_db()"
   ```
4. 点击 Web → Reload
