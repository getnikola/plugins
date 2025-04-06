# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import sys
import json
import shutil
import pytest
from pytest import fixture

from nikola import nikola
from nikola.utils import _reload


try:
    from freezegun import freeze_time

    _freeze_time = True
except ImportError:
    _freeze_time = False
    freeze_time = lambda x: lambda y: y

# Define the path to our V8 plugins
from tests import V8_PLUGIN_PATH


class TestCommandFuturePostsBase:
    """Base class for testing the future_posts command."""

    @fixture(autouse=True)
    def _copy_plugin_to_site(self, _init_site):
        """Copy the future_posts plugin to the test site's plugins directory."""
        if not os.path.exists("plugins"):
            os.makedirs("plugins")
        shutil.copytree(
            str(V8_PLUGIN_PATH / "future_posts"),
            os.path.join("plugins", "future_posts"),
        )

    def _add_test_post(self, title):
        """Helper to add a test post with specified date."""
        self._run_command(["new_post", "-f", "markdown", "-t", title, "-s"])

    def _force_scan(self):
        """Force a rescan of posts."""
        self._site._scanned = False
        self._site.scan_posts(True)

    @fixture(autouse=True)
    def _init_site(self, monkeypatch, tmp_path):
        """Initialize a demo site for testing."""
        from nikola.plugins.command.init import CommandInit

        # Create demo site
        monkeypatch.chdir(tmp_path)
        command_init = CommandInit()
        command_init.execute(options={"demo": True, "quiet": True}, args=["demo"])

        # Setup paths and load config
        sys.path.insert(0, "")
        monkeypatch.chdir(tmp_path / "demo")
        with open("conf.py", "a") as f:
            f.write(
                "SCHEDULE_RULE = 'RRULE:FREQ=WEEKLY;BYDAY=MO,WE,FR;BYHOUR=7;BYMINUTE=0;BYSECOND=0'\n"
            )
        import conf

        _reload(conf)
        sys.path.pop(0)

        # Initialize Nikola site
        self._site = nikola.Nikola(**conf.__dict__)
        # Initialize plugins (our plugin will be discovered from the plugins directory)
        self._site.init_plugins()

    def _run_command(self, args=[]):
        """Run a Nikola command."""
        from nikola.__main__ import main

        return main(args)

    def _get_command_output(self, args):
        """Run command and capture its output."""
        import subprocess

        try:
            output = subprocess.check_output(args)
            return output.decode("utf-8")
        except (OSError, subprocess.CalledProcessError):
            return ""


@pytest.mark.skipif(not _freeze_time, reason="freezegun package not installed.")
class TestCommandFuturePosts(TestCommandFuturePostsBase):
    """Test the future_posts command functionality."""

    @fixture(autouse=True)
    def setUp(self):
        """Set up test posts."""
        # Add some test posts with future dates
        for i in range(3):
            self._add_test_post(f"Future Post {i+1}")
        self._force_scan()

    def test_json_output(self):
        """Test JSON output format."""
        output = self._get_command_output(["nikola", "future_posts", "--json"])
        posts = json.loads(output)
        assert isinstance(posts, list)
        assert len(posts) >= 3
        assert all(isinstance(post, dict) for post in posts)
        assert all("title" in post and "date" in post for post in posts)

    def test_calendar_output(self):
        """Test calendar output format."""
        output = self._get_command_output(["nikola", "future_posts", "--calendar"])
        print(output)
        assert "## indicates days with scheduled posts" in output
        assert any(month in output for month in ["January", "February", "March"])

    def test_details_output(self):
        """Test detailed list output format."""
        output = self._get_command_output(["nikola", "future_posts", "--details"])
        assert "Found" in output
        assert "Future Post" in output
        assert "Title:" in output
        assert "Date:" in output

    def test_html_output(self):
        """Test HTML output format."""
        output = self._get_command_output(["nikola", "future_posts", "--html"])
        assert "<!DOCTYPE html>" in output
        assert "<title>Future Posts</title>" in output
        assert "Future Post" in output

    def test_no_future_posts(self):
        """Test behavior when no future posts exist."""
        # Clear existing posts
        for post in os.listdir("posts"):
            os.remove(os.path.join("posts", post))
        self._force_scan()
        output = self._get_command_output(["nikola", "future_posts", "--details"])
        assert "No future posts scheduled." in output

    @pytest.mark.skipif(not _freeze_time, reason="freezegun package not installed.")
    @freeze_time("2025-01-01")
    def test_months_parameter(self):
        """Test the --months parameter."""
        output = self._get_command_output(
            ["nikola", "future_posts", "--calendar", "--months", "2"]
        )
        month_headers = [
            line
            for line in output.split("\n")
            if any(
                month in line
                for month in [
                    "January",
                    "February",
                    "March",
                    "April",
                    "May",
                    "June",
                    "July",
                    "August",
                    "September",
                    "October",
                    "November",
                    "December",
                ]
            )
        ]
        assert len(month_headers) == 2
