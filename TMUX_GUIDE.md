# MateBot Tmux 配置指南

基于 [gpakosz/.tmux](https://github.com/gpakosz/.tmux) 的 MateBot 优化配置

## 快速安装

```bash
# 1. 克隆 oh-my-tmux
cd ~
git clone --depth 1 https://github.com/gpakosz/.tmux.git ~/.tmux

# 2. 创建主配置符号链接
ln -sf ~/.tmux/.tmux.conf ~/.tmux.conf

# 3. 复制本项目的本地配置
cp /home/ares/yyscode/matebot/MateBot/.tmux.conf.local ~/.tmux.conf.local

# 4. 重新加载 tmux（如果已在运行）
tmux source-file ~/.tmux.conf
```

## MateBot 专属优化

### 🎨 主题定制
- **深蓝/青色主题**：专业外观，长时间使用不疲劳
- **顶部状态栏**：不干扰终端底部输入
- **MateBot 标识**：状态栏显示 🤖 MateBot 标识

### ⚡ 性能优化
- **50,000 行历史**：适合长时间运行 bridge
- **10ms 响应**：更快的按键响应
- **快速同步**：窗格同步快捷键 `prefix + y`

### 🖱️ 易用性
- **鼠标支持**：滚动、选择、调整窗格大小
- **Vi 模式**：熟悉的 Vim 快捷键
- **Alt+数字**：无需前缀快速切换窗口

## 核心快捷键

### 前缀键
```
Ctrl+b  - 主前缀键
Ctrl+a  - 辅助前缀键（也可使用）
```

### 会话操作
| 快捷键 | 功能 |
|--------|------|
| `Ctrl+b d` | 分离会话（保持后台运行）|
| `Ctrl+b s` | 切换/查看会话列表 |
| `Ctrl+b $` | 重命名当前会话 |

### 窗口操作（标签页）
| 快捷键 | 功能 |
|--------|------|
| `Ctrl+b c` | 创建新窗口 |
| `Ctrl+b 0-9` | 切换到对应窗口 |
| `Alt+1` ~ `Alt+5` | 快速切换（无需前缀）|
| `Ctrl+b ,` | 重命名窗口 |
| `Ctrl+b &` | 关闭窗口 |
| `Ctrl+b n` | 下一个窗口 |
| `Ctrl+b p` | 上一个窗口 |
| `Ctrl+b l` | 上一个活动窗口 |

### 窗格操作（分屏）
| 快捷键 | 功能 |
|--------|------|
| `Ctrl+b %` | 垂直分割 |
| `Ctrl+b "` | 水平分割 |
| `Ctrl+b \|` | 垂直分割（自定义）|
| `Ctrl+b -` | 水平分割（自定义）|
| `Ctrl+b x` | 关闭当前窗格 |
| `Ctrl+b z` | 最大化/恢复窗格 |
| `Ctrl+b q` | 显示窗格编号 |
| `Ctrl+b {` / `}` | 交换窗格位置 |

### 实用功能
| 快捷键 | 功能 |
|--------|------|
| `Ctrl+b r` | 重新加载配置 |
| `Ctrl+b m` | 切换鼠标模式 |
| `Ctrl+b y` | 切换窗格同步（同时输入）|
| `Ctrl+b t` | 显示时钟 |
| `Ctrl+b [` | 进入复制模式 |
| `Ctrl+b C-l` | 清除历史 |

## MateBot 工作流示例

### 1. 基本启动流程
```bash
# 启动 tmux 会话
tmux new -s claude

# 在会话中启动 MateBot
cd ~/yyscode/matebot/MateBot
./matecode.sh start

# 分离会话（保持运行）
Ctrl+b d

# 稍后重新连接
tmux attach -t claude
```

### 2. 监控模式（多窗格）
```bash
# 创建水平分割（上下两个窗格）
Ctrl+b -

# 在下方窗格监控日志
tail -f ~/yyscode/matebot/MateBot/bridge.log

# 按 Ctrl+b ↑ 回到上方窗格操作
```

### 3. 开发模式（三分屏）
```bash
# 垂直分割
Ctrl+b %

# 在右侧再水平分割
Ctrl+b →
Ctrl+b -

# 窗格 1: 编辑代码 (vim/nano)
# 窗格 2: 运行 MateBot
# 窗格 3: 监控日志
```

### 4. 批量操作多个窗格
```bash
# 开启同步模式（命令同时发送到所有窗格）
Ctrl+b y

# 输入的命令会在所有窗格执行
# 再次 Ctrl+b y 关闭同步
```

## 复制粘贴指南

### 在 Tmux 内复制
```
1. 按 Ctrl+b [ 进入复制模式
2. 按 v 开始选择（或 V 选择行）
3. 使用方向键移动选择区域
4. 按 y 复制并退出
```

### 粘贴
```
Ctrl+b ]  # 粘贴 tmux 缓冲区
```

## 配置自定义

编辑 `~/.tmux.conf.local`：

```bash
# 修改历史记录限制
set -g history-limit 100000

# 禁用鼠标
set -g mouse off

# 更改状态栏位置
set -g status-position bottom

# 添加自定义快捷键
bind C-s source-file ~/.tmux.conf \; display "Reloaded!"
```

重新加载：
```bash
tmux source-file ~/.tmux.conf
# 或按 Ctrl+b r
```

## 故障排除

### 颜色显示异常
```bash
# 检查终端类型
echo $TERM

# 应输出 screen-256color 或 xterm-256color
# 如果不是，添加到 ~/.bashrc:
export TERM=screen-256color
```

### 鼠标无法滚动
```bash
# 确保鼠标模式开启
tmux show -g mouse
# 应显示 mouse on

# 临时开启
Ctrl+b m

# 永久开启（编辑 ~/.tmux.conf.local）
set -g mouse on
```

### 剪贴板不工作
```bash
# Linux 安装剪贴板工具
sudo apt-get install xclip
# 或
sudo apt-get install xsel

# macOS 内置支持
# WSL 需要特殊配置
```

### 快捷键冲突
某些终端（如 VS Code 终端）可能占用 `Ctrl+b`：
```bash
# 使用辅助前缀 Ctrl+a
Ctrl+a + 命令

# 或在 .tmux.conf.local 中更改前缀：
set -g prefix C-a
unbind C-b
bind C-a send-prefix
```

## 常用命令速查

```bash
# 会话管理
tmux new -s name          # 新建会话
tmux ls                   # 列出会话
tmux attach -t name       # 附加会话
tmux detach               # 分离会话
tmux kill-session -t name # 结束会话
tmux rename-session -t old new

# 窗口管理
Ctrl+b c                  # 新建窗口
Ctrl+b ,                  # 重命名窗口
Ctrl+b &                  # 关闭窗口
Ctrl+b 0-9                # 切换窗口

# 窗格管理
Ctrl+b %                  # 垂直分割
Ctrl+b "                  # 水平分割
Ctrl+b x                  # 关闭窗格
Ctrl+b z                  # 最大化
Ctrl+b Space              # 切换布局

# 其他
Ctrl+b ?                  # 查看所有快捷键
Ctrl+b :                  # 命令模式
Ctrl+b r                  # 重载配置
Ctrl+b t                  # 时钟
Ctrl+b ~                  # 显示消息历史
```

## 与 MateBot 集成

### 一键启动脚本
创建 `~/start-matebot.sh`：

```bash
#!/bin/bash
SESSION="matebot"

# 检查会话是否存在
tmux has-session -t $SESSION 2>/dev/null

if [ $? != 0 ]; then
    # 创建新会话
    tmux new-session -d -s $SESSION

    # 窗口 1: MateBot
    tmux rename-window -t $SESSION:0 'main'
    tmux send-keys -t $SESSION:0 'cd ~/yyscode/matebot/MateBot' C-m
    tmux send-keys -t $SESSION:0 './matecode.sh start' C-m

    # 窗口 2: 日志监控
    tmux new-window -t $SESSION:1 -n 'logs'
    tmux send-keys -t $SESSION:1 'cd ~/yyscode/matebot/MateBot' C-m
    tmux send-keys -t $SESSION:1 './matecode.sh logs' C-m

    # 窗口 3: 编辑
    tmux new-window -t $SESSION:2 -n 'edit'
    tmux send-keys -t $SESSION:2 'cd ~/yyscode/matebot/MateBot' C-m
fi

# 附加到会话
tmux attach -t $SESSION
```

```bash
chmod +x ~/start-matebot.sh
~/start-matebot.sh
```

## 资源

- [Tmux 官方文档](https://github.com/tmux/tmux/wiki)
- [Oh my tmux! GitHub](https://github.com/gpakosz/.tmux)
- [Tmux 快捷键速查表](https://tmuxcheatsheet.com/)
- 本地 Skill: `~/.claude/SKILL-tmux-matebot.md`
