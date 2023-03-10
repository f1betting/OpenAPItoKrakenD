<a name="readme-top"></a>

<div>
<h3 align="center">OpenAPItoKrakenD</h3>

  <p align="center">
    A tool to batch-convert OpenAPI 3.0 files to a flexible KrakenD configuration
    <br />
    <a href="https://github.com/f1betting/OpenAPItoKrakenD/issues">Report Bug</a>
    ยท
    <a href="https://github.com/f1betting/OpenAPItoKrakenD/issues">Request Feature</a>
    <br />
    <br />
    <img alt="GitHub Latest Version" src="https://img.shields.io/github/v/release/f1betting/OpenAPItoKrakenD?label=Latest%20release&style=flat">
    <br />
    <img alt="SonarCloud coverage" src="https://sonarcloud.io/api/project_badges/measure?project=f1betting_OpenAPItoKrakenD&metric=coverage">
    <img alt="SonarCloud quality gate" src="https://sonarcloud.io/api/project_badges/measure?project=f1betting_OpenAPItoKrakenD&metric=alert_status">
    <img alt="SonarCloud code smells" src="https://sonarcloud.io/api/project_badges/measure?project=f1betting_OpenAPItoKrakenD&metric=code_smells">
    <br />
    <img alt="GitHub Workflow Status" src="https://img.shields.io/github/actions/workflow/status/f1betting/OpenAPItoKrakenD/python_on_push_master.yml?label=Build&branch=main">
  </p>
</div>



<!-- TABLE OF CONTENTS -->

## ๐ Table of contents

- [โน๏ธ About The Project](#-about-the-project)
    - [๐ง Built With](#-built-with)
- [๐จ Getting Started](#-getting-started)
    - [โ  Prerequisites](#-prerequisites)
    - [๐ก Running the converter](#-running-the-converter)
- [๐ Usage ](#-usage)
    - [๐ Supported authorization headers](#-supported-authorization-headers)
    - [๐ข Versioning](#-versioning-your-apis)
        - [๐ค Automatic versioning](#-automatic-versioning)
        - [๐ท Manual versioning](#-manual-versioning)
        - [๐ซ No versioning](#-no-versioning)
    - [๐ Environments](#-environments)
    - [๐งฐ Customizing KrakenD configuration](#-customizing-krakend-configuration)
        - [๐พ Configuration files](#-configuration-files)
    - [๐ฌ Using in GitHub Actions](#-using-in-github-actions)
        - [๐ Configuration](#-configuration)
        - [๐พ Detailed example](#-detailed-example)
- [๐ License](#-license)

<!-- ABOUT THE PROJECT -->

## โน๏ธ About The Project

A tool to batch-convert OpenAPI 3.0 files to a flexible KrakenD configuration

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### ๐ง Built With

[![Python]][Python-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->

## ๐จ Getting Started

Below are the instructions for running the API for development and general usage.

### โ  Prerequisites

Install the dependencies using:

```shell
$ pip install -r requirements.txt
```

### ๐ก Running the converter

Run main.py to execute the converter:

```shell
 Usage: python -m app.main [OPTIONS] INPUT_FOLDER OUTPUT_FOLDER

 The converter CLI command

โญโ Arguments โโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโฎ
โ *    input_folder       TEXT  Input folder that contains all the OpenAPI specifications [required]                                                                                                                                                                 โ
โ *    output_folder      TEXT  Output folder [required]                                                                                                                                                                                                             โ
โฐโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโฏ
โญโ Options โโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโฎ
โ --debug                                     Enable debug mode                                                                                                                                                                                                      โ
โ --env                                 TEXT  Choose the environment (prod, dev, etc..)                                                                                                                                                                              โ
โ --disable-automatic-versioning              Disable versioning based on 'version' field in OpenAPI specification and use filename based-versioning instead.                                                                                                        โ
โ --help                                      Show this message and exit.                                                                                                                                                                                            โ
โฐโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโโฏ
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->

## ๐ Usage

1. Place the OpenAPI files you wish to convert in the input folder
2. Run main.py
3. Find the config folder in ``output``

### ๐ Supported authorization headers

Depending on your authorization method, it might be possible to automatically add authorization headers to the endpoints
that require them. Below is a table of the supported authorization schemes.

| Method                         | Supported | Header name             |
|--------------------------------|-----------|-------------------------|
| HTTP (Basic)                   | Yes       | Authorization           |
| HTTP (Bearer)                  | Yes       | Authorization           |
| API Keys (header)              | Yes       | Defined in OpenAPI spec |
| API Keys (cookie)              | No        |                         |
| OAuth 2.0 (Implicit)           | Yes       | Authorization           |
| OAuth 2.0 (Authorization code) | No        |                         |
| OAuth 2.0 (Password)           | No        |                         |
| OAuth 2.0 (Client Credentials) | No        |                         |
| OpenID Connect Discovery       | No        |                         |

### ๐ข Versioning your APIs

#### ๐ค Automatic versioning

By default, the converter will automatically version your APIs based on the ``version`` field inside your OpenAPI
specification.

#### ๐ท Manual versioning

The converter can handle manual versioning as well by using the ``--disable-automatic-versioning`` flag.

To version your APIs, you have to name the OpenAPI file in the ``<api>.<version>.json``.

Example:

``F1.V1.json`` will create the API on ``/f1/v1``

#### ๐ซ No versioning

If you do not wish to use versioning, you can just name your file as normal and run the converter with
the ``--disable-automatic-versioning`` flag. Do note that if you add ``.v`` to the
OpenAPI name, it will create a version.

### ๐ Environments

Using the ``--env`` flag, you can specify the environment you wish to use. This matches the description field inside the
servers object of the OpenAPI specifications.

### ๐งฐ Customizing KrakenD configuration

It's possible to customize the default configuration by adding a ``config`` folder with the configuration files inside
it. To view the default configuration files, see the files inside [app/config](app/config).

To view an example of this,
see [KrakenD Cloud Run service account plugin](examples/krakend-cloud-run-service-account-plugin)

#### ๐พ Configuration files

Below are the configuration files that you can use to configure KrakenD to your liking.

| File          | Function                                                                                                                                                 |
|---------------|----------------------------------------------------------------------------------------------------------------------------------------------------------|
| backend.json  | The configuration for the ``backend`` section in an endpoint. _See [Declaring and connecting to backends](https://www.krakend.io/docs/backends/)_        |
| endpoint.json | The configuration for the ``endpoint`` section in an endpoint file. _See [Creating API endpoints](https://www.krakend.io/docs/endpoints/)_               |
| krakend.json  | The general KrakenD configuration. Refer to the [KrakenD docs](https://www.krakend.io/docs/) for more information.                                       |
| Dockerfile    | The Dockerfile to build a Docker image of the final KrakenD gateway. _See [Generating a Docker artifact](https://www.krakend.io/docs/deploying/docker/)_ |

### ๐ฌ Using in GitHub Actions

It's possible to use this in a GitHub action to automatically generate the configuration with provided specifications.
Running this action will create an artifact named ``krakend-config``. To use this artifact in other jobs, you
can use ``actions/download-artifact@v2`` to download the action. This can be handy if you wish to automatically deploy
it to a cloud service, like Google Cloud Run.

The converter will automatically create a full Docker-ready configuration. All you have to do is build the Docker image
and run it.

Below is a basic example of how to use the converter

````yaml
name: Convert Specs to KrakenD config

on: workflow_dispatch

jobs:
  convert:
    runs-on: ubuntu-latest
    steps:
      - name: Convert specs to KrakenD config
        uses: f1betting/OpenAPItoKrakenD@v2
        with:
          input-folder: input
````

#### ๐ Configuration

There are a few configurations options possible. These are the ones that are available to use:

| Name               | Required | Description                                                                                                                                  |
|--------------------|----------|----------------------------------------------------------------------------------------------------------------------------------------------|
| input-folder       | Yes      | The input folder that contains the OpenAPI specs and optional custom configuration files                                                     |
| environment        | No       | Set the backend target URL to the description of the server object inside the OpenAPI specification (picks the first entry if not specified) |
| disable-versioning | No       | Disable automatic versioning based on OpenAPI specifications                                                                                 |

#### ๐พ Detailed example

For a more detailed example, which automatically deploys the KrakenD gateway to Google Cloud Run,
see [automatic cloud run deployment](examples/automatic_cloud_run_deployment).

You can find an example using a custom configuration
in [KrakenD Cloud Run service account plugin](examples/krakend-cloud-run-service-account-plugin)


<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->

## ๐ License

Distributed under the MIT License. See `LICENSE.md` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[Python]: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54

[Python-url]: https://python.org
