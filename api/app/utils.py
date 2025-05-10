import asyncio
import math
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional, Tuple, Type, TypeVar

import aiofiles
import cloudinary.uploader
from cloudinary.exceptions import Error as CloudinaryError
from cloudinary.exceptions import GeneralError
from fastapi import File, UploadFile
from sqlalchemy import func
from sqlalchemy.orm import Load
from sqlmodel import select

from .cloudinary_config import configure_cloudinary
from .common.dependencies import SessionDep

configure_cloudinary()

T = TypeVar("T")


async def get_entity_by_params(
    session: SessionDep,
    entity_class: Type[T],
    *,
    return_all: bool = False,
    options: Optional[List[Load]] = None,
    limit: Optional[int] = None,
    page: Optional[int] = None,
    with_total_pages: bool = False,
    **params,
) -> Tuple[List[T] | Optional[T], int]:
    statement = select(entity_class)
    statement = apply_filters_to_statement(
        statement,
        entity_class,
        **params,
    )

    if options:
        statement = statement.options(*options)

    total_pages = await get_total_pages(
        session,
        entity_class,
        limit,
        **params,
    )

    if limit and page:
        offset = (page - 1) * limit
        statement = statement.limit(limit).offset(offset)

    result = await session.exec(statement)

    if with_total_pages and limit and page and return_all:
        return result.unique().all(), total_pages

    if return_all:
        return result.unique().all()

    return result.first()


def apply_filters_to_statement(
    statement,
    entity_class: Type[T],
    **params,
):
    for key, value in params.items():
        if hasattr(entity_class, key) and value is not None:
            statement = statement.where(getattr(entity_class, key) == value)

    return statement


async def get_total_pages(
    session: SessionDep,
    entity_class: Type[T],
    limit: int,
    **kwargs,
) -> int:

    count_statement = select(func.count()).select_from(entity_class)
    count_statement = apply_filters_to_statement(
        count_statement,
        entity_class,
        **kwargs,
    )

    total_count = await session.scalar(count_statement)
    return math.ceil(total_count / limit) if limit else 1


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
