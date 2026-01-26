# Claude Code Telegram Bridge - 保姆级使用指南

> **重要提示**: 如果还没设置 TELEGRAM_BOT_TOKEN，请先跳到 [第一部分](#第一部分：获取-telegram-bot-token)

---

## 快速开始 (TL;DR)

如果你已经配置好了所有东西，只想快速启动：

```bash
cd claudecode-telegram
export TELEGRAM_BOT_TOKEN="你的token"
./start.sh start
```

然后在 Telegram 中给你的 bot 发送消息即可开始对话！

---

## 完整部署指南

### 第一部分：获取 Telegram Bot Token

1. **打开 Telegram**
   - 搜索 `@BotFather`（这是 Telegram 官方的 bot 创建工具）

2. **创建新 Bot**
   - 发送 `/newbot` 命令
   - 按照提示设置 bot 名称和用户名（用户名必须以 `bot` 结尾）

3. **获取 Token**
   - BotFather 会给出一个类似这样的 token：
     ```
     123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ
     ```
   - **⚠️ 重要：复制并保存这个 token，后面会用到**

---

### 第二部分：环境准备

#### 前提条件检查

运行启动脚本的自动检查：

```bash
./start.sh status
```

它会检查以下工具：
- `tmux` - 终端复用器
- `cloudflared` - Cloudflare Tunnel 工具
- `python3` - Python 3.x
- `pip` - Python 包管理器

#### 安装缺失工具

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tmux python3-pip

# 安装 cloudflared
curl -L -o cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared.deb
rm cloudflared.deb
```

**macOS:**
```bash
brew install tmux cloudflared
```

**其他系统:**
访问 https://github.com/cloudflare/cloudflared/releases 下载适合你系统的版本

---

### 第三部分：一键部署

#### 方法 A：临时设置 Token（推荐）

```bash
# 进入项目目录
cd claudecode-telegram

# 设置 token 并启动（这个 token 只在当前终端有效）
TELEGRAM_BOT_TOKEN="123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ" ./start.sh start
```

#### 方法 B：永久设置 Token

```bash
# 进入项目目录
cd claudecode-telegram

# 设置环境变量（写入当前 bash session）
export TELEGRAM_BOT_TOKEN="123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ"

# 启动服务
./start.sh start
```

**让 Token 永久生效（可选）：**

将下面这行添加到你的 `~/.bashrc` 或 `~/.zshrc` 文件中：

```bash
export TELEGRAM_BOT_TOKEN="你的token"
```

然后运行：
```bash
source ~/.bashrc  # 或 source ~/.zshrc
```

---

### 第四部分：启动过程详解

执行 `./start.sh start` 后，脚本会自动完成以下步骤：

#### 1. 环境检查
```
[→] 检查环境依赖...
[✓] 所有依赖已满足
```

**作用：** 检查 tmux、cloudflared、python3 是否已安装

#### 2. Python 虚拟环境配置
```
[→] 配置 Python 虚拟环境...
[✓] 虚拟环境已创建/激活
[✓] Python 依赖已安装
```

**作用：**
- 创建 `.venv` 虚拟环境（如果不存在）
- 安装必要的 Python 包

#### 3. Claude 钩子配置
```
[→] 配置 Claude 钩子...
[✓] 钩子脚本已安装
[✓] Bot token 已配置
[✓] Claude 配置文件已创建
```

**作用：**
- 安装 `send-to-telegram.sh` 钩子脚本
- 在 `~/.claude/settings.json` 中配置钩子
- 让 Claude 回复后自动发送消息回 Telegram

#### 4. 启动 tmux + Claude Code
```
[→] 启动 tmux + Claude Code...
[✓] tmux 会话 'claude' 正在运行
[✓] Claude Code 已在 tmux 中启动
```

**作用：**
- 创建 tmux 会话（保持 Claude 持久运行）
- 在会话中启动 Claude Code

#### 5. 启动 Bridge 服务器
```
[→] 启动 Bridge 服务器...
[✓] Bot 命令已注册
[✓] Bridge 服务器已启动 (PID: 12345)
```

**作用：**
- 启动 Python bridge 服务（监听 8080 端口）
- 注册 Telegram bot 命令（/status, /clear 等）

#### 6. 启动 Cloudflare Tunnel
```
[→] 启动 Cloudflare Tunnel...
[✓] Tunnel 已启动: https://xxx.trycloudflare.com
[✓] Telegram webhook 已设置
```

**作用：**
- 创建到 Cloudflare 的隧道
- 设置 Telegram webhook（告诉 Telegram 消息发往哪里）

#### 7. 最终状态
```
[✓] tmux 'claude': running
[✓] Bridge 正在运行 (PID: 12345)
[✓] Tunnel 正在运行: https://xxx.trycloudflare.com

[→] Telegram Bot Webhook URL:
  https://xxx.trycloudflare.com/
```

**🎉 启动完成！**

---

### 第五部分：在 Telegram 中使用

#### 发送第一条消息

1. 在 Telegram 中搜索你的 bot（你在 @BotFather 设置的名称）
2. 点击 `/start` 或发送任意消息
3. 等待几秒钟，你应该会收到 Claude 的回复

#### 可用命令

| 命令 | 作用 |
|------|------|
| `/start` | 开始使用 |
| `/status` | 查看服务状态 |
| `/clear` | 清空对话历史 |
| `/continue_` | 继续上一次的对话 |
| `/resume` | 选择历史会话恢复（显示会话列表） |
| `/loop <提示词>` | 使用 Ralph Loop 模式（自动迭代 5 次） |
| `/stop` | 中断当前的 Claude 回复 |

#### 普通对话

直接发送消息即可，无需使用命令。例如：

```
你：写一个 Python 的快速排序函数
Claude: [代码实现]
```

#### 代码相关任务示例

```
你：帮我分析这个项目的结构
Claude: [分析项目的文件结构和架构]

你：/loop 优化这个函数的性能
Claude: [进行 5 轮迭代优化]

你：/clear
Claude: （清空历史，开始新对话）
```

---

### 第六部分：服务管理

#### 查看状态

```bash
./start.sh status
```

输出示例：
```
[✓] tmux 'claude': running
[✓] Bridge 正在运行 (PID: 12345)
[✓] Tunnel 正在运行: https://xxx.trycloudflare.com
```

#### 查看日志

```bash
./start.sh logs
```

显示：
- Bridge 服务器日志（最近 20 行）
- Tunnel 日志（最近 20 行）
- tmux 会话内容（最近 20 行）

**实时监控日志：**
```bash
# 监控 Bridge
tail -f bridge.log

# 监控 Tunnel
tail -f tunnel.log

# 监控 tmux
tmux attach -t claude
```

#### 停止服务

```bash
./start.sh stop
```

这会停止：
- Bridge 服务器
- Cloudflare Tunnel

**注意：** tmux 会话会保持运行（包含 Claude Code），这是为了方便下次快速启动。

如果需要完全关闭：
```bash
# 1. 停止服务
./start.sh stop

# 2. 进入 tmux 会话并退出 Claude
tmux attach -t claude
# 按 Ctrl+C 退出 Claude
# 输入 exit 退出 tmux
```

#### 重启服务

```bash
./start.sh restart
```

等同于 stop → start。

---

### 第七部分：故障排查

#### 问题 1：启动时提示 "TELEGRAM_BOT_TOKEN 未设置"

**原因：** 没有设置 bot token

**解决：**
```bash
# 方法 1：临时设置
TELEGRAM_BOT_TOKEN="你的token" ./start.sh start

# 方法 2：永久设置
export TELEGRAM_BOT_TOKEN="你的token"
./start.sh start

# 方法 3：最佳实践 - 添加到 .bashrc
echo 'export TELEGRAM_BOT_TOKEN="你的token"' >> ~/.bashrc
source ~/.bashrc
./start.sh start
```

#### 问题 2：Bot 不回复消息

**排查步骤：**

1. **检查服务状态**
   ```bash
   ./start.sh status
   ```
   确认所有服务都在运行

2. **查看日志**
   ```bash
   ./start.sh logs
   ```
   查找错误信息

3. **检查 Telegram webhook**
   ```bash
   curl https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getWebhookInfo
   ```
   确认 webhook URL 正确

4. **重新设置 webhook**
   ```bash
   # 获取 tunnel URL
   cat tunnel.url

   # 手动设置 webhook
   curl "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/setWebhook?url=https://xxx.trycloudflare.com/"
   ```

#### 问题 3：cloudflared 命令找不到

**原因：** cloudflared 未安装或不在 PATH 中

**解决：**
```bash
# Ubuntu/Debian
curl -L -o cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared.deb
rm cloudflared.deb

# 或者下载二进制文件到本地
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
chmod +x cloudflared-linux-amd64
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared
```

#### 问题 4：端口 8080 被占用

**原因：** 其他程序占用了 8080 端口

**解决：**
```bash
# 使用不同的端口
export PORT=8081
TELEGRAM_BOT_TOKEN="你的token" ./start.sh start
```

或者修改环境变量：
```bash
export PORT=8081
export TELEGRAM_BOT_TOKEN="你的token"
./start.sh start
```

#### 问题 5：tmux session 不存在

**原因：** tmux 会话被意外关闭

**解决：**
```bash
# 停止所有服务
./start.sh stop

# 重新启动
./start.sh start
```

---

### 第八部分：高级用法

#### 多个 Claude 实例

如果你想运行多个 Claude 实例：
```bash
# 实例 1
export TMUX_SESSION="claude1"
export PORT="8080"
TELEGRAM_BOT_TOKEN="token1" ./start.sh start

# 实例 2（在另一个终端）
export TMUX_SESSION="claude2"
export PORT="8081"
TELEGRAM_BOT_TOKEN="token2" ./start.sh start
```

#### 调试模式

查看详细日志：
```bash
# 实时查看所有日志
tail -f bridge.log tunnel.log -n 50

# 进入 tmux 查看 Claude 实时输出
tmux attach -t claude
```

#### 备份和迁移

需要备份的文件：
```bash
# Claude 配置和数据
~/.claude/history.jsonl          # 对话历史
~/.claude/projects/              # 项目数据
~/.claude/settings.json          # 设置
~/.claude/hooks/send-to-telegram.sh  # hook 脚本

# Bridge 相关
claudecode-telegram/bridge.log   # 日志
claudecode-telegram/tunnel.log   # Tunnel 日志
```

---

### 第九部分：完整示例

#### 从零开始的完整流程

```bash
# 1. 克隆项目（如果还没有）
git clone https://github.com/hanxiao/claudecode-telegram.git
cd claudecode-telegram

# 2. 检查依赖
./start.sh status

# 3. 获取 token（从 @BotFather）
#    假设 token 是: 123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ

# 4. 启动服务
TELEGRAM_BOT_TOKEN="123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ" ./start.sh start

# 5. 查看状态
./start.sh status

# 6. 在 Telegram 中开始使用
#    - 搜索你的 bot
#    - 发送 /start
#    - 开始对话！

# 7. 使用完成后停止
./start.sh stop
```

---

## 常见问题 FAQ

**Q: 为什么需要 tmux？**
A: tmux 让 Claude Code 在后台持续运行，即使关闭终端也不会停止。Bridge 通过 tmux 的 send-keys 功能向 Claude 发送消息。

**Q: Cloudflare Tunnel 安全吗？**
A: Tunnel 使用 Cloudflare 的基础设施，提供端到端加密。你的本地服务不会被公开暴露，只有 Telegram 可以通过 webhook 访问。

**Q: 可以同时在手机和电脑使用吗？**
A: 可以！只要连接到同一个 Telegram bot，所有消息都会发送到同一个 Claude 实例。

**Q: 如何查看 Claude Code 的原始输出？**
A: 运行 `tmux attach -t claude` 可以进入 tmux 会话，看到 Claude 的实时输出。

**Q: 服务重启后需要重新设置 webhook 吗？**
A: 不需要。启动脚本会自动设置 webhook。但 Tunnel URL 会变化，这是正常的（Cloudflare 的免费隧道每次都会分配新 URL）。

**Q: 为什么 Tunnel URL 每次都不一样？**
A: 免费版的 Cloudflare Tunnel 每次启动都会分配随机 URL。如果需要固定域名，可以购买 Cloudflare 的付费服务或使用自己的域名。

**Q: 可以修改 bot 命令吗？**
A: 可以，修改 `bridge.py` 中的 `BOT_COMMANDS` 列表，然后重启服务。

**Q: 如何更新项目？**
A:
```bash
cd claudecode-telegram
git pull
# 如果需要更新依赖
source .venv/bin/activate
pip install -e .
./start.sh restart
```

---

## 相关文件说明

| 文件 | 说明 |
|------|------|
| `start.sh` | 一键启动脚本 |
| `bridge.py` | Telegram Bridge 主程序 |
| `bridge-polling.py` | Bridge 的轮询模式版本（备用） |
| `bridge.log` | Bridge 运行日志 |
| `tunnel.log` | Cloudflare Tunnel 日志 |
| `bridge.pid` | Bridge 进程 ID |
| `tunnel.pid` | Tunnel 进程 ID |
| `tunnel.url` | Tunnel 公网 URL |
| `hooks/send-to-telegram.sh` | Claude 的 Stop hook 脚本 |

---

## 获取帮助

如果遇到问题：

1. 查看日志：`./start.sh logs`
2. 检查状态：`./start.sh status`
3. 查看本指南的 [故障排查](#第七部分：故障排查) 部分
4. 在 GitHub 项目页面提交 issue

---

## 许可证

MIT License

---

**祝使用愉快！🎉**
