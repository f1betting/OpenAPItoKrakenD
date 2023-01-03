from __future__ import annotations

import glob
import json
import logging
import os
import re
import shutil

from app.utils.errors import InvalidOpenAPIError, OpenAPIFileNotFoundError


class OpenAPIToKrakenD:
    """
    Batch-convert OpenApi 3 files to a flexible KrakenD configuration
    """

    # pylint: disable=too-many-arguments
    def __init__(self, logging_mode: int, input_folder_path: str, output_folder_path: str, no_versioning: bool = False):
        """
        Initialize converter
        """
        logging.basicConfig(level=logging_mode, format="[%(levelname)s]: %(message)s")  # NOSONAR

        self.paths: list = glob.glob(f"{input_folder_path}/*.json")
        self.config_paths: list = glob.glob(f"{input_folder_path}/config/*")
        self.files: list = []
        self.config_files: list = []
        self.input_folder_path: str = input_folder_path
        self.output_folder_path: str = output_folder_path

        self.versioning: bool = not no_versioning

    def convert(self) -> OpenAPIToKrakenD:
        """
        Convert the OpenAPI files to a flexible KrakenD configuration
        """
        for path in self.paths:
            self.files.append(os.path.basename(path))

        if len(self.paths) <= 0:
            raise OpenAPIFileNotFoundError(f"No files found in '{self.input_folder_path}'")

        if len(self.config_paths) > 0:
            logging.info("Using custom configuration files")
            for config_path in self.config_paths:
                self.config_files.append(os.path.basename(config_path))

        logging.info("Verifying OpenAPI files")
        for file in self.files:
            logging.info(f"Verifying {file}")
            self.__verify_openapi(file)
            logging.info(f"Verified {file}")
        logging.info("Verified OpenAPI files")

        logging.info("Creating folders")
        self.__create_folders()
        logging.info("Created folder")

        logging.info("Writing endpoint files")
        for file in self.files:
            logging.info(f"Writing {file[:-5]}.tmpl")
            self.__format_endpoints(file, file[:-5].upper())
            logging.info(f"Finished writing {file[:-5]}.tmpl")
        logging.info("Finished writing endpoint files")

        logging.info("Writing templates/Endpoints.tmpl")
        self.__write_endpoints_template()
        logging.info("Finished writing templates/Endpoints.tmpl")

        logging.info("Writing settings/service.json")
        self.__write_service()
        logging.info("Finished writing settings/service.json")

        logging.info("Writing krakend.json")
        self.__write_krakend_json()
        logging.info("Finished writing krakend.json")

        logging.info("Writing Dockerfile")
        self.__write_dockerfile()
        logging.info("Finished writing Dockerfile")

        return self

    def __new_endpoint(self, endpoint: str, method: str, headers: list):
        """
        Create a KrakenD endpoint
        """
        logging.debug("Creating headers")
        headers.append("Content-Type")

        logging.debug("Creating endpoint")
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

        logging.debug("Adding endpoint configuration")
        if "endpoint.json" in self.config_files:
            logging.debug("Using custom endpoint configuration")
            with open(f"{self.input_folder_path}/config/endpoint.json", "r", encoding="utf-8") as endpoint_config_file:
                endpoint_config = json.load(endpoint_config_file)
        else:
            logging.debug("Using default endpoint configuration")
            with open("app/config/endpoint.json", "r", encoding="utf-8") as endpoint_config_file:
                endpoint_config = json.load(endpoint_config_file)

        for key in endpoint_config:
            logging.debug(f"Adding {key}")
            formatted_endpoint[key] = endpoint_config[key]
        logging.debug("Added endpoint configuration")

        logging.debug("Adding backend configuration")
        if "backend.json" in self.config_files:
            logging.debug("Using custom backend configuration")
            with open(f"{self.input_folder_path}/config/backend.json", "r", encoding="utf-8") as backend_config_file:
                backend_config = json.load(backend_config_file)
        else:
            logging.debug("Using default backend configuration")
            with open("app/config/backend.json", "r", encoding="utf-8") as backend_config_file:
                backend_config = json.load(backend_config_file)

        for key in backend_config:
            formatted_endpoint["backend"][0][key] = backend_config[key]
        logging.debug("Added backend configuration")

        return formatted_endpoint

    @staticmethod
    def __get_security_headers(security_scheme):
        """
        Get the correct security headers for the security scheme
        """

        match security_scheme["type"]:
            case "http" if security_scheme["scheme"] == "bearer":
                logging.debug("Bearer Authentication schema found")

                logging.debug("Setting security header to 'Authorization'")
                return "Authorization"
            case "http" if security_scheme["scheme"] == "basic":
                logging.debug("Basic Authentication schema found")

                logging.debug("Setting security header to 'Authorization'")
                return "Authorization"
            case "apiKey" if security_scheme["in"] == "header":
                logging.debug("API Key Header authentication schema found")

                logging.debug(f"Setting security header to '{security_scheme['name']}'")
                return security_scheme["name"]
            case "oauth2" if "implicit" in security_scheme["flows"]:
                logging.debug("OAuth2 Implicit Authentication schema found")

                logging.debug("Setting security header to 'Authorization'")
                return "Authorization"
            case _:
                return None

    def __get_name_with_version(self, filename, data):
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
        Verify if the OpenAPI files contain all the required fields
        """

        with open(f"{self.input_folder_path}/{file}", "r", encoding="utf-8") as openapi_file:
            data: dict = json.load(openapi_file)

            logging.debug("Verifying server")

            if "servers" in data.keys() and len(data["servers"]) >= 1 and "url" in data["servers"][0]:
                server = data["servers"][0]["url"]
                if "http://" not in server and "https://" not in server:  # NOSONAR
                    raise InvalidOpenAPIError(f"{file}: invalid server")
            else:
                raise InvalidOpenAPIError(f"{file}: no servers defined")

            logging.debug("Verifying version")

            if "info" not in data.keys() or "version" not in data["info"].keys():
                raise InvalidOpenAPIError("No version found")

    def __write_dockerfile(self):
        """
        Copy the dockerfile
        """
        if "Dockerfile" in self.config_files:
            logging.debug("Using custom Dockerfile")
            shutil.copy(f"{self.input_folder_path}/config/Dockerfile", f"{self.output_folder_path}")
        else:
            logging.debug("Using default Dockerfile")
            shutil.copy("app/config/Dockerfile", f"{self.output_folder_path}")

    def __write_endpoints_template(self):
        """
        Write the endpoints files
        """
        service = "{{$service := .}}\n\n"
        define = "{{define \"Endpoints\"}}\n\n"
        end = "\n\n{{end}}"

        with open(f"{self.output_folder_path}/config/templates/Endpoints.tmpl", "w+",
                  encoding="utf-8") as endpoints_file:
            logging.info("Formatting endpoints file")

            logging.debug("Writing template")
            endpoints_file.write(define + service)

            for file in self.files:
                logging.debug(f"Loaded {file}")

                with open(f"{self.input_folder_path}/{file}", "r", encoding="utf-8") as json_file:
                    data = json.load(json_file)

                name = self.__get_name_with_version(file, data)

                # https://docs.python.org/3/library/string.html#format-string-syntax
                data = f'{{{{template "{name}" $service.{name}}}}}\n'

                logging.debug(f"Writing service {file[:-5].upper()}")
                endpoints_file.write(data)

            logging.debug("Writing end template")
            endpoints_file.write(end)

            endpoints_file.seek(0)

            logging.debug("Reading file data")
            file_data = endpoints_file.read()

            logging.debug("Converting file data to JSON")
            file_data = file_data.replace("}}\n{{", "}},\n{{")

            endpoints_file.seek(0)

            logging.info("Writing file")
            endpoints_file.write(file_data)

    def __write_service(self):
        """
        Write service.json
        """
        service_array = {}

        for filename in self.files:
            with open(f"{self.input_folder_path}/{filename}", "r", encoding="utf-8") as file:
                data = json.load(file)

            service_name = self.__get_name_with_version(filename, data)
            service = {service_name: data["servers"][0]["url"]}

            service_array.update(service)

        with open(f"{self.output_folder_path}/config/settings/service.json", "w+", encoding="utf-8") as file:
            json.dump(service_array, file, indent=4)

    def __write_krakend_json(self):
        """
        Write the KrakenD configuration
        """
        logging.info("Generating config")
        krakend_config = {
            "endpoints": '[{{template "Endpoints".service}}]'
        }

        logging.debug("Adding configuration")
        if "krakend.json" in self.config_files:
            logging.debug("Using custom krakend configuration")
            with open(f"{self.input_folder_path}/config/krakend.json", "r", encoding="utf-8") as config_file:
                config = json.load(config_file)
        else:
            logging.debug("Using default krakend configuration")
            with open("app/config/krakend.json", "r", encoding="utf-8") as config_file:
                config = json.load(config_file)

        for key in config:
            logging.debug(f"Adding {key}")
            krakend_config[key] = config[key]
        logging.debug("Added configuration")

        logging.debug("Loading config")
        config_data = json.dumps(krakend_config, indent=4)

        logging.debug("Reformatting endpoints value")

        json_string = config_data.replace("\"[{{template \\\"Endpoints\\\".service}}]\"",
                                          "[{{template \"Endpoints\".service}}]")

        logging.debug("Reformatted endpoints value")

        logging.info("Config generated")

        with open(f"{self.output_folder_path}/config/krakend.json", "w+", encoding="utf-8") as config_file:
            logging.info("Writing file")
            config_file.write(json_string)
            logging.info("Finished writing file")

    def __format_endpoints(self, file_input, file_output):
        """
        Convert all the endpoints to the KrakenD format
        """
        logging.info(f"Formatting endpoints for {file_input}")

        endpoints_list = []

        host = "{{$host := .}}\n"
        end = "\n\n\n{{end}}"

        output_path = f"{self.output_folder_path}/config/templates/{file_output}"

        with open(f"{self.input_folder_path}/{file_input}", "r+", encoding="utf-8") as openapi_file:
            logging.debug(f"Loaded {file_input}")
            data = json.load(openapi_file)

            if ".V" in file_output and not self.versioning:
                api_prefix = file_output.replace(".V", "/V").lower()
                api_define = file_output.replace(".V", "V")

            elif ".V" in file_output and self.versioning:
                version = "V" + data["info"]["version"][0:1]
                api_name = re.sub(r"\.V\d", "", file_output)

                api_prefix = (api_name + "/" + version).lower()
                api_define = api_name + version

            elif self.versioning:
                api_prefix = str(file_output + "/V" + data["info"]["version"][0:1]).lower()
                api_define = file_output + "V" + data["info"]["version"][0:1]

            else:
                api_prefix = file_output.lower()
                api_define = file_output

            # https://docs.python.org/3/library/string.html#format-string-syntax
            define = f'{{{{define "{api_define}"}}}}\n\n'
            prefix = f'{{{{$prefix := "/{api_prefix}"}}}}\n\n'

            openapi_security_schemes = None

            if "components" in data and "securitySchemes" in data["components"]:
                logging.debug("Security schemes found in OpenAPI")
                openapi_security_schemes = data["components"]["securitySchemes"]

            for path in data["paths"]:
                logging.info(f"Starting conversion for {path}")

                for method in data["paths"][path]:
                    logging.info(f"Preparing conversion for {path}: {method}")

                    headers = self.__get_headers(data["paths"][path][method], openapi_security_schemes)

                    logging.info(f"Converting {path}: {method}")
                    krakend_endpoint = self.__new_endpoint(path, method.upper(), headers)
                    logging.info(f"Converted {path}: {method}")

                    logging.debug("Adding endpoint to list")
                    endpoints_list.append(krakend_endpoint)
                    logging.debug("Added endpoint to list")

        endpoints = endpoints_list

        with open(f"{output_path}.tmpl", "w+", encoding="utf-8") as file:
            logging.debug("Write start template")
            file.write(define + host + prefix)

            for endpoint in endpoints:
                logging.debug(f'Writing endpoint {endpoint["backend"][0]["url_pattern"]}')
                file.write(json.dumps(endpoint, indent=4))

            logging.debug("Writing end template")
            file.write(end)
            file.seek(0)

            logging.debug("Reading file")
            file_data = file.read()

            logging.info("Converting endpoints to valid JSON")
            file_data = file_data.replace("}{", "},\n{")
            file.seek(0)

            logging.info(f"Writing {output_path}.tmpl")
            file.write(file_data)

    def __get_headers(self, endpoint, security_schemes):
        """
        Get the headers for the endpoint
        """
        headers = []

        if "security" in endpoint and endpoint["security"] is not None:
            logging.debug("Adding security headers")
            headers = self.__add_security_headers(endpoint, security_schemes)
            logging.debug("Added security headers")
        else:
            logging.debug("No authorization header required")

        if "parameters" in endpoint and endpoint["parameters"] is not None:
            for parameter in endpoint["parameters"]:
                if parameter["in"] == "header":
                    logging.debug(f'Adding {parameter["name"]} to headers')
                    headers.append(parameter["name"])
                    logging.debug(f'Added {parameter["name"]} to headers')
        else:
            logging.debug("No parameters found")

        return headers

    def __add_security_headers(self, endpoint, security_schemes):
        """
        Add the security headers
        """
        headers = []

        schemes = [list(item.keys())[0] for item in [scheme for scheme in endpoint["security"]]]

        for scheme in schemes:
            if scheme not in security_schemes:
                raise InvalidOpenAPIError(f"{scheme} does not exist in OpenAPI specification")

            logging.debug(f"Adding header for components.securitySchemes.{scheme}")
            header = self.__get_security_headers(security_schemes[scheme])
            if header in headers:
                raise InvalidOpenAPIError(f"Header '{header}' already exists")

            headers.append(header)

            logging.debug(f"Added header for components.securitySchemes.{scheme}")

        return headers

    def __create_folders(self):
        """
        Create the configuration folders
        """
        paths = ["config", "config/settings", "config/templates"]

        for folder in paths:
            if not os.path.exists(os.path.join(self.output_folder_path, folder)):
                os.mkdir(os.path.join(self.output_folder_path, folder))
