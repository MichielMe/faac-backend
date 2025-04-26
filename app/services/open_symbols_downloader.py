import os
from pathlib import Path

import cairosvg
import requests
from fastapi.responses import JSONResponse
from loguru import logger
from PIL import Image

# Import directly from the source module instead of app.services
from app.services.open_symbols_client import OpenSymbolsClient

pictogram_dir = Path("app/assets/pictograms")


def generate_pictogram_open_symbols(
    keyword: str, output_filename=None, generate_multiple=False, num_images=2
) -> JSONResponse:
    """
    Generate pictograms by searching and downloading from OpenSymbols API.

    Args:
        keyword: The word or phrase to search for
        output_filename: Optional custom filename
        generate_multiple: Whether to generate multiple variations
        num_images: Number of images to generate when generate_multiple is True

    Returns:
        JSONResponse with success status and paths to generated images
    """
    # Ensure the pictogram directory exists
    pictogram_dir.mkdir(parents=True, exist_ok=True)

    # Initialize OpenSymbols client
    client = OpenSymbolsClient()

    # Search for symbols matching the keyword
    symbols = client.search_symbols(query=keyword, locale="en")

    # If no symbols found, return empty response
    if not symbols:
        logger.warning(f"No symbols found for keyword: {keyword}")
        return JSONResponse(
            content={"success": False, "error": "No symbols found"}, status_code=404
        )

    # Limit to the first num_images symbols if we found more
    symbols = symbols[:num_images] if generate_multiple else symbols[:1]

    # Process each symbol and download the image
    generated_files = []

    for i, symbol in enumerate(symbols):
        try:
            # Get the image URL
            image_url = symbol.get("image_url")
            if not image_url:
                logger.warning(f"No image URL for symbol {i+1}")
                continue

            # Create the output filename
            if generate_multiple:
                if output_filename is None:
                    current_filename = f"pic_{keyword}_{i+5:02d}.png"
                else:
                    base, ext = os.path.splitext(output_filename)
                    current_filename = f"{base}_{i+5:02d}{ext}"
            else:
                if output_filename is None:
                    current_filename = f"pic_{keyword}.png"
                else:
                    current_filename = output_filename

            # Download the image
            response = requests.get(image_url)
            response.raise_for_status()

            # Check if it's an SVG (based on content)
            content_type = response.headers.get("Content-Type", "")
            content = response.content
            file_path = pictogram_dir / current_filename

            if (
                "svg" in content_type.lower()
                or content.startswith(b"<?xml")
                or content.startswith(b"<svg")
            ):
                # It's an SVG, we need to convert to PNG
                logger.info(f"Converting SVG to PNG for '{keyword}'")
                # Convert SVG to PNG using cairosvg
                png_data = cairosvg.svg2png(bytestring=content)

                # Save the PNG
                with open(file_path, "wb") as f:
                    f.write(png_data)

                # Verify the image can be opened with PIL
                try:
                    Image.open(file_path)
                except Exception as e:
                    logger.error(f"Error validating converted PNG: {e}")
                    continue
            else:
                # Save the image directly if it's not an SVG
                with open(file_path, "wb") as f:
                    f.write(content)

            generated_files.append(str(file_path))
            logger.info(
                f"OpenSymbols image for '{keyword}' saved as '{current_filename}'"
            )

        except Exception as e:
            logger.error(f"Error downloading symbol {i+1} for {keyword}: {e}")

    # Return results
    if generated_files:
        return JSONResponse(content={"success": True, "files": generated_files})
    else:
        return JSONResponse(
            content={"success": False, "error": "Failed to download any images"},
            status_code=500,
        )
