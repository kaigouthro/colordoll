from colordoll import default_colorizer, vibranttheme, minimalisttheme, darktheme, DataHandler, YamlHandler, ColorRemoverHandler, vibrant_theme_colors, dark_theme_colors, magenta, red, green, blue, bright_cyan, bright_yellow, wrapmono
import yaml
import random
from typing import Dict


if __name__ == "__main__":
    print("Welcome to the artistic colordoll demo!\n")

    colorizer = default_colorizer  # Updated from _default_colorizer

    print(colorizer.colorize("-" * 40, "cyan"))
    print(colorizer.colorize("  Demonstrating Basic Colored Lines", "bright_white"))
    print(colorizer.colorize("-" * 40, "cyan"))

    print(colorizer.colorize("Red", "red") + colorizer.colorize(" Line: ") + colorizer.colorize("---", "red"))
    print(colorizer.colorize("Green", "green") + colorizer.colorize(" Line: ") + colorizer.colorize("---", "green"))
    print(colorizer.colorize("Blue", "blue") + colorizer.colorize(" Line: ") + colorizer.colorize("---", "blue"))
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
            insides = random.randint(1, (3 + (square_side % random.randint(2, square_side // 4))))
            middle_section = "██" * insides
            spaces = " " * (square_side - 2 - insides)
            line_content = f" █{spaces}{magenta(middle_section)}{spaces}█ "  # magenta() uses default_colorizer
            line = colorizer.colorize(text=line_content, color="red", background_color="grey")
        print(line)

    print()

    print(colorizer.colorize("-" * 40, "red", "black"))
    print(colorizer.colorize("  Creating a Colored Heart Text Art    ", "black", "magenta"))
    print(colorizer.colorize("-" * 40, "red", "black"))

    heart_art = (
        """

     ███   ███
    █████ █████
   █████████████
  ███████████████
 ██████"""
        + (red("1") + green(" 2 ") + blue("3"))  # red(), green(), blue() use default_colorizer
        + """██████
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
    )

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

    @minimalisttheme(True)  # minimalisttheme uses default_colorizer
    def get_minimalist_heart(heart_art) -> str:
        return heart_art

    print(get_minimalist_heart(heart_art=heart_art))
    print()

    # Themed Heart Art (Vibrant with Background)

    print(colorizer.colorize("-" * 40, "green"))
    print(colorizer.colorize("  Themed Heart Art (Vibrant with Background)", color="bright_white"))
    print(colorizer.colorize("-" * 40, "green"))

    @vibranttheme  # vibranttheme uses default_colorizer
    def get_vibrant_heart() -> str:
        """
        Provides a vibrant heart art string with colorized elements.
        """
        return heart_art

    print(get_vibrant_heart())
    print()

    print(colorizer.colorize("-" * 40, "cyan"))
    print(colorizer.colorize("  Themed JSON Data Display (Dark Theme)", "bright_white"))
    print(colorizer.colorize("-" * 40, "cyan"))

    sample_json_data = {"name": "Artistic Demo", "type": "Text Art", "colors_used": ["red", "green", "blue", "yellow"], "is_artistic": True, "value": 123}

    @darktheme  # darktheme uses default_colorizer
    def get_themed_json_data() -> Dict:
        return sample_json_data

    print(get_themed_json_data())
    print()

    print(colorizer.colorize("-" * 40, "cyan"))
    print(colorizer.colorize("  Direct Color Functions Example (Corrected)", "bright_white"))
    print(colorizer.colorize("-" * 40, "cyan"))
    print()

    print(bright_cyan("This message is in bright cyan."))  # bright_cyan() uses default_colorizer
    print(bright_yellow("And this one is in bright yellow."))  # bright_yellow() uses default_colorizer
    print()

    print(colorizer.colorize("-" * 40, "cyan"))
    print(colorizer.colorize("  End of colordoll Artistic Demo", "bright_white"))
    print(colorizer.colorize("-" * 40, "cyan"))
    print()
    print()
    print()

    sample_data = {"name": "Handler Demo", "formats": ["JSON", "Dict/List", "YAML", "HTML", "Color Removed"], "value": 123, "is_demo": True, "nested": {"item": "nested_value", "list": [1, 2, "three"]}}

    print(" * " * 20)
    print(default_colorizer.colorize("Demonstrating Output Handlers", "bright_white"))  # Updated
    print(" * " * 20)
    print()

    print(default_colorizer.colorize("-" * 40, "green"))  # Updated
    print(default_colorizer.colorize("  JSON (Gets converted) Output", "bright_white"))  # Updated
    print(default_colorizer.colorize("-" * 40, "green"))  # Updated
    print(default_colorizer.theme_colorize(sample_data, dark_theme_colors))  # Updated
    print()

    print(default_colorizer.colorize("-" * 40, "cyan"))  # Updated
    print(default_colorizer.colorize("  Dict/List Handler Output", "bright_white"))  # Updated
    # The following line uses 'colorizer' which is 'default_colorizer'
    print(colorizer.colorize("-" * 40, "cyan"))
    default_colorizer.set_output_handler(DataHandler())  # Updated
    print(default_colorizer.theme_colorize(sample_data, dark_theme_colors))  # Updated

    if yaml is not None:
        print(default_colorizer.colorize("-" * 40, "bright_yellow"))  # Updated
        print(default_colorizer.colorize("  YAML Handler Output", "bright_white"))  # Updated
        print(default_colorizer.colorize("-" * 40, "bright_yellow"))  # Updated
        default_colorizer.set_output_handler(YamlHandler())  # Updated

        def getyaml() -> str:
            return default_colorizer.theme_colorize(sample_data, dark_theme_colors)  # Updated

        print(getyaml())
    else:
        print(default_colorizer.colorize("YAML Handler skipped due to PyYAML installation issue.", "yellow"))  # Updated
        print()

    print(default_colorizer.colorize("-" * 40, "cyan"))  # Updated
    print(default_colorizer.colorize("  Color Remover Handler Output", "bright_white"))  # Updated
    print(default_colorizer.colorize("-" * 40, "cyan"))  # Updated
    default_colorizer.set_output_handler(ColorRemoverHandler())  # Updated
    removed_color_output = default_colorizer.theme_colorize(sample_data, dark_theme_colors)  # Updated
    print(f"{removed_color_output}")

    default_colorizer.set_output_handler(DataHandler())  # Updated
    print(default_colorizer.theme_colorize(removed_color_output, vibrant_theme_colors))  # Updated

    print(" * " * 20)
    print(default_colorizer.colorize("End of Output Handler Demo", "bright_white"))  # Updated
    print(" * " * 20)

    # some fun new abilities to wrap and nest wrap printing

    # will print the dict when called.
    @darktheme()
    def thing1():
        """
        dict: A dictionary with a single key-value pair.
        """
        return {"mynumber": 1234}

    # create a single color wrapper
    red_themed = wrapmono("red")

    @red_themed(True)
    def thing2():
        """
        dict: A dictionary with a wrappped single key-value pair.
        """
        return {"the_other_thing": "This is a string"}

    @vibranttheme(True)
    def thing_double():
        """
        dict: A dictionary with a wrappped single key-value pair.
        """
        return {
            # with not print here, will nest colorization,  but the value is now the colorized string here with ansi codes.
            "Thing1": thing1(),
            # will Print during thing_double call in it's own color
            # but be printed ALSO by thing_double's output overwritten by this functions vibranttheme
            "Thing2": thing2(),
        }

    # you can do this:
    thing_double()

    # or this
    print(thing_double())

    # there's some chaining nd nestinng rules i don't have time for atm.. will do soonish.
    # but prints like this
    # {
    #   "the_other_thing": "This is a string"
    # }
    # {
    #   "Thing1": "{
    #   "mynumber": 1234
    # }",
    #   "Thing2": {
    #     "the_other_thing": "This is a string"
    #   }
    # }
    # {
    #   "the_other_thing": "This is a string"
    # }
    # {
    #   "Thing1": "{
    #   "mynumber": 1234
    # }",
    #   "Thing2": {
    #     "the_other_thing": "This is a string"
    #   }
    # }
    # {'Thing1': '\x1b[90m{\x1b[0m\n  "\x1b[96mmynumber\x1b[0m": \x1b[91m1234\x1b[0m\n\x1b[90m}\x1b[0m', 'Thing2': {'the_other_thing': 'This is a string'}}
    #
