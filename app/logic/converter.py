from __future__ import annotations

import glob
import json
import os
import re
import shutil

from app.utils.customlogger import CustomLogger
from app.utils.errors import InvalidOpenAPIError, OpenAPIFileNotFoundError


# Disable pylint too-few-public-methods due to the converter only requiring one public method to work.
# pylint: disable=too-few-public-methods
class OpenAPIToKrakenD:
    """
    Batch-convert OpenApi 3 files to a flexible KrakenD configuration
    """

    # Disable pylint too-many-instance-attributes due to required attributes for the converter to work.
    # pylint: disable=too-many-instance-attributes
    # Disable pylint too-many-arguments due to required attributes for the converter to work.
    # pylint: disable=too-many-arguments
    def __init__(self, logging_mode: int, input_folder_path: str, output_folder_path: str, no_versioning: bool = False,
                 env: str = None):
        """
        Initialize converter

        Arguments:
        logging_mode -- The logging mode used. Use the logging mode from the python logging library
        input_folder_path -- The path of the input folder that contains the OpenAPI specifications
        output_folder_path -- The path of the output folder where the configuration gets generated
        env -- Set the backend target URL to the description of the server object inside the OpenAPI specification
               (picks the first entry if not specified)
        no_versioning -- Disable automatic versioning based on the OpenAPI specification
        """
        self.logger = CustomLogger(logging_mode)

        self.paths: list = glob.glob(f"{input_folder_path}/*.json")
        self.config_paths: list = glob.glob(f"{input_folder_path}/config/*")
        self.files: list = []
        self.config_files: list = []
        self.input_folder_path: str = input_folder_path
        self.output_folder_path: str = output_folder_path

        self.env = env

        self.versioning: bool = not no_versioning

    def convert(self) -> OpenAPIToKrakenD:
        """
        Convert OpenAPI files to a flexible KrakenD configuration.
        """
        for path in self.paths:
            self.files.append(os.path.basename(path))

        if len(self.paths) <= 0:
            raise OpenAPIFileNotFoundError(f"No files found in '{self.input_folder_path}'")

        if len(self.config_paths) > 0:
            self.logger.info("Using custom configuration files")
            for config_path in self.config_paths:
                self.config_files.append(os.path.basename(config_path))

        self.logger.info("Verifying OpenAPI files")
        for file in self.files:
            self.logger.info(f"Verifying {file}")
            self.__verify_openapi(file)
            self.logger.info(f"Verified {file}")
        self.logger.info("Verified OpenAPI files")

        self.logger.info("Creating folders")
        self.__create_folders()
        self.logger.info("Created folder")

        self.logger.info("Writing endpoint files")
        for file in self.files:
            self.logger.info(f"Writing {file[:-5]}.tmpl")
            self.__format_endpoints(file, file[:-5].upper())
            self.logger.info(f"Finished writing {file[:-5]}.tmpl")
        self.logger.info("Finished writing endpoint files")

        self.logger.info("Writing templates/Endpoints.tmpl")
        self.__write_endpoints_template()
        self.logger.info("Finished writing templates/Endpoints.tmpl")

        self.logger.info("Writing settings/service.json")
        self.__write_service()
        self.logger.info("Finished writing settings/service.json")

        self.logger.info("Writing krakend.json")
        self.__write_krakend_json()
        self.logger.info("Finished writing krakend.json")

        self.logger.info("Writing Dockerfile")
        self.__write_dockerfile()
        self.logger.info("Finished writing Dockerfile")

        return self

    def __new_endpoint(self, endpoint: str, method: str, headers: list):
        """
        Create a KrakenD formatted endpoint.
        """
        self.logger.debug("Creating headers")
        headers.append("Content-Type")

        self.logger.debug("Creating endpoint")
        formatted_endpoint = {
            "endpoint": "{{ $prefix }}" + endpoint,
            "method": method,
            "backend": [
                {
                    "url_pattern": endpoint,
                    "method": method,
                    "host": [
                        "{{ $host }}"
                    ],
                }
            ],
            "input_headers": headers
        }

        self.logger.debug("Adding endpoint configuration")
        if "endpoint.json" in self.config_files:
            self.logger.debug("Using custom endpoint configuration")
            with open(f"{self.input_folder_path}/config/endpoint.json", "r", encoding="utf-8") as endpoint_config_file:
                endpoint_config = json.load(endpoint_config_file)
        else:
            self.logger.debug("Using default endpoint configuration")
            with open("app/config/endpoint.json", "r", encoding="utf-8") as endpoint_config_file:
                endpoint_config = json.load(endpoint_config_file)

        for key in endpoint_config:
            self.logger.debug(f"Adding {key}")
            formatted_endpoint[key] = endpoint_config[key]
        self.logger.debug("Added endpoint configuration")

        self.logger.debug("Adding backend configuration")
        if "backend.json" in self.config_files:
            self.logger.debug("Using custom backend configuration")
            with open(f"{self.input_folder_path}/config/backend.json", "r", encoding="utf-8") as backend_config_file:
                backend_config = json.load(backend_config_file)
        else:
            self.logger.debug("Using default backend configuration")
            with open("app/config/backend.json", "r", encoding="utf-8") as backend_config_file:
                backend_config = json.load(backend_config_file)

        for key in backend_config:
            formatted_endpoint["backend"][0][key] = backend_config[key]
        self.logger.debug("Added backend configuration")

        return formatted_endpoint

    def __get_security_headers(self, security_scheme):
        """
        Get the correct security headers for the security scheme.
        """
        match security_scheme["type"]:
            case "http":
                self.logger.debug("HTTP authentication schema found")

                self.logger.debug("Setting security header to 'Authorization'")
                return "Authorization"
            case "apiKey" if security_scheme["in"] == "header":
                self.logger.debug("API Key Header authentication schema found")

                self.logger.debug(f"Setting security header to '{security_scheme['name']}'")
                return security_scheme["name"]
            case "oauth2" if "implicit" in security_scheme["flows"]:
                self.logger.debug("OAuth2 Implicit Authentication schema found")

                self.logger.debug("Setting security header to 'Authorization'")
                return "Authorization"
            case _:
                return None

    def __get_api_define_prefix(self, filename: str, data: dict):
        """
        Get the API define and prefix based on the versioning system used.
        """
        if ".V" in filename and not self.versioning:
            api_prefix = filename.replace(".V", "/V").lower()
            api_define = filename.replace(".V", "V")

        elif ".V" in filename and self.versioning:
            version = "V" + data["info"]["version"][0:1]
            api_name = re.sub(r"\.V\d", "", filename)

            api_prefix = (api_name + "/" + version).lower()
            api_define = api_name + version

        elif self.versioning:
            api_prefix = str(filename + "/V" + data["info"]["version"][0:1]).lower()
            api_define = filename + "V" + data["info"]["version"][0:1]

        else:
            api_prefix = filename.lower()
            api_define = filename

        return [api_prefix, api_define]

    def __get_name_with_version(self, filename: str, data: dict):
        """
        Get the api name based on the versioning system used.
        """
        name = filename.upper()[:-5]

        if ".V" in name and not self.versioning:
            return name.replace(".V", "V")

        if ".V" in name and self.versioning:
            version = "V" + data["info"]["version"][0:1]
            api_name = re.sub(r"\.V\d", "", name)

            return api_name + version

        if self.versioning:
            return name + "V" + data["info"]["version"][0:1]

        return name

    def __verify_openapi(self, file):
        """
        Verify if the OpenAPI files contain all the required fields.

        If the verification fails an InvalidOpenAPIError is raised.
        """
        with open(f"{self.input_folder_path}/{file}", "r", encoding="utf-8") as openapi_file:
            data: dict = json.load(openapi_file)

            self.logger.debug("Verifying server")

            if "servers" in data.keys() and len(data["servers"]) >= 1 and "url" in data["servers"][0]:
                server = data["servers"][0]["url"]
                if "http://" not in server and "https://" not in server:  # NOSONAR
                    raise InvalidOpenAPIError(f"{file}: invalid server")
            else:
                raise InvalidOpenAPIError(f"{file}: no servers defined")

            self.logger.debug("Verifying version")

            if "info" not in data.keys() or "version" not in data["info"].keys():
                raise InvalidOpenAPIError("No version found")

    def __write_dockerfile(self):
        """
        Copy the dockerfile to the output folder.
        """
        if "Dockerfile" in self.config_files:
            self.logger.debug("Using custom Dockerfile")
            shutil.copy(f"{self.input_folder_path}/config/Dockerfile", f"{self.output_folder_path}")
        else:
            self.logger.debug("Using default Dockerfile")
            shutil.copy("app/config/Dockerfile", f"{self.output_folder_path}")

    def __write_endpoints_template(self):
        """
        Write the endpoints file which links the API definitions and services together.
        """
        service = "{{$service := .}}\n\n"
        define = "{{define \"Endpoints\"}}\n\n"
        end = "\n\n{{end}}"

        with open(f"{self.output_folder_path}/config/templates/Endpoints.tmpl", "w+",
                  encoding="utf-8") as endpoints_file:
            self.logger.info("Formatting endpoints file")

            self.logger.debug("Writing template")
            endpoints_file.write(define + service)

            for file in self.files:
                self.logger.debug(f"Loaded {file}")

                with open(f"{self.input_folder_path}/{file}", "r", encoding="utf-8") as json_file:
                    data = json.load(json_file)

                name = self.__get_name_with_version(file, data)

                # https://docs.python.org/3/library/string.html#format-string-syntax
                data = f'{{{{template "{name}" $service.{name}}}}}\n'

                self.logger.debug(f"Writing service {file[:-5].upper()}")
                endpoints_file.write(data)

            self.logger.debug("Writing end template")
            endpoints_file.write(end)

            endpoints_file.seek(0)

            self.logger.debug("Reading file data")
            file_data = endpoints_file.read()

            self.logger.debug("Converting file data to JSON")
            file_data = file_data.replace("}}\n{{", "}},\n{{")

            endpoints_file.seek(0)

            self.logger.info("Writing file")
            endpoints_file.write(file_data)

    def __get_target_backend(self, data, service_name, filename):
        """
        Get the target backend for the API based on the environment chosen
        """
        service = None

        # If an environment is specified, attempt to search for server
        if self.env:
            self.logger.debug(f"[{filename}] Custom environment provided")
            for server in data["servers"]:
                if "description" not in server:
                    self.logger.debug(f"[{filename}] Description not found, trying next")
                    continue

                if server["description"] == self.env:
                    self.logger.debug(f"[{filename}] Description found")
                    service = {service_name: server["url"]}
                    break

        # If no environment is specified or if no server is found, use first entry in server list
        if service is None:
            if self.env:
                self.logger.error(
                    f"[{filename}] Server environment `{self.env}` unknown. Using {data['servers'][0]['url']}")

            self.logger.debug("Custom environment not provided, using first entry in server list")
            service = {service_name: data["servers"][0]["url"]}

        return service

    def __write_service(self):
        """
        Write the service.json file which contains all the urls to the services.
        """
        service_array = {}

        for filename in self.files:
            with open(f"{self.input_folder_path}/{filename}", "r", encoding="utf-8") as file:
                data = json.load(file)

            service_name = self.__get_name_with_version(filename, data)
            service = self.__get_target_backend(data, service_name, filename)

            service_array.update(service)

        with open(f"{self.output_folder_path}/config/settings/service.json", "w+", encoding="utf-8") as file:
            json.dump(service_array, file, indent=4)

    def __write_krakend_json(self):
        """
        Write the KrakenD configuration file.
        """
        self.logger.info("Generating config")
        krakend_config = {
            "endpoints": '[{{template "Endpoints".service}}]'
        }

        self.logger.debug("Adding configuration")
        if "krakend.json" in self.config_files:
            self.logger.debug("Using custom krakend configuration")
            with open(f"{self.input_folder_path}/config/krakend.json", "r", encoding="utf-8") as config_file:
                config = json.load(config_file)
        else:
            self.logger.debug("Using default krakend configuration")
            with open("app/config/krakend.json", "r", encoding="utf-8") as config_file:
                config = json.load(config_file)

        for key in config:
            self.logger.debug(f"Adding {key}")
            krakend_config[key] = config[key]
        self.logger.debug("Added configuration")

        self.logger.debug("Loading config")
        config_data = json.dumps(krakend_config, indent=4)

        self.logger.debug("Reformatting endpoints value")

        json_string = config_data.replace("\"[{{template \\\"Endpoints\\\".service}}]\"",
                                          "[{{template \"Endpoints\".service}}]")

        self.logger.debug("Reformatted endpoints value")

        self.logger.info("Config generated")

        with open(f"{self.output_folder_path}/config/krakend.json", "w+", encoding="utf-8") as config_file:
            self.logger.info("Writing file")
            config_file.write(json_string)
            self.logger.info("Finished writing file")

    # Disable pylint too-many-locals due to a high amount of variables required for this method to work.
    # pylint: disable=too-many-locals
    def __format_endpoints(self, file_input, file_output):
        """
        Convert all the endpoints to the KrakenD format

        KrakenD creates a separate endpoint object per route and method, unlike OpenAPI where a path can have multiple
        methods under the same parent object. Therefor there needs to be a nested for loop for all the methods inside
        the paths.
        """
        self.logger.info(f"Formatting endpoints for {file_input}")

        endpoints_list = []

        host = "{{$host := .}}\n"
        end = "\n\n\n{{end}}"

        output_path = f"{self.output_folder_path}/config/templates/{file_output}"

        with open(f"{self.input_folder_path}/{file_input}", "r+", encoding="utf-8") as openapi_file:
            self.logger.debug(f"Loaded {file_input}")
            data = json.load(openapi_file)

            api_prefix, api_define = self.__get_api_define_prefix(file_output, data)

            # https://docs.python.org/3/library/string.html#format-string-syntax
            define = f'{{{{define "{api_define}"}}}}\n\n'
            prefix = f'{{{{$prefix := "/{api_prefix}"}}}}\n\n'

            openapi_security_schemes = None

            if "components" in data and "securitySchemes" in data["components"]:
                self.logger.debug("Security schemes found in OpenAPI")
                openapi_security_schemes = data["components"]["securitySchemes"]

            # Loop over every path inside the OpenAPI spec
            for path in data["paths"]:
                self.logger.info(f"Starting conversion for {path}")

                # Loop over every method inside the OpenAPI spec
                for method in data["paths"][path]:
                    self.logger.info(f"Preparing conversion for {path}: {method}")

                    headers = self.__get_headers(data["paths"][path][method], openapi_security_schemes)

                    self.logger.info(f"Converting {path}: {method}")
                    krakend_endpoint = self.__new_endpoint(path, method.upper(), headers)
                    self.logger.info(f"Converted {path}: {method}")

                    self.logger.debug("Adding endpoint to list")
                    endpoints_list.append(krakend_endpoint)
                    self.logger.debug("Added endpoint to list")

        endpoints = endpoints_list

        with open(f"{output_path}.tmpl", "w+", encoding="utf-8") as file:
            self.logger.debug("Write start template")
            file.write(define + host + prefix)

            for endpoint in endpoints:
                self.logger.debug(f'Writing endpoint {endpoint["backend"][0]["url_pattern"]}')
                file.write(json.dumps(endpoint, indent=4))

            self.logger.debug("Writing end template")
            file.write(end)
            file.seek(0)

            self.logger.debug("Reading file")
            file_data = file.read()

            self.logger.info("Converting endpoints to valid JSON")
            file_data = file_data.replace("}{", "},\n{")
            file.seek(0)

            self.logger.info(f"Writing {output_path}.tmpl")
            file.write(file_data)

    def __get_headers(self, endpoint, security_schemes):
        """
        Get the headers for the endpoint from the parameters and authorization methods
        """
        headers = []

        if "security" in endpoint and endpoint["security"] is not None:
            self.logger.debug("Adding security headers")
            headers = self.__add_security_headers(endpoint, security_schemes)
            self.logger.debug("Added security headers")
        else:
            self.logger.debug("No authorization header required")

        if "parameters" in endpoint and endpoint["parameters"] is not None:
            for parameter in endpoint["parameters"]:
                if parameter["in"] == "header":
                    self.logger.debug(f'Adding {parameter["name"]} to headers')
                    headers.append(parameter["name"])
                    self.logger.debug(f'Added {parameter["name"]} to headers')
        else:
            self.logger.debug("No parameters found")

        return headers

    def __add_security_headers(self, endpoint, security_schemes):
        """
        Add the security headers
        """
        headers = []

        # Disable pylint unnecessary-comprehension due to a false positive. The pylint suggestion does NOT work.
        # pylint: disable=unnecessary-comprehension
        schemes = [list(item.keys())[0] for item in [scheme for scheme in endpoint["security"]]]

        for scheme in schemes:
            if scheme not in security_schemes:
                raise InvalidOpenAPIError(f"{scheme} does not exist in OpenAPI specification")

            self.logger.debug(f"Adding header for components.securitySchemes.{scheme}")
            header = self.__get_security_headers(security_schemes[scheme])
            if header in headers:
                raise InvalidOpenAPIError(f"Header '{header}' already exists")
            if header is None:
                raise InvalidOpenAPIError("Unsupported authorization method used")

            headers.append(header)

            self.logger.debug(f"Added header for components.securitySchemes.{scheme}")

        return headers

    def __create_folders(self):
        """
        Create the configuration folders
        """
        paths = ["config", "config/settings", "config/templates"]

        for folder in paths:
            if not os.path.exists(os.path.join(self.output_folder_path, folder)):
                os.mkdir(os.path.join(self.output_folder_path, folder))
