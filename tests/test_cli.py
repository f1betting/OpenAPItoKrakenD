import json
import os
import shutil
import unittest

from typer.testing import CliRunner

from app.main import app


class TestCLI(unittest.TestCase):
    """
    Test the CLI
    """

    @classmethod
    def setUpClass(cls):
        """
        Initialize CLI runner
        """
        cls.runner = CliRunner()

    @classmethod
    def setUp(cls):
        """
        Create the output folder if it doesn't exist
        """
        if not os.path.exists(os.path.join("tests/output")):
            os.mkdir(os.path.join("tests/output"))

    @classmethod
    def tearDown(cls):
        """
        Delete the output folder if it exists
        """
        if os.path.exists(os.path.join("tests/output")):
            shutil.rmtree(os.path.join("tests/output"))

    def test_cli(self):
        """
        Test if the name in KrakenD.json is the same as the name provided
        """
        self.runner.invoke(app, ["tests/mock_data/full", "tests/output", "--name", "Test gateway"])

        with open("tests/output/config/krakend.json", "r", encoding="utf-8") as config_file:
            config = config_file.read()

        config_data = config.replace("[{{template \"Endpoints\".service}}]",
                                     "\"[{{template \\\"Endpoints\\\".service}}]\"")

        config_json = json.loads(config_data)

        self.assertEqual(config_json["name"], "Test gateway")
