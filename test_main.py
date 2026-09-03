import argparse
import contextlib
import io
from pathlib import Path
from string import ascii_letters
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

import main


class CliAndConfigTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.home = Path(self.temporary_directory.name)
        self.environment = {"HOME": str(self.home)}
        self.config_path = (
            self.home / ".config" / "auto-rewards" / "config.toml"
        )

    def write_config(self, content):
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config_path.write_text(content, encoding="utf-8")

    def test_defaults_when_config_is_absent(self):
        options = main.parse_arguments([], self.environment)

        self.assertEqual(options.searches, 15)
        self.assertEqual(options.delay, 7)
        self.assertIsNone(options.config_path)

    def test_cli_options(self):
        options = main.parse_arguments(
            ["-n", "3", "--delay", "2.5", "--dry-run", "--verbose"],
            self.environment,
        )

        self.assertEqual(options.searches, 3)
        self.assertEqual(options.delay, 2.5)
        self.assertTrue(options.dry_run)
        self.assertTrue(options.verbose)

    def test_invalid_cli_values(self):
        for arguments in (
            ["--searches", "0"],
            ["--searches", "text"],
            ["--delay", "-1"],
            ["--delay", "text"],
        ):
            with self.subTest(arguments=arguments), contextlib.redirect_stderr(
                io.StringIO()
            ):
                with self.assertRaises(SystemExit) as error:
                    main.parse_arguments(arguments, self.environment)
                self.assertEqual(error.exception.code, 2)

    def test_valid_config(self):
        self.write_config("searches = 9\ndelay = 1.5\n")

        options = main.parse_arguments([], self.environment)

        self.assertEqual(options.searches, 9)
        self.assertEqual(options.delay, 1.5)
        self.assertEqual(options.config_path, self.config_path)

    def test_cli_overrides_config(self):
        self.write_config("searches = 9\ndelay = 1.5\n")

        options = main.parse_arguments(
            ["--searches", "4", "--delay", "3"], self.environment
        )

        self.assertEqual(options.searches, 4)
        self.assertEqual(options.delay, 3.0)

    def test_invalid_toml(self):
        self.write_config("searches = [\n")

        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as error:
                main.parse_arguments([], self.environment)

        self.assertEqual(error.exception.code, 2)

    def test_invalid_config_values(self):
        for content in (
            "searches = 0\n",
            'searches = "15"\n',
            "delay = -1\n",
            'delay = "7"\n',
        ):
            with self.subTest(content=content):
                self.write_config(content)
                with contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit) as error:
                        main.parse_arguments([], self.environment)
                self.assertEqual(error.exception.code, 2)


class SearchTests(unittest.TestCase):
    def test_generate_search_term_preserves_current_generator(self):
        with patch("main.randrange", side_effect=range(9)):
            term = main.generate_search_term()

        self.assertEqual(term, ascii_letters[:9])
        self.assertEqual(len(term), 9)

    def test_build_search_url_escapes_query(self):
        query = "café & python/wayland?"

        url = main.build_search_url(query)
        parsed_url = urlparse(url)

        self.assertEqual(parsed_url.scheme, "https")
        self.assertEqual(parsed_url.netloc, "www.bing.com")
        self.assertEqual(parsed_url.path, "/search")
        self.assertEqual(
            parse_qs(parsed_url.query), {"q": [query], "form": ["TSASDS"]}
        )


class EnvironmentTests(unittest.TestCase):
    def test_detect_session_and_hyprland(self):
        environment = {
            "XDG_SESSION_TYPE": "Wayland",
            "HYPRLAND_INSTANCE_SIGNATURE": "instance",
        }

        self.assertEqual(main.detect_session(environment), "wayland")
        self.assertEqual(main.detect_compositor(environment), "Hyprland")

    def test_find_browser_uses_browser_environment_variable(self):
        environment = {"BROWSER": "custom-browser --new-tab %s"}

        with patch("main.shutil.which", return_value="/usr/bin/custom-browser"):
            browser = main.find_browser(environment)

        self.assertEqual(browser, "custom-browser --new-tab %s")

    def test_check_environment_returns_detected_values(self):
        with patch("main.detect_session", return_value="wayland"), patch(
            "main.detect_compositor", return_value="Hyprland"
        ), patch("main.find_browser", return_value="firefox"), patch(
            "main.shutil.which", return_value="/usr/bin/ydotool"
        ):
            environment_info = main.check_environment({})

        self.assertEqual(
            environment_info,
            {
                "browser": "firefox",
                "session": "wayland",
                "compositor": "Hyprland",
            },
        )

    def test_check_environment_rejects_missing_dependencies(self):
        error_output = io.StringIO()
        with patch("main.detect_session", return_value="wayland"), patch(
            "main.detect_compositor", return_value=None
        ), patch("main.find_browser", return_value=None), patch(
            "main.shutil.which", return_value=None
        ), contextlib.redirect_stderr(error_output):
            environment_info = main.check_environment({})

        self.assertIsNone(environment_info)
        self.assertIn("ydotool não encontrado", error_output.getvalue())
        self.assertIn("Nenhum navegador", error_output.getvalue())


class ExecutionTests(unittest.TestCase):
    environment_info = {
        "browser": None,
        "session": "wayland",
        "compositor": None,
    }

    def test_dry_run_has_no_external_effects(self):
        options = argparse.Namespace(
            searches=2,
            delay=7,
            dry_run=True,
            verbose=False,
            config_path=None,
        )
        output = io.StringIO()

        with patch("main.parse_arguments", return_value=options), patch(
            "main.check_environment", return_value=self.environment_info
        ) as check_environment, patch(
            "main.generate_search_term", return_value="AbCdEfGhi"
        ), patch("main.webbrowser.open") as open_browser, patch(
            "main.subprocess.run"
        ) as run_command, patch("main.sleep") as wait, contextlib.redirect_stdout(
            output
        ):
            result = main.main([])

        self.assertEqual(result, 0)
        check_environment.assert_called_once_with(require_dependencies=False)
        open_browser.assert_not_called()
        run_command.assert_not_called()
        wait.assert_not_called()
        self.assertIn("[dry-run] Abriria no navegador", output.getvalue())

    def test_environment_error_blocks_execution(self):
        options = argparse.Namespace(
            searches=1,
            delay=7,
            dry_run=False,
            verbose=False,
            config_path=None,
        )

        with patch("main.parse_arguments", return_value=options), patch(
            "main.check_environment", return_value=None
        ), patch("main.open_tabs") as open_tabs:
            result = main.main([])

        self.assertEqual(result, 1)
        open_tabs.assert_not_called()


if __name__ == "__main__":
    unittest.main()
