"""
Apple-style Design System
Inspired by Apple Human Interface Guidelines & iOS 17 Dark Mode
"""

import customtkinter as ctk

# ─── Appearance ──────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ─── Color Palette ────────────────────────────────────────────────────────────

# Backgrounds
BG_PRIMARY       = "#080808"   # Main window background (near black)
BG_SECONDARY     = "#111111"   # Card / panel surface
BG_TERTIARY      = "#1c1c1e"   # Input fields, inner containers
BG_QUATERNARY    = "#2c2c2e"   # Table headers, separators, inactive tabs
BG_HOVER         = "#3a3a3c"   # Hover state for interactive elements

# Gradient for login
BG_GRAD_TOP      = "#0a0a0f"   # Very dark with subtle navy hint
BG_GRAD_BOT      = "#040408"   # Near pure black

# Accent Colors (Apple system palette)
BLUE             = "#0a84ff"   # Apple Blue — primary action
BLUE_HOVER       = "#0070e0"
GREEN            = "#30d158"   # Apple Green — success
GREEN_HOVER      = "#25a244"
ORANGE           = "#ff9f0a"   # Apple Orange — warning
ORANGE_HOVER     = "#e08800"
RED              = "#ff453a"   # Apple Red — destructive
RED_HOVER        = "#d93025"
PURPLE           = "#bf5af2"   # Apple Purple — secondary accent
PURPLE_HOVER     = "#9b40cc"
TEAL             = "#5ac8fa"   # Apple Teal — info/log accent

# Text Colors
TEXT_PRIMARY     = "#ffffff"   # Headlines, important values
TEXT_SECONDARY   = "#8e8e93"   # Labels, subtitles (iOS secondary)
TEXT_TERTIARY    = "#48484a"   # Placeholders, disabled (iOS tertiary)
TEXT_ACCENT      = BLUE        # Active tab, links

# Borders & Separators
BORDER           = "#2c2c2e"   # Subtle border (iOS separator)
BORDER_FOCUS     = "#0a84ff"   # Focused input border

# ─── Typography ──────────────────────────────────────────────────────────────
FONT_FAMILY      = "Helvetica Neue"   # Renders as SF Pro on macOS

def font(size=13, weight="normal", family=None):
    """Return a CTkFont with Apple-style defaults."""
    return ctk.CTkFont(family=family or FONT_FAMILY, size=size, weight=weight)

# Predefined type styles
def title_large():   return font(28, "bold")
def title():         return font(20, "bold")
def headline():      return font(16, "bold")
def subheadline():   return font(14, "bold")
def body():          return font(14)
def body_bold():     return font(14, "bold")
def callout():       return font(13)
def callout_bold():  return font(13, "bold")
def footnote():      return font(11)
def caption():       return font(10)
def mono(size=12):   return ctk.CTkFont(family="SF Mono", size=size)

# ─── Shape & Layout ───────────────────────────────────────────────────────────
RADIUS_SM        = 8
RADIUS_MD        = 12
RADIUS_LG        = 16
RADIUS_PILL      = 50

PADDING_SM       = 8
PADDING_MD       = 16
PADDING_LG       = 24

# ─── Widget Factory Helpers ───────────────────────────────────────────────────

def card(parent, **kwargs):
    """Standard iOS-style card frame."""
    defaults = dict(
        corner_radius=RADIUS_MD,
        fg_color=BG_SECONDARY,
        border_width=1,
        border_color=BORDER
    )
    defaults.update(kwargs)
    return ctk.CTkFrame(parent, **defaults)


def navbar(parent, **kwargs):
    """Top navigation bar frame."""
    defaults = dict(
        height=56,
        corner_radius=RADIUS_MD,
        fg_color=BG_SECONDARY,
        border_width=1,
        border_color=BORDER
    )
    defaults.update(kwargs)
    return ctk.CTkFrame(parent, **defaults)


def label(parent, text, style="body", color=None, **kwargs):
    """Convenience label with predefined type styles."""
    style_map = {
        "title_large": (title_large, TEXT_PRIMARY),
        "title": (title, TEXT_PRIMARY),
        "headline": (headline, TEXT_PRIMARY),
        "subheadline": (subheadline, TEXT_PRIMARY),
        "body": (body, TEXT_PRIMARY),
        "body_bold": (body_bold, TEXT_PRIMARY),
        "callout": (callout, TEXT_SECONDARY),
        "callout_bold": (callout_bold, TEXT_SECONDARY),
        "footnote": (footnote, TEXT_SECONDARY),
        "caption": (caption, TEXT_TERTIARY),
    }
    fn, default_color = style_map.get(style, (body, TEXT_PRIMARY))
    return ctk.CTkLabel(
        parent, text=text, font=fn(),
        text_color=color or default_color,
        **kwargs
    )


def primary_button(parent, text, command=None, width=0, height=44, **kwargs):
    """Full-width, Apple Blue primary action button."""
    defaults = dict(
        text=text,
        height=height,
        width=width,
        corner_radius=RADIUS_MD,
        fg_color=BLUE,
        hover_color=BLUE_HOVER,
        text_color=TEXT_PRIMARY,
        font=body_bold(),
        command=command
    )
    defaults.update(kwargs)
    return ctk.CTkButton(parent, **defaults)


def secondary_button(parent, text, command=None, width=0, height=36, **kwargs):
    """Muted secondary button."""
    defaults = dict(
        text=text,
        height=height,
        width=width,
        corner_radius=RADIUS_MD,
        fg_color=BG_QUATERNARY,
        hover_color=BG_HOVER,
        text_color=TEXT_SECONDARY,
        font=callout_bold(),
        command=command
    )
    defaults.update(kwargs)
    return ctk.CTkButton(parent, **defaults)


def danger_button(parent, text, command=None, width=0, height=36, **kwargs):
    """Red destructive action button."""
    defaults = dict(
        text=text,
        height=height,
        width=width,
        corner_radius=RADIUS_MD,
        fg_color=RED,
        hover_color=RED_HOVER,
        text_color=TEXT_PRIMARY,
        font=callout_bold(),
        command=command
    )
    defaults.update(kwargs)
    return ctk.CTkButton(parent, **defaults)


def text_input(parent, placeholder="", height=44, **kwargs):
    """iOS-style text input field."""
    defaults = dict(
        placeholder_text=placeholder,
        height=height,
        corner_radius=RADIUS_MD,
        border_color=BORDER,
        border_width=1,
        fg_color=BG_TERTIARY,
        text_color=TEXT_PRIMARY,
        placeholder_text_color=TEXT_TERTIARY,
        font=body()
    )
    defaults.update(kwargs)
    return ctk.CTkEntry(parent, **defaults)


def separator(parent, **kwargs):
    """Thin horizontal separator line."""
    defaults = dict(height=1, fg_color=BORDER, corner_radius=0)
    defaults.update(kwargs)
    return ctk.CTkFrame(parent, **defaults)


def status_badge_colors(status: str):
    """Returns (text, fg_color, text_color) for inventory status badges."""
    if status == "Expired":
        return "Expired", RED, TEXT_PRIMARY
    elif status == "Low Stock":
        return "Low Stock", ORANGE, TEXT_PRIMARY
    else:
        return "In Stock", GREEN, TEXT_PRIMARY
