from typing import Generic, TypeVar

from fastapi import HTTPException, status
from sqlmodel import SQLModel, func, select

from ..common.dependencies import SessionDep

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=SQLModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=SQLModel)
ResponseSchemaType = TypeVar("ResponseSchemaType", bound=SQLModel)


class CuisineCRUDService(
    Generic[ModelType, CreateSchemaType, UpdateSchemaType, ResponseSchemaType]
):
    def __init__(self, model: type[ModelType]):
        self.model = model

    async def create(
        self, session: SessionDep, obj_in: CreateSchemaType
    ) -> ResponseSchemaType:
        statement = select(self.model).filter(
            self.model.title_ua == obj_in.title_ua,
            self.model.title_en == obj_in.title_en,
        )
        result = await session.exec(statement)
        existing_obj = result.first()

        if existing_obj:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{self.model.__name__} already exists",
            )

        db_obj = self.model()
        for key, value in obj_in.model_dump().items():
            setattr(db_obj, key, value)

        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def get_all(self, session: SessionDep, page: int = 1, limit: int = 6) -> dict:
        statement = select(func.count()).select_from(self.model)
        result = await session.exec(statement)
        total_records = result.one()
        total_pages = (total_records + limit - 1) // limit

        statement = select(self.model).limit(limit).offset((page - 1) * limit)
        result = await session.exec(statement)
        items = result.all()

        return {"items": items, "total_pages": total_pages}

    async def get_by_id(self, session: SessionDep, obj_id: int) -> ResponseSchemaType:
        statement = select(self.model).filter(self.model.id == obj_id)
        result = await session.exec(statement)
        obj = result.first()

        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} not found",
            )
        return obj

    async def update(
        self, session: SessionDep, obj_id: int, obj_in: UpdateSchemaType
    ) -> ResponseSchemaType:
        statement = select(self.model).filter(self.model.id == obj_id)
        result = await session.exec(statement)
        existing_obj = result.first()

        if not existing_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} not found",
            )

        for key, value in obj_in.model_dump().items():
            setattr(existing_obj, key, value)

        await session.merge(existing_obj)
        await session.commit()
        await session.refresh(existing_obj)
        return existing_obj

    async def delete(self, session: SessionDep, obj_id: int) -> None:
        statement = select(self.model).filter(self.model.id == obj_id)
        result = await session.exec(statement)
        existing_obj = result.first()

        if not existing_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} not found",
            )

        await session.delete(existing_obj)
        await session.commit()
