import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from loguru import logger

from app.core import SupabaseCRUD, get_supabase_client, settings
from app.models import Keyword, Voice
from app.services.bg_remover import remove_background
from app.services.do_bucket import DOSpacesClient
from app.services.pictogram_generator_ideogram import generate_pictogram_ideogram
from app.services.voice_generator import generate_voice


class KeywordContentGenerator:
    """
    Service to generate content (pictograms and audio) for keywords.
    """

    def __init__(self):
        # Lazy import ImageJudge to avoid circular dependency
        from app.services.image_judge import ImageJudge

        self.image_judge = ImageJudge()
        self.do_client = DOSpacesClient()

        # Ensure directories exist
        self._initialize_directories()

        # Initialize Supabase client
        self.supabase_client = get_supabase_client()
        self.supabase_crud = SupabaseCRUD(self.supabase_client)

    def _initialize_directories(self) -> None:
        """Initialize necessary directories for storing assets."""
        self.pictograms_dir = Path("app/assets/pictograms")
        self.pictograms_dir_final = Path("app/assets/pictograms_final")
        self.audio_dir = Path("app/assets/audio")

        self.pictograms_dir.mkdir(parents=True, exist_ok=True)
        self.pictograms_dir_final.mkdir(parents=True, exist_ok=True)
        self.audio_dir.mkdir(parents=True, exist_ok=True)

    def _cleanup_local_file(self, file_path: Path) -> None:
        """Remove a local file if it exists."""
        try:
            if file_path and file_path.exists():
                file_path.unlink()
                logger.info(f"Removed local file: {file_path}")
            else:
                logger.debug(f"File does not exist, no cleanup needed: {file_path}")
        except Exception as e:
            logger.error(f"Error removing local file {file_path}: {e}")

    def _cleanup_keyword_local_files(self, keyword_name: str) -> None:
        """Clean up all local files related to a keyword."""
        try:
            # Clean up all generated pictograms
            for index in range(1, 5):
                filename = f"pic_{keyword_name}_{index:02d}.png"
                file_path = self.pictograms_dir / filename
                self._cleanup_local_file(file_path)

            # Clean up the final processed pictogram
            final_path = self.pictograms_dir_final / f"pic_{keyword_name}_final.png"
            self._cleanup_local_file(final_path)

            logger.info(
                f"Cleaned up all local pictogram files for keyword: {keyword_name}"
            )
        except Exception as e:
            logger.error(f"Error cleaning up pictogram files for {keyword_name}: {e}")

    async def generate_content_for_keyword(self, keyword: Keyword) -> Keyword:
        """
        Generate pictogram and audio for a keyword.

        Steps:
        1. Generate pictures for the keyword
        2. Judge the best picture
        3. Generate voice clips
        4. Update the keyword with pictogram and audio
        5. Return the updated keyword
        """
        try:
            # Get or create keyword in database
            db_keyword = self._get_or_create_keyword(keyword)

            # 1. Generate pictures
            logger.info(f"Generating pictures for keyword: {db_keyword['name']}")
            await self._generate_pictures(db_keyword["name"])

            # 2. Process the best picture
            db_keyword = await self._process_best_picture(db_keyword)

            # 3. Generate and save voice clips
            db_keyword = await self._process_voice_clips(db_keyword)

            logger.info(
                f"Content generation completed successfully for keyword: {db_keyword['name']}"
            )
            return Keyword.model_validate(db_keyword)
        except Exception as e:
            logger.error(f"Error in generate_content_for_keyword: {e}", exc_info=True)
            # Re-raise to allow the background task system to log it
            raise

    def _get_or_create_keyword(self, keyword: Keyword) -> dict:
        """Get existing keyword or create a new one."""
        db_keywords = self.supabase_crud.read_filtered("keywords", "name", keyword.name)
        logger.info(f"db_keywords: {db_keywords}")

        # Check if we found any matching keywords
        if db_keywords and len(db_keywords) > 0:
            # Use the first matching keyword
            db_keyword = db_keywords[0]
            logger.info(f"Found existing keyword: {db_keyword}")
        else:
            # Create a dictionary from the keyword object for JSON serialization
            keyword_dict = {"name": keyword.name}
            if hasattr(keyword, "language"):
                keyword_dict["language"] = keyword.language

            self.supabase_crud.create("keywords", keyword_dict)
            db_keywords = self.supabase_crud.read_filtered(
                "keywords", "name", keyword.name
            )

            if db_keywords and len(db_keywords) > 0:
                db_keyword = db_keywords[0]
                logger.info(f"Created new keyword: {db_keyword}")
            else:
                raise ValueError(f"Failed to create keyword: {keyword.name}")

        return db_keyword

    async def _process_best_picture(self, keyword: dict) -> dict:
        """Process, upload and save the best picture for the keyword."""
        # Judge the best picture
        logger.info(f"Judging the best picture for keyword: {keyword['name']}")
        best_picture_path, explanation = self._judge_pictures(keyword["name"])

        if not best_picture_path:
            logger.error(f"No suitable picture found for keyword: {keyword['name']}")
            return keyword

        # Process the selected picture
        output_path = self.pictograms_dir_final / f"pic_{keyword['name']}_final.png"

        try:
            # Remove background from the best picture
            logger.info(
                f"Removing background from the best picture: {best_picture_path}"
            )
            remove_background(best_picture_path, output_path)

            # Upload the processed image - using output_path directly
            filename = f"pic_{keyword['name']}_final.png"
            self._upload_image_to_spaces(output_path, filename)

            # Get and save the CDN URL
            uploaded_image_url = self.do_client.get_cdn_url_for_image(filename)
            if uploaded_image_url:
                keyword["pictogram_url"] = uploaded_image_url
                self.supabase_crud.update("keywords", keyword["id"], keyword)
                logger.info(f"Updated keyword: {keyword}")

                # Clean up local files now that we have the CDN URL
                self._cleanup_keyword_local_files(keyword["name"])
            else:
                logger.error(f"Failed to get CDN URL for image: {filename}")
        except Exception as e:
            logger.error(f"Error processing picture for {keyword['name']}: {e}")

        return keyword

    def _upload_image_to_spaces(self, local_path: Path, filename: str) -> bool:
        """Upload an image to Digital Ocean Spaces."""
        try:
            logger.debug(f"Uploading image to Digital Ocean Spaces: {local_path}")
            self.do_client.upload_image(
                local_file_path=local_path,
                destination_key=filename,
            )

            # Verify upload was successful
            if self.do_client.check_file_exists(f"pictograms/{filename}"):
                logger.info(f"Image pictograms/{filename} successfully uploaded")
                return True
            else:
                logger.error(f"Image pictograms/{filename} upload verification failed")
                return False
        except Exception as e:
            logger.error(f"Failed to upload image {filename}: {e}")
            return False

    async def _process_voice_clips(self, keyword: dict) -> dict:
        """Generate, upload and save voice clips for the keyword."""
        # Generate voice clips
        language = keyword.get("language", "en")  # Default to 'en' if language not set
        logger.info(f"Generating voice clips for keyword: {keyword['name']}")
        audio_paths = self._generate_voice_clips(keyword["name"], language)

        # Upload audio files and get URLs
        audio_urls = self._upload_audio_files(audio_paths)

        # Save to database
        audio = self._save_audio_to_db(keyword["id"], audio_urls)
        if audio:
            keyword["audio_id"] = audio["id"]  # Access id as a dictionary key
            self.supabase_crud.update("keywords", keyword["id"], keyword)
            logger.info(f"Updated keyword: {keyword}")

            # Clean up local audio files now that they're saved in the database
            for voice_type, audio_path in audio_paths.items():
                if audio_path and audio_urls.get(voice_type):
                    self._cleanup_local_file(Path(audio_path))

        return keyword

    def _upload_audio_files(self, audio_paths: Dict[str, str]) -> Dict[str, str]:
        """Upload audio files to Digital Ocean Spaces and return URLs."""
        audio_urls = {}

        for voice_type, audio_path in audio_paths.items():
            if not audio_path:
                continue

            try:
                audio_filename = os.path.basename(audio_path)
                self.do_client.upload_audio(
                    local_file_path=audio_path,
                    destination_key=f"voice_clips/{audio_filename}",
                )
                logger.info(
                    f"Uploaded audio file to Digital Ocean Spaces: {audio_filename}"
                )

                cdn_url = self.do_client.get_cdn_url_for_audio(f"{audio_filename}")
                if cdn_url:
                    audio_urls[voice_type] = cdn_url
                else:
                    logger.error(f"Failed to get CDN URL for audio: {audio_filename}")
            except Exception as e:
                logger.error(f"Error uploading audio file {audio_path}: {e}")

        return audio_urls

    async def _generate_pictures(self, keyword_name: str) -> List[str]:
        """
        Generate pictures for the keyword and return file paths.
        Currently using 4 images from Ideogram.
        """
        generated_files = []

        # Generate Ideogram images
        try:
            logger.info(f"Generating 4 Ideogram images for keyword: {keyword_name}")
            generate_pictogram_ideogram(keyword=keyword_name)

            # Add expected filenames based on naming convention
            ideogram_files = [
                f"pic_{keyword_name}_01.png",
                f"pic_{keyword_name}_02.png",
                f"pic_{keyword_name}_03.png",
                f"pic_{keyword_name}_04.png",
            ]
            generated_files.extend(ideogram_files)
            logger.info(f"Added Ideogram images: {ideogram_files}")

        except Exception as e:
            logger.error(
                f"Exception generating Ideogram pictures for {keyword_name}: {e}"
            )

        logger.info(
            f"Total images generated for {keyword_name}: {len(generated_files)}"
        )
        return generated_files

    def _judge_pictures(self, keyword_name: str) -> Tuple[Optional[Path], str]:
        """Judge the best picture from the generated ones."""
        try:
            logger.info(f"Judging pictures for keyword: {keyword_name}")

            # First try using the AI-based image judge
            best_image_path, explanation = self.image_judge.find_best_image_for_keyword(
                keyword_name
            )

            # Ensure best_image_path is a Path object if it's a string
            if isinstance(best_image_path, str):
                best_image_path = Path(best_image_path)

            # Verify the path exists
            if best_image_path and best_image_path.exists():
                logger.info(f"Selected best image: {best_image_path}")
                return best_image_path, explanation
            elif best_image_path:
                logger.warning(f"Selected image doesn't exist: {best_image_path}")
            else:
                logger.warning(f"Image judge returned None for keyword: {keyword_name}")

            # Fallback if image judge failed or returned None
            return self._fallback_image_selection(keyword_name)

        except Exception as e:
            logger.error(f"Exception judging pictures for {keyword_name}: {e}")
            return self._fallback_image_selection(keyword_name)

    def _fallback_image_selection(
        self, keyword_name: str
    ) -> Tuple[Optional[Path], str]:
        """Select a fallback image based on naming convention."""
        fallback_paths = []

        # Try to find files with expected naming patterns
        for index in range(1, 5):  # We're using 4 Ideogram images
            filename = f"pic_{keyword_name}_{index:02d}.png"
            file_path = self.pictograms_dir / filename
            if file_path.exists():
                fallback_paths.append(file_path)

        # Return the first file found, or None if no files exist
        if fallback_paths:
            logger.info(f"Using fallback image selection: {fallback_paths[0]}")
            return fallback_paths[0], "Fallback selection due to judge error"

        logger.error(f"No pictures found for keyword: {keyword_name}")
        return None, f"No pictures found for keyword: {keyword_name}"

    def _generate_voice_clips(
        self, keyword_name: str, language: str = "en"
    ) -> Dict[str, str]:
        """
        Generate voice clips for the keyword in the specified language.
        Returns a dictionary with voice paths for man and woman voices.
        """
        voice_paths = {
            "voice_man": None,
            "voice_woman": None,
        }

        # Check if API key is available
        if not settings.ELEVEN_LABS_API_KEY:
            logger.error("Missing ELEVEN_LABS_API_KEY environment variable")
            return voice_paths

        voice_configs = self._get_voice_configs(language)

        for voice_type, voice_id in voice_configs.items():
            try:
                logger.info(
                    f"Generating {voice_type} voice for keyword: {keyword_name}"
                )
                file_path = generate_voice(keyword_name, voice_id)

                if file_path and os.path.exists(file_path):
                    voice_paths[voice_type] = file_path
                    logger.info(
                        f"Successfully generated {voice_type} voice: {file_path}"
                    )
                else:
                    logger.error(f"Voice generation returned invalid path: {file_path}")
            except Exception as e:
                logger.error(
                    f"Error generating {voice_type} voice for {keyword_name}: {e}"
                )

        return voice_paths

    def _get_voice_configs(self, language: str) -> Dict[str, Voice]:
        """Get voice configurations based on language."""
        if language == "en":
            return {"voice_man": Voice.MAN, "voice_woman": Voice.WOMAN}
        elif language == "vl":
            return {"voice_man": Voice.MAN_FLEMISH, "voice_woman": Voice.WOMAN_FLEMISH}
        else:
            logger.warning(f"Unsupported language: {language}, defaulting to English")
            return {"voice_man": Voice.MAN, "voice_woman": Voice.WOMAN}

    def _save_audio_to_db(
        self, keyword_id: int, audio_paths: Dict[str, str]
    ) -> Optional[dict]:
        """Save audio to the Supabase database."""
        if not (audio_paths.get("voice_man") or audio_paths.get("voice_woman")):
            logger.warning(f"No audio files to save for keyword_id: {keyword_id}")
            return None

        try:
            # Create audio record for Supabase
            audio_dict = {
                "voice_man": audio_paths.get("voice_man"),
                "voice_woman": audio_paths.get("voice_woman"),
                "keyword_id": keyword_id,
            }

            # Insert into Supabase
            result = self.supabase_crud.create("audio_files", audio_dict)

            # In our updated implementation, result is directly the dictionary
            if result and "id" in result:
                audio_id = result["id"]
                logger.info(
                    f"Successfully saved audio to Supabase for keyword {keyword_id}, audio ID: {audio_id}"
                )
                return {"id": audio_id, **audio_dict}
            else:
                logger.error(f"Error saving audio to Supabase: {result}")
                return None

        except Exception as e:
            logger.error(f"Error saving audio to database: {e}")
            return None
