import json
import logging
import os
import re
import shutil
import unittest
from http.client import HTTPException

from app.logic.converter import OpenAPIToKrakenD


class TestConverter(unittest.TestCase):
    """
    Test the converter features
    """

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

    def test_name(self):
        """
        Test if the name in KrakenD.json is the same as the name provided
        """
        converter = OpenAPIToKrakenD(logging_mode=logging.ERROR,
                                     input_folder_path="tests/mock_data/full/",
                                     output_folder_path="tests/output",
                                     name="Test gateway")
        converter.convert()

        with open("tests/output/config/krakend.json", "r", encoding="utf-8") as config_file:
            config = config_file.read()

        config_data = config.replace("[{{template \"Endpoints\".service}}]",
                                     "\"[{{template \\\"Endpoints\\\".service}}]\"")

        config_json = json.loads(config_data)

        self.assertEqual(config_json["name"], "Test gateway")

    def test_stackdriver(self):
        """
        Test if the stackdriver field has been added and the stackdriver project id is the same as the one provided
        """
        converter = OpenAPIToKrakenD(logging_mode=logging.ERROR,
                                     input_folder_path="tests/mock_data/full/",
                                     output_folder_path="tests/output",
                                     name="Test gateway",
                                     stackdriver_project_id="gateway-stackdriver")
        converter.convert()

        with open("tests/output/config/krakend.json", "r", encoding="utf-8") as config_file:
            config = config_file.read()

        config_data = config.replace("[{{template \"Endpoints\".service}}]",
                                     "\"[{{template \\\"Endpoints\\\".service}}]\"")

        config_json = json.loads(config_data)

        self.assertEqual(config_json["extra_config"]["telemetry/opencensus"]["exporters"]["stackdriver"]["project_id"],
                         "gateway-stackdriver")

    def test_no_server(self):
        """
        Test if a KeyError is thrown if there is no server field in the OpenAPI spec
        """
        converter = OpenAPIToKrakenD(logging_mode=logging.ERROR,
                                     input_folder_path="tests/mock_data/no_server/",
                                     output_folder_path="tests/output",
                                     name="Test gateway")

        with self.assertRaises(KeyError):
            converter.convert()

    def test_invalid_server(self):
        """
        Test if an HTTPException is thrown if there is no valid server in the server field
        """
        converter = OpenAPIToKrakenD(logging_mode=logging.ERROR,
                                     input_folder_path="tests/mock_data/invalid_server/",
                                     output_folder_path="tests/output",
                                     name="Test gateway")

        with self.assertRaises(HTTPException):
            converter.convert()

    def test_security_header_on_endpoint(self):
        """
        Test if a specific endpoint contains the Authorization header
        """
        converter = OpenAPIToKrakenD(logging_mode=logging.ERROR,
                                     input_folder_path="tests/mock_data/full/",
                                     output_folder_path="tests/output",
                                     name="Test gateway")
        converter.convert()

        with open("tests/output/config/templates/OPENAPI.tmpl", "r", encoding="utf-8") as template_file:
            template = template_file.read()

        # Remove templating
        config_data = re.sub(r"^({{(.*?)}})", "", template, flags=re.M).strip()

        # Split objects
        endpoints_data = re.split(r"(?<=}),", config_data, flags=re.M)

        endpoints = []

        # Load JSON to array
        for endpoint in endpoints_data:
            endpoints.append(json.loads(endpoint))

        # /bet/{season}/{race} (auth required)
        self.assertTrue("Authorization" in endpoints[3]["input_headers"])

        # /users (no auth required)
        self.assertFalse("Authorization" in endpoints[0]["input_headers"])

    def test_header_parameter_on_endpoint(self):
        """
        Test if a specific endpoint contains the header from the parameters
        """
        converter = OpenAPIToKrakenD(logging_mode=logging.ERROR,
                                     input_folder_path="tests/mock_data/headers/",
                                     output_folder_path="tests/output",
                                     name="Test gateway")
        converter.convert()

        with open("tests/output/config/templates/OPENAPI.tmpl", "r", encoding="utf-8") as template_file:
            template = template_file.read()

        # Remove templating
        config_data = re.sub(r"^({{(.*?)}})", "", template, flags=re.M).strip()

        # Split objects
        endpoints_data = re.split(r"(?<=}),", config_data, flags=re.M)

        endpoints = []

        # Load JSON to array
        for endpoint in endpoints_data:
            endpoints.append(json.loads(endpoint))

        # /users/{user_id} (user_id as header parameter)
        self.assertTrue("user_id" in endpoints[2]["input_headers"])

    def test_no_version_define(self):
        """
        Test the path if there is no version defined
        """
        converter = OpenAPIToKrakenD(logging_mode=logging.ERROR,
                                     input_folder_path="tests/mock_data/full/",
                                     output_folder_path="tests/output",
                                     name="Test gateway")
        converter.convert()

        with open("tests/output/config/templates/OPENAPI.tmpl", "r", encoding="utf-8") as template_file:
            template = template_file.read()

        # Separate path templating
        config_data = re.findall(r"^({{\$prefix := (.*?)}})", template, flags=re.M)

        # Find path value
        endpoints_data = re.findall(r"\"(.*?)\"", str(config_data[0]))

        # Assign path value
        path = endpoints_data[0]

        self.assertEqual(path, "/openapi")

    def test_v1_version_define(self):
        """
        Test the path if there is a version (v1) defined
        """
        converter = OpenAPIToKrakenD(logging_mode=logging.ERROR,
                                     input_folder_path="tests/mock_data/version/",
                                     output_folder_path="tests/output",
                                     name="Test gateway")
        converter.convert()

        with open("tests/output/config/templates/OPENAPI.V1.tmpl", "r", encoding="utf-8") as template_file:
            template = template_file.read()

        # Separate path templating
        config_data = re.findall(r"^({{\$prefix := (.*?)}})", template, flags=re.M)

        # Find path value
        endpoints_data = re.findall(r"\"(.*?)\"", str(config_data[0]))

        # Assign path value
        path = endpoints_data[0]

        self.assertEqual(path, "/openapi/v1")

    def test_service(self):
        """
        Test settings/service.json
        """
        converter = OpenAPIToKrakenD(logging_mode=logging.ERROR,
                                     input_folder_path="tests/mock_data/full/",
                                     output_folder_path="tests/output",
                                     name="Test gateway")
        converter.convert()

        with open("tests/output/config/settings/service.json", "r", encoding="utf-8") as service_file:
            service_json = json.load(service_file)

        self.assertEqual(service_json["OPENAPI"], "https://f1-betting.app")
