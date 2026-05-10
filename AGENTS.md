# AGENTS.md — yk_tool 个人工具集

## 项目性质

个人游戏服务端开发工具集（作者: zhengzhichun, zheng6655@163.com）。非标准应用项目，无 CI/CD、无测试、无 lint/typecheck 配置。

## 仓库布局

```
F:\server_tools/          ← Git 根目录（.git 在此）
  AGENTS.md
  .gitignore              ← 忽略 __pycache__/ .local/ .vscode/ .desk/
  .venv/                  ← Python 虚拟环境
  flog/                   ← Python 包，游戏日志分析（py -m flog 入口）
  jira/                   ← Jira 任务监控 GUI（tkinter），独立 requirements.txt
  pyweb/                  ← Flask + waitress Web 应用，独立 requirements.txt
  erl/                    ← Erlang 编译好的 .beam 及源码
  cc.py                   ← 目录文件同步守护（读 .cc.cnf 配置）
  delete_db.py            ← DB 增量备份清理（常驻进程 / Windows 定时任务）
  find_hrl_dir.py         ← IDEA Erlang 项目 .hrl 目录查找（写 .iml）
  st.py                   ← 文本对比/周报导出/录像统计
  watch_file.py           ← 全盘文件变动监听（watchdog）
  README.md
  yk_tool.code-workspace
  play/                   ← 无关的 turtle 图形实验
```

## 关键入口点与命令

### flog 日志分析包
```powershell
py -m flog                             # 显示帮助
py -m flog log/fight.l* start end      # 在匹配文件中查找内容
py -m flog -line xxxx.log 3            # 显示文件指定行
py -m flog -fxa fight_analysis2.log    # 战报分析 → 输出 .csv
py -m flog -fxe event.txt              # 事件耗时分析 → 输出 event.csv
```

### Web 服务（pyweb）
```powershell
cd pyweb
pip install -r requirements.txt        # 安装依赖（Flask, waitress, SQLAlchemy）
py run.py                              # 启动服务 → http://192.168.22.9:80
```
- 使用 `waitress` 生产级服务器，监听 80 端口
- SQLite 数据库 `example.db`，首次启动自动建表
- 上传文件存到 `up/` 目录

### Jira 监控
```powershell
cd jira
pip install -r requirements.txt
py jira.py                             # 启动 tkinter GUI
py db_read.py                          # 启动 DB 工具箱（时间转换 + 表 bin 读写）
```
- 首次运行自动生成 `.cfg.txt` 配置模板（需手动填写 host/user/pwd）
- 使用 `requests_html` + `pyppeteer`，需 Chromium 环境
- Chromium 下载: `PYPPETEER_CHROMIUM_REVISION=1348689`，镜像站: `registry.npmmirror.com`

### VSCode 任务（`.vscode/tasks.json`）
- `"1db"` → 在 `jira` 目录下运行 `db_read.py`（配置缓存在 `.desk/`）
- `"2jira"` → 在 `jira` 目录下运行 `jira.py`（配置缓存在 `.desk/`）
- `"oc"` → 运行 `opencode`

### OpenCode 自定义快捷键（全局 `opencode.json`）
- 全局: `%USERPROFILE%\.config\opencode\opencode.json`
- `F1` → 新会话（`session_new`）
- `F3` → 会话列表（`session_list`）
- 注意: `%USERPROFILE%\Documents\PowerShell\Microsoft.PowerShell_profile.ps1` 中已移除 PSReadLine 对 F3 的拦截

## 配置与编码

- **配置文件都在 `.local/`**（被 gitignore），首次运行自动生成模板：
  - `.cc.cnf` ← `cc.py` 的目录同步配置
  - `.cfg.txt` ← `jira.py` 的登录配置
- **编码**: 源文件 `# coding=utf-8`，配置文件读写用 `utf-8-sig`（带 BOM）
- **Python**: 3.12.5+，虚拟环境 `.venv`（Python 3.14.2 at `D:\Programs\Python`）
- **平台**: Windows 优先（`msvcrt`、`schtasks`、`os.startfile`、`winreg` 模式）

## Erlang 工具

```powershell
cd erl
cc.bat    # 编译 + 执行 cmd_tool（export_record）+ 拷贝 + TortoiseSVN 提交
erl -s cmd_tool main export_record "path\to\ebin" -s init stop
```
- 已预编译 `.beam`，可直接使用
- `cmd_tool.erl` 支持子命令: `url_ok`, `del_log`, `cmd`, `export_record`

## 重要注意事项

- **不是标准 Python 项目** — 无 `setup.py` / `pyproject.toml`，无测试框架，不要运行 pytest
- **不要修改 `.local/`、`.desk/` 下的文件** — 它们是运行时配置/缓存，被 gitignore（`.desk/` 在各工具目录下，如 `jira/.desk/`）
- **`play/` 目录无关** — 纯 turtle 图形实验，与主线无关
- **`delete_db.py`** 会在 Windows 创建计划任务（`schtasks /create`），或生成 crontab 命令
- **文件头模板**（所有 `.py` 文件一致）:
  ```python
  # coding=utf-8
  # py3.12.5
  # Auther:zhengzhichun [zheng6655@163.com]
  ```
- **Erlang include 路径维护**: 用 `py find_hrl_dir.py` 打开 GUI，选择 IDEA 项目目录，自动写入 `.iml`
