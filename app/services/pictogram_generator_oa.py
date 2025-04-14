import os
from pathlib import Path

import requests
from fastapi.responses import FileResponse
from loguru import logger
from openai import OpenAI

from app.core import settings

api_key = settings.OPENAI_API_KEY
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
    "- Limit to 3-5 colors maximum with strong visual differentiation\n\n"
    "VISUAL STYLE FOR AAC PICTOGRAMS:\n"
    "- Create clean, simple, iconic representations using basic shapes\n"
    "- For 'come here': show a single figure with arm extended, using a clear beckoning gesture\n"
    "- Use bold, smooth lines with rounded corners and minimal detail\n"
    "- Apply flat coloring with no gradients, shadows, or 3D effects\n"
    "- Ensure the symbol is instantly recognizable from a distance and at smaller sizes\n\n"
    "CONCEPTUAL CLARITY:\n"
    "- Focus on universal, culturally-neutral representations when possible\n"
    "- For action words (like 'come here'), use clear gestural representation\n"
    "- Emphasize the core meaning through visual hierarchy - make the action obvious\n"
    "- Design for immediate recognition by users of all cognitive abilities\n\n"
    "Remember: Generate ONLY the single pictogram representing the concept, not an interface or board containing multiple symbols. The image should look like ONE professional AAC symbol that could be placed on a button."
)


def generate_pictogram(keyword, output_filename=None):
    # Combine the system prompt with the user-provided keyword
    final_prompt = f"{SYSTEM_PROMPT}\n\nCreate a professional '{keyword}' pictogram that would work well in an AAC system. ONLY the pictogram itself with transparent background. NO borders, frames, or lines below the image."

    # Instantiate the OpenAI client with your API key
    client = OpenAI(api_key=api_key)

    try:
        # Generate the pictogram using the latest OpenAI image generation API (DALL-E 3)
        response = client.images.generate(
            model="dall-e-3",
            prompt=final_prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )

        # Retrieve the image URL from the response
        image_url = response.data[0].url
        logger.info(f"Generated Image URL: {image_url}")

        if output_filename is None:
            output_filename = f"pic_{keyword}.png"

        # Download the image and save it locally
        image_data = requests.get(image_url).content
        with open(pictogram_dir / output_filename, "wb") as f:
            f.write(image_data)

        logger.info(f"Pictogram for '{keyword}' saved as '{output_filename}'.")
        return FileResponse(pictogram_dir / output_filename)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
