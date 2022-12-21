import os
import shutil


def create_output_folder():
    """
    Create the output folder if it doesn't exist
    """
    if not os.path.exists(os.path.join("tests/output")):
        os.mkdir(os.path.join("tests/output"))


def delete_output_folder():
    """
    Delete the output folder if it exists
    """
    if os.path.exists(os.path.join("tests/output")):
        shutil.rmtree(os.path.join("tests/output"))
