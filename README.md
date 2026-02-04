# Personal Life OS 使用教程

一个简洁高效的个人效率工具，支持手机和电脑多端使用。

---

## ✨ 功能特性

| 功能 | 说明 |
|------|------|
| **速记流** | 快速记录碎片化想法，支持 Markdown 和标签 |
| **稍后读** | 收藏网页链接，自动获取标题 |
| **提醒** | 定时提醒，支持多设备浏览器通知 |
| **多设备同步** | 一处修改，其他设备自动刷新 |
| **PWA 支持** | 可添加到手机主屏幕，像 App 一样使用 |
| **绿色主题** | 护眼的 Emerald 绿色配色 |

---

## 🚀 快速开始

### 本地运行

```bash
cd c:\Users\zhangch64\Desktop\RecordingTools
.venv\Scripts\activate
python app.py
```

访问 `http://127.0.0.1:5000`，使用默认账号登录：
- 用户名: `admin`
- 密码: `admin123`

### 云端部署

推荐部署到 PythonAnywhere，详见 [DEPLOY_PYTHONANYWHERE.md](DEPLOY_PYTHONANYWHERE.md)

---

## 📝 功能模块

### 速记流 (Memos)

- 支持 **Markdown** 格式（加粗、列表、代码块等）
- 支持 **标签**，逗号分隔多个标签
- 点击标签可筛选相关速记
- 支持搜索内容和标签

### 稍后读 (Bookmarks)

- 粘贴 URL 自动获取标题
- 状态管理：未读 → 已读 → 归档
- 支持编辑和删除

### 提醒 (Reminders)

- 设置日期时间的定时提醒
- **多设备通知**：每个打开的浏览器都能收到通知
- 支持浏览器桌面通知（需授权）
- 到期提醒音效提示

---

## 📱 多端使用

| 平台 | 使用方式 |
|------|----------|
| **电脑** | 浏览器直接访问 |
| **手机 (Android)** | Chrome 打开 → 菜单 → "添加到主屏幕" |
| **手机 (iPhone)** | **Safari** 打开 → 分享 → "添加到主屏幕" |

> ⚠️ iPhone 必须用 Safari 添加，Chrome 不支持完整 PWA 功能

### 多设备同步

- 在 A 设备修改数据后，B 设备会在 15 秒内自动刷新
- 提醒通知会发送到所有打开网页的设备

---

## 🔔 关于通知

| 场景 | 是否收到通知 |
|------|-------------|
| 电脑浏览器打开网页 | ✅ 收到 |
| 手机浏览器打开网页 | ✅ 收到 |
| 手机浏览器在后台 | ❌ 不收到 |
| 浏览器关闭 | ❌ 不收到 |

> 这是浏览器技术限制，只有原生 App 才能后台推送

---

## ⚙️ 配置说明

### 修改默认密码

编辑 `app.py` 中的默认密码：
```python
user.set_password('你的新密码')
```

删除 `instance/app.db` 后重启应用。

### 数据备份

复制 `instance/app.db` 文件即可完整备份所有数据。

---

## 📁 项目结构

```
Personal-Life-OS/
├── app.py              # 主程序
├── config.py           # 配置
├── models.py           # 数据模型
├── requirements.txt    # 依赖
├── instance/app.db     # SQLite 数据库
├── static/
│   ├── css/style.css   # 样式
│   ├── manifest.json   # PWA 配置
│   ├── sw.js           # Service Worker
│   └── icon-*.png      # 应用图标
└── templates/          # HTML 模板
```

---

## 🔧 技术栈

- **后端**: Flask + SQLite
- **前端**: TailwindCSS + HTMX
- **通知**: Web Notifications API
- **PWA**: Service Worker + Manifest
