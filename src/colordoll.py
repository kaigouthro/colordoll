
import contextlib
import json
from functools import wraps


class AnsiColor:
    """
    Represents an ANSI escape code for text coloration.
    """

    def __init__(self, code: int, name: str = ""):
        """
        Initializes an AnsiColor object.

        :param code: The ANSI escape code.
        :param name: The name of the color.
        """
        assert isinstance(code, int), "ANSI code must be an integer"
        self.code: int = code
        self.name: str = name

    def __str__(self) -> str:
        """
        Returns the ANSI escape code sequence as a string.
        """
        return f"\033[{self.code}m"

    def __repr__(self) -> str:
        """
        Returns a string representation of the AnsiColor object.
        """
        return f"AnsiColor(code={self.code}, name='{self.name}')"


class ColorConfig:
    """
    Manages color configurations, including loading from a file or a dictionary.
    """

    def __init__(self, config_source: str | dict = None):
        """
        Initializes a ColorConfig object.

        :param config_source: A file path or a dictionary containing color configurations.
        """
        self.config: dict = self.load_config(
            config_source) if config_source else {}

    def load_config(self, config_source: str | dict) -> dict:
        """
        Loads color configurations from a file or a dictionary.

        :param config_source: A file path or a dictionary containing color configurations.
        :return: A dictionary containing the loaded color configurations.
        """
        assert isinstance(
            config_source, (str, dict)
        ), "Config source must be a file path or a dictionary"

        if isinstance(config_source, str):
            with open(config_source, "r") as f:
                return json.load(f)
        return config_source

    def get_color_code(self, color_name: str) -> str:
        """
        Retrieves the ANSI escape code based on the given color name.

        :param color_name: The name of the color to retrieve.
        :return: The ANSI escape code string for the requested color, or an empty string if not found.
        """
        color = self.get_color_obj(color_name)
        return str(color) if color else ""

    def get_bg_color_code(self, color_name: str) -> str:
        """
        Retrieves the ANSI escape code for background colors based on the given color name.

        :param color_name: The name of the background color to retrieve.
        :return: The ANSI escape code string for the requested background color, or an empty string if not found.
        """
        color = self.get_bg_color_obj(color_name)
        return str(color) if color else ""

    def get_color_obj(self, color_name: str) -> AnsiColor | None:
        """
        Retrieves an AnsiColor object based on the given color name.

        :param color_name: The name of the color to retrieve.
        :return: An AnsiColor object representing the requested color, or None if not found.
        """
        return self._get_color_object(color_name)

    def get_bg_color_obj(self, color_name: str) -> AnsiColor | None:
        """
        Retrieves an AnsiColor object for background colors based on the given color name.

        :param color_name: The name of the background color to retrieve.
        :return: An AnsiColor object representing the requested background color, or None if not found.
        """
        bg_color_name = f"bg_{color_name}"
        return self._get_color_object(bg_color_name)

    def _get_color_object(self, arg0):
        if arg0 not in self.config:
            return None
        color_data: dict = self.config[arg0]
        assert (
            "code" in color_data
        ), f"Invalid color configuration for '{arg0}': missing 'code' field"
        return AnsiColor(code=color_data["code"], name=arg0)


class Colorizer:
    """
    Provides methods for colorizing text using ANSI escape codes.
    """
    RESET: AnsiColor = AnsiColor(0, "reset")

    def __init__(self, config: ColorConfig = None):
        """
        Initializes a Colorizer object.

        :param config: A ColorConfig object containing color configurations.
        """
        self.config: ColorConfig = config or ColorConfig()
        self.colors: dict[str, AnsiColor] = {}
        self.bg_colors: dict[str, AnsiColor] = {}
        self._load_ansi_colors()

    def _load_ansi_colors(self):
        """
        Loads ANSI color codes into the Colorizer object.
        """
        ansi_colors = {
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
        }
        ansi_bg_colors = {
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
            # corrected: use bg_name as key, but store full name in AnsiColor for reference.
            self.bg_colors[bg_name] = AnsiColor(code, name)

    def get_color_code(self, color_name: str) -> str:
        """
        Retrieves the ANSI escape code for a given color name.

        :param color_name: The name of the color.
        :return: The ANSI escape code string, or an empty string if the color is not defined.
        """
        color_obj = self.colors.get(color_name.lower())
        return str(color_obj) if color_obj else ""

    def get_bg_color_code(self, color_name: str) -> str:
        """
        Retrieves the ANSI escape code for a given background color name.

        :param color_name: The name of the background color.
        :return: The ANSI escape code string, or an empty string if the color is not defined.
        """
        color_obj = self.bg_colors.get(color_name.lower())
        return str(color_obj) if color_obj else ""

    def colorize(self, text: str, color: str = None, background_color: str = None) -> str:
        """
        Colorizes a string with foreground and/or background colors, handling nested colors.

        :param text: The text to colorize.
        :param color: The foreground color name.
        :param background_color: The background color name.
        :return: The colorized text string.
        """
        reset_code = str(Colorizer.RESET)
        color_code = self.get_color_code(color) if color else ""
        bg_color_code = self.get_bg_color_code(
            background_color) if background_color else ""

        if not color_code and not bg_color_code:
            return text

        start_tag = ""
        if color_code and bg_color_code:
            start_tag = f"\033[{color_code.split('[')[1].split('m')[0]};{bg_color_code.split('[')[1].split('m')[0]}m"
        elif color_code:
            start_tag = color_code
        elif bg_color_code:
            start_tag = bg_color_code

        end_tag = reset_code

        def _process_text(text_segment):
            """Applies color codes to a text segment, handling resets."""
            processed_segments = []
            i = 0
            while i < len(text_segment):
                if text_segment.startswith(reset_code, i):
                    processed_segments.append(reset_code)
                    i += len(reset_code)
                    # Re-apply style after reset
                    processed_segments.append(start_tag)
                else:
                    processed_segments.append(text_segment[i])
                    i += 1
            return "".join(processed_segments)

        processed_text = _process_text(text)
        return start_tag + processed_text + end_tag

    def color_decorator(self, color_name):
        """
        Creates a decorator that colorizes the output of a function with a specified color.

        :param color_name: The name of the color to use for decoration.
        :return: A decorator function.
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                if isinstance(result, (str, bool, float, int, dict, list)):
                    return self.colorize(str(result), color_name)
                try:
                    return self.colorize(str(result), color_name)
                except TypeError:
                    return result

            return wrapper

        return decorator

    def create_themed_decorator_factory(self, theme_name, theme_colors):
        """
        Creates a decorator factory for themed colorization.

        :param theme_name: The name of the theme.
        :param theme_colors: A dictionary of theme colors.
        :return: A theme decorator factory function.
        """
        def themed_decorator_factory(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                return self.theme_colorize(result, theme_colors)
            return wrapper
        return themed_decorator_factory

    def theme_colorize(self, data, theme_colors, indent_level=0):
        """
        Recursively colorizes data structures (dicts, lists, JSON strings) based on a theme.

        :param data: The data to colorize. Can be a dict, list, or JSON string.
        :param theme_colors: A dictionary defining colors for different data types (key, string, number, etc.).
        :param indent_level: The current indentation level for pretty printing.
        :return: The colorized string representation of the data.
        """
        indent = "  " * indent_level
        colored_output = []

        if isinstance(data, (dict, list)):
            with contextlib.suppress(TypeError, OverflowError):
                data = json.loads(json.dumps(data))
        if isinstance(data, dict):
            colored_output.append(self.colorize("{", "grey"))
            for key, value in data.items():
                colored_output.extend(
                    (
                        f"""\n{indent}  \"{self.colorize(key, theme_colors['key'])}\" : """,
                        self.theme_colorize(
                            value, theme_colors, indent_level + 1),
                        self.colorize(",", "grey"),
                    )
                )
            colored_output.append(f"\n{indent}{self.colorize('}', 'grey')}")
        elif isinstance(data, list):
            colored_output.append(self.colorize("[", "grey"))
            for item in data:
                colored_output.extend(
                    (
                        f"\n{indent}  ",
                        self.theme_colorize(
                            item, theme_colors, indent_level + 1),
                        self.colorize(",", "grey"),
                    )
                )
            colored_output.append(f"\n{indent}{self.colorize(']', 'grey')}")
        elif isinstance(data, str):
            try:
                data = json.loads(data)
                colored_output.append(self.theme_colorize(
                    data, theme_colors, indent_level + 1))
            except json.JSONDecodeError:
                if data.isnumeric():
                    data = float(data)
                    colored_output.append(self.theme_colorize(
                        data, theme_colors, indent_level))
                elif data.lower() in ["true", "false"]:
                    data = data.lower() == "true"
                    colored_output.append(self.theme_colorize(
                        data, theme_colors, indent_level))
                else:
                    colored_output.append(
                        self.colorize(f'"{data}"', theme_colors["string"]))
        elif isinstance(data, bool):
            colored_output.append(self.colorize(
                str(data), theme_colors["bool"]))
        elif isinstance(data, (int, float)):
            colored_output.append(self.colorize(
                str(data), theme_colors["number"]))
        elif data is None:
            colored_output.append(self.colorize("null", theme_colors["null"]))
        else:
            colored_output.append(
                self.colorize(str(data), theme_colors["other"]))

        return "".join(colored_output)


# Initialize Colorizer
default_colorizer = Colorizer()

# Generate color decorators using the default Colorizer instance
blackcolor = default_colorizer.color_decorator("black")
whitecolor = default_colorizer.color_decorator("white")
redcolor = default_colorizer.color_decorator("red")
greencolor = default_colorizer.color_decorator("green")
yellowcolor = default_colorizer.color_decorator("yellow")
bluecolor = default_colorizer.color_decorator("blue")
magentacolor = default_colorizer.color_decorator("magenta")
cyancolor = default_colorizer.color_decorator("cyan")
bright_blackcolor = default_colorizer.color_decorator("bright_black")
bright_whitecolor = default_colorizer.color_decorator("bright_white")
bright_redcolor = default_colorizer.color_decorator("bright_red")
bright_greencolor = default_colorizer.color_decorator("bright_green")
bright_yellowcolor = default_colorizer.color_decorator("bright_yellow")
bright_bluecolor = default_colorizer.color_decorator("bright_blue")
bright_magentacolor = default_colorizer.color_decorator("bright_magenta")
bright_cyancolor = default_colorizer.color_decorator("bright_cyan")


black = blackcolor(lambda text="": text)
white = whitecolor(lambda text="": text)
red = redcolor(lambda text="": text)
green = greencolor(lambda text="": text)
yellow = yellowcolor(lambda text="": text)
blue = bluecolor(lambda text="": text)
magenta = magentacolor(lambda text="": text)
cyan = cyancolor(lambda text="": text)
bright_black = bright_blackcolor(lambda text="": text)
bright_white = bright_whitecolor(lambda text="": text)
bright_red = bright_redcolor(lambda text="": text)
bright_green = bright_greencolor(lambda text="": text)
bright_yellow = bright_yellowcolor(lambda text="": text)
bright_blue = bright_bluecolor(lambda text="": text)
bright_magenta = bright_magentacolor(lambda text="": text)
bright_cyan = bright_cyancolor(lambda text="": text)


# Define Themes
dark_theme_colors = {"key": "bright_cyan", "string": "yellow", "number": "bright_red",
                     "bool": "magenta", "null": "bright_magenta", "other": "yellow"}

light_theme_colors = {
    "key": "blue",
    "string": "bright_yellow",
    "number": "bright_cyan",
    "bool": "bright_magenta",
    "null": "bright_magenta",
    "other": "yellow",
}

minimalist_theme_colors = {
    "key": "bright_black",
    "string": "yellow",
    "number": "magenta",
    "bool": "bright_black",
    "null": "white",
    "other": "white",
}

vibrant_theme_colors = {
    "key": "bright_yellow",
    "string": "bright_green",
    "number": "bright_magenta",
    "bool": "bright_cyan",
    "null": "yellow",
    "other": "bright_white",
}


# Create theme decorators using the default Colorizer instance
darktheme = default_colorizer.create_themed_decorator_factory(
    "dark", dark_theme_colors)
lighttheme = default_colorizer.create_themed_decorator_factory(
    "light", light_theme_colors)
minimalisttheme = default_colorizer.create_themed_decorator_factory(
    "minimalist", minimalist_theme_colors)
vibranttheme = default_colorizer.create_themed_decorator_factory(
    "vibrant", vibrant_theme_colors)


# --- Example Usage ---
if __name__ == "__main__":

    def get_status():
        return "ERROR"

    def get_success_message():
        return "Success!"

    @darktheme
    def get_json_data():
        return """
        {
            "name": "Example",
            "version": 1.0,
            "debug_mode": true,
            "values": [1, 2.5, null, "hello"],
            "config": {
                "host": "localhost",
                "port": 8080,
                "nested_config": {
                    "inner_key": "inner_value",
                    "inner_list": [true, false, null, 100]
                }
            },
            "status": "ok"
        }
        """

    @darktheme
    def get_list_data():
        return ["item1", {"key": "value", "nested_list": [True, False, "nested_string", 5]}, 123, None, True]

    @vibranttheme
    def some_calculation():
        return 42

    print(" * " * 20)
    # Test case: foreground and background color together
    print(default_colorizer.colorize(blue("This is " + default_colorizer.colorize(get_status(), "red") +
          " and " + default_colorizer.colorize(get_success_message(), "green") + " text."), background_color="bg_red"))

    # Test case: nested colorization with background - fixed version should handle this correctly
    nested_colored_text = default_colorizer.colorize(
        f"This is {default_colorizer.colorize('red text with bright black', 'red', "bright_black")} on yellow with bright_blue background",
        "yellow",
        "bright_blue")

    print(nested_colored_text)

    print(get_json_data())
    print(get_list_data())
    print(default_colorizer.colorize(some_calculation(), "yellow"))

    @minimalisttheme
    def get_minimalist_json():
        return """
        {
            "app": "Minimalist Settings",
            "features": ["clean", "simple", "fast"],
            "config": {
                "theme": "minimalist",
                "verbose_output": false
            },
            "numeric" : 100
        }
        """

    @vibranttheme
    def get_vibrant_json():
        return """
        {
            "module": "Data Visualization",
            "charts": ["bar", "pie", "line"],
            "options": {
                "color_palette": "vibrant",
                "data_points": 150
            }
        }
        """

    print("\n--- Minimalist Theme ---")
    print(get_minimalist_json())

    print("\n--- Vibrant Theme ---")
    print(default_colorizer.colorize(
        get_vibrant_json(), background_color="bright_white"))
