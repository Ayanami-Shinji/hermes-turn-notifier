# hermes-turn-notifier

macOS 系统通知插件 —— Hermes 每轮回答完成后弹出一条通知，显示回答预览。

> 仅 macOS，非 Mac 静默跳过，不影响主流程。

## 安装

```bash
hermes plugins install Ayanami-Shinji/hermes-turn-notifier
```

安装完提示 `Enable now? [y/N]`，输入 `y`。重启 Hermes 生效。

## 效果

每次 Hermes 回答完，macOS 通知中心弹出：

```
          Hermes
          好的，我来帮你看看那个问题…
```

## 卸载

```bash
hermes plugins disable hermes-turn-notifier
hermes plugins remove hermes-turn-notifier
```

## 兼容性

- TUI（`hermes --tui`）✅
- CLI（`hermes`）✅
- iTerm2 / Terminal.app / Warp / kitty 等任意终端 ✅
- gateway（Telegram / Discord 等）不会触发
