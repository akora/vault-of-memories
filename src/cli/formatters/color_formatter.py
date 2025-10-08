"""
Color formatter.

ANSI color formatting utilities.
"""

import sys
import os


class ColorFormatter:
    """ANSI color formatting utilities."""

    # ANSI color codes
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

    def __init__(self):
        """Initialize color formatter."""
        # Disable colors if not TTY or NO_COLOR set
        if not self.is_terminal():
            self.GREEN = self.YELLOW = self.RED = self.BLUE = ''
            self.CYAN = self.MAGENTA = self.BOLD = self.RESET = ''

    def colorize(self, text: str, color: str, bold: bool = False) -> str:
        """
        Apply color to text.

        Args:
            text: Text to colorize
            color: Color name (green, yellow, red, blue, cyan, magenta)
            bold: Whether to make text bold

        Returns:
            Text with ANSI color codes
        """
        color_codes = {
            'green': self.GREEN,
            'yellow': self.YELLOW,
            'red': self.RED,
            'blue': self.BLUE,
            'cyan': self.CYAN,
            'magenta': self.MAGENTA
        }

        code = color_codes.get(color.lower(), '')
        if code:
            prefix = f"{self.BOLD}{code}" if bold else code
            return f"{prefix}{text}{self.RESET}"
        return text

    def success(self, text: str) -> str:
        """Colorize text as success (green)."""
        return self.colorize(text, 'green')

    def warning(self, text: str) -> str:
        """Colorize text as warning (yellow)."""
        return self.colorize(text, 'yellow')

    def error(self, text: str) -> str:
        """Colorize text as error (red)."""
        return self.colorize(text, 'red')

    def info(self, text: str) -> str:
        """Colorize text as info (blue)."""
        return self.colorize(text, 'blue')

    def is_terminal(self) -> bool:
        """
        Check if output is a terminal (supports colors).

        Returns:
            True if TTY, False otherwise
        """
        # Check NO_COLOR environment variable
        if os.environ.get('NO_COLOR'):
            return False

        # Check if stdout is a TTY
        return sys.stdout.isatty()
