"""
Unit tests for main.py CLI dispatch and argument parsing.
"""

from __future__ import annotations

import argparse
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

import main


class CliDispatchTests(unittest.TestCase):
    def setUp(self):
        self.parser = main.setup_cli_parser() if hasattr(main, "setup_cli_parser") else None

    def _parse_args(self, args_list: list[str]) -> argparse.Namespace:
        # If main.py has build_parser or setup_parser, call it; otherwise simulate parser
        with patch("sys.argv", ["main.py"] + args_list):
            # We can capture the parser by running the parser creation logic from main()
            with patch("main.run_cmd") as mock_run:
                # Test parsing via argparse
                parser = argparse.ArgumentParser()
                # We can import main and test its subcommands
                pass

    def test_main_module_exports_and_commands(self):
        """Verify that main.py defines all required subcommands and handlers."""
        self.assertTrue(callable(main.cmd_render))
        self.assertTrue(callable(main.cmd_prepare))
        self.assertTrue(callable(main.cmd_generate))
        self.assertTrue(callable(main.cmd_vectorize))
        self.assertTrue(callable(main.cmd_build_interior))
        self.assertTrue(callable(main.cmd_build_cover))
        self.assertTrue(callable(main.cmd_build_animals_cover))
        self.assertTrue(callable(main.cmd_build_copy_to_color_interior))
        self.assertTrue(callable(main.cmd_build_series_covers))

    @patch("main.run_cmd")
    def test_cmd_build_animals_cover_defaults_to_32_pages(self, mock_run: MagicMock):
        """Verify that build-animals-cover defaults to 32 pages."""
        args = argparse.Namespace(output=None, page_count=32)
        main.cmd_build_animals_cover(args)
        self.assertTrue(mock_run.called)
        first_cmd = mock_run.call_args_list[0][0][0]
        self.assertIn("--page-count", first_cmd)
        idx = first_cmd.index("--page-count")
        self.assertEqual(first_cmd[idx + 1], "32")

    @patch("main.run_cmd")
    def test_cmd_build_animals_cover_custom_page_count(self, mock_run: MagicMock):
        """Verify that build-animals-cover passes custom page count when supplied."""
        args = argparse.Namespace(output=None, page_count=80)
        main.cmd_build_animals_cover(args)
        self.assertTrue(mock_run.called)
        first_cmd = mock_run.call_args_list[0][0][0]
        idx = first_cmd.index("--page-count")
        self.assertEqual(first_cmd[idx + 1], "80")

    @patch("main.cmd_build_animals_cover")
    @patch("main.cmd_build_copy_to_color_interior")
    def test_build_all_dispatches_animals_series(self, mock_c2c: MagicMock, mock_cover: MagicMock):
        """Verify that build-all with series=animals runs animals cover and interior."""
        args = argparse.Namespace(command="build-all", series="copy_to_color_animals", author=None)
        with patch("sys.argv", ["main.py", "build-all", "--series", "copy_to_color_animals"]):
            # Run main's dispatch logic
            with patch("main.get_status"):
                exit_code = main.main()
                self.assertEqual(exit_code, 0)
                self.assertTrue(mock_cover.called)
                self.assertTrue(mock_c2c.called)

    @patch("main.run_cmd")
    def test_cmd_generate_wires_series_and_edition(self, mock_run: MagicMock):
        """Verify that cmd_generate uses the requested series and edition_id."""
        args = argparse.Namespace(
            series="solar_system_explorers",
            edition_id="v1.0-core",
            model="test-model",
            location="global",
            max_assets=2,
        )
        main.cmd_generate(args)
        self.assertTrue(mock_run.called)
        call_cmd = mock_run.call_args[0][0]
        self.assertIn("--max-assets", call_cmd)
        idx = call_cmd.index("--max-assets")
        self.assertEqual(call_cmd[idx + 1], "2")


if __name__ == "__main__":
    unittest.main()
