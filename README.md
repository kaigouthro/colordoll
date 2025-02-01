# ColorDoll: Nested ANSI Colorization for Python

[![PyPI version](https://badge.fury.io/py/colordoll.svg)](https://badge.fury.io/py/colordoll)

ColorDoll is a Python library that provides flexible and powerful ANSI colorization, including nested colorization and theming for complex data structures like dictionaries, lists, and JSON strings.

And, it's fairly Quick. 


## 🚀 Performance Benchmarks ⏱️
`(amd 3800, 3200mhz ram, single XPG-8200 nvme, win11)`

| Function             | Runs      | Min Time (sec) | Max Time (sec) | Avg Time (sec) | As milliseconds | Runs / second  |
|----------------------|-----------|----------------|----------------|----------------|-----------------|----------------|
| `colorize`           | 10,000    | 0.000006       | 0.000006       | 0.000006       |       0.006     | ~165000        |
| `theme_colorize`     | 10,000    | 0.000059       | 0.000060       | 0.000059       |       0.059     | ~16950         |
| Themed Decorator     | 10,000    | 0.000023       | 0.000023       | 0.000023       |       0.023     | ~43450         |

## Features

* **Nested Colorization:**  Handles nested ANSI color codes gracefully, ensuring correct color rendering even with complex formatting.
* **Theming:** Supports predefined and custom themes for consistent colorization across your output.
* **Data Structure Coloring:** Colorizes dictionaries, lists, and JSON strings recursively, highlighting keys, values, and different data types.
* **Decorator Support:** Provides decorators for easily colorizing function outputs and applying themes.
* **Customizable Configurations:** Allows loading color configurations from JSON files or dictionaries.

## Installation

```bash
pip install colordoll
```

## Usage

### Basic Colorization

```python
from colordoll import default_colorizer, red, blue, green

# Using color functions
print(red("This is red text."))
print(blue("This is blue text."))

# Using the colorize method with foreground and background colors
print(default_colorizer.colorize("Yellow text on a blue background", "yellow", "blue"))

# Handling nested colors correctly
print(default_colorizer.colorize(f"This is {default_colorizer.colorize('red text', 'red')} inside blue text.", "blue"))
```

### Themed Colorization

```python
from colordoll import darktheme, vibranttheme

@darktheme
def get_data():
    return {"key1": "value1", "key2": [1, 2, 3], "key3": True}

@vibranttheme
def get_other_data():
    return [{"name": "Item 1", "value": 10}, {"name": "Item 2", "value": 20}]

print(get_data())
print(get_other_data())
```

### Custom Themes and Configurations

```python
from colordoll import Colorizer, ColorConfig

# Load a custom color configuration from a JSON file
config = ColorConfig("my_colors.json")  # my_colors.json contains your custom color definitions
colorizer = Colorizer(config)

# Create a custom theme
my_theme = {
    "key": "bright_magenta",
    "string": "cyan",
    "number": "yellow",
    "bool": "green",
    "null": "red",
    "other": "blue"
}

# Colorize data using the custom theme
colored_data = colorizer.theme_colorize({"my_key": "my_value", "numbers": [1, 2, 3]}, my_theme)
print(colored_data)

```

![](https://github.com/kaigouthro/colordoll/blob/66c6f1d2913dfa5134c6f231a429241b728ec984/media/demo.png)

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.


## License

This project is licensed under the MIT License.


## Change Log
### 0.1 (Initial Release)
* Implemented core colorization functionality.
* Created nested colorization and background colorization abilities. Superpower!
* Introduced theming and decorator support.
* Enabled custom color configurations.
* Included various pre-defined themes.

### 0.1.2 Refactor
* Added Bench



