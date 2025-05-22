
# ColorDoll: Nested ANSI Colorization for Python

[![PyPI version](https://badge.fury.io/py/colordoll.svg)](https://badge.fury.io/py/colordoll)

ColorDoll is a Python library that provides flexible and powerful ANSI colorization, including nested colorization and theming for complex data structures like dictionaries, lists, JSON, and YAML strings.

And, it's fairly Quick.

## 🚀 Performance Benchmarks ⏱️
`(amd 3800, 3200mhz ram, single XPG-8200 nvme, win11) - v0.1.7`

| Function             | Runs      | Min Time (sec) | Max Time (sec) | Avg Time (sec) | As milliseconds | Runs / second  |
|----------------------|-----------|----------------|----------------|----------------|-----------------|----------------|
| `colorize`           | 10,000    | 0.000006       | 0.000006       | 0.000006       |       0.006     | ~166000        |
| `theme_colorize`     | 10,000    | 0.000046       | 0.000047       | 0.000047       |       0.047     | ~21000         |
| Themed Decorator     | 10,000    | 0.000015       | 0.000015       | 0.000015       |       0.015     | ~66000         |

## Features

*   **Nested Colorization:** Handles nested ANSI color codes gracefully, ensuring correct color rendering even with complex formatting.
*   **Theming:** Supports predefined and custom themes for consistent colorization across your output.
*   **Data Structure Coloring:** Colorizes dictionaries, lists, JSON, and YAML strings recursively, highlighting keys, values, and different data types.
*   **Decorator Support:** Provides decorators for easily colorizing function outputs and applying themes, including monotone (single-color) wraps.
*   **Customizable Configurations:** Allows loading color configurations from JSON or YAML files/strings, or dictionaries.
*   **YAML Output:** Provides a handler for colorized YAML output of structured data.
*   **Color Removal:** Includes a utility handler to strip ANSI color codes from output.
*   **Extensible Output Formatting:** Supports custom output handlers for diverse formatting needs.

## Installation

```bash
pip install colordoll
```
For YAML-specific features (like `YamlHandler` or loading YAML configurations), you'll also need `PyYAML`:
```bash
pip install PyYAML
```
Alternatively, you might be able to install with an extra:
```bash
pip install colordoll[yaml]
```
(Check the project's `setup.py` or `pyproject.toml` for available extras.)


## Usage

### Basic Colorization

```python

from colordoll import default_colorizer, red, blue, bright_black, bg_blue

# Using color functions
print(red("This is red text."))
print(blue("This is blue text."))

# Using the colorize method with foreground and background colors
yellow_text = default_colorizer.colorize("This is yellow text on blue background\nSome terminals have trouble with both, but it is there on highlight", "yellow")
added_bg = bg_blue(yellow_text)
print(added_bg)

# Handling nested colors correctly
print(bright_black(f"This is {red('red text')} inside grey text."))


```

### Themed Colorization (JSON/Dict)

The default output handler formats data structures like dictionaries and lists into a JSON-like string.

```python

from colordoll import default_colorizer, darktheme, vibranttheme, DataHandler

# Ensure default handler is DataHandler (it usually is by default)
default_colorizer.set_output_handler(DataHandler())


@darktheme
def get_data():
    return {"key1": "value1", "key2": [1, 2, 3], "key3": True}


@vibranttheme
def get_other_data():
    return [{"name": "Item 1", "value": 10}, {"name": "Item 2", "value": 20}]


print(get_data())
print(get_other_data())


```

### Monotone Theming (Wrap Decorators)
Quickly theme an entire structured output with a single color using wrap decorators.
```python


from colordoll import wrapmono


@wrapmono("red")
def get_all_red_data():
    return {"alert": "System critical", "items": [1, 2, 3], "active": False}


@wrapmono("green")
def get_all_green_data():
    return {"info": "System nominal", "details": {"status": "OK", "code": 200}}


print(get_all_red_data())
print(get_all_green_data())

```

### Custom Themes and Configurations

```python

from colordoll import Colorizer, ColorConfig, DataHandler

# Ensure DataHandler is used for this example if not default
custom_colorizer = Colorizer(output_handler=DataHandler())


# Load a custom color configuration from a JSON file
# config = ColorConfig("my_colors.json")  # my_colors.json contains your custom color definitions
# colorizer_with_custom_config = Colorizer(config, output_handler=DataHandler())

# Create a custom theme
my_theme = {"key": "bright_magenta", "string": "cyan", "number": "yellow", "bool": "green", "null": "red", "other": "blue"}

# Colorize data using the custom theme
data_to_color = {"my_key": "my_value", "numbers": [1.00, 2.6, 3], "valid": None}
colored_data = custom_colorizer.theme_colorize(data_to_color, my_theme)
print(colored_data)

```

### YAML Output
ColorDoll can output data as colorized YAML. Requires `PyYAML`.
```python

from colordoll import default_colorizer, YamlHandler, light_theme_colors

# Set the output handler to YamlHandler
default_colorizer.set_output_handler(YamlHandler())

my_data = {"project": "ColorDoll", "version": "0.1", "features": ["theming", "yaml_output", "nested_colors"], "config": {"active": True, "level": 5}}

colored_yaml_output = default_colorizer.theme_colorize(my_data, light_theme_colors)
print(colored_yaml_output)

# Remember to set the handler back if you need JSON/Dict output later
# from colordoll import DataHandler
# default_colorizer.set_output_handler(DataHandler())

```

### Removing ANSI Colors
You can strip ANSI color codes from the output.
```python


from colordoll import default_colorizer, ColorRemoverHandler, DataHandler, vibrant_theme_colors

# Sample data
data_to_process = {"message": "This is a colorful message!", "id": 12345}

# 1. Get a normally colored output (using DataHandler)
default_colorizer.set_output_handler(DataHandler())
normally_colored_output = default_colorizer.theme_colorize(data_to_process, vibrant_theme_colors)
print(f"Normally Colored:\n{normally_colored_output}")

# 2. Get output with colors stripped (using ColorRemoverHandler)
# ColorRemoverHandler internally uses DataHandler to format, then strips colors.
default_colorizer.set_output_handler(ColorRemoverHandler())
stripped_output = default_colorizer.theme_colorize(data_to_process, vibrant_theme_colors)
print(f"\nColors Stripped:\n{stripped_output}")

# Set handler back to DataHandler for normal operations if needed
default_colorizer.set_output_handler(DataHandler())

```

## Examples Above in terminal

![example image](https://raw.githubusercontent.com/kaigouthro/colordoll/main/media/examples.png)

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## License

This project is licensed under the MIT License.

## Change Log

### v0.1.8
*   Default theme in colorizer
*   `Colorizer.set_theme({})` to set theme to use with `Colorizer.theme_colorize(text)` making the theme input optional for temp over-riding.
*   Wrapping themes can now take a bool asnd pass  return value and print at the same time.. see examples in demo.

### v0.1.7
*   Updated performance benchmarks with latest figures for v0.1.7.
*   Improved internal logic for `colorize` for more robust nested color and background/foreground combination handling.
*   Documentation enhancements and README update to reflect new features.
*   General code cleanup and minor internal refinements.

### v0.1.6
*   Added "monotone wrap" decorators (e.g., `@wrapmono("red")`) for quick single-color theming of structured data output.
*   Expanded the set of direct color applicationns to strings to have all bg coloring as well.

### v0.1.5
*   Implemented `ColorRemoverHandler` to strip ANSI escape codes from formatted output, allowing for easy generation of plain text versions.

### v0.1.4
*   Added `YamlHandler` for colorized YAML output of dictionaries and lists. Requires `PyYAML`.
*   Enhanced `ConfigLoader` to support loading color configurations from YAML files and strings, in addition to JSON and dictionaries.

### v0.1.3
*   Introduced a pluggable `OutputHandler` system (`OutputHandler`, `DataHandler`) allowing for more flexible and extensible output formatting.
*   Refactored `Colorizer` to utilize the new `OutputHandler` system for `theme_colorize` operations.

### v0.1.2
*   Added performance benchmarks (`bench.py`) to the repository.
*   Minor refactorings and code improvements.

### v0.1 (Initial Release)
*   Implemented core colorization functionality for basic string coloring.
*   Created robust nested colorization and background colorization abilities.
*   Introduced theming for structured data (dictionaries, lists) and decorator support (`@darktheme`, etc.).
*   Enabled custom color configurations via dictionaries (and implicitly JSON files).
*   Included various pre-defined themes (dark, light, vibrant, minimalist).


![demo image](media/demo.png)
