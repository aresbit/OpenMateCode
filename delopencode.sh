#!/usr/bin/env bash
# =============================================================
# OpenCode / oh-my-opencode FULL CLEAN UNINSTALL (Linux)
# =============================================================
set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[0;37m'
NC='\033[0m'

info()    { echo -e "${CYAN}$*${NC}"; }
step()    { echo -e "${YELLOW}$*${NC}"; }
run()     { echo -e "${GRAY}>> $*${NC}"; eval "$@" 2>/dev/null || true; }
cmd_exists() { command -v "$1" &>/dev/null; }

info "=== OpenCode / oh-my-opencode FULL CLEAN UNINSTALL (Linux) ==="
echo ""

# ------------------------------------------------------------
# 0. 官方 CLI 自卸载
# ------------------------------------------------------------
step "[1/9] Running official opencode uninstall"
if cmd_exists opencode; then
    run "opencode uninstall --force"
else
    echo "  opencode CLI not found, skip"
fi

# ------------------------------------------------------------
# 1. Node 生态（npm / pnpm / yarn / bun）
# ------------------------------------------------------------
step "[2/9] Removing Node-based installs"

if cmd_exists npm; then
    run "npm uninstall -g opencode-ai"
    run "npm uninstall -g opencode"
    run "npm cache clean --force"
fi

if cmd_exists pnpm; then
    run "pnpm uninstall -g opencode-ai"
    run "pnpm store prune"
fi

if cmd_exists yarn; then
    run "yarn global remove opencode-ai"
fi

if cmd_exists bun; then
    run "bun remove -g opencode-ai"
    run "rm -rf '$HOME/.bun'"
fi

# ------------------------------------------------------------
# 2. Homebrew (Linux/Linuxbrew)
# ------------------------------------------------------------
step "[3/9] Checking Homebrew"
if cmd_exists brew; then
    run "brew uninstall opencode"
    run "brew autoremove"
fi

# ------------------------------------------------------------
# 3. Mise (ubi)
# ------------------------------------------------------------
step "[4/9] Checking Mise"
if cmd_exists mise; then
    run "mise uninstall -g ubi:sst/opencode"
fi

# ------------------------------------------------------------
# 4. 系统包管理器残留二进制
# ------------------------------------------------------------
step "[5/9] Removing standalone binaries"

BINARY_PATHS=(
    "/usr/local/bin/opencode"
    "/usr/bin/opencode"
    "$HOME/.local/bin/opencode"
    "$HOME/.bin/opencode"
    "$HOME/bin/opencode"
)

for p in "${BINARY_PATHS[@]}"; do
    if [ -f "$p" ] || [ -L "$p" ]; then
        echo "  Removing $p"
        run "rm -f '$p'"
    fi
done

# ------------------------------------------------------------
# 5. Docker
# ------------------------------------------------------------
step "[6/9] Checking Docker"
if cmd_exists docker; then
    docker ps -a --format "{{.ID}} {{.Image}}" 2>/dev/null | grep "opencode" | while read -r id _; do
        run "docker rm -f $id"
    done

    docker images --format "{{.Repository}}:{{.Tag}}" 2>/dev/null | grep "opencode" | while read -r img; do
        run "docker image rm -f $img"
    done
fi

# ------------------------------------------------------------
# 6. 配置与数据目录
# ------------------------------------------------------------
step "[7/9] Removing config & data directories"

DATA_PATHS=(
    "$HOME/.config/opencode"
    "$HOME/.local/share/opencode"
    "$HOME/.opencode"
    "$HOME/.oh-my-opencode"
    "$HOME/.config/opencode/plugins/oh-my-opencode"
    # npm global 模块
    "$HOME/.npm/node_modules/opencode-ai"
    "/usr/local/lib/node_modules/opencode-ai"
    # bun global
    "$HOME/.bun/install/global/node_modules/opencode-ai"
    # Mise 工具链目录
    "$HOME/.local/share/mise/installs/ubi-sst-opencode"
    # 临时缓存
    "$HOME/.cache/opencode"
    "/tmp/opencode-*"
)

for p in "${DATA_PATHS[@]}"; do
    # 支持 glob（/tmp/opencode-*）
    for expanded in $p; do
        if [ -e "$expanded" ]; then
            echo "  Removing $expanded"
            run "rm -rf '$expanded'"
        fi
    done
done

# ------------------------------------------------------------
# 7. PATH 清理（~/.bashrc / ~/.zshrc / ~/.profile 等）
# ------------------------------------------------------------
step "[8/9] Cleaning PATH entries in shell configs"

SHELL_CONFIGS=(
    "$HOME/.bashrc"
    "$HOME/.bash_profile"
    "$HOME/.zshrc"
    "$HOME/.zprofile"
    "$HOME/.profile"
    "$HOME/.config/fish/config.fish"
)

for cfg in "${SHELL_CONFIGS[@]}"; do
    if [ -f "$cfg" ]; then
        if grep -q "opencode" "$cfg" 2>/dev/null; then
            echo "  Cleaning $cfg"
            # 删除含 opencode 的行（PATH export 或 source 行）
            run "sed -i '/opencode/d' '$cfg'"
        fi
    fi
done

# ------------------------------------------------------------
# 8. 检查残留（只报告，不删除）
# ------------------------------------------------------------
step "[9/9] Scanning for remaining traces"

echo ""
echo "  Checking 'which opencode' ..."
which opencode 2>/dev/null && echo "  WARNING: opencode still found in PATH!" || echo "  OK: not in PATH"

echo ""
echo "  Searching filesystem for opencode files (may take a moment)..."
FOUND=$(find /usr /home/"$USER" "$HOME" -name "*opencode*" \
    -not -path "*/proc/*" \
    -not -path "*/.git/*" \
    2>/dev/null | head -20 || true)

if [ -n "$FOUND" ]; then
    echo -e "${YELLOW}  Remaining files found (manual review recommended):${NC}"
    echo "$FOUND"
else
    echo "  No remaining files found."
fi

# ------------------------------------------------------------
echo ""
echo -e "${GREEN}=== DONE ===${NC}"
echo "Please restart your shell and verify:"
echo "  opencode --version"
echo "  which opencode"