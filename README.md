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
    <img alt="GitHub Workflow Status" src="https://img.shields.io/github/workflow/status/f1betting/OpenAPItoKrakenD/Python%20on%20Push%20Master?label=Build">
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
$ python main.py --help

Usage: main.py [OPTIONS] INPUT_FOLDER OUTPUT_FOLDER

╭─ Arguments ─────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    input_folder       TEXT  Input folder that contains all the OpenAPI specifications [required]              │
│ *    output_folder      TEXT  Output folder [required]                                                          │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --name                                    TEXT  API gateway name [default: KrakenD API Gateway]                 │
│ --stackdriver-project-id                  TEXT  Google Cloud project id [default: None]                         │
│ --debug                     --no-debug          Enable debug mode [default: no-debug]                           │
│ --help                                          Show this message and exit.                                     │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->

## 🚀 Usage

1. Place the OpenAPI files you wish to convert in the input folder
2. Run main.py
3. Find the config folder in ``output``

### 🔢 Versioning your APIs

The converter can handle versioning as well. To do this, you have to name the OpenAPI file a specific way. Example:

``F1.V1.json`` will create the API on ``/f1/v1``

If you do not wish to use versioning, you can just name your file as normal. Do note that if you add ``.v`` to the
OpenAPI name, this will create a version.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->

## 📜 License

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[Python]: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54

[Python-url]: https://python.org
