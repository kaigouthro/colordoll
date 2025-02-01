import timeit


# --- Performance Benchmarks ---
print("\n--- Performance Benchmarks ---")

# Benchmark colorize function
colorize_setup = """
from colordoll import default_colorizer
text = "Performance test string"
"""
colorize_statement = """
default_colorizer.colorize(text, color="red", background_color="bg_blue")
"""
colorize_timer = timeit.Timer(colorize_statement, setup=colorize_setup)
colorize_runs = 1000
colorize_times = colorize_timer.repeat(5, colorize_runs)
print(f"Colorize function - {colorize_runs} runs:")
print(f"  Min time: {min(colorize_times)/colorize_runs:.6f} sec")
print(f"  Max time: {max(colorize_times)/colorize_runs:.6f} sec")
print(
    f"  Avg time: {sum(colorize_times)/len(colorize_times)/colorize_runs:.6f} sec")

# Benchmark theme_colorize function
theme_colorize_setup = """
from colordoll import default_colorizer, dark_theme_colors
data = {"key1": "value1", "key2": 123, "key3": True, "key4": None, "key5": [1, 2, "three"]}
"""
theme_colorize_statement = """
default_colorizer.theme_colorize(data, dark_theme_colors)
"""
theme_colorize_timer = timeit.Timer(
    theme_colorize_statement, setup=theme_colorize_setup)
theme_colorize_runs = 10000
theme_colorize_times = theme_colorize_timer.repeat(5, theme_colorize_runs)

print(f"\nTheme colorize function - {theme_colorize_runs} runs:")
print(
    f"  Min time: {min(theme_colorize_times)/theme_colorize_runs:.6f} sec")
print(
    f"  Max time: {max(theme_colorize_times)/theme_colorize_runs:.6f} sec")
print(
    f"  Avg time: {sum(theme_colorize_times)/len(theme_colorize_times)/theme_colorize_runs:.6f} sec")

# Benchmark themed decorator
themed_decorator_setup = """
from colordoll import darktheme

@darktheme
def dummy_function():
    return {"key": "value", "number": 10}
"""
themed_decorator_statement = """
dummy_function()
"""

themed_decorator_timer = timeit.Timer(
    themed_decorator_statement, setup=themed_decorator_setup)
themed_decorator_runs = 10000
themed_decorator_times = themed_decorator_timer.repeat(
    5, themed_decorator_runs)

print(f"\nThemed Decorator - {themed_decorator_runs} runs:")
print(
    f"  Min time: {min(themed_decorator_times)/themed_decorator_runs:.6f} sec")
print(
    f"  Max time: {max(themed_decorator_times)/themed_decorator_runs:.6f} sec")
print(
    f"  Avg time: {sum(themed_decorator_times)/len(themed_decorator_times)/themed_decorator_runs:.6f} sec")
