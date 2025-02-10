import os
from typing import Dict

import cloudinary.uploader
from cloudinary.exceptions import Error as CloudinaryError, GeneralError
from fastapi import UploadFile, File

from application.cloudinary_config import configure_cloudinary

configure_cloudinary()


def upload_to_cloudinary(file_path: str, folder: str = "default_folder", public_id: str = None) -> dict:
    try:
        result = cloudinary.uploader.upload(
            file_path,
            folder=folder,
            public_id=public_id,
            overwrite=True,
            resource_type="auto"
        )
        return result

    except CloudinaryError as e:
        raise GeneralError(f"Failed to upload file to Cloudinary: {str(e)}")


async def upload_file(filename: str, folder: str, file: UploadFile = File(...)) -> Dict[str, str]:
    with open(file.filename, "wb") as buffer:
        buffer.write(await file.read())

    result = upload_to_cloudinary(file_path=file.filename, folder=folder, public_id=filename)

    os.remove(file.filename)

    return {'url': result["secure_url"], 'image_id': result["public_id"]}


def delete_file(public_id: str) -> bool:
    try:
        result = cloudinary.uploader.destroy(public_id)
        if result.get("result") == "ok":
            return True
        else:
            raise Exception(f"Failed to delete file: {result}")

    except CloudinaryError as e:
        print(f"Cloudinary error: {str(e)}")
        return False
