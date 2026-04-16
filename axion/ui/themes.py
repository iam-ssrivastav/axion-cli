"""
Color themes for Axion CLI terminal output.
"""

THEMES = {
    "dark": {
        "primary": "#a78bfa",       # Purple
        "secondary": "#67e8f9",     # Cyan
        "accent": "#f472b6",        # Pink
        "success": "#4ade80",       # Green
        "warning": "#fbbf24",       # Amber
        "error": "#f87171",         # Red
        "info": "#60a5fa",          # Blue
        "text": "#e2e8f0",          # Light gray
        "muted": "#94a3b8",         # Gray
        "border": "#475569",        # Slate
        "bg_panel": "#1e293b",      # Dark slate
        "tool_name": "#fbbf24",     # Amber for tool names
        "tool_arg": "#67e8f9",      # Cyan for tool args
        "user_prompt": "#a78bfa",   # Purple for user prompt marker
        "ai_response": "#e2e8f0",   # Light for AI text
        "code_bg": "#0f172a",       # Very dark for code blocks
    },
    "light": {
        "primary": "#7c3aed",
        "secondary": "#0891b2",
        "accent": "#db2777",
        "success": "#16a34a",
        "warning": "#d97706",
        "error": "#dc2626",
        "info": "#2563eb",
        "text": "#1e293b",
        "muted": "#64748b",
        "border": "#cbd5e1",
        "bg_panel": "#f1f5f9",
        "tool_name": "#d97706",
        "tool_arg": "#0891b2",
        "user_prompt": "#7c3aed",
        "ai_response": "#1e293b",
        "code_bg": "#f8fafc",
    },
}


def get_theme(name: str = "dark") -> dict:
    """Get a theme by name, defaulting to dark."""
    return THEMES.get(name, THEMES["dark"])
