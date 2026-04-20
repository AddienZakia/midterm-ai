from dataclasses import dataclass


@dataclass(frozen=True)
class ColorPalette:
    # Primary
    primary_main: str    = "#FFA32B"
    primary_hover: str   = "#E69524"
    primary_active: str  = "#CC841F"
    primary_surface: str = "#FFF4E5"
    primary_border: str  = "#FFD9A8"
    primary_focus: str   = "#FFA32B"

    # Neutral
    neutral_white: str   = "#F8FAFC"
    neutral_black: str   = "#1D1F20"
    neutral_10: str      = "#F8FAFC"
    neutral_20: str      = "#F1F5F9"
    neutral_30: str      = "#E2E8F0"
    neutral_40: str      = "#CBD5E1"
    neutral_50: str      = "#94A3B8"
    neutral_60: str      = "#64748B"
    neutral_70: str      = "#475569"
    neutral_80: str      = "#334155"
    neutral_90: str      = "#1E293B"

    # Success
    success_main: str    = "#16A34A"
    success_hover: str   = "#15803D"
    success_active: str  = "#166534"
    success_surface: str = "#DCFCE7" 
    success_border: str = "#86EFAC" 
    success_focus: str = "#4ADE80" 

    # Warning
    warning_main: str    = "#D97706"
    warning_hover: str   = "#B45309"
    warning_active: str  = "#92400E"
    warning_surface: str = "#FEF3C7" 
    warning_border: str = "#FCD34D" 
    warning_focus: str = "#FBBF24" 

    # Error
    error_main: str      = "#DC2626"
    error_hover: str     = "#B91C1C"
    error_active: str    = "#991B1B"
    error_surface: str = "#FEE2E2" 
    error_border: str = "#FCA5A5" 
    error_focus: str = "#F87171" 


Colors = ColorPalette()