# openmatecode - 免费在手机上玩Code Agent 📱✨

> 人人都能上手的AI编程助手，让你在Telegram上免费使用opencode写代码！ 下一步即将支持国内非书平台 start && fork!!

![demo](demo.gif)

## 🌟 一句话介绍
**在手机上免费使用opencode，就像和朋友聊天一样简单！**

## 🚀 极速上手（3步搞定）

### 第1步：准备电脑（任何电脑都行）
```bash
# 复制这个项目到你的电脑
git clone https://github.com/aresbit/OpenMateCode.git
cd OpenMateCode
```

### 第2步：创建Telegram机器人（就像注册微信一样简单）
1. **打开Telegram**（手机App或电脑版都可以）
2. **搜索 `@BotFather`**（这是Telegram的机器人管家）
3. **发送 `/newbot`** 创建新机器人
4. **给机器人起个名字**（比如：`我的Code助手`）
5. **复制机器人Token**（一串像`123456:ABCdefGhIJKlmNoPQRsTUVwxyZ`的密码）

### 第3步：一键启动
```bash
# 设置机器人密码（把YOUR_TOKEN换成你刚复制的）
export TELEGRAM_BOT_TOKEN="你的机器人Token"

## 安装依赖

**macOS:**
```bash
brew install tmux
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tmux python3
```

---

## 配置

### 1. 配置 Claude 钩子

```bash
cp hooks/send-to-telegram.sh ~/.claude/hooks/
chmod +x ~/.claude/hooks/send-to-telegram.sh
```

编辑 `~/.claude/hooks/send-to-telegram.sh`，设置你的 bot token。

### 2. 配置 Claude settings

在 `~/.claude/settings.json` 中添加：

```json
{
  "hooks": {
    "Stop": [{"hooks": [{"type": "command", "command": "~/.claude/hooks/send-to-telegram.sh"}]}]
  }
}
```

# 启动！
./matecode.sh start
```

**🎉 搞定！** 现在回到Telegram，给你的机器人发消息，就能开始写代码了！

## 📱 手机使用指南

### 在手机上聊天写代码
1. **打开Telegram App**
2. **找到你的机器人**（就是刚才创建的那个）
3. **像和朋友聊天一样发送指令**：
   ```
   帮我写一个Python爬虫
   ```
4. **等待AI回复代码**（自动发送到你的手机）

### 常用命令（直接在聊天框输入）
| 命令 | 功能 | 例子 |
|------|------|------|
| `/start` | 开始对话 | `/start` |
| `/clear` | 清空对话 | `/clear` |
| `/continue_` | 继续上次对话 | `/continue_` |
| `/stop` | 停止AI思考 | `/stop` |
| `/remember 内容` | 保存重要信息 | `/remember Python爬虫用requests库` |
| `/recall 关键词` | 查找记忆 | `/recall Python` |

## 💻 电脑端设置（更详细版）

### 安装依赖（超级简单）
**macOS：**
```bash
brew install tmux
```

**Windows（用WSL）：**
```bash
# 在Microsoft Store安装Ubuntu
sudo apt-get install tmux python3
```

**Linux：**
```bash
sudo apt-get install tmux python3
```

### 配置opencode（如果还没安装）

**opencode是什么？** 一个免费的AI编程助手命令行工具。

**安装方法：**
1. **访问官网**：打开浏览器访问 [opencode.ai](https://opencode.ai)
2. **下载安装**：根据你的系统（Windows/macOS/Linux）下载安装包
3. **验证安装**：打开终端，输入 `opencode --version`，看到版本号就成功了！

**如果已经安装Claude Code：**
- 你可以直接使用，项目会自动兼容
- 或者也安装opencode获得更好体验

## 🧠 智能记忆功能
**你的AI助手会记住你说过的话！**
- 🤖 **自动记忆**：每次对话自动保存重点
- 🔍 **智能搜索**：需要时自动回忆相关历史
- 🔒 **完全私密**：所有数据存在你电脑，不上传云端
- 🗑️ **随时删除**：用 `/forget all` 清空所有记忆

## 🔧 高级配置（可选）

### 环境变量设置
```bash
# 启用记忆功能（默认开启）
export MEMORY_ENABLED=true

# 设置每次最多回忆5条历史
export MEMORY_MAX_RESULTS=5

# 发送原始消息（推荐开启）
export TELEGRAM_RAW_MESSAGES=true
```

### 开机自启动
```bash
# 编辑启动脚本
nano ~/.bashrc

# 添加这行（记得替换YOUR_TOKEN）
export TELEGRAM_BOT_TOKEN="你的Token"
```

## ❓ 常见问题

### 🤔 机器人不回复？
```bash
# 1. 检查Token
echo $TELEGRAM_BOT_TOKEN

# 2. 查看日志
./matecode.sh logs

# 3. 重启服务
./matecode.sh restart
```

### 🔄 重复回复？
```bash
rm -f ~/.claude/telegram_pending
./matecode.sh restart
```

### 📶 网络问题？
- 确保电脑能访问Telegram（可能需要科学上网）
- 检查防火墙设置

## 🎯 使用技巧

### 编程任务示例
```
请帮我写一个网站登录页面
```

```
分析这个错误：ImportError: No module named 'requests'
```

```
教我学JavaScript，从变量开始
```

### 生活助手
```
帮我写一封英文求职信
```

```
规划一个周末旅行行程
```

```
给我讲个编程笑话
```

## 🔐 安全提示
- 🔒 **Token是密码**：不要分享给他人
- 💾 **数据本地存储**：所有对话存在你电脑
- 🚫 **无费用**：完全免费使用
- 📞 **无客服**：社区互助解决问题

## 📁 文件说明
| 文件 | 用途 |
|------|------|
| `matecode.sh` | 一键启动脚本 |
| `bridge.py` | 核心桥接程序 |
| `memory.py` | 记忆系统 |
| `hooks/send-to-telegram.sh` | 消息转发脚本 |

## 🤝 贡献与反馈
- **遇到问题**：查看 [GUIDE.md](GUIDE.md) 详细指南
- **建议改进**：提交Issue或Pull Request
- **分享经验**：帮助其他新手

## 📄 许可证
MIT License - 免费使用，自由修改

---

**✨ 现在就去创建你的机器人，开始免费在手机上写代码吧！**

> 提示：如果遇到困难，再看一遍第2步，创建机器人是最关键的一步！

