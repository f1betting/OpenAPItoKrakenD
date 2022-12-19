import logging
from typing import Optional

import typer

from app.logic.converter import OpenAPIToKrakenD

app = typer.Typer()


@app.command()
def main(input_folder: str = typer.Argument(..., help="Input folder that contains all the OpenAPI specifications",
                                            show_default=False),
         output_folder: str = typer.Argument(..., help="Output folder", show_default=False),
         name: str = typer.Option("KrakenD API Gateway", help="API gateway name"),
         stackdriver_project_id: Optional[str] = typer.Option(None, help="Google Cloud project id"),
         debug: Optional[bool] = typer.Option(False, "--debug", help="Enable debug mode"),
         disable_automatic_versioning: Optional[bool] = typer.Option(False,
                                                                     "--disable-automatic-versioning",
                                                                     help="Disable versioning based on 'version' "
                                                                          "field in OpenAPI specification and use "
                                                                          "filename based-versioning instead. (If "
                                                                          "disabled and no filename versioning is "
                                                                          "done, the API will not get a version in "
                                                                          "the endpoint)")):
    """
    The converter CLI command
    """
    converter = OpenAPIToKrakenD(logging_mode=logging.DEBUG if debug else logging.INFO,
                                 input_folder_path=input_folder,
                                 output_folder_path=output_folder,
                                 name=name,
                                 stackdriver_project_id=stackdriver_project_id,
                                 no_versioning=disable_automatic_versioning)
    converter.convert()


if __name__ == "__main__":  # pragma: no coverage
    typer.run(main)
