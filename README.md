<a name="readme-top"></a>

<div>
<h3 align="center">OpenAPItoKrakenD</h3>

  <p align="center">
    A tool to batch-convert OpenAPI 3.0 files to a flexible KrakenD configuration
    <br />
    <a href="https://github.com/niek-o/OpenAPItoKrakenD/issues">Report Bug</a>
    ·
    <a href="https://github.com/OpenAPItoKrakenD/issues">Request Feature</a>
    <br />
    <br />
    <img alt="SonarCloud coverage" src="https://sonarcloud.io/api/project_badges/measure?project=f1betting_OpenAPItoKrakenD&metric=coverage">
    <img alt="SonarCloud quality gate" src="https://sonarcloud.io/api/project_badges/measure?project=f1betting_OpenAPItoKrakenD&metric=alert_status">
    <img alt="SonarCloud code smells" src="https://sonarcloud.io/api/project_badges/measure?project=f1betting_OpenAPItoKrakenD&metric=code_smells">
    <br />
    <img alt="GitHub Workflow Status" src="https://img.shields.io/github/actions/workflow/status/f1betting/OpenAPItoKrakenD/python_on_push_master.yml?label=Build&branch=main">
  </p>
</div>



<!-- TABLE OF CONTENTS -->

## 📋 Table of contents

- [ℹ️ About The Project](#-about-the-project)
    - [🚧 Built With](#-built-with)
- [🔨 Getting Started](#-getting-started)
    - [⚠ Prerequisites](#-prerequisites)
    - [🏡 Running the converter](#-running-the-converter)
- [🚀 Usage ](#-usage)
    - [🔢 Versioning](#-versioning-your-apis)
        - [🤖 Automatic versioning](#-automatic-versioning)
        - [👷 Manual versioning](#-manual-versioning)
        - [🚫 No versioning](#-no-versioning)
- [📜 License](#-license)

<!-- ABOUT THE PROJECT -->

## ℹ️ About The Project

A tool to batch-convert OpenAPI 3.0 files to a flexible KrakenD configuration

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### 🚧 Built With

[![Python]][Python-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->

## 🔨 Getting Started

Below are the instructions for running the API for development and general usage.

### ⚠ Prerequisites

Install the dependencies using:

```shell
$ pip install -r requirements.txt
```

### 🏡 Running the converter

Run main.py to execute the converter:

```shell
$ python -m app.main --help     

Usage: python -m app.main [OPTIONS] INPUT_FOLDER OUTPUT_FOLDER

The converter CLI command

╭─ Arguments ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    input_folder       TEXT  Input folder that contains all the OpenAPI specifications [required]                                                                                                                                                                 │
│ *    output_folder      TEXT  Output folder [required]                                                                                                                                                                                                             │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --name                                TEXT  API gateway name [default: KrakenD API Gateway]                                                                                                                                                                        │
│ --stackdriver-project-id              TEXT  Google Cloud project id [default: None]                                                                                                                                                                                │
│ --debug                                     Enable debug mode                                                                                                                                                                                                      │
│ --disable-automatic-versioning              Disable versioning based on 'version' field in OpenAPI specification and use filename based-versioning instead. (If disabled and no filename versioning is done, the API will not get a version in the endpoint)       │
│ --help                                      Show this message and exit.                                                                                                                                                                                            │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->

## 🚀 Usage

1. Place the OpenAPI files you wish to convert in the input folder
2. Run main.py
3. Find the config folder in ``output``

### 🔢 Versioning your APIs

#### 🤖 Automatic versioning

By default, the converter will automatically version your APIs based on the ``version`` field inside your OpenAPI
specification.

#### 👷 Manual versioning

The converter can handle manual versioning as well by using the ``--disable-automatic-versioning`` flag.

To version your APIs, you have to name the OpenAPI file in the ``<api>.<version>.json``.

Example:

``F1.V1.json`` will create the API on ``/f1/v1``

#### 🚫 No versioning

If you do not wish to use versioning, you can just name your file as normal and run the converter with
the ``--disable-automatic-versioning`` flag. Do note that if you add ``.v`` to the
OpenAPI name, it will create a version.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->

## 📜 License

Distributed under the MIT License. See `LICENSE.md` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[Python]: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54

[Python-url]: https://python.org
