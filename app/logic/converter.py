from __future__ import annotations

import glob
import json
import logging
import os
from http.client import HTTPException


class OpenAPIToKrakenD:
    def __init__(self, logging_mode: int, input_folder_path: str, output_folder_path: str, name: str,
                 stackdriver_project_id: str = None):
        logging.basicConfig(level=logging_mode, format="[%(levelname)s]: %(message)s")

        self.paths = glob.glob(f"{input_folder_path}/*.json")
        self.files = []
        self.input_folder_path = input_folder_path
        self.output_folder_path = output_folder_path

        self.enable_stackdriver = bool(stackdriver_project_id)
        self.stackdriver_project_id = stackdriver_project_id

        self.name = name

    def convert(self) -> OpenAPIToKrakenD:
        for path in self.paths:
            self.files.append(os.path.basename(path))

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

    def __verify_openapi(self, file):
        with open(f"{self.input_folder_path}/{file}", "r", encoding="utf-8") as openapi_file:
            try:
                logging.debug("Verifying server")
                data = json.load(openapi_file)["servers"][0]["url"]

                if "http://" not in data and "https://" not in data:
                    logging.error(f"{file}: invalid server")
                    raise HTTPException
            except KeyError:
                logging.error(f"{file}: no servers defined")
                raise KeyError

    @staticmethod
    def __new_endpoint(endpoint: str, method: str, headers: list):
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
        header = None

        if security_scheme["type"] == "http" \
                and security_scheme["scheme"] == "bearer":
            logging.debug("Bearer Authentication schema found")

            logging.debug("Setting security header to 'Authorization'")
            header = "Authorization"
            logging.debug("Set security header to 'Authorization'")

        return header

    def __write_dockerfile(self):
        data = """FROM devopsfaith/krakend:2.1.2

COPY . /etc/krakend/

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

                name = file[:-5].upper().replace(".V", "V")

                data = f'{{{{ template "{name}" $service.{name}}}}}\n'

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
        service_array = {}

        for filename in self.files:
            with open(f"{self.input_folder_path}/{filename}", "r", encoding="utf-8") as file:
                data = json.load(file)["servers"][0]["url"]

                service_name = filename.upper().replace(".V", "V")[:-5]
                service = {service_name: data}

                service_array.update(service)

        with open(f"{self.output_folder_path}/config/settings/service.json", "w+", encoding="utf-8") as file:
            json.dump(service_array, file, indent=4)

    def __write_krakend_json(self):
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

        if self.enable_stackdriver:
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
        logging.info(f"Formatting endpoints for {file_input}")

        endpoints_list = []

        api_prefix = file_output.replace(".V", "/V").lower()
        api_define = file_output.replace(".V", "V")

        define = f'{{{{define "{api_define}"}}}}\n\n'
        prefix = f'{{{{$prefix := "/{api_prefix}"}}}}\n\n'
        host = "{{$host := .}}\n"
        end = "\n\n\n{{end}}"

        output_path = f"{self.output_folder_path}/config/templates/{file_output}"

        with open(f"{self.input_folder_path}/{file_input}", "r+", encoding="utf-8") as openapi_file:
            logging.debug(f"Loaded {file_input}")
            data = json.load(openapi_file)

            for path in data["paths"]:
                logging.info(f"Starting conversion for {path}")

                for method in data["paths"][path]:
                    logging.info(f"Preparing conversion for {path}: {method}")

                    security_schemes = None
                    try:
                        security_schemes = data["components"]["securitySchemes"]
                        logging.debug("Security schemes found")
                    except KeyError:
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
        headers = []
        try:
            if endpoint["security"] is not None:
                logging.debug("Adding security headers")
                headers = self.__add_security_headers(endpoint, security_schemes)
                logging.debug("Added security headers")
        except KeyError:
            logging.debug("No authorization header required")

        try:
            if endpoint["parameters"] is not None:
                for parameter in endpoint["parameters"]:
                    if parameter["in"] == "header":
                        logging.debug(f'Adding {parameter["name"]} to headers')
                        headers.append(parameter["name"])
                        logging.debug(f'Added {parameter["name"]} to headers')
        except KeyError:
            logging.debug("No parameters found")

        return headers

    def __add_security_headers(self, endpoint, security_schemes):
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
        paths = ["config", "config/settings", "config/templates"]

        for folder in paths:
            if not os.path.exists(os.path.join(self.output_folder_path, folder)):
                os.mkdir(os.path.join(self.output_folder_path, folder))
