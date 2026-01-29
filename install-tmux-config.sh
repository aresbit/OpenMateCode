#!/bin/bash
# =============================================================================
# MateBot Tmux Configuration Installer
# Installs and configures oh-my-tmux for MateBot
# =============================================================================

set -e

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_success() { echo -e "${GREEN}[✓]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[!]${NC} $1"; }
print_error() { echo -e "${RED}[✗]${NC} $1"; }
print_info() { echo -e "${BLUE}[→]${NC} $1"; }

echo ""
echo "=========================================="
echo "   MateBot Tmux Configuration Setup"
echo "=========================================="
echo ""

# Check if tmux is installed
if ! command -v tmux &> /dev/null; then
    print_error "tmux not found. Please install tmux first."
    echo ""
    echo "Installation:"
    echo "  Ubuntu/Debian: sudo apt-get install tmux"
    echo "  macOS:         brew install tmux"
    echo "  RHEL/CentOS:   sudo yum install tmux"
    exit 1
fi

TMUX_VERSION=$(tmux -V | cut -d' ' -f2 | tr -d 'a-z')
print_success "tmux version: $TMUX_VERSION"

# Check minimum version (2.6)
if [ "$(printf '%s\n' "2.6" "$TMUX_VERSION" | sort -V | head -n1)" != "2.6" ]; then
    print_warning "tmux version >= 2.6 recommended"
fi

# Install oh-my-tmux
if [ -d "$HOME/.tmux" ]; then
    print_info "Updating oh-my-tmux..."
    cd ~/.tmux && git pull origin master
else
    print_info "Installing oh-my-tmux..."
    git clone --depth 1 https://github.com/gpakosz/.tmux.git ~/.tmux
fi

# Create symbolink
print_info "Creating symlinks..."
ln -sf ~/.tmux/.tmux.conf ~/.tmux.conf

# Copy local configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/.tmux.conf.local" ]; then
    print_info "Installing MateBot configuration..."
    cp "$SCRIPT_DIR/.tmux.conf.local" ~/.tmux.conf.local
else
    print_warning "MateBot local config not found, using default"
    cp ~/.tmux/.tmux.conf.local ~/.tmux.conf.local
fi

print_success "Configuration installed"

# Create .hushlogin to suppress login messages
if [ ! -f "$HOME/.hushlogin" ]; then
    touch ~/.hushlogin
    print_success "Created .hushlogin (suppresses login messages)"
fi

# Verify installation
echo ""
print_info "Verifying installation..."

if [ -L "$HOME/.tmux.conf" ] && [ -f "$HOME/.tmux.conf.local" ]; then
    print_success "Installation successful!"
else
    print_error "Installation verification failed"
    exit 1
fi

# Display summary
echo ""
echo "=========================================="
echo "         Installation Complete"
echo "=========================================="
echo ""
echo "Configuration files:"
echo "  ~/.tmux.conf        →  Main config (symlink)"
echo "  ~/.tmux.conf.local  →  Local customizations"
echo "  ~/.tmux/            →  oh-my-tmux repository"
echo ""
echo "Quick start:"
echo ""
echo "  1. Start new session:"
echo "     tmux new -s claude"
echo ""
echo "  2. Detach (keep running):"
echo "     Ctrl+b d"
echo ""
echo "  3. Reattach:"
echo "     tmux attach -t claude"
echo ""
echo "Essential shortcuts:"
echo "  Ctrl+b c     Create window"
echo "  Ctrl+b 0-9   Switch window"
echo "  Alt+1~5      Quick switch"
echo "  Ctrl+b %     Split vertical"
echo "  Ctrl+b -     Split horizontal"
echo "  Ctrl+b r     Reload config"
echo "  Ctrl+b ?     Help"
echo ""
echo "Read the full guide:"
echo "  cat ~/yyscode/matebot/MateBot/TMUX_GUIDE.md"
echo ""

# Check if already in tmux
if [ -n "$TMUX" ]; then
    print_info "You're already in tmux. Reload config with:"
    echo "  tmux source-file ~/.tmux.conf"
    echo "  or press Ctrl+b r"
else
    read -p "Start tmux now? [Y/n]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        echo ""
        print_info "Starting tmux session 'claude'..."
        echo ""
        tmux new -s claude
    fi
fi

echo ""
