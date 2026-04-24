from enum import Enum
from typing import Any, Generic, Optional, Type, TypeVar
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import ColumnElement, and_, asc, desc, func, select
from sqlalchemy import exists as sa_exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel


class FilterOp(str, Enum):
    EQ = "eq"
    NE = "ne"
    LT = "lt"
    LTE = "lte"
    GT = "gt"
    GTE = "gte"
    IN = "in"


class OrderDirection(str, Enum):
    ASC = "asc"
    DESC = "desc"


# === TypeVars ===

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
ReadSchemaType = TypeVar("ReadSchemaType", bound=BaseModel)


# === Exceptions ===


class InvalidFilterFieldError(ValueError):
    def __init__(self, field: str, model: type[SQLModel]) -> None:
        super().__init__(f"Invalid field '{field}' for model '{model.__name__}'")


# === DAL ===


class AsyncPostgreSQLDAL(
    Generic[ModelType, ReadSchemaType, CreateSchemaType, UpdateSchemaType]
):
    IMMUTABLE_FIELDS: set[str] = {"id", "created_at"}

    def __init__(
        self,
        model: Type[ModelType],
        read_model: Type[ReadSchemaType],
    ):
        self.model = model
        self.read_model = read_model

    def _to_read_model(self, db_obj: ModelType) -> ReadSchemaType:
        return self.read_model.model_validate(db_obj)

    def _get_column(self, field: str) -> Any:
        if not hasattr(self.model, field):
            raise InvalidFilterFieldError(field, self.model)
        return getattr(self.model, field)

    async def get(self, session: AsyncSession, id: UUID) -> Optional[ReadSchemaType]:
        db_obj: Optional[ModelType] = await session.get(self.model, id)
        return self._to_read_model(db_obj) if db_obj else None

    async def create(
        self, session: AsyncSession, obj_in: CreateSchemaType
    ) -> ReadSchemaType:
        db_obj: ModelType = self.model.model_validate(obj_in)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return self._to_read_model(db_obj)

    async def update_by_id(
        self, session: AsyncSession, id: UUID, obj_in: UpdateSchemaType
    ) -> Optional[ReadSchemaType]:
        db_obj: Optional[ModelType] = await session.get(self.model, id)
        if db_obj is None:
            return None
        return await self._update(session, db_obj, obj_in)

    async def _update(
        self, session: AsyncSession, db_obj: ModelType, obj_in: UpdateSchemaType
    ) -> ReadSchemaType:
        update_data: dict[str, Any] = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if field not in self.IMMUTABLE_FIELDS and hasattr(db_obj, field):
                setattr(db_obj, field, value)

        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return self._to_read_model(db_obj)

    def _resolve_filter_condition(
        self,
        field: str,
        op: FilterOp,
        value: Any,
    ) -> ColumnElement[bool]:
        column = self._get_column(field)

        if op == FilterOp.EQ:
            return column == value
        if op == FilterOp.NE:
            return column != value
        if op == FilterOp.LT:
            return column < value
        if op == FilterOp.LTE:
            return column <= value
        if op == FilterOp.GT:
            return column > value
        if op == FilterOp.GTE:
            return column >= value
        if op == FilterOp.IN and isinstance(value, list):
            return column.in_(value)

        raise ValueError(f"Unsupported filter op: {op}")

    def _build_filter_conditions(
        self,
        filters: Optional[dict[str, tuple[FilterOp, Any]]],
    ) -> list[ColumnElement[bool]]:
        if not filters:
            return []

        conditions: list[ColumnElement[bool]] = []
        for field, (op, value) in filters.items():
            conditions.append(self._resolve_filter_condition(field, op, value))
        return conditions

    async def list(
        self,
        session: AsyncSession,
        filters: Optional[dict[str, tuple[FilterOp, Any]]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[list[tuple[str, OrderDirection]]] = None,
    ) -> list[ReadSchemaType]:
        stmt = select(self.model)

        conditions = self._build_filter_conditions(filters)
        if conditions:
            stmt = stmt.where(and_(*conditions))

        if order_by:
            ordering_clauses: list[ColumnElement[Any]] = [
                desc(self._get_column(field))
                if direction == OrderDirection.DESC
                else asc(self._get_column(field))
                for field, direction in order_by
            ]
            stmt = stmt.order_by(*ordering_clauses)

        if limit is not None:
            stmt = stmt.limit(limit)
        if offset is not None:
            stmt = stmt.offset(offset)

        result = await session.execute(stmt)
        rows = result.scalars().all()
        return [self._to_read_model(row) for row in rows]

    async def count(
        self,
        session: AsyncSession,
        filters: Optional[dict[str, tuple[FilterOp, Any]]] = None,
    ) -> int:
        stmt = select(func.count()).select_from(self.model)

        conditions = self._build_filter_conditions(filters)
        if conditions:
            stmt = stmt.where(and_(*conditions))

        result = await session.execute(stmt)
        return result.scalar_one()

    async def exists(
        self,
        session: AsyncSession,
        filters: Optional[dict[str, tuple[FilterOp, Any]]] = None,
    ) -> bool:
        conditions = self._build_filter_conditions(filters)
        stmt = (
            select(sa_exists().where(and_(*conditions)))
            if conditions
            else select(sa_exists().select_from(self.model))
        )
        result = await session.execute(stmt)
        scalar: Optional[bool] = result.scalar_one_or_none()
        return scalar is True
