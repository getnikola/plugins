from datetime import datetime, timedelta
import calendar
from nikola.plugin_categories import Command
import json


class CommandFuturePosts(Command):
    """List all future scheduled posts with configurable output formats."""

    name = "future_posts"
    doc_usage = (
        "[--json] [--calendar] [--details] [--html] [--months N] [--output FILE]"
    )
    doc_purpose = "List scheduled future posts in various formats"
    cmd_options = [
        {
            "name": "json",
            "short": "j",
            "long": "json",
            "type": bool,
            "default": False,
            "help": "Output in JSON format",
        },
        {
            "name": "calendar",
            "short": "c",
            "long": "calendar",
            "type": bool,
            "default": False,
            "help": "Show ASCII calendar view",
        },
        {
            "name": "details",
            "short": "d",
            "long": "details",
            "type": bool,
            "default": False,
            "help": "Show detailed list view",
        },
        {
            "name": "html",
            "short": "h",
            "long": "html",
            "type": bool,
            "default": False,
            "help": "Output as HTML",
        },
        {
            "name": "months",
            "short": "m",
            "long": "months",
            "type": int,
            "default": None,
            "help": "Number of months to show in calendar (default: from config or all scheduled months)",
        },
        {
            "name": "output",
            "short": "o",
            "long": "output",
            "type": str,
            "default": None,
            "help": "Output file (default: from config or stdout)",
        },
    ]

    def _get_future_posts(self):
        """Get all future posts sorted by date."""
        current_date = datetime.now()
        future_posts = []

        for post in self.site.timeline:
            post_date = datetime.fromtimestamp(post.date.timestamp())
            if post_date > current_date:
                post_info = {
                    "title": post.title(),
                    "date": post_date.strftime("%Y-%m-%d"),
                    "permalink": post.permalink(),
                    "source_path": post.source_path,
                }
                future_posts.append(post_info)

        return sorted(future_posts, key=lambda x: x["date"])

    def _format_calendar(self, future_posts, months_ahead=None):
        """Generate ASCII calendar with marked posts."""
        output = []
        start_date = datetime.now().date()
        post_dates = {
            datetime.strptime(post["date"], "%Y-%m-%d").date() for post in future_posts
        }

        last_post_date = datetime.strptime(future_posts[-1]["date"], "%Y-%m-%d")
        if months_ahead is None:
            months_ahead = (last_post_date.year - start_date.year) * 12 + last_post_date.month - start_date.month + 2

        for month_offset in range(months_ahead):
            target_date = start_date + timedelta(days=32 * month_offset)
            year = target_date.year
            month = target_date.month

            cal = calendar.monthcalendar(year, month)
            month_name = calendar.month_name[month]

            output.append(f"\n{month_name} {year}".center(20))
            output.append("Mo Tu We Th Fr Sa Su")

            for week in cal:
                week_str = ""
                for day in week:
                    if day == 0:
                        week_str += "   "
                    else:
                        date = datetime(year, month, day).date()
                        if date in post_dates:
                            week_str += "## "
                        else:
                            week_str += f"{day:2d} "
                output.append(week_str)

        output.append("\n## indicates days with scheduled posts")
        return "\n".join(output)

    def _format_details(self, future_posts):
        """Generate detailed text listing."""
        output = [f"\nFound {len(future_posts)} future posts:", "-" * 40]

        for post in future_posts:
            output.extend(
                [
                    f"Title: {post['title']}",
                    f"Date: {post['date']}",
                    f"Source: {post['source_path']}",
                    f"Permalink: {post['permalink']}",
                    "-" * 40,
                ]
            )

        return "\n".join(output)

    def _format_html(self, future_posts, include_calendar=True):
        """Generate HTML output."""
        html = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "<title>Future Posts</title>",
            "<style>",
            ".calendar { margin: 20px; font-family: monospace; }",
            ".calendar-month { margin-bottom: 20px; }",
            ".post-list { margin: 20px; }",
            ".post { margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid #eee; }",
            "</style>",
            "</head>",
            "<body>",
            f"<h1>Future Posts ({len(future_posts)})</h1>",
        ]

        if include_calendar:
            html.append('<div class="calendar">')
            html.append(self._format_calendar(future_posts).replace("\n", "<br>"))
            html.append("</div>")

        html.append('<div class="post-list">')
        for post in future_posts:
            html.extend(
                [
                    '<div class="post">',
                    f'<h2><a href="{post["permalink"]}">{post["title"]}</a></h2>',
                    f'<p>Date: {post["date"]}</p>',
                    f'<p>Source: {post["source_path"]}</p>',
                    "</div>",
                ]
            )
        html.extend(["</div>", "</body>", "</html>"])

        return "\n".join(html)

    def _execute(self, options, args):
        """Execute the future posts command."""
        self.site.scan_posts()

        # Get configuration values
        config_months = self.site.config.get("FUTURE_POSTS_DEFAULT_MONTHS", None)
        config_format = self.site.config.get("FUTURE_POSTS_DEFAULT_FORMAT", "details")
        config_output = self.site.config.get("FUTURE_POSTS_DEFAULT_OUTPUT", None)

        # Apply config values if command-line options aren't set
        if options["months"] is None:
            options["months"] = config_months

        if options["output"] is None:
            options["output"] = config_output

        if not any(
            [options["json"], options["calendar"], options["details"], options["html"]]
        ):
            # Use config format if no format specified
            if config_format == "json":
                options["json"] = True
            elif config_format == "calendar":
                options["calendar"] = True
            elif config_format == "html":
                options["html"] = True
            else:  # default to details
                options["details"] = True

        future_posts = self._get_future_posts()

        if not future_posts:
            print("No future posts scheduled.")
            return

        # Prepare output
        output = []

        # Generate requested formats
        if options["json"]:
            output.append(json.dumps(future_posts, indent=2))

        if options["calendar"]:
            output.append(self._format_calendar(future_posts, options["months"]))

        if options["details"]:
            output.append(self._format_details(future_posts))

        if options["html"]:
            output = [self._format_html(future_posts, options["calendar"])]

        # Output to file or stdout
        result = "\n\n".join(output)
        if options["output"]:
            with open(options["output"], "w") as f:
                f.write(result)
        else:
            print(result)
