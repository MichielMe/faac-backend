import os
from pathlib import Path

import requests
from fastapi.responses import JSONResponse
from loguru import logger
from openai import OpenAI

from app.core import settings

api_key = settings.OPENAI_API_KEY
pictogram_dir = Path("app/assets/pictograms")


SYSTEM_PROMPT = (
    "Create a professional AAC (Augmentative and Alternative Communication) pictogram following these EXACT technical specifications:\n\n"
    "TECHNICAL REQUIREMENTS:\n"
    "- Simple, clear pictogram with a COMPLETELY TRANSPARENT background\n"
    "- Size: 512x512 pixels (already set in the system)\n"
    "- Format: PNG with transparency (already set in the system)\n"
    "- Clear black outlines (2-4 points thick) for ALL elements\n"
    "- Flat color fill with NO gradients, NO shadows, NO 3D effects\n"
    "- Maximum 3-4 colors total (including black for outlines)\n"
    "- NO text within the symbol\n"
    "- NO borders, frames, or background elements of any kind\n\n"
    "DESIGN PRINCIPLES:\n"
    "- High 'iconicity' - immediately recognizable even at small sizes\n"
    "- Show objects in canonical (most recognizable) positions\n"
    "- Use the simplest possible representation that maintains identity\n"
    "- Create uncluttered designs with only essential elements\n"
    "- Follow the visual style of established AAC systems like ARASAAC or Mulberry Symbols\n"
    "- Culturally neutral representations unless specifically requested\n\n"
    "DO NOT INCLUDE:\n"
    "- No backgrounds of any kind (not even white)\n"
    "- No frames, borders, UI elements, or decorative features\n"
    "- No contextual scenes or environments\n"
    "- No gradients, shading, or 3D effects\n"
    "- No text elements of any kind\n\n"
    "- ONLY THE SIMPLE ICON!!!!"
    "- NO BACKGROUND, NO FRAME, NO TEXT, NO SHADOWS, NO GRADIENTS, NO 3D EFFECTS, NO SHADING, NO BACKGROUNDS, NO UI ELEMENTS, NO DECORATIVE FEATURES, NO CONTEXTUAL SCENES OR ENVIRONMENTS"
    "- ONLY ICON"
)


def generate_pictogram_openai(
    keyword, output_filename=None, generate_multiple=False, num_images=2, start_index=1
):
    """
    Generate one or more pictograms using OpenAI's DALL-E.

    Args:
        keyword: The word or phrase to generate a pictogram for
        output_filename: Optional custom filename
        generate_multiple: Whether to generate multiple variations
        num_images: Number of images to generate when generate_multiple is True
        start_index: Starting index for numbering the images (default: 1)

    Returns:
        JSONResponse with success status and paths to generated images
    """
    # Instantiate the OpenAI client with your API key
    client = OpenAI(api_key=api_key)

    # If not generating multiple images, use the original behavior
    if not generate_multiple:
        # Combine the system prompt with the user-provided keyword
        final_prompt = f"{SYSTEM_PROMPT}\n\nCreate a professional '{keyword}' pictogram that would work well in an AAC system. ONLY the pictogram itself with transparent background. NO borders, frames, or lines below the image. Create a simple AAC pictogram in the style of Mulberry Symbols or ARASAAC with clean black outlines, flat colors, and 100% transparent background. The image must be a single isolated symbol with NO frame, NO background, and NO text. Focus on creating a pictogram that is immediately recognizable to users with cognitive disabilities and suitable for communication purposes."

        try:
            # Generate the pictogram using the latest OpenAI image generation API (DALL-E 3)
            response = client.images.generate(
                model="dall-e-3",
                prompt=final_prompt,
                size="1024x1024",
                quality="hd",
                style="natural",
                n=1,
            )

            # Retrieve the image URL from the response
            image_url = response.data[0].url
            logger.info(f"Generated Image URL: {image_url}")

            if output_filename is None:
                output_filename = f"pic_{keyword}.png"

            # Download the image and save it locally
            image_data = requests.get(image_url).content
            file_path = pictogram_dir / output_filename
            with open(file_path, "wb") as f:
                f.write(image_data)

            logger.info(f"Pictogram for '{keyword}' saved as '{output_filename}'.")
            return JSONResponse(content={"success": True, "files": [str(file_path)]})
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return JSONResponse(
                content={"success": False, "error": str(e)}, status_code=500
            )

    # Generate multiple images with numbered suffixes
    else:
        generated_files = []

        for i in range(start_index, start_index + num_images):
            # Create numbered filename
            if output_filename is None:
                current_filename = f"pic_{keyword}_{i:02d}.png"
            else:
                base, ext = os.path.splitext(output_filename)
                current_filename = f"{base}_{i:02d}{ext}"

            # Alternate between the two prompts for more variation
            prompt_template = SYSTEM_PROMPT
            final_prompt = f"{prompt_template}\n\nCreate a professional '{keyword}' pictogram that would work well in an AAC system. ONLY the pictogram itself with transparent background. NO borders, frames, or lines below the image."

            try:
                # Generate the pictogram
                response = client.images.generate(
                    model="dall-e-3",
                    prompt=final_prompt,
                    size="1024x1024",
                    quality="hd",
                    style="natural",
                    n=1,
                )

                # Retrieve the image URL from the response
                image_url = response.data[0].url
                logger.info(f"Generated Image URL for image {i}: {image_url}")

                # Download the image and save it locally
                image_data = requests.get(image_url).content
                file_path = pictogram_dir / current_filename

                with open(file_path, "wb") as f:
                    f.write(image_data)

                generated_files.append(str(file_path))
                logger.info(
                    f"Pictogram {i} for '{keyword}' saved as '{current_filename}'."
                )

            except Exception as e:
                logger.error(f"An error occurred generating image {i}: {e}")

        if generated_files:
            return JSONResponse(content={"success": True, "files": generated_files})
        else:
            return JSONResponse(
                content={"success": False, "error": "Failed to generate any images"},
                status_code=500,
            )


def generate_two_pictograms_openai(keyword):
    """
    Helper function to generate exactly two pictograms with OpenAI using _03 and _04 suffixes.

    Args:
        keyword: The word or phrase to generate pictograms for

    Returns:
        JSONResponse with paths to the two generated images
    """
    return generate_pictogram_openai(
        keyword=keyword,
        generate_multiple=True,
        num_images=2,
        start_index=3,  # Start at 3 to create _03 and _04 suffixes
    )
