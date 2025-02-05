# Future Posts Plugin for Nikola

A command plugin for [Nikola](https://getnikola.com) that helps you manage and visualize your scheduled future blog posts. Get an overview of upcoming content through ASCII calendars, detailed lists, JSON data, or HTML output.

## Overview

This plugin adds a `future_posts` command to Nikola that displays information about posts scheduled for future dates. It supports multiple output formats that can be used individually or combined.

## Features

-   📅 ASCII calendar view showing scheduled post dates
-   📋 Detailed list view of upcoming posts
-   🔄 JSON output for integration with other tools
-   🌐 HTML output for web viewing
-   📦 Modular design - mix and match output formats
-   💾 Save output to file or display in terminal

## Installation

You can install this plugin using Nikola's plugin manager:

```bash
nikola plugin -i future_posts
```

Or manually:

1. Create a `future_posts` directory in your Nikola site's plugins directory:

    ```bash
    mkdir -p plugins/future_posts
    ```

2. Copy `future_posts.plugin` and `future_posts.py` into the new directory

3. Add "future_posts" to your `COMMANDS` list in `conf.py`:
    ```python
    COMMANDS.append('future_posts')
    ```

## Usage

Basic usage:

```bash
nikola future_posts
```

### Output Formats

You can combine any of these options:

-   `--calendar` (`-c`): Show ASCII calendar with marked post dates
-   `--details` (`-d`): Show detailed list of posts
-   `--json` (`-j`): Output in JSON format
-   `--html` (`-h`): Generate HTML output

### Additional Options

-   `--months N` (`-m N`): Show N months in calendar view (default: 3)
-   `--output FILE` (`-o FILE`): Save output to file instead of stdout

### Examples

Show calendar for next 3 months:

```bash
nikola future_posts --calendar
```

Show both calendar and detailed list:

```bash
nikola future_posts --calendar --details
```

Generate JSON output:

```bash
nikola future_posts --json
```

Save HTML view to file:

```bash
nikola future_posts --html --output future-posts.html
```

Show calendar for next 6 months:

```bash
nikola future_posts --calendar --months 6
```

## Configuration

Optional configuration settings can be added to your site's `conf.py`:

```python
# Default number of months to show in calendar view
FUTURE_POSTS_DEFAULT_MONTHS = 3

# Default output format
FUTURE_POSTS_DEFAULT_FORMAT = "details"

# Default output file path
FUTURE_POSTS_DEFAULT_OUTPUT = None
```

## Sample Output

### Calendar View

```
    February 2025
Mo Tu We Th Fr Sa Su
          1  2  3  4
 5  6  7  8  9 ## 11
12 13 14 15 16 17 18
19 20 21 22 23 24 ##
26 27 28

## indicates days with scheduled posts
```

### Detailed View

```
Found 2 future posts:
----------------------------------------
Title: My First Future Post
Date: 2025-02-10
Source: posts/first-post.rst
Permalink: /blog/2025/02/first-post/
----------------------------------------
```

## Contributing

Contributions are welcome! Please feel free to:

1. 🐛 Report bugs
2. ✨ Suggest new features
3. 📝 Improve documentation
4. 🔧 Submit pull requests

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Jesper Dramsch

## Support

If you find any issues or have questions, please file an issue on the [Nikola Plugins repository](https://github.com/getnikola/plugins).
