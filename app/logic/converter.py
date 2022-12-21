from __future__ import annotations

import glob
import json
import logging
import os
import re


class OpenAPIToKrakenD:
    """
    Batch-convert OpenApi 3 files to a flexible KrakenD configuration
    """

    def __init__(self, logging_mode: int, input_folder_path: str, output_folder_path: str, name: str,
                 stackdriver_project_id: str = None, no_versioning: bool = False):
        """
        Initialize converter
        """
        logging.basicConfig(level=logging_mode, format="[%(levelname)s]: %(message)s")  # NOSONAR

        self.paths: list = glob.glob(f"{input_folder_path}/*.json")
        self.files: list = []
        self.input_folder_path: str = input_folder_path
        self.output_folder_path: str = output_folder_path

        self.stackdriver_project_id: str = stackdriver_project_id

        self.name: str = name

        self.versioning: bool = not no_versioning

    def convert(self) -> OpenAPIToKrakenD:
        """
        Convert the OpenAPI files to a flexible KrakenD configuration
        """
        for path in self.paths:
            self.files.append(os.path.basename(path))

        if len(self.paths) <= 0:
            logging.error(f"No files found in '{self.input_folder_path}'")
            raise FileNotFoundError

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

    @staticmethod
    def __new_endpoint(endpoint: str, method: str, headers: list):
        """
        Create a KrakenD endpoint
        """
        logging.debug("Creating headers")
        headers.append("Content-Type")

        logging.debug("Creating endpoint")
        formatted_endpoint = {
            "endpoint": "{{ $prefix }}" + endpoint,
            "method": method,
            "output_encoding": "no-op",
            "timeout": "3600s",
            "input_query_strings": [],
            "backend": [
                {
                    "url_pattern": endpoint,
                    "encoding": "no-op",
                    "method": method,
                    "host": [
                        "{{ $host }}"
                    ],
                    "disable_host_sanitize": False
                }
            ],
            "input_headers": headers
        }

        return formatted_endpoint

    @staticmethod
    def __get_security_headers(security_scheme):
        """
        Get the correct security headers for the security scheme
        """
        header = None

        if security_scheme["type"] == "http" \
                and security_scheme["scheme"] == "bearer":
            logging.debug("Bearer Authentication schema found")

            logging.debug("Setting security header to 'Authorization'")
            header = "Authorization"
            logging.debug("Set security header to 'Authorization'")

        return header

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
                    logging.error(f"{file}: invalid server")
                    raise ValueError
            else:
                logging.error(f"{file}: no servers defined")
                raise ValueError

            logging.debug("Verifying version")

            if "info" not in data.keys() or "version" not in data["info"].keys():
                logging.error("No version found")
                raise ValueError

    def __write_dockerfile(self):
        """
        Write the dockerfile
        """
        data = """FROM devopsfaith/krakend:2.1.2

COPY /config /etc/krakend/config

RUN FC_ENABLE=1 \\
    FC_SETTINGS="config/settings" \\
    FC_TEMPLATES="config/templates" \\
    krakend check -t -d -c "config/krakend.json"
ENTRYPOINT FC_ENABLE=1 \\
    FC_SETTINGS="/etc/krakend/config/settings"\\
    FC_TEMPLATES="/etc/krakend/config/templates" \\
    krakend run -c "/etc/krakend/config/krakend.json"
"""

        with open(f"{self.output_folder_path}/Dockerfile", "w+", encoding="utf-8") as dockerfile:
            dockerfile.write(data)

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
            "version": 3,
            "name": self.name,
            "cache_ttl": "3600s",
            "timeout": "45s",
            "extra_config": {
                "security/cors": {
                    "allow_origins": [
                        "http*"
                    ],
                    "allow_methods": [
                        "GET",
                        "HEAD",
                        "POST",
                        "PUT",
                        "DELETE",
                        "OPTIONS"
                    ],
                    "expose_headers": [
                        "Content-Length",
                        "Content-Type"
                    ],
                    "allow_headers": [
                        "Content-Type",
                        "Accept-Language",
                        "Origin",
                        "Authorization"
                    ],
                    "max_age": "12h",
                    "allow_credentials": True,
                    "debug": True
                },
                "router": {
                    "logger_skip_paths": [
                        "/__health"
                    ],
                    "disable_access_log": True
                },
                "telemetry/logging": {
                    "level": "INFO",
                    "prefix": "[KRAKEND]",
                    "syslog": True,
                    "stdout": True,
                    "format": "logstash"
                }
            },
            "endpoints": '[{{template "Endpoints".service}}]'
        }

        if self.stackdriver_project_id:
            logging.debug("Adding stackdriver configuration")
            krakend_config["extra_config"]["telemetry/opencensus"] = \
                {
                    "sample_rate": 100,
                    "reporting_period": 60,
                    "enabled_layers": {
                        "backend": True,
                        "router": True,
                        "pipe": True
                    },
                    "exporters": {
                        "stackdriver": {
                            "project_id": self.stackdriver_project_id,
                            "metric_prefix": "krakend",
                            "default_labels": {
                                "env": "production"
                            }
                        }
                    }
                }
            logging.debug("Added stackdriver configuration")

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

            for path in data["paths"]:
                logging.info(f"Starting conversion for {path}")

                for method in data["paths"][path]:
                    logging.info(f"Preparing conversion for {path}: {method}")

                    security_schemes = None
                    if "components" in data and "securitySchemes" in data["components"]:
                        security_schemes = data["components"]["securitySchemes"]
                        logging.debug("Security schemes found")
                    else:
                        logging.debug("No security schemes found")

                    headers = self.__get_headers(data["paths"][path][method], security_schemes)

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
        security = endpoint["security"]
        schemes = list(security_schemes.keys())

        for method in security:
            for scheme in schemes:
                if scheme in method:
                    logging.debug(f"Adding {scheme}")
                    headers.append(self.__get_security_headers(security_schemes[scheme]))
                    logging.debug(f"Added {scheme}")

        return headers

    def __create_folders(self):
        """
        Create the configuration folders
        """
        paths = ["config", "config/settings", "config/templates"]

        for folder in paths:
            if not os.path.exists(os.path.join(self.output_folder_path, folder)):
                os.mkdir(os.path.join(self.output_folder_path, folder))
