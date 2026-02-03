# PythonAnywhere 部署指南

按照以下步骤将 Personal Life OS 部署到 PythonAnywhere 免费账户。

---

## 第一步：注册账号

1. 访问 [www.pythonanywhere.com](https://www.pythonanywhere.com)
2. 点击 **"Start running Python online"** 注册免费账户
3. 用户名将成为你的网址：`edwardzch.pythonanywhere.com`

---

## 第二步：上传代码

在 **Consoles** 页面打开 **Bash**，运行：

```bash
git clone https://github.com/edwardzch/Personal-Life-OS.git
```

---

## 第三步：创建虚拟环境

在 Bash 控制台运行（逐行执行）：

```bash
mkvirtualenv --python=/usr/bin/python3.12 personal-life-os-venv
cd ~/Personal-Life-OS
pip install -r requirements.txt
python -c "from app import init_db; init_db()"
```

---

## 第四步：配置 Web 应用

1. 进入 **Web** 页面
2. 点击 **"Add a new web app"**
3. 选择 **Manual configuration**
4. 选择 **Python 3.12**

### 配置项设置：

| 配置项 | 值 |
|--------|-----|
| **Source code** | `/home/edwardzch/Personal-Life-OS` |
| **Working directory** | `/home/edwardzch/Personal-Life-OS` |
| **Virtualenv** | `/home/edwardzch/.virtualenvs/personal-life-os-venv` |

### 编辑 WSGI 配置文件

点击 **WSGI configuration file** 链接，**删除全部内容**，替换为：

```python
import sys
import os

project_home = '/home/edwardzch/Personal-Life-OS'

if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ['FLASK_ENV'] = 'production'

from app import app as application
```

---

## 第五步：启动应用

1. 回到 **Web** 页面
2. 点击绿色的 **"Reload"** 按钮
3. 访问 https://edwardzch.pythonanywhere.com

🎉 **完成！** 使用 `admin / admin123` 登录。

---

## 常见问题

### Q: 页面显示 502 错误？
打开 **Web** 页面的 **Error log**，查看具体错误信息。

### Q: 如何更新代码？
```bash
cd ~/Personal-Life-OS
git pull
# 回到 Web 页面点击 Reload
```

### Q: 免费账户有什么限制？
- 每天 100 秒 CPU 时间（个人使用完全够）
- 512MB 存储空间
- 网站 3 个月不活跃会被暂停（登录续期即可）

---

## 安全建议

部署后请修改默认密码：

1. 在 Bash 中编辑 `nano ~/Personal-Life-OS/app.py`
2. 找到 `user.set_password('admin123')`
3. 改为你的新密码
4. 删除数据库：`rm ~/Personal-Life-OS/instance/app.db`
5. 重新初始化：
   ```bash
   cd ~/Personal-Life-OS
   workon personal-life-os-venv
   python -c "from app import init_db; init_db()"
   ```
6. 回到 Web 页面点击 Reload
