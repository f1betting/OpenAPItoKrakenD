import logging
from typing import Optional

import typer

from app.logic.converter import OpenAPIToKrakenD
from app.utils.customlogger import CustomLogger
from app.utils.errors import OpenAPIFileNotFoundError, InvalidOpenAPIError

app = typer.Typer(pretty_exceptions_short=True, pretty_exceptions_show_locals=False)


@app.command()
def main(input_folder: str = typer.Argument(..., help="Input folder that contains all the OpenAPI specifications",
                                            show_default=False),
         output_folder: str = typer.Argument(..., help="Output folder", show_default=False),
         debug: Optional[bool] = typer.Option(False, "--debug", help="Enable debug mode"),
         disable_automatic_versioning: Optional[bool] = typer.Option(False,
                                                                     "--disable-automatic-versioning",
                                                                     help="Disable versioning based on 'version' "
                                                                          "field in OpenAPI specification and use "
                                                                          "filename based-versioning instead.")):
    """
    The converter CLI command
    """
    converter = OpenAPIToKrakenD(logging_mode=logging.DEBUG if debug else logging.INFO,
                                 input_folder_path=input_folder,
                                 output_folder_path=output_folder,
                                 no_versioning=disable_automatic_versioning)
    converter.convert()


if __name__ == "__main__":  # pragma: no coverage
    try:
        app()
    except (OpenAPIFileNotFoundError, InvalidOpenAPIError) as e:
        CustomLogger().error(e)
