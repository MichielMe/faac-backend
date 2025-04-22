# import os
# from io import BytesIO
# from pathlib import Path
# from typing import List, Optional

# import cairosvg
# import requests
# from fastapi import APIRouter, Depends, HTTPException, status
# from fastapi.responses import JSONResponse, Response
# from fastapi.security import APIKeyHeader
# from PIL import Image
# from pydantic import BaseModel

# from app.core import settings
# from app.services import (
#     OpenSymbolsClient,
#     generate_pictogram_google,
#     generate_pictogram_ideogram,
#     generate_pictogram_openai,
#     generate_two_pictograms_google,
#     generate_two_pictograms_openai,
# )
# from app.services.open_symbols_sec_fetcher import update_env_with_new_secret

# router = APIRouter(prefix="/pictogram", tags=["pictogram"])


# # Security for admin endpoints
# API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


# # def verify_admin_api_key(api_key: str = Depends(API_KEY_HEADER)):
# #     """Verify that the API key matches the admin API key."""
# #     admin_api_key = settings.ADMIN_API_KEY
# #     if not admin_api_key or api_key != admin_api_key:
# #         raise HTTPException(
# #             status_code=status.HTTP_401_UNAUTHORIZED,
# #             detail="Invalid API key",
# #         )
# #     return True


# # # Models
# # class PictogramResponse(BaseModel):
# #     success: bool
# #     files: List[dict]
# #     count: int
# #     sources: Optional[dict] = None


# # # Admin endpoints
# # @router.post("/admin/refresh-opensymbols-secret", tags=["admin"])
# # async def refresh_opensymbols_secret(authorized: bool = Depends(verify_admin_api_key)):
# #     """
# #     Refresh the OpenSymbols secret key used for API authentication.

# #     This endpoint will:
# #     1. Fetch a new secret from the OpenSymbols website
# #     2. Update the .env file with the new secret
# #     3. Return success or failure information

# #     Requires admin API key authentication.
# #     """
# #     result = update_env_with_new_secret()

# #     if result["success"]:
# #         # When successful, reload the environment settings if possible
# #         try:
# #             # This is a simplified approach - in production you might want
# #             # to handle settings reloading differently based on your app structure
# #             settings.reload_settings()
# #         except Exception as e:
# #             # If reload fails, still return success since the .env was updated
# #             result["warning"] = (
# #                 f"Secret updated but environment reload failed: {str(e)}"
# #             )

# #         return JSONResponse(content=result)
# #     else:
# #         return JSONResponse(
# #             content=result,
# #             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
# #         )


# # # Single pictogram generation endpoints
# # @router.post("/generate/openai", tags=["generation"])
# # def generate_openai_pictogram(keyword: str):
# #     """Generate a single pictogram using OpenAI"""
# #     return generate_pictogram_openai(keyword)


# # @router.post("/generate/google", tags=["generation"])
# # def generate_google_pictogram(keyword: str):
# #     """Generate a single pictogram using Google"""
# #     return generate_pictogram_google(keyword)


# # # Double pictogram generation endpoints
# # @router.post("/generate/openai/double", tags=["generation"])
# # def generate_openai_double_pictogram(keyword: str):
# #     """Generate two pictograms using OpenAI"""
# #     return generate_two_pictograms_openai(keyword)


# # @router.post("/generate/google/double", tags=["generation"])
# # def generate_google_double_pictogram(keyword: str):
# #     """Generate two pictograms using Google"""
# #     return generate_two_pictograms_google(keyword)


# # # Multi-source pictogram generation
# # @router.post("/generate/four", tags=["generation"])
# # def generate_four_pictograms(keyword: str):
# #     """
# #     Generate four pictograms, two from OpenAI and two from Google

# #     Args:
# #         keyword: The word to generate pictograms for

# #     Returns:
# #         Combined results with up to four pictograms
# #     """
# #     google_response = generate_two_pictograms_google(keyword)
# #     openai_response = generate_two_pictograms_openai(keyword)

# #     # Extract content from responses
# #     import json

# #     google_content = (
# #         google_response.body.decode() if hasattr(google_response, "body") else "{}"
# #     )
# #     openai_content = (
# #         openai_response.body.decode() if hasattr(openai_response, "body") else "{}"
# #     )

# #     try:
# #         google_data = json.loads(google_content)
# #         openai_data = json.loads(openai_content)

# #         # Check if both generations were successful
# #         if google_data.get("success", False) and openai_data.get("success", False):
# #             # Combine the files from both generators
# #             google_files = google_data.get("files", [])
# #             openai_files = openai_data.get("files", [])
# #             all_files = google_files + openai_files

# #             if all_files:
# #                 return JSONResponse(content={"success": True, "files": all_files})
# #             else:
# #                 return JSONResponse(
# #                     content={"success": False, "error": "No pictograms were generated"},
# #                     status_code=500,
# #                 )
# #         else:
# #             # If either generation wasn't successful, return an error
# #             return JSONResponse(
# #                 content={
# #                     "success": False,
# #                     "error": "Failed to generate all pictograms",
# #                     "google_error": (
# #                         None
# #                         if google_data.get("success", False)
# #                         else google_data.get("error")
# #                     ),
# #                     "openai_error": (
# #                         None
# #                         if openai_data.get("success", False)
# #                         else openai_data.get("error")
# #                     ),
# #                 },
# #                 status_code=500,
# #             )
# #     except json.JSONDecodeError:
# #         return JSONResponse(
# #             content={"success": False, "error": "Error processing generator responses"},
# #             status_code=500,
# #         )


# @router.post("/generate/ideogram", tags=["generation"])
# def generate_ideogram_pictogram(keyword: str):
#     """Generate two pictograms using Ideogram"""
#     return generate_pictogram_ideogram(keyword)


# @router.post("/generate/eight", tags=["generation"])
# async def generate_eight_pictograms(keyword: str):
#     """
#     Generate eight pictograms for a keyword:
#     - Two from OpenAI
#     - Two from Google / Deprecated
#     - Two from Ideogram
#     - Two from OpenSymbols

#     Just generate 4 pictures with Ideogram and get 2 form Open Symbols.

#     We keep the other ones for the future if needed.

#     Args:
#         keyword: The word or phrase to generate pictograms for

#     Returns:
#         JSONResponse with success status and paths to all generated pictograms
#     """
#     results = {"success": False, "files": [], "sources": {}}

#     # # 1. Get pictograms from OpenAI
#     # openai_response = generate_two_pictograms_openai(keyword)
#     # if hasattr(openai_response, "body"):
#     #     import json

#     #     openai_data = json.loads(openai_response.body.decode())
#     #     if openai_data.get("success", False):
#     #         results["sources"]["openai"] = {
#     #             "success": True,
#     #             "files": openai_data.get("files", []),
#     #         }
#     #         results["files"].extend(openai_data.get("files", []))
#     #     else:
#     #         results["sources"]["openai"] = {
#     #             "success": False,
#     #             "error": openai_data.get("error", "Unknown error"),
#     #         }

#     # 2. Get pictograms from Google
#     # google_response = generate_two_pictograms_google(keyword)
#     # if hasattr(google_response, "body"):
#     #     import json

#     #     google_data = json.loads(google_response.body.decode())
#     #     if google_data.get("success", False):
#     #         results["sources"]["google"] = {
#     #             "success": True,
#     #             "files": google_data.get("files", []),
#     #         }
#     #         results["files"].extend(google_data.get("files", []))
#     #     else:
#     #         results["sources"]["google"] = {
#     #             "success": False,
#     #             "error": google_data.get("error", "Unknown error"),
#     #         }

#     # 3. Get pictograms from Ideogram
#     ideogram_response = generate_pictogram_ideogram(keyword)
#     if hasattr(ideogram_response, "body"):
#         import json

#         ideogram_data = json.loads(ideogram_response.body.decode())
#         if ideogram_data.get("success", False):
#             results["sources"]["ideogram"] = {
#                 "success": True,
#                 "files": ideogram_data.get("files", []),
#             }
#             results["files"].extend(ideogram_data.get("files", []))

#     # # 3. Get pictograms from OpenSymbols
#     # client = OpenSymbolsClient()
#     # pictogram_dir = Path(os.path.join("app", "assets", "pictograms"))
#     # pictogram_dir.mkdir(exist_ok=True, parents=True)

#     # opensymbols_files = []
#     # all_symbols = client.search_symbols(keyword)

#     # if all_symbols:
#     #     # Sort by relevance and take top 2
#     #     sorted_symbols = sorted(
#     #         all_symbols, key=lambda s: s.get("relevance", 0), reverse=True
#     #     )
#     #     selected_symbols = sorted_symbols[:2]

#     #     for i, symbol in enumerate(selected_symbols):
#     #         file_index = i + 5
#     #         image_url = symbol.get("image_url")
#     #         if not image_url:
#     #             continue

#     #         try:
#     #             # Download the image
#     #             response = requests.get(image_url)
#     #             response.raise_for_status()

#     #             is_svg = image_url.lower().endswith(".svg")
#     #             output_filename = f"pic_{keyword}_{file_index:02d}.png"
#     #             output_path = pictogram_dir / output_filename

#     #             # Convert and save the image
#     #             if is_svg:
#     #                 png_data = cairosvg.svg2png(bytestring=response.content)
#     #                 with open(output_path, "wb") as f:
#     #                     f.write(png_data)
#     #             else:
#     #                 img = Image.open(BytesIO(response.content))
#     #                 img = img.convert("RGBA")
#     #                 img.save(output_path, "PNG")

#     #             # Add to results
#     #             file_info = {
#     #                 "filename": output_filename,
#     #                 "path": str(output_path),
#     #                 "url": f"/assets/pictograms/{output_filename}",
#     #                 "original_repo": symbol.get("repo_key"),
#     #                 "original_name": symbol.get("name"),
#     #                 "original_url": image_url,
#     #                 "relevance": symbol.get("relevance", 0),
#     #             }
#     #             opensymbols_files.append(file_info)
#     #             results["files"].append(file_info)
#     #         except Exception as e:
#     #             print(f"Error processing {image_url}: {str(e)}")

#     #     if opensymbols_files:
#     #         results["sources"]["opensymbols"] = {
#     #             "success": True,
#     #             "files": opensymbols_files,
#     #         }
#     #     else:
#     #         results["sources"]["opensymbols"] = {
#     #             "success": False,
#     #             "error": "Failed to process OpenSymbols pictograms",
#     #         }
#     # else:
#     #     results["sources"]["opensymbols"] = {
#     #         "success": False,
#     #         "error": "No symbols found",
#     #     }

#     # Return the final results
#     if results["files"]:
#         results["success"] = True
#         results["count"] = len(results["files"])
#         return JSONResponse(content=results)
#     else:
#         return JSONResponse(
#             content={
#                 "success": False,
#                 "message": "Failed to generate any pictograms",
#                 "sources": results["sources"],
#             },
#             status_code=500,
#         )


# # # OpenSymbols endpoints
# # @router.get("/opensymbols/search", tags=["opensymbols"])
# # def search_opensymbols(keyword: str):
# #     """Search OpenSymbols for pictograms matching the keyword"""
# #     client = OpenSymbolsClient()
# #     result = client.search_symbols(keyword)

# #     if not result:
# #         return JSONResponse(
# #             content={
# #                 "success": False,
# #                 "message": "No symbols found or API connection issue",
# #                 "note": "The OpenSymbols API may only be accessible through their web interface. Consider contacting them for API access.",
# #                 "symbols": [],
# #             }
# #         )

# #     return JSONResponse(content={"success": True, "symbols": result})


# # @router.get("/opensymbols/image", tags=["opensymbols"])
# # async def get_opensymbols_image(url: str):
# #     """Proxy endpoint to serve images from OpenSymbols"""
# #     try:
# #         response = requests.get(url)
# #         response.raise_for_status()

# #         # Determine content type
# #         content_type = response.headers.get("Content-Type")
# #         if not content_type:
# #             if url.lower().endswith(".svg"):
# #                 content_type = "image/svg+xml"
# #             elif url.lower().endswith(".png"):
# #                 content_type = "image/png"
# #             elif url.lower().endswith(".jpg") or url.lower().endswith(".jpeg"):
# #                 content_type = "image/jpeg"
# #             else:
# #                 content_type = "application/octet-stream"

# #         return Response(content=response.content, media_type=content_type)

# #     except Exception as e:
# #         return JSONResponse(
# #             content={"success": False, "error": str(e)}, status_code=404
# #         )


# # @router.get("/opensymbols/info/{symbol_id}", tags=["opensymbols"])
# # async def get_opensymbols_symbol_info(symbol_id: int):
# #     """Get detailed information about a specific symbol"""
# #     try:
# #         client = OpenSymbolsClient()
# #         symbols = client.search_symbols("id:" + str(symbol_id))

# #         for symbol in symbols:
# #             if symbol.get("id") == symbol_id:
# #                 return JSONResponse(content={"success": True, "symbol": symbol})

# #         return JSONResponse(
# #             content={
# #                 "success": False,
# #                 "error": f"Symbol with ID {symbol_id} not found",
# #             },
# #             status_code=404,
# #         )

# #     except Exception as e:
# #         return JSONResponse(
# #             content={"success": False, "error": str(e)}, status_code=500
# #         )


# # @router.post("/opensymbols/download", tags=["opensymbols"])
# # async def download_opensymbols_pictograms(keyword: str):
# #     """
# #     Search for pictograms and download the top 2 with highest relevance,
# #     save as PNG files, and return the local paths.
# #     """
# #     client = OpenSymbolsClient()
# #     all_symbols = client.search_symbols(keyword)

# #     if not all_symbols:
# #         return JSONResponse(
# #             content={
# #                 "success": False,
# #                 "message": f"No symbols found for keyword: {keyword}",
# #             },
# #             status_code=404,
# #         )

# #     # Sort symbols by relevance (highest first)
# #     sorted_symbols = sorted(
# #         all_symbols, key=lambda s: s.get("relevance", 0), reverse=True
# #     )

# #     # Take the top 2 symbols with highest relevance
# #     selected_symbols = sorted_symbols[:2]
# #     pictogram_dir = Path(os.path.join("app", "assets", "pictograms"))
# #     pictogram_dir.mkdir(exist_ok=True, parents=True)

# #     saved_files = []

# #     for i, symbol in enumerate(selected_symbols):
# #         # Start numbering at 05 and 06
# #         file_index = i + 5
# #         image_url = symbol.get("image_url")
# #         if not image_url:
# #             continue

# #         try:
# #             # Download the image
# #             response = requests.get(image_url)
# #             response.raise_for_status()

# #             # Determine file extension from URL
# #             is_svg = image_url.lower().endswith(".svg")
# #             output_filename = f"pic_{keyword}_{file_index:02d}.png"
# #             output_path = pictogram_dir / output_filename

# #             # Convert and save the image
# #             if is_svg:
# #                 # Convert SVG to PNG
# #                 png_data = cairosvg.svg2png(bytestring=response.content)
# #                 with open(output_path, "wb") as f:
# #                     f.write(png_data)
# #             else:
# #                 # For other formats, convert to PNG using PIL
# #                 img = Image.open(BytesIO(response.content))
# #                 img = img.convert("RGBA")
# #                 img.save(output_path, "PNG")

# #             # Add information about the saved file
# #             saved_files.append(
# #                 {
# #                     "filename": output_filename,
# #                     "path": str(output_path),
# #                     "url": f"/assets/pictograms/{output_filename}",
# #                     "original_repo": symbol.get("repo_key"),
# #                     "original_name": symbol.get("name"),
# #                     "original_url": image_url,
# #                     "relevance": symbol.get("relevance", 0),
# #                 }
# #             )

# #         except Exception as e:
# #             print(f"Error processing {image_url}: {str(e)}")
# #             continue

# #     # Return the results
# #     if saved_files:
# #         return JSONResponse(
# #             content={
# #                 "success": True,
# #                 "keyword": keyword,
# #                 "files": saved_files,
# #                 "count": len(saved_files),
# #             }
# #         )
# #     else:
# #         return JSONResponse(
# #             content={
# #                 "success": False,
# #                 "message": f"Failed to download any pictograms for keyword: {keyword}",
# #             },
# #             status_code=500,
# #         )
