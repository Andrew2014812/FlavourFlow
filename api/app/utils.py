import os
from typing import Dict
import asyncio
import aiofiles
import cloudinary.uploader
from concurrent.futures import ThreadPoolExecutor
from cloudinary.exceptions import Error as CloudinaryError, GeneralError
from fastapi import UploadFile, File

from api.app.cloudinary_config import configure_cloudinary

configure_cloudinary()


async def upload_to_cloudinary(
    file_path: str, folder: str = "default_folder", public_id: str = None
) -> dict:
    try:
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor,
                lambda: cloudinary.uploader.upload(
                    file_path,
                    folder=folder,
                    public_id=public_id,
                    overwrite=True,
                    resource_type="auto",
                ),
            )
        return result

    except CloudinaryError as e:
        raise GeneralError(f"Failed to upload file to Cloudinary: {str(e)}")


async def upload_file(
    filename: str, folder: str, file: UploadFile = File(...)
) -> Dict[str, str]:
    async with aiofiles.open(file.filename, "wb") as buffer:
        await buffer.write(await file.read())

    result = await upload_to_cloudinary(
        file_path=file.filename, folder=folder, public_id=filename
    )
    await asyncio.create_task(asyncio.to_thread(os.remove, file.filename))

    return {"url": result["secure_url"], "image_id": result["public_id"]}


async def delete_file(public_id: str) -> bool:
    try:
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor, lambda: cloudinary.uploader.destroy(public_id)
            )
        if result.get("result") == "ok":
            return True
        else:
            raise Exception(f"Failed to delete file: {result}")

    except CloudinaryError as e:
        print(f"Cloudinary error: {str(e)}")
        return False
