import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from loguru import logger
from sqlmodel import Session, select

from app.core.config import settings
from app.models import Audio, Keyword, Voice
from app.services.bg_remover import remove_background
from app.services.open_symbols_downloader import generate_pictogram_open_symbols
from app.services.photoroom_rmbg import remove_background as remove_background_photoroom
from app.services.pictogram_generator_google import generate_two_pictograms_google
from app.services.pictogram_generator_ideogram import generate_pictogram_ideogram
from app.services.pictogram_generator_openai import generate_two_pictograms_openai
from app.services.voice_generator import generate_voice


class KeywordContentGenerator:
    """
    Service to generate content (pictograms and audio) for keywords.
    """

    def __init__(self, db: Session):
        self.db = db
        # Lazy import ImageJudge to avoid circular dependency
        from app.services.image_judge import ImageJudge

        self.image_judge = ImageJudge()

        # Ensure directories exist
        self.pictograms_dir = Path("app/assets/pictograms")
        self.pictograms_dir_final = Path("app/assets/pictograms_final")
        self.audio_dir = Path("app/assets/audio")
        self.pictograms_dir.mkdir(parents=True, exist_ok=True)
        self.pictograms_dir_final.mkdir(parents=True, exist_ok=True)
        self.audio_dir.mkdir(parents=True, exist_ok=True)

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
        # Get keyword ID if keyword exists in database, if not make a new one
        db_keyword = self.db.exec(
            select(Keyword).where(Keyword.name == keyword.name)
        ).first()
        if not db_keyword:
            db_keyword = Keyword(name=keyword.name)
            self.db.add(db_keyword)
            self.db.commit()
            self.db.refresh(db_keyword)

        # 1. Generate pictures
        logger.info(f"Generating pictures for keyword: {db_keyword.name}")
        picture_files = await self._generate_pictures(db_keyword.name)

        # 2. Judge the best picture
        logger.info(f"Judging the best picture for keyword: {db_keyword.name}")
        best_picture_path, explanation = self._judge_pictures(db_keyword.name)
        output_path = Path(
            f"{self.pictograms_dir_final}/pic_{db_keyword.name}_final.png"
        )
        # 2.1. Remove background from the best picture
        if best_picture_path:
            logger.info(
                f"Removing background from the best picture: {best_picture_path}"
            )
            best_picture_path = remove_background(best_picture_path, output_path)

        # 3. Set the pictogram URL
        if best_picture_path:
            # Convert Path object to string before storing in database
            db_keyword.pictogram_url = str(output_path)
        elif picture_files:
            db_keyword.pictogram_url = picture_files[0]
        else:
            logger.error(f"No pictures generated for keyword: {db_keyword.name}")

        self.db.add(db_keyword)
        self.db.commit()
        self.db.refresh(db_keyword)

        # 4. Generate voice clips
        logger.info(f"Generating voice clips for keyword: {db_keyword.name}")
        audio_paths = self._generate_voice_clips(db_keyword.name, db_keyword.language)

        # 5. Save audio files to database
        audio = self._save_audio_to_db(db_keyword.id, audio_paths)
        if audio:
            db_keyword.audio_id = audio.id
            self.db.add(db_keyword)
            self.db.commit()
            self.db.refresh(db_keyword)

        return db_keyword

    async def _generate_pictures(self, keyword_name: str) -> List[str]:
        """
        Generate pictures for the keyword and return file paths:
        # - 2 from Google Gemini
        # - 2 from Open Symbols API
        - 4 from Ideogram, 2 from Open Symbols
        """
        generated_files = []

        ############################################### GOOGLE AND OPENAI - START ###############################################
        # # 1. Generate 2 images with Google
        # google_files = []
        # try:
        #     logger.info(f"Generating 2 Google images for keyword: {keyword_name}")
        #     generate_two_pictograms_google(keyword=keyword_name)

        #     # Add expected filenames based on naming convention
        #     google_files = [f"pic_{keyword_name}_01.png", f"pic_{keyword_name}_02.png"]
        #     generated_files.extend(google_files)
        #     logger.info(f"Added Google images: {google_files}")

        # except Exception as e:
        #     logger.error(
        #         f"Exception generating Google pictures for {keyword_name}: {e}"
        #     )

        # # 1.5. Generate 2 images with OpenAI
        # openai_files = []
        # try:
        #     logger.info(f"Generating 2 OpenAI images for keyword: {keyword_name}")
        #     generate_two_pictograms_openai(keyword=keyword_name)

        #     # Add expected filenames based on naming convention
        #     openai_files = [f"pic_{keyword_name}_03.png", f"pic_{keyword_name}_04.png"]
        #     generated_files.extend(openai_files)
        #     logger.info(f"Added OpenAI images: {openai_files}")

        # except Exception as e:
        #     logger.error(
        #         f"Exception generating OpenAI pictures for {keyword_name}: {e}"
        #     )
        ############################################### GOOGLE AND OPENAI - END ###############################################

        # IDEOGRAM
        ideogram_files = []
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

        # OPEN SYMBOLS
        # os_files = []
        # try:
        #     logger.info(f"Generating 2 Open Symbols images for keyword: {keyword_name}")
        #     generate_pictogram_open_symbols(
        #         keyword=keyword_name, generate_multiple=True, num_images=2
        #     )

        #     # Add expected filenames based on naming convention
        #     os_files = [f"pic_{keyword_name}_05.png", f"pic_{keyword_name}_06.png"]
        #     generated_files.extend(os_files)
        #     logger.info(f"Added Open Symbols images: {os_files}")

        # except Exception as e:
        #     logger.error(
        #         f"Exception generating Open Symbols pictures for {keyword_name}: {e}"
        #     )

        # Return all generated files
        logger.info(
            f"Total images generated for {keyword_name}: {len(generated_files)}"
        )
        return generated_files

    def _judge_pictures(self, keyword_name: str) -> Tuple[Optional[str], str]:
        """Judge the best picture from the generated ones."""
        try:
            logger.info(f"Judging pictures for keyword: {keyword_name}")

            # First try using the AI-based image judge
            best_image_path, explanation = self.image_judge.find_best_image_for_keyword(
                keyword_name
            )
            return best_image_path, explanation

        except Exception as e:
            logger.error(f"Exception judging pictures for {keyword_name}: {e}")

            # Fallback: pick a pictogram manually based on naming convention
            # We'll prefer in this order: Google (01-02), OpenSymbols (05-06)
            fallback_paths = []

            # Try to find files with expected naming patterns
            for index in range(1, 7):
                filename = f"pic_{keyword_name}_{index:02d}.png"
                file_path = os.path.join(self.pictograms_dir, filename)
                if os.path.exists(file_path):
                    fallback_paths.append(file_path)

            # Return the first file found, or None if no files exist
            if fallback_paths:
                return fallback_paths[0], "Fallback selection due to API error"

            return None, f"Error judging pictures and no fallback found: {str(e)}"

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

        # Generate voices based on language
        if language == "en":
            # English voices
            try:
                logger.info(f"Generating man voice for keyword: {keyword_name}")
                file_path = generate_voice(keyword_name, Voice.MAN)
                if file_path and os.path.exists(file_path):
                    voice_paths["voice_man"] = file_path
                    logger.info(f"Successfully generated man voice: {file_path}")
                else:
                    logger.error(f"Voice generation returned invalid path: {file_path}")
            except Exception as e:
                logger.error(f"Error generating man voice for {keyword_name}: {str(e)}")

            try:
                logger.info(f"Generating woman voice for keyword: {keyword_name}")
                file_path = generate_voice(keyword_name, Voice.WOMAN)
                if file_path and os.path.exists(file_path):
                    voice_paths["voice_woman"] = file_path
                    logger.info(f"Successfully generated woman voice: {file_path}")
                else:
                    logger.error(f"Voice generation returned invalid path: {file_path}")
            except Exception as e:
                logger.error(f"Error generating woman voice for {keyword_name}: {e}")

        elif language == "vl":
            # Flemish voices
            try:
                logger.info(f"Generating Flemish man voice for keyword: {keyword_name}")
                file_path = generate_voice(keyword_name, Voice.MAN_FLEMISH)
                if file_path and os.path.exists(file_path):
                    voice_paths["voice_man"] = file_path
                    logger.info(
                        f"Successfully generated Flemish man voice: {file_path}"
                    )
                else:
                    logger.error(f"Voice generation returned invalid path: {file_path}")
            except Exception as e:
                logger.error(
                    f"Error generating Flemish man voice for {keyword_name}: {e}"
                )

            try:
                logger.info(
                    f"Generating Flemish woman voice for keyword: {keyword_name}"
                )
                file_path = generate_voice(keyword_name, Voice.WOMAN_FLEMISH)
                if file_path and os.path.exists(file_path):
                    voice_paths["voice_woman"] = file_path
                    logger.info(
                        f"Successfully generated Flemish woman voice: {file_path}"
                    )
                else:
                    logger.error(f"Voice generation returned invalid path: {file_path}")
            except Exception as e:
                logger.error(
                    f"Error generating Flemish woman voice for {keyword_name}: {e}"
                )

        logger.info(f"Generated voice files for {keyword_name}: {voice_paths}")
        return voice_paths

    def _save_audio_to_db(
        self, keyword_id: int, audio_paths: Dict[str, str]
    ) -> Optional[Audio]:
        """Save audio to the database."""
        if not (audio_paths.get("voice_man") or audio_paths.get("voice_woman")):
            logger.warning(f"No audio files to save for keyword_id: {keyword_id}")
            return None

        try:
            # Create and save audio record
            audio = Audio(
                voice_man=(
                    str(audio_paths.get("voice_man"))
                    if audio_paths.get("voice_man")
                    else None
                ),
                voice_woman=(
                    str(audio_paths.get("voice_woman"))
                    if audio_paths.get("voice_woman")
                    else None
                ),
                keyword_id=keyword_id,
            )
            self.db.add(audio)
            self.db.commit()
            self.db.refresh(audio)

            logger.info(f"Successfully saved audio for keyword {keyword_id}")
            return audio
        except Exception as e:
            logger.error(f"Error saving audio to database: {e}")
            return None
