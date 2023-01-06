import json
import logging
import os
import re
import unittest

from app.logic.converter import OpenAPIToKrakenD
from app.utils.errors import InvalidOpenAPIError, OpenAPIFileNotFoundError
from tests.logic.test_setup_logic import delete_output_folder, create_output_folder


# pylint:disable=duplicate-code
# pylint:disable=too-many-public-methods

class TestConverter(unittest.TestCase):
    """
    Test the converter features
    """

    @classmethod
    def setUp(cls):
        """
        Create the output folder if it doesn't exist
        """
        create_output_folder()

    @classmethod
    def tearDown(cls):
        """
        Delete the output folder if it exists
        """
        delete_output_folder()

    def test_name(self):
        """
        Test if the name in KrakenD.json is equal to "Test gateway"
        """
        converter = OpenAPIToKrakenD(logging_mode=logging.ERROR,
                                     input_folder_path="tests/mock_data/full/",
                                     output_folder_path="tests/output")
        converter.convert()

        with open("tests/output/config/krakend.json", "r", encoding="utf-8") as config_file:
            config = config_file.read()

        config_data = config.replace("[{{template \"Endpoints\".service}}]",
                                     "\"[{{template \\\"Endpoints\\\".service}}]\"")

        config_json = json.loads(config_data)

        # Test if the name in KrakenD.json is equal to "Test gateway"
        self.assertEqual(config_json["name"], "Test gateway")

    def test_stackdriver(self):
        """
        Test if the stackdriver field has been added
        Test if the stackdriver project id is the same as the one provided
        """
        converter = OpenAPIToKrakenD(logging_mode=logging.ERROR,
                                     input_folder_path="tests/mock_data/stackdriver/",
                                     output_folder_path="tests/output")
        converter.convert()

        with open("tests/output/config/krakend.json", "r", encoding="utf-8") as config_file:
            config = config_file.read()

        config_data = config.replace("[{{template \"Endpoints\".service}}]",
                                     "\"[{{template \\\"Endpoints\\\".service}}]\"")

        config_json = json.loads(config_data)

        # Test if the stackdriver field has been added
        self.assertTrue("stackdriver" in config_json["extra_config"]["telemetry/opencensus"]["exporters"])

        # Test if the stackdriver project id is the same as the one provided
        self.assertEqual(config_json["extra_config"]["telemetry/opencensus"]["exporters"]["stackdriver"]["project_id"],
                         "gateway-stackdriver")

    def test_no_server(self):
        """
        Test if a InvalidOpenAPIError is thrown if there is no server field in the OpenAPI spec
        """
        converter = OpenAPIToKrakenD(logging_mode=logging.ERROR,
                                     input_folder_path="tests/mock_data/no_server/",
                                     output_folder_path="tests/output")

        # Test if a KeyError is thrown if there is no server field in the OpenAPI spec
        with self.assertRaises(InvalidOpenAPIError):
            converter.convert()

    def test_no_info_field(self):
        """
        Test if a InvalidOpenAPIError is thrown if there is no info field in the OpenAPI spec
        """
        converter = OpenAPIToKrakenD(logging_mode=logging.ERROR,
                                     input_folder_path="tests/mock_data/no_info/",
                                     output_folder_path="tests/output")

        # Test if a InvalidOpenAPIError is thrown if there is no info field in the OpenAPI spec
        with self.assertRaises(InvalidOpenAPIError):
            converter.convert()

    def test_no_version_field(self):
        """
        Test if a InvalidOpenAPIError is thrown if there is no version field in the OpenAPI spec
        """
        converter = OpenAPIToKrakenD(logging_mode=logging.ERROR,
                                     input_folder_path="tests/mock_data/no_version/",
                                     output_folder_path="tests/output")

        # Test if a InvalidOpenAPIError is thrown if there is no version field in the OpenAPI spec
        with self.assertRaises(InvalidOpenAPIError):
            converter.convert()

    def test_invalid_server(self):
        """
        Test if an InvalidOpenAPIError is thrown if there is no valid server in the server field
        """
        converter = OpenAPIToKrakenD(logging_mode=logging.ERROR,
                                     input_folder_path="tests/mock_data/invalid_server/",
                                     output_folder_path="tests/output")

        # Test if an InvalidOpenAPIError is thrown if there is no valid server in the server field
        with self.assertRaises(InvalidOpenAPIError):
            converter.convert()

    def test_empty_folder(self):
        """
        Test if a folder with no JSON files raises a OpenAPIFileNotFoundError
        """
        converter = OpenAPIToKrakenD(logging_mode=logging.ERROR,
                                     input_folder_path="tests/mock_data/empty_folder/",
                                     output_folder_path="tests/output")

        # Test if a folder with no JSON files raises a OpenAPIFileNotFoundError
        with self.assertRaises(OpenAPIFileNotFoundError):
            converter.convert()

    def test_http_bearer_security_header_on_endpoint(self):
        """
        Test if /bet/{season}/{race} contains the Authorization header
        Test if /users does not contain the Authorization header
        """
        converter = OpenAPIToKrakenD(logging_mode=logging.ERROR,
                                     input_folder_path="tests/mock_data/full/",
                                     output_folder_path="tests/output")
        converter.convert()

        with open("tests/output/config/templates/OPENAPI.tmpl", "r", encoding="utf-8") as template_file:
            template = template_file.read()

        # Remove templating
        config_data = re.sub(r"^({{(.*?)}})", "", template, flags=re.M).strip()

        # Split objects
        # "(?<=}),\n" selects all the commas (",") after a closing curly bracket ("}") that prepend a newline ("\n")
        # "^(?!\s)" matches all the spaces after the newline and removes them from the match
        endpoints_data = re.split(r"(?<=}),\n^(?!\s)", config_data, flags=re.M)

        endpoints = []

        # Load JSON to array
        for endpoint in endpoints_data:
            endpoints.append(json.loads(endpoint))

        # Test if /bet/{season}/{race} contains the Authorization header
        self.assertTrue("Authorization" in endpoints[3]["input_headers"])

        # Test if /users does not contain the Authorization header
        self.assertFalse("Authorization" in endpoints[0]["input_headers"])

    def test_http_basic_security_header_on_endpoint(self):
        """
        Test if /bet/{season}/{race} contains the Authorization header
        Test if /users does not contain the Authorization header
        """
        converter = OpenAPIToKrakenD(logging_mode=logging.ERROR,
                                     input_folder_path="tests/mock_data/http_basic/",
                                     output_folder_path="tests/output")
        converter.convert()

        with open("tests/output/config/templates/OPENAPI.tmpl", "r", encoding="utf-8") as template_file:
            template = template_file.read()

        # Remove templating
        config_data = re.sub(r"^({{(.*?)}})", "", template, flags=re.M).strip()

        # Split objects
        # "(?<=}),\n" selects all the commas (",") after a closing curly bracket ("}") that prepend a newline ("\n")
        # "^(?!\s)" matches all the spaces after the newline and removes them from the match
        endpoints_data = re.split(r"(?<=}),\n^(?!\s)", config_data, flags=re.M)

        endpoints = []

        # Load JSON to array
        for endpoint in endpoints_data:
            endpoints.append(json.loads(endpoint))

        # Test if /bet/{season}/{race} contains the Authorization header
        self.assertTrue("Authorization" in endpoints[3]["input_headers"])

        # Test if /users does not contain the Authorization header
        self.assertFalse("Authorization" in endpoints[0]["input_headers"])

    def test_oauth2_security_header_on_endpoint(self):
        """
        Test if /bet/{season}/{race} contains the Authorization header
        Test if /users does not contain the Authorization header
        """
        converter = OpenAPIToKrakenD(logging_mode=logging.ERROR,
                                     input_folder_path="tests/mock_data/oauth2/",
                                     output_folder_path="tests/output")
        converter.convert()

        with open("tests/output/config/templates/OPENAPI.tmpl", "r", encoding="utf-8") as template_file:
            template = template_file.read()

        # Remove templating
        config_data = re.sub(r"^({{(.*?)}})", "", template, flags=re.M).strip()

        # Split objects
        # "(?<=}),\n" selects all the commas (",") after a closing curly bracket ("}") that prepend a newline ("\n")
        # "^(?!\s)" matches all the spaces after the newline and removes them from the match
        endpoints_data = re.split(r"(?<=}),\n^(?!\s)", config_data, flags=re.M)

        endpoints = []

        # Load JSON to array
        for endpoint in endpoints_data:
            endpoints.append(json.loads(endpoint))

        # Test if /bet/{season}/{race} contains the Authorization header
        self.assertTrue("Authorization" in endpoints[3]["input_headers"])

        # Test if /users does not contain the Authorization header
        self.assertFalse("Authorization" in endpoints[0]["input_headers"])

    def test_oauth2_not_implicit_security_header_on_endpoint(self):
        """
        Test if an InvalidOpenAPIError is being raised when an unsupported authorization schema is used
        """
        converter = OpenAPIToKrakenD(logging_mode=logging.ERROR,
                                     input_folder_path="tests/mock_data/oauth2_not_implicit/",
                                     output_folder_path="tests/output")
        with self.assertRaises(InvalidOpenAPIError):
            converter.convert()

    def test_no_security_headers(self):
        """
        Test if /bet/{season}/{race} does not contain the Authorization header
        (Security schemes do not exist in the entire spec)
        """
        converter = OpenAPIToKrakenD(logging_mode=logging.ERROR,
                                     input_folder_path="tests/mock_data/no_security_schemes/",
                                     output_folder_path="tests/output")
        converter.convert()

        with open("tests/output/config/templates/OPENAPI.tmpl", "r", encoding="utf-8") as template_file:
            template = template_file.read()

        # Remove templating
        config_data = re.sub(r"^({{(.*?)}})", "", template, flags=re.M).strip()

        # Split objects
        # "(?<=}),\n" selects all the commas (",") after a closing curly bracket ("}") that prepend a newline ("\n")
        # "^(?!\s)" matches all the spaces after the newline and removes them from the match
        endpoints_data = re.split(r"(?<=}),\n^(?!\s)", config_data, flags=re.M)

        endpoints = []

        # Load JSON to array
        for endpoint in endpoints_data:
            endpoints.append(json.loads(endpoint))

        # Test if /bet/{season}/{race} does not contain the Authorization header
        self.assertFalse("Authorization" in endpoints[3]["input_headers"])

    def test_wrong_security_headers(self):
        """
        Test if an InvalidOpenAPIError is being raised when the security scheme is named different from the one in
        the header
        """
        converter = OpenAPIToKrakenD(logging_mode=logging.ERROR,
                                     input_folder_path="tests/mock_data/wrong_security_scheme/",
                                     output_folder_path="tests/output")

        # Test if a folder with no JSON files raises a InvalidOpenAPIError
        with self.assertRaises(InvalidOpenAPIError):
            converter.convert()

    def test_duplicate_security_headers(self):
        """
        Test if an InvalidOpenAPIError is being raised when two security schemes have the same header on the same
        endpoint
        """
        converter = OpenAPIToKrakenD(logging_mode=logging.ERROR,
                                     input_folder_path="tests/mock_data/duplicate_security_headers/",
                                     output_folder_path="tests/output")

        # Test if a folder with no JSON files raises a InvalidOpenAPIError
        with self.assertRaises(InvalidOpenAPIError):
            converter.convert()

    def test_header_parameter_on_endpoint(self):
        """
        Test if /users/{user_id} contains user_id as a header parameter
        """
        converter = OpenAPIToKrakenD(logging_mode=logging.ERROR,
                                     input_folder_path="tests/mock_data/headers/",
                                     output_folder_path="tests/output")
        converter.convert()

        with open("tests/output/config/templates/OPENAPI.tmpl", "r", encoding="utf-8") as template_file:
            template = template_file.read()

        # Remove templating
        config_data = re.sub(r"^({{(.*?)}})", "", template, flags=re.M).strip()

        # Split objects
        # "(?<=}),\n" selects all the commas (",") after a closing curly bracket ("}") that prepend a newline ("\n")
        # "^(?!\s)" matches all the spaces after the newline and removes them from the match
        endpoints_data = re.split(r"(?<=}),\n^(?!\s)", config_data, flags=re.M)

        endpoints = []

        # Load JSON to array
        for endpoint in endpoints_data:
            endpoints.append(json.loads(endpoint))

        # Test if /users/{user_id} contains user_id as a header parameter
        self.assertTrue("user_id" in endpoints[2]["input_headers"])

    def test_no_version_defined(self):
        """
        Test if OPENAPI.tmpl has the correct prefix without a version
        Test if Endpoints.tmpl has the correct name and version
        """
        converter = OpenAPIToKrakenD(logging_mode=logging.ERROR,
                                     input_folder_path="tests/mock_data/full/",
                                     output_folder_path="tests/output",
                                     no_versioning=True)
        converter.convert()

        with open("tests/output/config/templates/OPENAPI.tmpl", "r", encoding="utf-8") as openapi_template_file:
            openapi_data = openapi_template_file.read()

        # Test if OPENAPI.tmpl has the correct prefix without a version
        self.assertTrue('{{$prefix := "/openapi"}}' in openapi_data)

        with open("tests/output/config/templates/Endpoints.tmpl", "r", encoding="utf-8") as endpoints_file:
            endpoints = endpoints_file.read()

        # Test if Endpoints.tmpl has the correct name and version
        self.assertTrue('{{template "OPENAPI" $service.OPENAPI}}' in endpoints)

    def test_auto_versioning(self):
        """
        Test if OPENAPI.tmpl has the correct prefix with version V1
        (no_versioning set to False, meaning it should pick V1 from the OpenAPI spec's Version field)
        """
        converter = OpenAPIToKrakenD(logging_mode=logging.ERROR,
                                     input_folder_path="tests/mock_data/full/",
                                     output_folder_path="tests/output",
                                     no_versioning=False)
        converter.convert()

        with open("tests/output/config/templates/OPENAPI.tmpl", "r", encoding="utf-8") as openapi_template_file:
            openapi_data = openapi_template_file.read()

        # Test if OPENAPI.tmpl has the correct prefix with version V1
        self.assertTrue('{{$prefix := "/openapi/v1"}}' in openapi_data)

        with open("tests/output/config/templates/Endpoints.tmpl", "r", encoding="utf-8") as endpoints_file:
            endpoints = endpoints_file.read()

        # Test if Endpoints.tmpl has the correct name and version
        self.assertTrue('{{template "OPENAPIV1" $service.OPENAPIV1}}' in endpoints)

    def test_auto_versioning_conflict_v1(self):
        """
        Test if OPENAPI.V1.tmpl has the correct prefix with version V1
        Test if Endpoints.tmpl has the correct name and version
        (no_versioning set to True, meaning it should pick V1 from the filename)
        """
        converter = OpenAPIToKrakenD(logging_mode=logging.ERROR,
                                     input_folder_path="tests/mock_data/version_conflict/",
                                     output_folder_path="tests/output",
                                     no_versioning=True)
        converter.convert()

        with open("tests/output/config/templates/OPENAPI.V1.tmpl", "r", encoding="utf-8") as openapi_template_file:
            openapi_data = openapi_template_file.read()

        # Test if OPENAPI.V1.tmpl has the correct prefix with version V1
        self.assertTrue('{{$prefix := "/openapi/v1"}}' in openapi_data)

        with open("tests/output/config/templates/Endpoints.tmpl", "r", encoding="utf-8") as endpoints_file:
            endpoints = endpoints_file.read()

        # Test if Endpoints.tmpl has the correct name and version
        self.assertTrue('{{template "OPENAPIV1" $service.OPENAPIV1}}' in endpoints)

    def test_auto_versioning_conflict_v2(self):
        """
        Test if OPENAPI.V1.tmpl has the correct prefix with version V2
        Test if Endpoints.tmpl has the correct name and version
        (no_versioning set to False, meaning it should pick V2 from the OpenAPI spec's Version field)
        """
        converter = OpenAPIToKrakenD(logging_mode=logging.ERROR,
                                     input_folder_path="tests/mock_data/version_conflict/",
                                     output_folder_path="tests/output",
                                     no_versioning=False)
        converter.convert()

        with open("tests/output/config/templates/OPENAPI.V1.tmpl", "r", encoding="utf-8") as openapi_template_file:
            openapi_data = openapi_template_file.read()

        # Test if OPENAPI.V1.tmpl has the correct prefix with version V2
        self.assertTrue('{{$prefix := "/openapi/v2"}}' in openapi_data)

        with open("tests/output/config/templates/Endpoints.tmpl", "r", encoding="utf-8") as endpoints_file:
            endpoints = endpoints_file.read()

        # Test if Endpoints.tmpl has the correct name and version
        self.assertTrue('{{template "OPENAPIV2" $service.OPENAPIV2}}' in endpoints)

    def test_service(self):
        """
        Test settings/service.json
        """
        converter = OpenAPIToKrakenD(logging_mode=logging.ERROR,
                                     input_folder_path="tests/mock_data/full/",
                                     output_folder_path="tests/output",
                                     no_versioning=True)
        converter.convert()

        with open("tests/output/config/settings/service.json", "r", encoding="utf-8") as service_file:
            service_json = json.load(service_file)

        self.assertEqual(service_json["OPENAPI"], "https://f1-betting.app")

    def test_dockerfile(self):
        """
        Test if the dockerfile is copied correctly
        Test if the dockerfile is the same as the default dockerfile
        """
        converter = OpenAPIToKrakenD(logging_mode=logging.ERROR,
                                     input_folder_path="tests/mock_data/full/",
                                     output_folder_path="tests/output")
        converter.convert()

        # Test if the dockerfile is copied correctly
        self.assertTrue(os.path.exists("tests/output/Dockerfile"))

        with open("tests/output/Dockerfile", "r", encoding="utf-8") as dockerfile:
            dockerfile_string = dockerfile.read()

        with open("tests/mock_data/default_dockerfile", "r", encoding="utf-8") as custom_dockerfile:
            dockerfile_template = custom_dockerfile.read()

        # Test if the dockerfile is the same as the default dockerfile
        self.assertEqual(dockerfile_string, dockerfile_template)

    def test_custom_dockerfile(self):
        """
        Test if the custom dockerfile is copied correctly
        Test if the custom dockerfile is the same as the one in the input folder
        """
        converter = OpenAPIToKrakenD(logging_mode=logging.ERROR,
                                     input_folder_path="tests/mock_data/custom_dockerfile/",
                                     output_folder_path="tests/output")
        converter.convert()

        # Test if the custom dockerfile is copied correctly
        self.assertTrue(os.path.exists("tests/output/Dockerfile"))

        with open("tests/output/Dockerfile", "r", encoding="utf-8") as dockerfile:
            dockerfile_string = dockerfile.read()

        with open("tests/mock_data/custom_dockerfile/config/Dockerfile", "r", encoding="utf-8") as custom_dockerfile:
            dockerfile_template = custom_dockerfile.read()

        # Test if the custom dockerfile is the same as the one in the input folder
        self.assertEqual(dockerfile_string, dockerfile_template)

    def test_folder_exists(self):
        """
        Test if KrakenD.json exists when the config folders already exist
        """
        os.mkdir(os.path.join("tests/output/config"))
        os.mkdir(os.path.join("tests/output/config/settings"))
        os.mkdir(os.path.join("tests/output/config/templates"))

        converter = OpenAPIToKrakenD(logging_mode=logging.ERROR,
                                     input_folder_path="tests/mock_data/full/",
                                     output_folder_path="tests/output")
        converter.convert()

        # Test if KrakenD.json exists when the config folders already exist
        self.assertTrue(os.path.exists("tests/output/config/krakend.json"))

    def test_debug_mode(self):
        """
        Test if the logger's logging level is being set properly
        """
        converter = OpenAPIToKrakenD(logging_mode=logging.DEBUG,
                                     input_folder_path="tests/mock_data/full/",
                                     output_folder_path="tests/output")

        self.assertEqual(converter.logger.get_logger().level, logging.DEBUG)
