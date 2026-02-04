# MyBackend (FastAPI) — 简易可部署模板

简介
- 基于 FastAPI + SQLModel（SQLite）实现的最小后端模板
- 提供：注册 / 登录（bcrypt）/ JWT 鉴权 / /me 接口
- 适合 1GB RAM 的 VPS（推荐使用 virtualenv + systemd，不使用 Docker）

目录结构（示例）
```
/home/youruser/mybackend
├─ app/
│  ├─ __init__.py
│  ├─ main.py
   ├─ auth.py
   ├─ db.py
   ├─ models.py
   └─ schemas.py
├─ requirements.txt
└─ .env.example
```

快速部署（不使用 Docker，推荐）
1. 在 VPS 上创建用户（若尚未）：
	- sudo adduser youruser
	- sudo usermod -aG sudo youruser
2. 登录并克隆项目到 `/home/youruser/mybackend`，或上传代码。
3. 安装系统依赖（Debian/Ubuntu）：
	- sudo apt update
	- sudo apt install -y python3 python3-venv python3-pip git
4. 进入项目并创建虚拟环境：
	- cd /home/youruser/mybackend
	- python3 -m venv .venv
	- source .venv/bin/activate
	- pip install -U pip
	- pip install -r requirements.txt
5. 配置环境变量
	- 编辑 systemd 文件或 export 环 环境变量（示例见 `.env.example`）
	- 生产至少修改 `SECRET_KEY` 为安全随机值
6. 初始化数据库（可由 app 自动创建，或手动）：
	- python -c "from app.db import init_db; init_db()"
	- 如果使用 SQLite，建议启用 WAL（提高并发写性能）：
	  - sqlite3 data.db "PRAGMA journal_mode=WAL;"
7. 配置 systemd（示例文件：`/etc/systemd/system/mybackend.service`）
	- 修改 `User`、`WorkingDirectory`、`Environment` 中的路径为你真实路径
	- sudo systemctl daemon-reload
	- sudo systemctl enable --now mybackend
	- sudo journalctl -u mybackend -f
8. 反向代理 / TLS
	- 你已经在用 s-ui 面板代理：请将面板里的代理指向 `127.0.0.1:8000`（HTTP），让 s-ui 管理 HTTPS/TLS
9. 测试接口
	- curl http://127.0.0.1:8000/ping
	- 注册：
	  - curl -X POST "http://127.0.0.1:8000/register" -H "Content-Type: application/json" -d '{"username":"test","password":"123456"}'
	- 登录得到 token：
	  - curl -X POST "http://127.0.0.1:8000/login" -H "Content-Type: application/json" -d '{"username":"test","password":"123456"}'
	- 使用 token 访问 /me：
	  - curl -H "Authorization: Bearer <token>" http://127.0.0.1:8000/me

资源限制 / 优化建议（针对 1GB VPS）
- Worker 只开 1 个（systemd 中 ExecStart 使用 `-w 1`）
- 不要在同一台 VPS 上额外运行 PostgreSQL 或 Redis（这些会占用较多内存）。初期用 SQLite 文件型 DB。
- 禁用/限制自动文档（可通过设置 DISABLE_DOCS=1）以减少信息泄露：FastAPI 文档默认开启，生产环境可关闭或加认证。
- 日志轮转：确保 systemd/journald 或 logrotate 管理日志，避免磁盘占满。
- 避免请求中加载大型模块或返回超大数据（使用分页与 limit）。
- 如需缓存或队列，优先使用外部托管服务或单独小 VPS。

如何为将来迁移到 Go 做准备
- 保持 API contract：在运行中可通过 /openapi.json 导出 OpenAPI 描述，Go 重写时可用 openapi-generator 或按 spec 实现。
- 把业务逻辑放在独立函数/模块（不要把逻辑都塞在路由函数），便于逐步替换框架层。
- 保留或记录数据库 schema（建表 SQL）。迁移到 PostgreSQL/MySQL 时只需修改 DATABASE_URL 与少数设置。

常见问题
- 是否必须使用 gunicorn？不必须，你也可以直接用 `uvicorn app.main:app --host 127.0.0.1 --port 8000`，但用 gunicorn+uvicorn worker 更稳定（更好处理重启/子进程）。
- 想在 VPS 上用 Docker？可以，但在 1GB 下建议先不要，除非你熟悉瘦镜像和资源限制。

如果你要我做的下一步：
- 我可以把这个模板打包成一个 GitHub 仓库结构（完整文件）并给出可直接粘贴的 systemd 文件与启动命令；或
- 我可以把部署步骤写成一个自动化 shell 脚本（创建 venv、安装、生成 systemd 并启用）——注意脚本会修改系统服务，需要你确认。
