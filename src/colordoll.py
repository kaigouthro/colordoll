import random
import json
import re
from functools import wraps
from typing import Dict, Union, Optional, Any, Callable
import yaml


class AnsiColor:
    """Represents an ANSI escape code for text coloration."""

    code: int
    name: str

    def __init__(self, code: int, name: str = "") -> None:
        """
        Initializes an AnsiColor object.

        Args:
            code (int): The ANSI escape code.
            name (str, optional): The name of the color. Defaults to "".

        Raises:
            ValueError: If the ANSI code is not an integer.
        """
        if not isinstance(code, int):
            raise ValueError("ANSI code must be an integer")
        self.code = code
        self.name = name

    def __str__(self) -> str:
        """Returns the ANSI escape code sequence as a string."""
        return f"\033[{self.code}m"

    def __repr__(self) -> str:
        """Returns a string representation of the AnsiColor object."""
        return f"AnsiColor(code={self.code}, name='{self.name}')"


class ConfigLoader:
    """Loads configuration from various sources (file, dict, string)."""

    def load_config(self, config_source: Union[str, Dict, Any]) -> Dict:
        """
        Loads configuration from a file, dictionary, or string.

        Args:
            config_source (Union[str, Dict, Any]): Path to config file, config dictionary, or config string.

        Returns:
            Dict: Configuration dictionary. Returns empty dict on loading failure.
        """
        if isinstance(config_source, str):
            return self._load_from_string_or_file(config_source)
        elif isinstance(config_source, Dict):
            return config_source
        return {}

    def _load_from_string_or_file(self, config_source: str) -> Dict:
        """
        Attempts to load config from a file path or a JSON/YAML string.

        Args:
            config_source (str): File path or configuration string.

        Returns:
            Dict: Configuration dictionary, empty if loading fails.
        """
        try:
            with open(config_source, "r") as file:
                if config_source.endswith((".yaml", ".yml")):
                    return yaml.safe_load(file) or {}
                return json.load(file)
        except FileNotFoundError:
            return self._parse_config_string(config_source)
        except (json.JSONDecodeError, yaml.YAMLError):
            return self._parse_config_string(config_source)
        return {}

    def _parse_config_string(self, config_string: str) -> Dict:
        """
        Attempts to parse a configuration string as JSON or YAML.

        Args:
            config_string (str): The configuration string.

        Returns:
            Dict: Configuration dictionary, empty if parsing fails.
        """
        try:
            return json.loads(config_string)
        except json.JSONDecodeError:
            try:
                return yaml.safe_load(config_string) or {}
            except (yaml.YAMLError, TypeError):
                return {}


class ColorConfig:
    """Manages color configurations."""

    config: Dict

    def __init__(self, config_source: Union[str, Dict, Any] = None) -> None:
        """
        Initializes ColorConfig by loading configurations.

        Args:
            config_source (Union[str, Dict, Any], optional): Configuration source (file, dict, string). Defaults to None.
        """
        self.config = ConfigLoader().load_config(config_source)

    def get_color_code(self, color_name: str) -> str:
        """
        Retrieves ANSI color code string for a given color name.

        Args:
            color_name (str): Name of the color.

        Returns:
            str: ANSI color code string, or empty string if color not found.
        """
        color = self.get_color_obj(color_name)
        return str(color) if color else ""

    def get_bg_color_code(self, color_name: str) -> str:
        """
        Retrieves ANSI background color code string for a color name.

        Args:
            color_name (str): Name of the color.

        Returns:
            str: ANSI background color code string, empty string if not found.
        """
        color = self.get_bg_color_obj(color_name)
        return str(color) if color else ""

    def get_color_obj(self, color_name: str) -> Optional[AnsiColor]:
        """
        Retrieves AnsiColor object for a given color name.

        Args:
            color_name (str): Name of the color.

        Returns:
            Optional[AnsiColor]: AnsiColor object, or None if not found.
        """
        return self._get_color_object(color_name)

    def get_bg_color_obj(self, color_name: str) -> Optional[AnsiColor]:
        """
        Retrieves AnsiColor object for a background color name.

        Args:
            color_name (str): Name of the color.

        Returns:
            Optional[AnsiColor]: AnsiColor background color object, or None if not found.
        """
        bg_color_name = f"bg_{color_name}"
        return self._get_color_object(bg_color_name)

    def _get_color_object(self, color_name: str) -> Optional[AnsiColor]:
        """
        Internal method to get AnsiColor object by name.

        Args:
            color_name (str): Name of the color.

        Returns:
            Optional[AnsiColor]: AnsiColor object, or None if configuration is invalid or color not found.

        Raises:
            ValueError: If color configuration is invalid (missing 'code' field).
        """
        if color_name not in self.config:
            return None
        color_data: Dict = self.config[color_name]
        if "code" not in color_data:
            raise ValueError(
                f"Invalid color configuration for '{color_name}': missing 'code' field")
        return AnsiColor(code=color_data["code"], name=color_name)


class OutputHandler:
    """Base class for output handlers."""

    def format(self, data: Any, theme_colors: Dict) -> str:
        """
        Formats the colorized data. Abstract method to be implemented by subclasses.

        Args:
            data (Any): Data to be formatted.
            theme_colors (Dict): Dictionary of theme colors.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError(
            "Subclasses must implement the format method.")


class Colorizer:
    """Provides methods for colorizing text and handling output formatting."""

    RESET: AnsiColor = AnsiColor(0, "reset")
    config: ColorConfig
    colors: Dict[str, AnsiColor]
    bg_colors: Dict[str, AnsiColor]
    output_handler: OutputHandler

    def __init__(self, config: Optional[ColorConfig] = None, output_handler: Optional[OutputHandler] = None) -> None:
        """
        Initializes a Colorizer object.

        Args:
            config (Optional[ColorConfig], optional): Color configuration object. Defaults to None (creates default ColorConfig).
            output_handler (Optional[OutputHandler], optional): Output handler object. Defaults to None (uses DataHandler).
        """
        self.config = config or ColorConfig()
        self.colors = {}
        self.bg_colors = {}
        self._load_ansi_colors()
        self.output_handler = output_handler or DataHandler(colorizer=self)

    def set_output_handler(self, handler: OutputHandler) -> None:
        """
        Sets the output handler for the Colorizer.

        Args:
            handler (OutputHandler): OutputHandler instance to be set.

        Raises:
            TypeError: If handler is not an instance of OutputHandler.
        """
        if not isinstance(handler, OutputHandler):
            raise TypeError("Handler must be an instance of OutputHandler")
        self.output_handler = handler

    def _load_ansi_colors(self) -> None:
        """Loads ANSI color codes for foreground and background colors."""
        ansi_colors: Dict[str, int] = {
            "black": 30, "red": 31, "green": 32, "yellow": 33, "blue": 34,
            "magenta": 35, "cyan": 36, "white": 37, "bright_black": 90,
            "bright_red": 91, "bright_green": 92, "bright_yellow": 93,
            "bright_blue": 94, "bright_magenta": 95, "bright_cyan": 96,
            "bright_white": 97, "grey": 90,
        }
        ansi_bg_colors: Dict[str, int] = {
            "bg_black": 40, "bg_red": 41, "bg_green": 42, "bg_yellow": 43,
            "bg_blue": 44, "bg_magenta": 45, "bg_cyan": 46, "bg_white": 47,
            "bg_bright_black": 100, "bg_bright_red": 101, "bg_bright_green": 102,
            "bg_bright_yellow": 103, "bg_bright_blue": 104, "bg_bright_magenta": 105,
            "bg_bright_cyan": 106, "bg_bright_white": 107,
        }

        for name, code in ansi_colors.items():
            self.colors[name] = AnsiColor(code, name)
        for name, code in ansi_bg_colors.items():
            bg_name = name.replace("bg_", "")
            self.bg_colors[bg_name] = AnsiColor(code, name)

    def get_color_code(self, color_name: str) -> str:
        """
        Retrieves the ANSI escape code for a given color name.

        Args:
            color_name (str): Name of the color.

        Returns:
            str: ANSI color code string, or empty string if color is not defined.
        """
        color_name = (color_name or "").lower()
        color_obj = self.colors.get(color_name)
        return str(color_obj) if color_obj else ""

    def get_bg_color_code(self, color_name: str) -> str:
        """
        Retrieves the ANSI escape code for a background color.

        Args:
            color_name (str): Name of the background color.

        Returns:
            str: ANSI background color code string, or empty string if not defined.
        """
        color_obj = self.bg_colors.get((color_name or "").lower())
        return str(color_obj) if color_obj else ""

    def colorize(self, text: str, color: Optional[str] = None, background_color: Optional[str] = None) -> str:
        """
        Colorizes a string with optional foreground and background colors, handling nested ANSI codes.

        Args:
            text (str): Text to colorize.
            color (Optional[str], optional): Foreground color name. Defaults to None.
            background_color (Optional[str], optional): Background color name. Defaults to None.

        Returns:
            str: Colorized text string.
        """
        reset_code = str(self.RESET)
        color_code = self.get_color_code(color) if color else ""
        bg_color_code = self.get_bg_color_code(
            background_color) if background_color else ""

        if not color_code and not bg_color_code:
            return text

        start_tag = ""
        if all((color_code, bg_color_code)):
            start_tag = f"\033[{color_code.split('[')[1].split('m')[0]};{bg_color_code.split('[')[1].split('m')[0]}m"
        elif color_code:
            start_tag = color_code
        else:
            start_tag = bg_color_code

        end_tag = reset_code

        def _process_text(text_segment: str) -> str:
            processed_segments = []
            i = 0
            while i < len(text_segment):
                if text_segment.startswith(reset_code, i):
                    processed_segments.append(reset_code)
                    i += len(reset_code)
                    processed_segments.append(start_tag)  # Re-apply style
                else:
                    processed_segments.append(text_segment[i])
                    i += 1
            return "".join(processed_segments)

        return start_tag + _process_text(text) + end_tag

    def color_decorator(self, color_name: str) -> Callable:
        """
        Creates a decorator to colorize the output of a function with a specific color.

        Args:
            color_name (str): Name of the color to apply.

        Returns:
            Callable: Decorator function.
        """

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                if isinstance(result, (str, bool, float, int, dict, list, type(None))):
                    return self.colorize(str(result), color_name)
                try:
                    return self.colorize(str(result), color_name)
                except TypeError:
                    return result
            return wrapper
        return decorator

    def create_themed_decorator_factory(self, theme_name: str, theme_colors: Dict) -> Callable:
        """
        Creates a decorator factory for themed colorization.

        Args:
            theme_name (str): Name of the theme.
            theme_colors (Dict): Dictionary of colors for the theme.

        Returns:
            Callable: Themed decorator factory.
        """

        def themed_decorator_factory(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                return self.output_handler.format(result, theme_colors)
            return wrapper
        return themed_decorator_factory

    def theme_colorize(self, data: Any, theme_colors: Dict) -> str:
        """
        Colorizes data structures based on a theme.

        Args:
            data (Any): Data to colorize.
            theme_colors (Dict): Dictionary of colors for the theme.

        Returns:
            str: Colorized data as a string.
        """
        return self.output_handler.format(data, theme_colors)


class DataHandler(OutputHandler):
    """Handles output formatting and colorization for various data types (primarily JSON-like)."""

    colorizer: Optional[Colorizer]

    def __init__(self, colorizer: Optional[Colorizer] = None) -> None:
        """
        Initializes DataHandler with an optional Colorizer instance.

        Args:
            colorizer (Optional[Colorizer], optional): Colorizer instance to use. Defaults to _default_colorizer.
        """
        self.colorizer = colorizer or _default_colorizer

    def format(self, data: Any, theme_colors: Dict) -> str:
        """
        Formats and colorizes data based on its type, attempting to parse strings as JSON if possible.

        Args:
            data (Any): Data to format and colorize.
            theme_colors (Dict): Dictionary of theme colors.

        Returns:
            str: Formatted and colorized data as a string.
        """
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                pass  # If not valid JSON, treat it as a string
        return self._theme_colorize_data(data, theme_colors)

    def _theme_colorize_data(self, data: Any, theme_colors: Dict, indent_level: int = 0) -> str:
        """
        Recursively colorizes data structures (dict, list, primitives).

        Args:
            data (Any): Data to colorize.
            theme_colors (Dict): Dictionary of theme colors.
            indent_level (int, optional): Indentation level for nested structures. Defaults to 0.

        Returns:
            str: Colorized data segment as a string.
        """
        indent = "  " * indent_level
        colored_output = []

        if isinstance(data, dict):
            colored_output.append(self.colorizer.colorize("{", "grey"))
            for i, (key, value) in enumerate(data.items()):
                colored_output.append(f"\n{indent}  ")
                colored_output.append(
                    f'"{self.colorizer.colorize(str(key), theme_colors["key"])}": ')
                colored_output.append(self._theme_colorize_data(
                    value, theme_colors, indent_level + 1))
                if i < len(data) - 1:
                    colored_output.append(self.colorizer.colorize(",", "grey"))
            colored_output.append(
                f"\n{indent}{self.colorizer.colorize('}', 'grey')}")

        elif isinstance(data, list):
            colored_output.append(self.colorizer.colorize("[", "grey"))
            for i, item in enumerate(data):
                colored_output.append(f"\n{indent}  ")
                colored_output.append(self._theme_colorize_data(
                    item, theme_colors, indent_level + 1))
                if i < len(data) - 1:
                    colored_output.append(self.colorizer.colorize(",", "grey"))
            colored_output.append(
                f"\n{indent}{self.colorizer.colorize(']', 'grey')}")

        elif isinstance(data, str):
            colored_output.append(self.colorizer.colorize(
                f'"{data}"', theme_colors["string"]))
        elif isinstance(data, bool):
            colored_output.append(self.colorizer.colorize(
                str(data).lower(), theme_colors["bool"]))
        elif isinstance(data, (int, float)):
            colored_output.append(self.colorizer.colorize(
                str(data), theme_colors["number"]))
        elif data is None:
            colored_output.append(self.colorizer.colorize(
                "null", theme_colors["null"]))
        else:
            colored_output.append(self.colorizer.colorize(
                str(data), theme_colors["other"]))

        return "".join(colored_output)


_default_colorizer = Colorizer()


class YamlHandler(OutputHandler):
    """Handles output formatting as YAML with colorization."""

    def format(self, data: Any, theme_colors: Dict) -> str:
        """
        Formats data as colorized YAML.

        Args:
            data (Any): Data to format as YAML.
            theme_colors (Dict): Dictionary of theme colors.

        Returns:
            str: Colorized YAML string.
        """
        yaml_string: str = yaml.dump(
            data, indent=2, allow_unicode=True, default_flow_style=False)
        return self._colorize_yaml_string(yaml_string, theme_colors)

    def _colorize_yaml_string(self, yaml_string: str, theme_colors: Dict, colorizer: Optional[Colorizer] = None) -> str:
        """
        Colorizes a YAML string based on theme colors using regex.

        Args:
            yaml_string (str): YAML formatted string to colorize.
            theme_colors (Dict): Dictionary of theme colors.
            colorizer (Optional[Colorizer], optional): Colorizer instance. Defaults to _default_colorizer.

        Returns:
            str: Colorized YAML string.
        """
        if colorizer is None:
            colorizer = _default_colorizer
        color_map: Dict[str, str] = {
            r"^(\s*)([\w\._-]+):": theme_colors["key"],
            r"(?<=-|:)(['\" ])([^\n]+)(\1|$)(?!\:)": theme_colors["string"],
            r"\b-?\d+\.?\d*\b": theme_colors["number"],
            r"\b(true|false)\b": theme_colors["bool"],
            r"\bnull\b": theme_colors["null"],
            r"(\s*):": "grey",
            r"^\s*-\s": "grey",
            r"^---": "grey",
            r"#.*": "grey",
        }

        colored_yaml = yaml_string
        for pattern, color_name in color_map.items():
            color_code = colorizer.get_color_code(color_name)
            if color_code:
                def colorize_match(match: re.Match) -> str:
                    full_match = match.group(0)
                    if pattern == r"^(\s*)([\w\._-]+):":
                        leading_space = match.group(
                            1) if match.group(1) else ""
                        key = match.group(2)
                        return f"{leading_space}{colorizer.colorize(key, color_name)}:"
                    elif pattern == r"(['\"])(.*?)(['\"])(?!\:)":
                        quote_char = match.group(1)
                        string_content = match.group(2)
                        return f"{quote_char}{colorizer.colorize(string_content, color_name)}{quote_char}"
                    elif pattern == r"(\s*):":
                        leading_space = match.group(
                            1) if match.group(1) else ""
                        return f"{leading_space}{colorizer.colorize(':', color_name)}"
                    elif pattern == r"^\s*-\s":
                        return colorizer.colorize(full_match, color_name)
                    elif pattern == r"^---":
                        return colorizer.colorize(full_match, color_name)
                    elif pattern == r"#.*":
                        return colorizer.colorize(full_match, color_name)
                    else:
                        return colorizer.colorize(full_match, color_name)

                colored_yaml = re.sub(
                    pattern, colorize_match, colored_yaml, flags=re.MULTILINE)

        return colored_yaml


class ColorRemoverHandler(OutputHandler):
    """Handles removing ANSI color codes from formatted output."""

    def format(self, data: Any, theme_colors: Dict) -> str:
        """
        Removes color from the formatted output using DataHandler for initial formatting.

        Args:
            data (Any): Data to remove colors from.
            theme_colors (Dict): Theme colors (not used in this handler but kept for interface consistency).

        Returns:
            str: Text with ANSI color codes removed.
        """
        handler = DataHandler()
        formatted_text = handler.format(data, theme_colors)
        return self._remove_ansi_colors(formatted_text)

    def _remove_ansi_colors(self, text: str) -> str:
        """
        Removes ANSI color codes using regex.

        Args:
            text (str): Text containing ANSI color codes.

        Returns:
            str: Text with ANSI color codes removed.
        """
        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        return ansi_escape.sub("", text)


def create_single_wrap(color_name: str) -> Dict:
    """
    Creates a theme dictionary with a single foreground color for all elements.

    Args:
        color_name (str): Name of the color to use for the single-color theme.

    Returns:
        Dict: Theme dictionary with all elements set to the same color.
    """
    return {
        "key": color_name,
        "string": color_name,
        "number": color_name,
        "bool": color_name,
        "null": color_name,
        "other": color_name,
    }


def monotone_decorator_factory(colorizer: Colorizer) -> Dict[str, Callable]:
    """
    Creates single color decorators using the theme decorator factory.

    Args:
        colorizer (Colorizer): Colorizer instance to create decorators with.

    Returns:
        Dict[str, Callable]: Dictionary of decorator functions, keyed by color name + "_wrap".
    """
    color_names = ["black", "white", "red", "green", "yellow", "blue", "magenta", "cyan", "bright_black",
                   "bright_white", "bright_red", "bright_green", "bright_yellow", "bright_blue", "bright_magenta", "bright_cyan"]
    decorators: Dict[str, Callable] = {}
    for color_name in color_names:
        theme = create_single_wrap(color_name)
        decorators[color_name + "_wrap"] = colorizer.create_themed_decorator_factory(
            color_name, theme)
    return decorators


color_decorators: Dict[str, Callable] = monotone_decorator_factory(
    _default_colorizer)

black_wrap = color_decorators["black_wrap"]
white_wrap = color_decorators["white_wrap"]
red_wrap = color_decorators["red_wrap"]
green_wrap = color_decorators["green_wrap"]
yellow_wrap = color_decorators["yellow_wrap"]
blue_wrap = color_decorators["blue_wrap"]
magenta_wrap = color_decorators["magenta_wrap"]
cyan_wrap = color_decorators["cyan_wrap"]
bright_black_wrap = color_decorators["bright_black_wrap"]
bright_white_wrap = color_decorators["bright_white_wrap"]
bright_red_wrap = color_decorators["bright_red_wrap"]
bright_green_wrap = color_decorators["bright_green_wrap"]
bright_yellow_wrap = color_decorators["bright_yellow_wrap"]
bright_blue_wrap = color_decorators["bright_blue_wrap"]
bright_magenta_wrap = color_decorators["bright_magenta_wrap"]
bright_cyan_wrap = color_decorators["bright_cyan_wrap"]


def black(text: str) -> str:
    return _default_colorizer.colorize(text, "black")


def white(text: str) -> str:
    return _default_colorizer.colorize(text, "white")


def red(text: str) -> str:
    return _default_colorizer.colorize(text, "red")


def green(text: str) -> str:
    return _default_colorizer.colorize(text, "green")


def yellow(text: str) -> str:
    return _default_colorizer.colorize(text, "yellow")


def blue(text: str) -> str:
    return _default_colorizer.colorize(text, "blue")


def magenta(text: str) -> str:
    return _default_colorizer.colorize(text, "magenta")


def cyan(text: str) -> str:
    return _default_colorizer.colorize(text, "cyan")


def bright_black(text: str) -> str:
    return _default_colorizer.colorize(text, "bright_black")


def bright_white(text: str) -> str:
    return _default_colorizer.colorize(text, "bright_white")


def bright_red(text: str) -> str:
    return _default_colorizer.colorize(text, "bright_red")


def bright_green(text: str) -> str:
    return _default_colorizer.colorize(text, "bright_green")


def bright_yellow(text: str) -> str:
    return _default_colorizer.colorize(text, "bright_yellow")


def bright_blue(text: str) -> str:
    return _default_colorizer.colorize(text, "bright_blue")


def bright_magenta(text: str) -> str:
    return _default_colorizer.colorize(text, "bright_magenta")


def bright_cyan(text: str) -> str:
    return _default_colorizer.colorize(text, "bright_cyan")


black_deco = _default_colorizer.color_decorator("black")
white_deco = _default_colorizer.color_decorator("white")
red_deco = _default_colorizer.color_decorator("red")
green_deco = _default_colorizer.color_decorator("green")
yellow_deco = _default_colorizer.color_decorator("yellow")
blue_deco = _default_colorizer.color_decorator("blue")
magenta_deco = _default_colorizer.color_decorator("magenta")
cyan_deco = _default_colorizer.color_decorator("cyan")
bright_black_deco = _default_colorizer.color_decorator("bright_black")
bright_white_deco = _default_colorizer.color_decorator("bright_white")
bright_red_deco = _default_colorizer.color_decorator("bright_red")
bright_green_deco = _default_colorizer.color_decorator("bright_green")
bright_yellow_deco = _default_colorizer.color_decorator("bright_yellow")
bright_blue_deco = _default_colorizer.color_decorator("bright_blue")
bright_magenta_deco = _default_colorizer.color_decorator("bright_magenta")
bright_cyan_deco = _default_colorizer.color_decorator("bright_cyan")


dark_theme_colors: Dict[str, str] = {"key": "bright_cyan", "string": "yellow", "number": "bright_red",
                                     "bool": "magenta", "null": "bright_magenta", "other": "yellow"}

light_theme_colors: Dict[str, str] = {
    "key": "blue",
    "string": "bright_yellow",
    "number": "bright_cyan",
    "bool": "bright_magenta",
    "null": "bright_magenta",
    "other": "bright_green",
}

minimalist_theme_colors: Dict[str, str] = {
    "key": "bright_green",
    "string": "yellow",
    "number": "magenta",
    "bool": "bright_black",
    "null": "white",
    "other": "white",
}

vibrant_theme_colors: Dict[str, str] = {
    "key": "bright_yellow",
    "string": "bright_green",
    "number": "bright_magenta",
    "bool": "bright_cyan",
    "null": "yellow",
    "other": "bright_white",
}


darktheme = _default_colorizer.create_themed_decorator_factory(
    "dark", dark_theme_colors)
lighttheme = _default_colorizer.create_themed_decorator_factory(
    "light", light_theme_colors)
minimalisttheme = _default_colorizer.create_themed_decorator_factory(
    "minimalist", minimalist_theme_colors)
vibranttheme = _default_colorizer.create_themed_decorator_factory(
    "vibrant", vibrant_theme_colors)

if __name__ == "__main__":
    print("Welcome to the artistic colordoll demo!\n")

    colorizer = _default_colorizer

    print(colorizer.colorize("-" * 40, "cyan"))
    print(colorizer.colorize("  Demonstrating Basic Colored Lines", "bright_white"))
    print(colorizer.colorize("-" * 40, "cyan"))

    print(colorizer.colorize("Red", "red") +
          colorizer.colorize(" Line: ") + colorizer.colorize("---", "red"))
    print(colorizer.colorize("Green", "green") +
          colorizer.colorize(" Line: ") + colorizer.colorize("---", "green"))
    print(colorizer.colorize("Blue", "blue") +
          colorizer.colorize(" Line: ") + colorizer.colorize("---", "blue"))
    print()

    print(colorizer.colorize("-" * 40, "cyan"))
    print(colorizer.colorize("  Creating a Simple Colored Square", "bright_white"))
    print(colorizer.colorize("-" * 40, "cyan"))

    square_color = "bright_green"
    square_side = 20
    for i in range(square_side):
        if i in [0, square_side - 1]:
            line = colorizer.colorize("██" * square_side, square_color)
        else:
            insides = random.randint(
                1, (3 + (square_side % random.randint(2, square_side // 4)))
            )
            middle_section = "██" * insides
            spaces = " " * (square_side - 2 - insides)
            line_content = f" █{spaces}{magenta(middle_section)}{spaces}█ "
            line = colorizer.colorize(
                text=line_content, color="red", background_color="grey")
        print(line)

    print()

    print(colorizer.colorize("-" * 40, "red", "black"))
    print(colorizer.colorize(
        "  Creating a Colored Heart Text Art    ", "black", "magenta"))
    print(colorizer.colorize("-" * 40, "red", "black"))

    heart_art = """

     ███   ███
    █████ █████
   █████████████
  ███████████████
 ██████""" + (
        red('1') +
        green(' 2 ') +
        blue('3')
    ) + """██████
 █████████████████
  ███████████████
   █████████████
    ███████████
     █████████
      ███████
       █████
        ███
         █

    """

    heart_lines = heart_art.split("\n")
    heart_colors = ["bright_red", "red", "magenta", "bright_magenta"]

    for i, line in enumerate(heart_lines):
        colored_line = ""
        color_index = i % len(heart_colors)
        line_color = heart_colors[color_index]
        colored_line = colorizer.colorize(line, line_color)
        print(colored_line)
    print()

    print(colorizer.colorize("-" * 40, "black", "bright_green"))
    print(colorizer.colorize("  Themed Heart Art (Minimalist)      ", "bright_white"))
    print(colorizer.colorize("-" * 40, "black", "bright_green"))

    @minimalisttheme
    def get_minimalist_heart() -> str:
        return heart_art

    print(get_minimalist_heart())
    print()

    print(colorizer.colorize("-" * 40, "green"))
    print(colorizer.colorize(
        "  Themed Heart Art (Vibrant with Background)", color="bright_white"))
    print(colorizer.colorize("-" * 40, "green"))

    @vibranttheme
    def get_vibrant_heart() -> str:
        return heart_art

    print(get_vibrant_heart())
    print()

    print(colorizer.colorize("-" * 40, "cyan"))
    print(colorizer.colorize(
        "  Themed JSON Data Display (Dark Theme)", "bright_white"))
    print(colorizer.colorize("-" * 40, "cyan"))

    sample_json_data = {"name": "Artistic Demo", "type": "Text Art", "colors_used": [
        "red", "green", "blue", "yellow"], "is_artistic": True, "value": 123}

    @darktheme
    def get_themed_json_data() -> Dict:
        return sample_json_data

    print(get_themed_json_data())
    print()

    print(colorizer.colorize("-" * 40, "cyan"))
    print(colorizer.colorize(
        "  Direct Color Functions Example (Corrected)", "bright_white"))
    print(colorizer.colorize("-" * 40, "cyan"))
    print()

    print(bright_cyan("This message is in bright cyan."))
    print(bright_yellow("And this one is in bright yellow."))
    print()

    print(colorizer.colorize("-" * 40, "cyan"))
    print(colorizer.colorize("  End of colordoll Artistic Demo", "bright_white"))
    print(colorizer.colorize("-" * 40, "cyan"))
    print()
    print()
    print()

    sample_data = {"name": "Handler Demo", "formats": ["JSON", "Dict/List", "YAML", "HTML", "Color Removed"],
                   "value": 123, "is_demo": True, "nested": {"item": "nested_value", "list": [1, 2, "three"]}}

    print(" * " * 20)
    print(_default_colorizer.colorize(
        "Demonstrating Output Handlers", "bright_white"))
    print(" * " * 20)
    print()

    print(_default_colorizer.colorize("-" * 40, "green"))
    print(_default_colorizer.colorize("  JSON Handler Output", "bright_white"))
    print(_default_colorizer.colorize("-" * 40, "green"))
    print(_default_colorizer.theme_colorize(sample_data, dark_theme_colors))
    print()

    print(_default_colorizer.colorize("-" * 40, "cyan"))
    print(_default_colorizer.colorize(
        "  Dict/List Handler Output", "bright_white"))
    print(colorizer.colorize("-" * 40, "cyan"))
    _default_colorizer.set_output_handler(DataHandler())
    print(_default_colorizer.theme_colorize(sample_data, dark_theme_colors))

    if yaml is not None:
        print(_default_colorizer.colorize("-" * 40, "cyan"))
        print(_default_colorizer.colorize(
            "  YAML Handler Output", "bright_white"))
        print(_default_colorizer.colorize("-" * 40, "cyan"))
        _default_colorizer.set_output_handler(YamlHandler())

        def getyaml() -> str:
            return _default_colorizer.theme_colorize(sample_data, dark_theme_colors)

        print(getyaml())
    else:
        print(_default_colorizer.colorize(
            "YAML Handler skipped due to PyYAML installation issue.", "yellow"))
        print()

    print(_default_colorizer.colorize("-" * 40, "cyan"))
    print(_default_colorizer.colorize(
        "  Color Remover Handler Output", "bright_white"))
    print(_default_colorizer.colorize("-" * 40, "cyan"))
    _default_colorizer.set_output_handler(ColorRemoverHandler())
    removed_color_output = _default_colorizer.theme_colorize(
        sample_data, dark_theme_colors)
    print(f"{removed_color_output}")

    _default_colorizer.set_output_handler(DataHandler())
    print(_default_colorizer.theme_colorize(
        removed_color_output, vibrant_theme_colors))

    print(" * " * 20)
    print(_default_colorizer.colorize(
        "End of Output Handler Demo", "bright_white"))
    print(" * " * 20)
