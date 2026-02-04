# 项目说明：MyBackend（FastAPI 模板）

本文件用于帮助你快速理解项目的整体架构、主要模块、如何运行与部署、以及如何在未来把后端重写成 Go 时的注意事项。

目录结构（关键文件）

- `app/`：应用代码包
  - `__init__.py`：包初始化
  - `db.py`：数据库引擎与会话（SQLModel + create_engine）
  - `models.py`：数据库模型（User）
  - `schemas.py`：Pydantic 数据模型（请求/响应）
  - `auth.py`：认证相关（密码哈希、JWT 生成/解析、获取当前用户）
  - `main.py`：FastAPI 应用与路由（/ping, /register, /login, /me）
- `requirements.txt`：Python 依赖
- `.env.example`：环境变量示例
- `deploy/mybackend.service`：systemd 服务模版（用于生产部署）

工作流与数据流

1. 启动阶段
   - 应用通过 `uvicorn` 或 `gunicorn + uvicorn worker` 启动。
   - 在 `startup` 事件中调用 `init_db()`，根据 `app.models` 中定义的模型自动创建数据库表（SQLite：data.db）。

2. 请求处理
   - 所有需要数据库访问的路由都通过 `Depends(get_session)` 获取一个独立的 `Session`。
   - 用户注册流程：接收 `RegisterIn` 请求体 -> 检查用户名 -> 使用 `passlib` 对密码哈希 -> 写入 DB -> 返回 JWT
   - 用户登录流程：查库验证密码 -> 返回 JWT
   - 受保护接口 `/me`：通过 `get_current_user` 依赖解析并验证 JWT，然后从 DB 加载用户对象返回。

安全要点

- 密钥与敏感配置请通过环境变量注入（`SECRET_KEY`, `DATABASE_URL` 等）。
- 不要在生产环境中公开 `/docs`，可通过设置 `DISABLE_DOCS=1` 关闭自动文档或在代理层限制访问。
- 密码使用 `bcrypt` 哈希（passlib），数据库中仅保存哈希值。

在 1GB VPS 上如何部署（推荐，不使用 Docker）

1. 将项目复制到 `/home/youruser/mybackend`
2. 创建并激活 virtualenv：

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

3. 配置 systemd：将 `deploy/mybackend.service` 拷贝到 `/etc/systemd/system/mybackend.service`，修改其中的 `User`、路径和 `Environment` 后执行：

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now mybackend
sudo journalctl -u mybackend -f
```

4. 使用你现有的 s-ui 面板将外网请求代理到 `127.0.0.1:8000`，由面板处理 TLS/证书。

测试常用命令

```bash
# 健康检查
curl http://127.0.0.1:8000/ping

# 注册
curl -X POST "http://127.0.0.1:8000/register" -H "Content-Type: application/json" -d '{"username":"test","password":"123456"}'

# 登录
curl -X POST "http://127.0.0.1:8000/login" -H "Content-Type: application/json" -d '{"username":"test","password":"123456"}'

# 使用返回的 token 访问受保护接口
curl -H "Authorization: Bearer <token>" http://127.0.0.1:8000/me
```

如何阅读代码以快速理解

- 从 `app/main.py` 开始：这里定义了路由与应用启动逻辑。
- 看 `app/auth.py`：包含认证相关的工具函数，理解 JWT 的生成与验证方式。
- 再看 `app/db.py` 与 `app/models.py`：了解数据模型与数据库会话的创建方式。

如何把项目迁移到 Go（简要注意事项）

- 保持 API contract：在运行时导出 `/openapi.json` 并保存，Go 端可以用 openapi-generator 加速生成接口骨架。
- 将业务逻辑（service 层）与路由逻辑分离——现有代码已经较为简单，迁移时把 `register/login` 的核心逻辑提取成独立函数会更好迁移。
- 数据库 schema 保持兼容（字段名、类型尽量通用），尽量避免 SQLite 专有行为。

FAQ

- Q: 我可以直接使用 `uvicorn` 启动吗？
  A: 可以，但在生产推荐使用 `gunicorn + uvicorn worker` 或 systemd 管理，便于守护和重启策略。

- Q: 什么时候需要换到 PostgreSQL？
  A: 当并发写/数据规模增长时，SQLite 的并发写限制（文件锁）会成为瓶颈，这时迁移到 PostgreSQL/MySQL。

如果你希望，我可以：
- 生成一个一键部署脚本（创建 venv、安装依赖、生成并启用 systemd）
- 把此模板推到一个新的 git 仓库并为你做首次提交
- 为项目增加更详细的注释或额外示例（例如使用 Alembic 做迁移）
