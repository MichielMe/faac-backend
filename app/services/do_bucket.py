"""
Digital Ocean Spaces Client

Provides a clean interface to interact with Digital Ocean Spaces object storage and CDN.
"""

import os
from typing import Any, Dict, Optional

import boto3
import botocore.exceptions

from app.core import settings


class DOSpacesClient:
    """Client for interacting with Digital Ocean Spaces object storage service.

    This class provides methods for uploading, downloading, and managing files
    in a Digital Ocean Spaces bucket, including generating URLs and checking file existence.
    """

    def __init__(
        self,
        spaces_key: str = settings.SPACES_KEY,
        spaces_secret: str = settings.SPACES_SECRET,
        bucket: str = settings.BUCKET,
        region: str = settings.REGION,
    ):
        """Initialize the Digital Ocean Spaces client.

        Args:
            spaces_key: DO Spaces API key
            spaces_secret: DO Spaces API secret
            bucket: Default bucket name
            region: DO Spaces region
        """
        self.spaces_key = spaces_key
        self.spaces_secret = spaces_secret
        self.bucket = bucket
        self.region = region

        # Initialize boto3 client
        session = boto3.session.Session()
        self.client = session.client(
            "s3",
            region_name=self.region,
            endpoint_url=f"https://{self.region}.digitaloceanspaces.com",
            aws_access_key_id=self.spaces_key,
            aws_secret_access_key=self.spaces_secret,
        )

    def upload_file(
        self,
        local_file_path: str,
        destination_key: str,
        extra_args: Optional[Dict[str, Any]] = None,
        public: bool = False,
        bucket: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Upload a file to Digital Ocean Spaces.

        Args:
            local_file_path: Path to the file on local filesystem
            destination_key: Path/name for the file in the bucket
            extra_args: Optional dict with additional arguments like ContentType
            public: If True, sets ACL to public-read for public access
            bucket: Optional bucket name override

        Returns:
            Dict with upload result and URLs if successful
        """
        try:
            bucket = bucket or self.bucket

            # Set up ACL if public access requested
            args = extra_args or {}
            if public:
                args["ACL"] = "public-read"

            # Upload the file
            response = self.client.upload_file(
                Filename=local_file_path,
                Bucket=bucket,
                Key=destination_key,
                ExtraArgs=args,
            )

            # Generate URLs for the uploaded file
            standard_url = self._construct_standard_url(destination_key, bucket)
            cdn_url = self._construct_cdn_url(destination_key, bucket)

            return {
                "success": True,
                "response": response,
                "url": standard_url,
                "cdn_url": cdn_url,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def upload_image(
        self,
        local_file_path: str,
        destination_key: Optional[str] = None,
        image_type: str = "png",
        folder: str = "pictograms",
        public: bool = True,
        bucket: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Upload an image file with proper content type.

        Args:
            local_file_path: Path to the image file on local filesystem
            destination_key: Path/name for the file in the bucket (defaults to filename)
            image_type: Image type (png, jpg, etc.) to determine content type
            folder: Folder to place the image in
            public: If True, sets ACL to public-read for public access
            bucket: Optional bucket name override

        Returns:
            Dict with upload result and URLs if successful
        """
        try:
            bucket = bucket or self.bucket

            # If no destination key provided, use the filename from the local path
            if destination_key is None:
                destination_key = os.path.basename(local_file_path)

            # Ensure it's in the specified folder
            if folder and not destination_key.startswith(f"{folder}/"):
                destination_key = f"{folder}/{destination_key}"

            # Make sure the file has the right extension
            if not destination_key.lower().endswith(f".{image_type.lower()}"):
                destination_key += f".{image_type.lower()}"

            # Set up content type
            extra_args = {"ContentType": self._get_image_content_type(image_type)}

            # Use the generic upload method
            return self.upload_file(
                local_file_path=local_file_path,
                destination_key=destination_key,
                extra_args=extra_args,
                public=public,
                bucket=bucket,
            )
        except Exception as e:
            return {"success": False, "error": str(e)}

    def upload_audio(
        self,
        local_file_path: str,
        destination_key: Optional[str] = None,
        folder: str = "voice_clips",
        public: bool = True,
        bucket: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Upload an audio file with proper content type.

        Args:
            local_file_path: Path to the audio file on local filesystem
            destination_key: Path/name for the file in the bucket (defaults to filename)
            folder: Folder to place the audio in (default: voice_clips)
            public: If True, sets ACL to public-read for public access
            bucket: Optional bucket name override

        Returns:
            Dict with upload result and URLs if successful
        """
        try:
            bucket = bucket or self.bucket

            # If no destination key provided, use the filename from the local path
            if destination_key is None:
                destination_key = os.path.basename(local_file_path)

            # Ensure it's in the specified folder
            if folder and not destination_key.startswith(f"{folder}/"):
                destination_key = f"{folder}/{destination_key}"

            # Get file extension and set appropriate content type
            content_type = self._get_audio_content_type(local_file_path)

            # Set up content type
            extra_args = {"ContentType": content_type}

            # Use the generic upload method
            return self.upload_file(
                local_file_path=local_file_path,
                destination_key=destination_key,
                extra_args=extra_args,
                public=public,
                bucket=bucket,
            )
        except Exception as e:
            return {"success": False, "error": str(e)}

    def download_file(
        self,
        bucket_key: str,
        local_path: Optional[str] = None,
        bucket: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Download a file from Digital Ocean Spaces to local filesystem.

        Args:
            bucket_key: Path/key of the file in the bucket
            local_path: Local path to save the file (defaults to filename if None)
            bucket: Optional bucket name override

        Returns:
            Dict with download result and local file path if successful
        """
        try:
            bucket = bucket or self.bucket

            # If no local path provided, use the filename from the key
            if local_path is None:
                local_path = os.path.basename(bucket_key)

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(local_path) or ".", exist_ok=True)

            # Download the file
            self.client.download_file(
                Bucket=bucket, Key=bucket_key, Filename=local_path
            )

            return {"success": True, "local_path": local_path}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def check_file_exists(self, bucket_key: str, bucket: Optional[str] = None) -> bool:
        """Check if a file exists in the Digital Ocean Spaces bucket.

        Args:
            bucket_key: Path/key of the file to check
            bucket: Optional bucket name override

        Returns:
            Boolean indicating if the file exists
        """
        try:
            bucket = bucket or self.bucket
            self.client.head_object(Bucket=bucket, Key=bucket_key)
            return True
        except botocore.exceptions.ClientError as e:
            # If a 404 error is returned, the object does not exist
            if e.response["Error"]["Code"] == "404":
                return False
            # For other errors, re-raise the exception
            raise

    def get_file_url(
        self,
        bucket_key: str,
        expires_in: int = 3600,
        public: bool = True,
        bucket: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate a URL for accessing a file in Digital Ocean Spaces.

        Args:
            bucket_key: Path/key of the file in the bucket
            expires_in: URL expiration time in seconds (for presigned URLs)
            public: If True, returns a public URL instead of presigned URL
            bucket: Optional bucket name override

        Returns:
            Dict with URL generation result and the URL if successful
        """
        try:
            bucket = bucket or self.bucket

            if public:
                # Generate public URL (works only if the file has public-read ACL)
                file_url = self._construct_standard_url(bucket_key, bucket)
                return {"success": True, "url": file_url, "expiration": None}
            else:
                # Generate a presigned URL that works for private files
                url = self.client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": bucket, "Key": bucket_key},
                    ExpiresIn=expires_in,
                )
                return {"success": True, "url": url, "expiration": expires_in}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_cdn_url_for_image(
        self, bucket_key: str, folder: str = "pictograms", bucket: Optional[str] = None
    ) -> str:
        """Generate a CDN URL for accessing a file through Digital Ocean's CDN.

        Args:
            bucket_key: Path/key of the file in the bucket
            bucket: Optional bucket name override

        Returns:
            String containing the CDN URL
        """
        bucket = bucket or self.bucket
        return self._construct_cdn_url(bucket_key, folder, bucket)

    def get_cdn_url_for_audio(
        self, bucket_key: str, folder: str = "voice_clips", bucket: Optional[str] = None
    ) -> str:
        """Generate a CDN URL for accessing a file through Digital Ocean's CDN.

        Args:
            bucket_key: Path/key of the file in the bucket
            folder: Folder to place the audio in (default: voice_clips)
            bucket: Optional bucket name override

        Returns:
            String containing the CDN URL
        """
        bucket = bucket or self.bucket
        return self._construct_cdn_url(bucket_key, folder, bucket)

    def get_file_metadata(
        self, object_key: str, bucket: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get metadata and URLs for an object in the bucket.

        Args:
            object_key: Path/key of the object in the bucket
            bucket: Optional bucket name override

        Returns:
            Dict containing file metadata and URLs
        """
        try:
            bucket = bucket or self.bucket

            # Check if object exists and get its metadata
            response = self.client.head_object(Bucket=bucket, Key=object_key)

            # Generate URLs
            standard_url = self._construct_standard_url(object_key, bucket)
            cdn_url = self._construct_cdn_url(object_key, bucket)

            # Extract relevant metadata
            metadata = {
                "content_type": response.get("ContentType"),
                "content_length": response.get("ContentLength"),
                "last_modified": response.get("LastModified"),
                "etag": response.get("ETag"),
                "content_encoding": response.get("ContentEncoding"),
            }

            # Clean up None values
            metadata = {k: v for k, v in metadata.items() if v is not None}

            return {
                "success": True,
                "exists": True,
                "cdn_url": cdn_url,
                "standard_url": standard_url,
                "metadata": metadata,
            }
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "404":
                # Object doesn't exist but operation was successful
                return {
                    "success": True,
                    "exists": False,
                    "cdn_url": None,
                    "standard_url": None,
                    "metadata": None,
                    "error": "Object does not exist",
                }
            # Other error occurred
            return {
                "success": False,
                "exists": False,
                "cdn_url": None,
                "standard_url": None,
                "metadata": None,
                "error": str(e),
            }
        except Exception as e:
            return {
                "success": False,
                "exists": False,
                "cdn_url": None,
                "standard_url": None,
                "metadata": None,
                "error": str(e),
            }

    def list_objects(
        self,
        prefix: Optional[str] = None,
        max_items: int = 1000,
        continuation_token: Optional[str] = None,
        bucket: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List objects in the Digital Ocean Spaces bucket with optional filtering.

        Args:
            prefix: Optional path prefix to filter objects (e.g., "images/")
            max_items: Maximum number of items to return (default 1000, max 1000)
            continuation_token: Token for pagination if there are more results
            bucket: Optional bucket name override

        Returns:
            Dict containing objects list and pagination info
        """
        try:
            bucket = bucket or self.bucket
            params = {"Bucket": bucket, "MaxKeys": max_items}

            # Add optional parameters if provided
            if prefix:
                params["Prefix"] = prefix

            if continuation_token:
                params["ContinuationToken"] = continuation_token

            # Make the API call
            response = self.client.list_objects_v2(**params)

            # Process the results
            objects = []
            if "Contents" in response:
                for obj in response["Contents"]:
                    # Extract relevant info for each object
                    key = obj.get("Key", "")
                    objects.append(
                        {
                            "key": key,
                            "size": obj.get("Size", 0),
                            "last_modified": obj.get("LastModified"),
                            "etag": obj.get("ETag", "").strip('"'),
                            "storage_class": obj.get("StorageClass"),
                            "standard_url": self._construct_standard_url(key, bucket),
                            "cdn_url": self._construct_cdn_url(key, bucket),
                        }
                    )

            # Check if results are truncated (more objects available)
            is_truncated = response.get("IsTruncated", False)
            next_token = response.get("NextContinuationToken") if is_truncated else None

            return {
                "success": True,
                "objects": objects,
                "count": len(objects),
                "is_truncated": is_truncated,
                "next_token": next_token,
                "prefix": prefix,
            }
        except Exception as e:
            return {
                "success": False,
                "objects": [],
                "count": 0,
                "is_truncated": False,
                "next_token": None,
                "error": str(e),
            }

    def get_categorized_objects(
        self, categories: Optional[Dict[str, str]] = None, bucket: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get bucket objects organized into categories based on prefixes.

        Args:
            categories: Dict mapping category names to their prefixes
                       (defaults to pictograms/ and voice_clips/)
            bucket: Optional bucket name override

        Returns:
            Dict containing objects organized by category
        """
        try:
            bucket = bucket or self.bucket

            # Default categories if none provided
            if not categories:
                categories = {
                    "pictograms": "pictograms/",
                    "voice_clips": "voice_clips/",
                }

            # Get all objects from the bucket
            result = self.list_objects(bucket=bucket)

            if not result["success"]:
                return {
                    "success": False,
                    "categories": {},
                    "total_count": 0,
                    "error": result.get("error", "Unknown error"),
                }

            # Initialize result with empty categories
            categorized = {
                "success": True,
                "total_count": 0,
                "categories": {name: [] for name in categories},
            }

            # Filter objects into categories
            for obj in result["objects"]:
                key = obj["key"]
                # Skip folder objects (they end with /)
                if key.endswith("/"):
                    continue

                # Assign to appropriate category
                for cat_name, prefix in categories.items():
                    if key.startswith(prefix):
                        categorized["categories"][cat_name].append(obj)
                        categorized["total_count"] += 1
                        break

            return categorized
        except Exception as e:
            return {
                "success": False,
                "categories": {},
                "total_count": 0,
                "error": str(e),
            }

    def get_cdn_urls_by_folder(self, bucket: Optional[str] = None) -> Dict[str, Any]:
        """Get just the CDN URLs for all files in the bucket, organized by folder.

        Args:
            bucket: Optional bucket name override

        Returns:
            Dict containing folder names as keys and lists of CDN URLs as values
        """
        try:
            bucket = bucket or self.bucket

            # Get all objects from the bucket
            result = self.list_objects(bucket=bucket)

            if not result["success"]:
                return {"error": result.get("error", "Unknown error")}

            # Initialize empty dictionary for results
            folders = {}

            for obj in result["objects"]:
                key = obj["key"]
                # Skip folder objects (they end with /)
                if key.endswith("/"):
                    continue

                # Extract folder name (everything before the last /)
                parts = key.split("/")
                if len(parts) > 1:
                    folder_name = "/".join(parts[:-1])
                    file_name = parts[-1]
                else:
                    folder_name = "root"
                    file_name = key

                # Initialize folder list if it doesn't exist
                if folder_name not in folders:
                    folders[folder_name] = []

                # Add cdn_url to the appropriate folder
                folders[folder_name].append(
                    {"file_name": file_name, "cdn_url": obj["cdn_url"]}
                )

            return folders
        except Exception as e:
            return {"error": str(e)}

    def _get_image_content_type(self, image_type: str) -> str:
        """Get the appropriate content type for an image type.

        Args:
            image_type: Image type/extension (png, jpg, etc.)

        Returns:
            Content type string
        """
        image_type = image_type.lower()
        content_types = {
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "gif": "image/gif",
            "webp": "image/webp",
            "svg": "image/svg+xml",
        }
        return content_types.get(image_type, "image/png")

    def _get_audio_content_type(self, file_path: str) -> str:
        """Get the appropriate content type for an audio file.

        Args:
            file_path: Path to the audio file

        Returns:
            Content type string
        """
        file_ext = os.path.splitext(file_path)[1].lower().lstrip(".")
        content_types = {
            "mp3": "audio/mpeg",
            "wav": "audio/wav",
            "ogg": "audio/ogg",
            "m4a": "audio/mp4",
            "flac": "audio/flac",
        }
        return content_types.get(file_ext, "audio/mpeg")

    def _construct_standard_url(
        self, bucket_key: str, bucket: Optional[str] = None
    ) -> str:
        """Construct a standard URL for accessing an object.

        Args:
            bucket_key: Object key in the bucket
            bucket: Optional bucket name override

        Returns:
            Standard URL string
        """
        bucket = bucket or self.bucket
        return f"https://{bucket}.{self.region}.digitaloceanspaces.com/{bucket_key}"

    def _construct_cdn_url(
        self, bucket_key: str, folder: str, bucket: Optional[str] = None
    ) -> str:
        """Construct a CDN URL for accessing an object.

        Args:
            bucket_key: Object key in the bucket
            bucket: Optional bucket name override

        Returns:
            CDN URL string
        """
        bucket = bucket or self.bucket
        return f"https://{bucket}.{self.region}.cdn.digitaloceanspaces.com/{folder}/{bucket_key}"
