import os
from io import BytesIO
from pathlib import Path

from fastapi.responses import JSONResponse
from google import genai
from google.genai import types
from loguru import logger
from PIL import Image

from app.core import settings

api_key = settings.GOOGLE_API_KEY
pictogram_dir = Path("app/assets/pictograms")


SYSTEM_PROMPT = (
    "You are an AI image generator specializing in creating high-quality pictograms for Augmentative and Alternative Communication (AAC) systems, following established AAC symbol design guidelines. Your pictograms will be used by individuals with communication difficulties, including children with autism, developmental disabilities, and adults with acquired communication challenges.\n\n"
    "TECHNICAL SPECIFICATIONS:\n"
    "- Create a 512x512 pixel image with a completely transparent background\n"
    "- NO borders or frames around the pictogram (it will be placed inside a card element)\n"
    "- Use clean vector-style graphics with smooth lines and shapes\n"
    "- Maintain consistent line thickness (3-5 points for main outlines, 2-3 points for interior details)\n"
    "- Ensure a minimum contrast ratio of 7:1 between elements for maximum visibility\n"
    "- Use a limited, purposeful color palette (3-5 colors maximum) with strong visual differentiation\n\n"
    "DESIGN PRINCIPLES:\n"
    "- Create symbols with high 'iconicity' - the meaning should be immediately guessable\n"
    "- Display objects in their canonical positions (viewpoint where their most prominent features are clearly visible)\n"
    "- Use simplified representations that maintain essential identifying features\n"
    "- Avoid unnecessary details, textures, or decorative elements that don't contribute to meaning\n"
    "- Design with cultural neutrality in mind unless specifically requested otherwise\n"
    "- NEVER include text within the image (the system will add labels separately)\n"
    "- Ensure the symbol works at different sizes and maintains clarity when scaled down\n\n"
    "VISUAL STYLE:\n"
    "- Use clean, geometric shapes with smooth curves and minimal angles\n"
    "- Apply flat coloring without gradients, shadows, or 3D effects\n"
    "- Create a visually appealing, modern aesthetic while maintaining simplicity\n"
    "- Design with visual hierarchy - make the most important elements larger or more central\n"
    "- Maintain consistent visual weight and balance across the image\n"
    "- Use color purposefully to distinguish elements and enhance understanding\n\n"
    "DARK MODE COMPATIBILITY:\n"
    "- Use lighter, brighter colors that will stand out against dark backgrounds\n"
    "- Add thin white or light-colored outlines (1-2px) to elements when needed for visibility\n"
    "- Avoid very dark colors that would blend into dark backgrounds\n"
    "- Test visual contrast against both light and dark backgrounds\n"
    "- Maintain clarity and visibility when viewed in low-light environments\n\n"
    "- Use a 100% TRANSPARENT BACKGROUND with NO BORDERS, NO FRAMES, NO UI ELEMENTS\n\n"
    "ADAPTABILITY CONSIDERATIONS:\n"
    "- Design for clarity in both color and potential monochrome/high-contrast viewing\n"
    "- Ensure the symbol works well for users with different visual acuity levels\n"
    "- Consider how the symbol might be interpreted across different ages and cultures\n"
    "- Design with potential for personalization or modification in mind\n\n"
    "For each concept, generate ONE clear, visually appealing pictogram that best represents the given word or phrase, optimized for immediate recognition and understanding."
)

SYSTEM_PROMPT_2 = (
    "You are an AI image generator creating SINGLE, ISOLATED PICTOGRAMS for an AAC system. Each request should produce ONE CLEAR SYMBOL, not a communication board or interface.\n\n"
    "CRITICAL REQUIREMENTS:\n"
    "- Generate ONLY ONE isolated pictogram centered in the frame\n"
    "- Create a SINGLE SYMBOL with ABSOLUTELY NO TEXT in the image\n"
    "- Use a 100% TRANSPARENT BACKGROUND with NO BORDERS, NO FRAMES, NO UI ELEMENTS\n"
    "- DO NOT create screenshots, interfaces, communication boards, or multi-symbol layouts\n\n"
    "TECHNICAL SPECIFICATIONS:\n"
    "- Create a 512x512 pixel image with the pictogram centered\n"
    "- Use consistent line weights: 3-4 points for main outlines, 2 points for interior details\n"
    "- Maintain a minimum 7:1 contrast ratio between elements\n"
    "- Limit to 3-5 colors maximum with strong visual differentiation\n"
    "- Optimize for dark mode: use lighter colors and add thin light outlines where needed\n\n"
    "VISUAL STYLE FOR AAC PICTOGRAMS:\n"
    "- Create clean, simple, iconic representations using basic shapes\n"
    "- For 'come here': show a single figure with arm extended, using a clear beckoning gesture\n"
    "- Use bold, smooth lines with rounded corners and minimal detail\n"
    "- Apply flat coloring with no gradients, shadows, or 3D effects\n"
    "- Ensure the symbol is instantly recognizable from a distance and at smaller sizes\n"
    "- Use colors that stand out against dark backgrounds\n\n"
    "CONCEPTUAL CLARITY:\n"
    "- Focus on universal, culturally-neutral representations when possible\n"
    "- For action words (like 'come here'), use clear gestural representation\n"
    "- Emphasize the core meaning through visual hierarchy - make the action obvious\n"
    "- Design for immediate recognition by users of all cognitive abilities\n\n"
    "Remember: Generate ONLY the single pictogram representing the concept, not an interface or board containing multiple symbols. The image should look like ONE professional AAC symbol that could be placed on a button."
)


def generate_pictogram_google(
    keyword, output_filename=None, generate_multiple=False, num_images=2
):
    """
    Generate one or more pictograms for a given keyword.

    Args:
        keyword: The word or phrase to generate a pictogram for
        output_filename: Optional custom filename
        generate_multiple: Whether to generate multiple variations
        num_images: Number of images to generate when generate_multiple is True

    Returns:
        JSONResponse with success status and paths to generated images
    """
    # Initialize the Google GenAI client with API key
    client = genai.Client(api_key=api_key)

    # If not generating multiple images, use the original behavior
    if not generate_multiple:
        # Set the output filename to include the keyword if not provided
        if output_filename is None:
            output_filename = f"pic_{keyword}.png"

        # Create the complete prompt for image generation
        prompt = f"{SYSTEM_PROMPT}\n\nCreate a professional '{keyword}' pictogram that would work well in an AAC system. ONLY the pictogram itself with transparent background. NO borders, frames, or lines below the image. Optimize for dark mode with lighter colors that stand out against dark backgrounds."

        try:
            # Generate the image using Gemini
            # response = client.models.generate_content(
            #     model="gemini-2.0-flash-exp-image-generation",
            #     contents=prompt,
            #     config=types.GenerateContentConfig(
            #         response_modalities=["Text", "Image"]
            #     ),
            # )

            response = client.generate_content(
                model="gemini-1.5-flash",
                prompt=prompt,
                response_mime_type="image/png",
            )

            # Process and save the generated image
            for part in response.candidates[0].content.parts:
                if (
                    part.inline_data is not None
                    and part.inline_data.mime_type.startswith("image/")
                ):
                    # Extract the image data
                    image_data = part.inline_data.data
                    image = Image.open(BytesIO(image_data))

                    # Ensure the image has an alpha channel for transparency
                    if image.mode != "RGBA":
                        image = image.convert("RGBA")

                    # Save the image
                    file_path = pictogram_dir / output_filename
                    image.save(file_path)
                    logger.info(
                        f"Pictogram for '{keyword}' saved as '{output_filename}'."
                    )
                    return JSONResponse(
                        content={"success": True, "files": [str(file_path)]}
                    )

            logger.error("No images were found in the response.")
            return JSONResponse(
                content={"success": False, "error": "No images found in the response"},
                status_code=500,
            )

        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return JSONResponse(
                content={"success": False, "error": str(e)}, status_code=500
            )

    # Generate multiple images with numbered suffixes
    else:
        generated_files = []

        for i in range(1, num_images + 1):
            # Create numbered filename
            if output_filename is None:
                current_filename = f"pic_{keyword}_{i:02d}.png"
            else:
                base, ext = os.path.splitext(output_filename)
                current_filename = f"{base}_{i:02d}{ext}"

            # Alternate between the two prompts for more variation
            prompt_template = SYSTEM_PROMPT if i % 2 == 1 else SYSTEM_PROMPT_2
            prompt = f"{prompt_template}\n\nCreate a professional '{keyword}' pictogram that would work well in an AAC system. ONLY the pictogram itself with transparent background. NO borders, frames, or lines below the image. Optimize for dark mode with lighter colors that stand out against dark backgrounds."

            try:
                # Generate the image
                response = client.models.generate_content(
                    model="gemini-2.0-flash-exp-image-generation",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_modalities=["Text", "Image"]
                    ),
                )

                # Process and save the generated image
                image_saved = False
                for part in response.candidates[0].content.parts:
                    if (
                        part.inline_data is not None
                        and part.inline_data.mime_type.startswith("image/")
                    ):
                        # Extract the image data
                        image_data = part.inline_data.data
                        image = Image.open(BytesIO(image_data))

                        # Ensure the image has an alpha channel for transparency
                        if image.mode != "RGBA":
                            image = image.convert("RGBA")

                        # Save the image
                        file_path = pictogram_dir / current_filename
                        image.save(file_path)
                        generated_files.append(str(file_path))
                        logger.info(
                            f"Pictogram {i} for '{keyword}' saved as '{current_filename}'."
                        )
                        image_saved = True
                        break

                if not image_saved:
                    logger.error(f"No images were found in the response for image {i}.")

            except Exception as e:
                logger.error(f"An error occurred generating image {i}: {e}")

        if generated_files:
            return JSONResponse(content={"success": True, "files": generated_files})
        else:
            return JSONResponse(
                content={"success": False, "error": "Failed to generate any images"},
                status_code=500,
            )


def generate_two_pictograms_google(keyword):
    """
    Helper function to generate exactly two pictograms with _01 and _02 suffixes.

    Args:
        keyword: The word or phrase to generate pictograms for

    Returns:
        JSONResponse with paths to the two generated images
    """
    return generate_pictogram_google(
        keyword=keyword, generate_multiple=True, num_images=2
    )
