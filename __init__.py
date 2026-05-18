"""hermes-turn-notifier — macOS notification after each Hermes response.

Registers a ``post_llm_call`` hook that fires a macOS system notification
via ``osascript`` whenever Hermes completes a final answer turn.

- Only fires on local terminals (CLI / TUI / terminal / ink_tui).
- Silently skips on non-macOS.
- All exceptions are swallowed — never affects the agent loop.
- Writes nothing to stdout/stderr so TUI rendering is never disturbed.
"""

from __future__ import annotations

import logging
import platform
import subprocess
from typing import Any

logger = logging.getLogger(__name__)

# Platform names that indicate a local interactive terminal session.
_LOCAL_TERMINAL_PLATFORMS = frozenset({
    "cli",
    "tui",
    "terminal",
    "ink_tui",
    "ink",
})

_OSASCRIPT = "/usr/bin/osascript"
_IS_MACOS = platform.system() == "Darwin"

# Max chars of the response to show in the notification body.
_PREVIEW_MAX_CHARS = 200


def _sanitize_for_applescript(text: str) -> str:
    """Escape double-quotes and backslashes for AppleScript string literal."""
    return text.replace("\\", "\\\\").replace('"', '\\"')


def _build_notification_script(response: str) -> str:
    """Build the AppleScript: ``display notification "preview" with title "Hermes"``."""

    # Take first non-empty line, truncate to preview length.
    preview = ""
    for line in response.splitlines():
        stripped = line.strip()
        if stripped:
            preview = stripped
            break

    if not preview:
        preview = "回答已完成"

    if len(preview) > _PREVIEW_MAX_CHARS:
        preview = preview[:_PREVIEW_MAX_CHARS] + "…"

    return (
        f'display notification "{_sanitize_for_applescript(preview)}"'
        f' with title "Hermes"'
    )


def _on_post_llm_call(
    session_id: str = "",
    user_message: str = "",
    assistant_response: str = "",
    conversation_history: Any = None,
    model: str = "",
    platform: str = "",
    **kwargs: Any,
) -> None:
    """Fire a macOS notification after each completed response turn."""
    try:
        if not platform or platform not in _LOCAL_TERMINAL_PLATFORMS:
            return

        if not _IS_MACOS:
            return

        script = _build_notification_script(
            response=assistant_response or "",
        )

        result = subprocess.run(
            [_OSASCRIPT, "-e", script],
            check=False,
            timeout=5,
            capture_output=True,
        )

        # Log failures to agent.log so plugin authors can debug.
        if result.returncode != 0:
            err = result.stderr.decode("utf-8", errors="replace").strip()
            logger.debug(
                "hermes-turn-notifier: osascript failed (rc=%d): %s",
                result.returncode, err,
            )
    except Exception:
        pass


def register(ctx) -> None:
    """Register the post_llm_call hook."""
    ctx.register_hook("post_llm_call", _on_post_llm_call)
