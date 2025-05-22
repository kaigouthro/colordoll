import contextlib
import json
import re
from functools import wraps
from typing import Dict, Union, Optional, Any, Callable, TypeVar
import yaml


# Type variable for the return type of the original function being decorated
_R = TypeVar("_R")

# Type variable for the function type being decorated
_F = TypeVar("_F", bound=Callable[..., _R])

# Type for the final wrapper that executes the decorated function
# It can return the original result type _R or a string (themed result)
FinalWrapperType = Callable[..., Union[_R, str]]

# Type for the factory that is returned when the configurable decorator is called with a config
# This factory takes a function _F and returns the FinalWrapperType
ConfigurableDecoratorFactoryInnerType = Callable[[_F], FinalWrapperType]

# Type for the callable object returned by create_themed_decorator_factory
# This object itself can be:
# 1. Called with a function to decorate directly (returns FinalWrapperType)
# 2. Called with a config (bool/None), returning a factory (ConfigurableDecoratorFactoryInnerType)
TopLevelConfigurableDecoratorType = Callable[
    [Optional[Union[bool, _F]]],  # Argument can be a function, a boolean, or None
    Union[ConfigurableDecoratorFactoryInnerType, FinalWrapperType],  # Return type depends on input
]

dark_theme_colors: Dict[str, str] = {"key": "bright_cyan", "string": "yellow", "number": "bright_red", "bool": "magenta", "null": "bright_magenta", "other": "yellow"}

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
            raise ValueError(f"Invalid color configuration for '{color_name}': missing 'code' field")
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
        raise NotImplementedError("Subclasses must implement the format method.")


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
        self.theme = dark_theme_colors
        self.output_handler = output_handler or OutputHandler()

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
            "black": 30,
            "red": 31,
            "green": 32,
            "yellow": 33,
            "blue": 34,
            "magenta": 35,
            "cyan": 36,
            "white": 37,
            "bright_black": 90,
            "bright_red": 91,
            "bright_green": 92,
            "bright_yellow": 93,
            "bright_blue": 94,
            "bright_magenta": 95,
            "bright_cyan": 96,
            "bright_white": 97,
            "grey": 90,
        }
        ansi_bg_colors: Dict[str, int] = {
            "bg_black": 40,
            "bg_red": 41,
            "bg_green": 42,
            "bg_yellow": 43,
            "bg_blue": 44,
            "bg_magenta": 45,
            "bg_cyan": 46,
            "bg_white": 47,
            "bg_bright_black": 100,
            "bg_bright_red": 101,
            "bg_bright_green": 102,
            "bg_bright_yellow": 103,
            "bg_bright_blue": 104,
            "bg_bright_magenta": 105,
            "bg_bright_cyan": 106,
            "bg_bright_white": 107,
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
        bg_color_code = self.get_bg_color_code(background_color) if background_color else ""

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

    def create_themed_decorator_factory(
        self,
        theme_name: str,  # theme_name captured for potential use, not active in this example
        theme_colors: Dict[str, str],
    ) -> TopLevelConfigurableDecoratorType:
        """
        Creates a configurable themed decorator factory.

        The returned callable can be used as a decorator directly (applies theme,
        returns themed string) or called with a boolean argument to control
        print behavior (True: prints themed, returns original; False: returns themed string).

        Args:
            theme_name (str): Name of the theme.
            theme_colors (Dict[str, str]): Dictionary of colors for the theme.

        Returns:
            TopLevelConfigurableDecoratorType: A callable that acts as the
                                               configurable themed decorator.
        """

        # This is the callable object that create_themed_decorator_factory will return.
        # It needs to determine if it's being called with a function to decorate directly,
        # or with a configuration argument (the do_print flag).
        def configurable_themed_decorator(arg_or_func: Optional[Union[bool, _F]] = None) -> Union[ConfigurableDecoratorFactoryInnerType, FinalWrapperType]:
            # This is the core logic that performs the actual wrapping of the function.
            # It's parameterized by the function to decorate and the do_print setting.
            def actual_decorator_logic(func_to_decorate: _F, do_print_setting: bool) -> FinalWrapperType:
                @wraps(func_to_decorate)
                def wrapper(*args: Any, **kwargs: Any) -> Union[_R, str]:
                    original_result: _R = func_to_decorate(*args, **kwargs)

                    # 'self' (for self.output_handler) and 'theme_colors'
                    # are captured from the enclosing scopes.
                    themed_result: str = self.output_handler.format(original_result, theme_colors)

                    if do_print_setting:
                        print(themed_result)
                        return original_result  # Return the original, non-themed result
                    else:
                        return themed_result  # Return the themed string result

                return wrapper

            if callable(arg_or_func):
                # Default 'do_print_setting' for direct decoration is False (return themed string).
                return actual_decorator_logic(arg_or_func, do_print_setting=False)

            # Convert the argument to a boolean for the do_print_setting.
            # bool(None) is False, so @my_theme_decorator() behaves like @my_theme_decorator(False).
            current_do_print_setting = bool(arg_or_func)

            # Return a factory that, when called with a function, applies the actual_decorator_logic.
            def decorator_factory_for_config(func_to_decorate_inner: _F) -> FinalWrapperType:
                return actual_decorator_logic(func_to_decorate_inner, current_do_print_setting)

            return decorator_factory_for_config

        return configurable_themed_decorator

    def theme_colorize(self, data: Any, theme_colors: Dict | None = None) -> str:
        """
        Colorizes data structures based on a theme.

        Args:
            data (Any): Data to colorize.
            theme_colors (Dict): Dictionary of colors for the theme.

        Returns:
            str: Colorized data as a string.
        """
        return self.output_handler.format(data, theme_colors or self.theme)

    def set_theme(self, theme_dict: Dict) -> None:
        """
        Sets the current theme.

        Args:
            theme_dict (Dict): Dictionary of colors for the theme.
        """
        self.theme = theme_dict


class DataHandler(OutputHandler):
    """Handles output formatting and colorization for various data types (primarily JSON-like)."""

    colorizer: Optional[Colorizer]

    def __init__(self, colorizer: Optional[Colorizer] = None) -> None:
        """
        Initializes DataHandler with an optional Colorizer instance.

        Args:
            colorizer (Optional[Colorizer], optional): Colorizer instance to use.
            Defaults to a new Colorizer
        """
        self.colorizer: Colorizer = colorizer or Colorizer()

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
            with contextlib.suppress(json.JSONDecodeError):
                data = json.loads(data)

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
        if self.colorizer is None:
            self.colorizer = Colorizer()
        indent = "  " * indent_level
        colored_output = []

        if isinstance(data, str) and indent == 0:
            try:
                # with contextlib.suppress(json.JSONDecodeError):
                data = json.loads(data)
            except ValueError:
                print("Json loads attempted and failed")
                print(f"   {data}  ")
                colored_output.append(self.colorizer.colorize(f'"{data}"', theme_colors["string"]))

        if isinstance(data, dict):
            colored_output.append(self.colorizer.colorize("{", "grey"))
            for i, (key, value) in enumerate(data.items()):
                colored_output.extend(
                    (
                        f"\n{indent}  ",
                        f'"{self.colorizer.colorize(str(key), theme_colors["key"])}": ',
                        self._theme_colorize_data(value, theme_colors, indent_level + 1),
                    )
                )
                if i < len(data) - 1:
                    colored_output.append(self.colorizer.colorize(",", "grey"))
            colored_output.append(f"\n{indent}{self.colorizer.colorize('}', 'grey')}")

        elif isinstance(data, list):
            colored_output.append(self.colorizer.colorize("[", "grey"))
            for i, item in enumerate(data):
                colored_output.extend(
                    (
                        f"\n{indent}  ",
                        self._theme_colorize_data(item, theme_colors, indent_level + 1),
                    )
                )
                if i < len(data) - 1:
                    colored_output.append(self.colorizer.colorize(",", "grey"))
            colored_output.append(f"\n{indent}{self.colorizer.colorize(']', 'grey')}")

        elif isinstance(data, str):
            colored_output.append(self.colorizer.colorize(f'"{data}"', theme_colors["string"]))
        elif isinstance(data, bool):
            colored_output.append(self.colorizer.colorize(str(data).lower(), theme_colors["bool"]))
        elif isinstance(data, (int, float)):
            colored_output.append(self.colorizer.colorize(str(data), theme_colors["number"]))
        elif data is None:
            colored_output.append(self.colorizer.colorize("null", theme_colors["null"]))
        else:
            colored_output.append(self.colorizer.colorize(str(data), theme_colors["other"]))

        return "".join(colored_output)


default_colorizer = Colorizer(output_handler=DataHandler())


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
        yaml_string: str = yaml.dump(data, indent=2, allow_unicode=True, default_flow_style=False)
        return self._colorize_yaml_string(yaml_string, theme_colors)

    def _colorize_yaml_string(self, yaml_string: str, theme_colors: Dict, colorizer: Optional[Colorizer] = None) -> str:
        """
        Colorizes a YAML string based on theme colors using regex.

        Args:
            yaml_string (str): YAML formatted string to colorize.
            theme_colors (Dict): Dictionary of theme colors.
            colorizer (Optional[Colorizer], optional): Colorizer instance. Defaults to default_colorizer.

        Returns:
            str: Colorized YAML string.
        """
        if colorizer is None:
            colorizer = default_colorizer
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
                    full_match = match[0]
                    if pattern == r"^(\s*)([\w\._-]+):":
                        leading_space = match[1] or ""
                        key = match[2]
                        return f"{leading_space}{colorizer.colorize(key, color_name)}:"
                    elif pattern == r"(['\"])(.*?)(['\"])(?!\:)":
                        quote_char = match[1]
                        string_content = match[2]
                        return f"{quote_char}{colorizer.colorize(string_content, color_name)}{quote_char}"
                    elif pattern == r"(\s*):":
                        leading_space = match[1] or ""
                        return f"{leading_space}{colorizer.colorize(':', color_name)}"
                    elif pattern == r"^\s*-\s":
                        return colorizer.colorize(full_match, color_name)
                    elif pattern == r"^---":
                        return colorizer.colorize(full_match, color_name)
                    elif pattern == r"#.*":
                        return colorizer.colorize(full_match, color_name)
                    else:
                        return colorizer.colorize(full_match, color_name)

                colored_yaml = re.sub(pattern, colorize_match, colored_yaml, flags=re.MULTILINE)

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
    color_names = ["black", "white", "red", "green", "yellow", "blue", "magenta", "cyan", "bright_black", "bright_white", "bright_red", "bright_green", "bright_yellow", "bright_blue", "bright_magenta", "bright_cyan"]
    decorators: Dict[str, Callable] = {}
    for color_name in color_names:
        theme = create_single_wrap(color_name)
        decorators[f"{color_name}"] = colorizer.create_themed_decorator_factory(color_name, theme)
    return decorators


def wrapmono(color: str = "white") -> Callable:
    return default_colorizer.create_themed_decorator_factory(color, create_single_wrap(color))


def black(text: str) -> str:
    return default_colorizer.colorize(text, "black")


def white(text: str) -> str:
    return default_colorizer.colorize(text, "white")


def red(text: str) -> str:
    return default_colorizer.colorize(text, "red")


def green(text: str) -> str:
    return default_colorizer.colorize(text, "green")


def yellow(text: str) -> str:
    return default_colorizer.colorize(text, "yellow")


def blue(text: str) -> str:
    return default_colorizer.colorize(text, "blue")


def magenta(text: str) -> str:
    return default_colorizer.colorize(text, "magenta")


def cyan(text: str) -> str:
    return default_colorizer.colorize(text, "cyan")


def bright_black(text: str) -> str:
    return default_colorizer.colorize(text, "bright_black")


def bright_white(text: str) -> str:
    return default_colorizer.colorize(text, "bright_white")


def bright_red(text: str) -> str:
    return default_colorizer.colorize(text, "bright_red")


def bright_green(text: str) -> str:
    return default_colorizer.colorize(text, "bright_green")


def bright_yellow(text: str) -> str:
    return default_colorizer.colorize(text, "bright_yellow")


def bright_blue(text: str) -> str:
    return default_colorizer.colorize(text, "bright_blue")


def bright_magenta(text: str) -> str:
    return default_colorizer.colorize(text, "bright_magenta")


def bright_cyan(text: str) -> str:
    return default_colorizer.colorize(text, "bright_cyan")


def bg_black(text: str) -> str:
    return default_colorizer.colorize(text, background_color="black")


def bg_white(text: str) -> str:
    return default_colorizer.colorize(text, background_color="white")


def bg_red(text: str) -> str:
    return default_colorizer.colorize(text, background_color="red")


def bg_green(text: str) -> str:
    return default_colorizer.colorize(text, background_color="green")


def bg_yellow(text: str) -> str:
    return default_colorizer.colorize(text, background_color="yellow")


def bg_blue(text: str) -> str:
    return default_colorizer.colorize(text, background_color="blue")


def bg_magenta(text: str) -> str:
    return default_colorizer.colorize(text, background_color="magenta")


def bg_cyan(text: str) -> str:
    return default_colorizer.colorize(text, background_color="cyan")


def bg_brblack(text: str) -> str:
    return default_colorizer.colorize(text, background_color="bright_black")


def bg_brwhite(text: str) -> str:
    return default_colorizer.colorize(text, background_color="bright_white")


def bg_brred(text: str) -> str:
    return default_colorizer.colorize(text, background_color="bright_red")


def bg_brgreen(text: str) -> str:
    return default_colorizer.colorize(text, background_color="bright_green")


def bg_bryellow(text: str) -> str:
    return default_colorizer.colorize(text, background_color="bright_yellow")


def bg_brblue(text: str) -> str:
    return default_colorizer.colorize(text, background_color="bright_blue")


def bg_brmagenta(text: str) -> str:
    return default_colorizer.colorize(text, background_color="bright_magenta")


def bg_brcyan(text: str) -> str:
    return default_colorizer.colorize(text, background_color="bright_cyan")


darktheme = default_colorizer.create_themed_decorator_factory("dark", dark_theme_colors)
lighttheme = default_colorizer.create_themed_decorator_factory("light", light_theme_colors)
minimalisttheme = default_colorizer.create_themed_decorator_factory("minimalist", minimalist_theme_colors)
vibranttheme = default_colorizer.create_themed_decorator_factory("vibrant", vibrant_theme_colors)

