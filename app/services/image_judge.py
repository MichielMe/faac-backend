import base64
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import openai
from loguru import logger

from app.core import settings


class ImageJudge:
    """
    A service that judges and selects the best image from a group of similar images
    based on evaluation using OpenAI's Vision API.
    """

    def __init__(self, pictograms_dir: str = "app/assets/pictograms"):
        """
        Initialize the ImageJudge service.

        Args:
            pictograms_dir: Path to the directory containing pictogram images
        """
        self.pictograms_dir = Path(pictograms_dir)

        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o"  # Updated to use the newer model

    def group_images_by_keyword(self) -> Dict[str, List[Path]]:
        """
        Group images in the pictograms directory by their keywords.

        Returns:
            A dictionary mapping keywords to lists of image paths
        """
        images_by_keyword = {}

        # Get all PNG files in the pictograms directory
        png_files = list(self.pictograms_dir.glob("*.png"))

        # Extract keywords from filenames and group images
        for image_path in png_files:
            # Extract keyword from filename (text between "pic_" and ".png" or any trailing numbers/variants)
            filename = image_path.name
            match = re.match(r"pic_(.*?)(?:_\d+)?\.png", filename)

            if match:
                keyword = match.group(1)
            else:
                # Handle files that don't match the expected pattern
                keyword = image_path.stem.replace("pic_", "")

            if keyword not in images_by_keyword:
                images_by_keyword[keyword] = []

            images_by_keyword[keyword].append(image_path)

        return images_by_keyword

    def encode_image(self, image_path: Path) -> str:
        """
        Encode an image to base64 for API submission.

        Args:
            image_path: Path to the image file

        Returns:
            Base64-encoded image data
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def judge_images(
        self, image_paths: List[Path], criteria: Optional[str] = None
    ) -> Tuple[Path, str]:
        """
        Judge a group of images using OpenAI's Vision API and return the best one.

        Args:
            image_paths: List of image paths to judge
            criteria: Optional criteria for judging (defaults to clarity and effectiveness)

        Returns:
            Tuple of (best_image_path, explanation)
        """
        if not image_paths:
            raise ValueError("No images provided for judging")

        if len(image_paths) == 1:
            return image_paths[0], "Only one image available"

        # Prepare the image data for the API
        base64_images = [self.encode_image(path) for path in image_paths]

        # Create content array for the new API format
        content = [
            {
                "type": "input_text",
                "text": f"I'm going to show you {len(image_paths)} pictogram images. "
                f"These are AAC (Augmentative and Alternative Communication) pictograms "
                f"that need to be clear, simple, and effective for communication. "
                f"Please evaluate them and tell me which one is the best based on: "
                f"1. Visual clarity and simplicity "
                f"2. Effectiveness in conveying meaning "
                f"3. Emotional appropriateness "
                f"4. Overall quality as a communication pictogram",
            }
        ]

        # Add each image with its identifier
        for i, base64_image in enumerate(base64_images):
            content.append(
                {
                    "type": "input_image",
                    "image_url": f"data:image/png;base64,{base64_image}",
                    "detail": "high",
                }
            )
            content.append(
                {"type": "input_text", "text": f"Image {i+1}: {image_paths[i].name}"}
            )

        # Add the final question
        content.append(
            {
                "type": "input_text",
                "text": "Which image is the best pictogram for clear communication? "
                "Please respond with the image number (1, 2, etc.) and a brief explanation why.",
            }
        )

        try:
            # Using the new responses API format
            response = self.client.responses.create(
                model=self.model, input=[{"role": "user", "content": content}]
            )

            # Extract the result from the API response
            result = response.output_text

            # Parse the response to get the best image
            match = re.search(r"Image (\d+)", result)
            if match:
                best_index = int(match.group(1)) - 1
                if 0 <= best_index < len(image_paths):
                    return image_paths[best_index], result

            # If parsing fails, return the first image with the explanation
            logger.warning(
                "Failed to parse best image from response, defaulting to first image"
            )
            return image_paths[0], result

        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            return image_paths[0], f"Error during judgment: {str(e)}"

    def find_best_image_for_keyword(self, keyword: str) -> Tuple[Optional[Path], str]:
        """
        Find the best image for a given keyword.

        Args:
            keyword: The keyword to search for

        Returns:
            Tuple of (best_image_path, explanation)
        """
        # Group images by keyword
        grouped_images = self.group_images_by_keyword()

        # Search for images with the given keyword
        matching_images = []
        for k, images in grouped_images.items():
            if keyword.lower() in k.lower():
                matching_images.extend(images)

        if not matching_images:
            return None, f"No images found for keyword: {keyword}"

        # Judge the images and get the best one
        return self.judge_images(matching_images)
