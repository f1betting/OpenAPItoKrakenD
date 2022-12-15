import logging
from typing import Optional

import typer

from app.logic.converter import OpenAPIToKrakenD


def main(input_folder: str = typer.Argument(..., help="Input folder that contains all the OpenAPI specifications",
                                            show_default=False),
         output_folder: str = typer.Argument(..., help="Output folder", show_default=False),
         name: str = typer.Option("KrakenD API Gateway", help="API gateway name"),
         stackdriver_project_id: Optional[str] = typer.Option(None, help="Google Cloud project id"),
         debug: Optional[bool] = typer.Option(False, help="Enable debug mode")):
    """
    The converter CLI command
    """
    converter = OpenAPIToKrakenD(logging_mode=logging.DEBUG if debug else logging.INFO,
                                 input_folder_path=input_folder,
                                 output_folder_path=output_folder,
                                 name=name,
                                 stackdriver_project_id=stackdriver_project_id)
    converter.convert()


if __name__ == "__main__":
    typer.run(main)
