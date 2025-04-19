"""
remove_bg.py

Module for removing background from images using rembg.
Provides a single function `remove_background` for easy import into your projects.
Dependencies:
    pip install rembg pillow
"""

import logging
import os

from PIL import Image
from rembg import remove

# Configure module-level logger
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def remove_background(input_path: str, output_path: str) -> None:
    """
    Remove the background from the image at `input_path` and save to `output_path`.
    Raises:
        FileNotFoundError: If the input file does not exist.
        OSError: If reading or writing the image fails.
    """
    # Check input file
    if not os.path.isfile(input_path):
        logger.error(f"Input file not found: {input_path}")
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # Open and process image
    img = Image.open(input_path)
    logger.info(f"Removing background from: {input_path}")
    result = remove(img)

    # Ensure output directory exists
    out_dir = os.path.dirname(os.path.abspath(output_path))
    os.makedirs(out_dir, exist_ok=True)

    # Save result
    result.save(output_path)
    logger.info(f"Saved background-removed image to: {output_path}")


# Expose the function for import
__all__ = ["remove_background"]
