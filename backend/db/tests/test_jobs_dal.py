from typing import AsyncGenerator
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from backend.db.dal import JobsDAL
from backend.db.dal.base import FilterOp, InvalidFilterFieldError, OrderDirection
from backend.db.data_models import Jobs
from backend.db.schemas import JobsCreate, JobsRead, JobsUpdate


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:", echo=False, future=True
    )
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


@pytest.fixture
def jobs_dal() -> JobsDAL:
    return JobsDAL(model=Jobs, read_model=JobsRead)


@pytest.mark.asyncio
async def test_create_and_get_job(db_session: AsyncSession, jobs_dal: JobsDAL) -> None:
    job_in = JobsCreate(
        job_type="test",
        status="queued",
        input_payload={"x": 1},
        result_payload=None,
        error_message=None,
        user_id=uuid4(),
        photobook_id=None,
        started_at=None,
        completed_at=None,
    )
    created = await jobs_dal.create(db_session, job_in)
    assert created.id is not None
    assert created.status == "queued"

    fetched = await jobs_dal.get(db_session, created.id)
    assert fetched is not None
    assert fetched.id == created.id


@pytest.mark.asyncio
async def test_update_job(db_session: AsyncSession, jobs_dal: JobsDAL) -> None:
    job_in = JobsCreate(
        job_type="gen",
        status="queued",
        input_payload=None,
        result_payload=None,
        error_message=None,
        user_id=None,
        photobook_id=None,
        started_at=None,
        completed_at=None,
    )
    created = await jobs_dal.create(db_session, job_in)

    update_in = JobsUpdate(status="complete", error_message="done")
    updated = await jobs_dal.update_by_id(db_session, created.id, update_in)
    assert updated is not None
    assert updated.status == "complete"
    assert updated.error_message == "done"


@pytest.mark.asyncio
async def test_list_filter_sort(db_session: AsyncSession, jobs_dal: JobsDAL) -> None:
    await jobs_dal.create(
        db_session,
        JobsCreate(
            job_type="a",
            status="queued",
            input_payload=None,
            result_payload=None,
            error_message=None,
            user_id=None,
            photobook_id=None,
            started_at=None,
            completed_at=None,
        ),
    )
    await jobs_dal.create(
        db_session,
        JobsCreate(
            job_type="b",
            status="queued",
            input_payload=None,
            result_payload=None,
            error_message=None,
            user_id=None,
            photobook_id=None,
            started_at=None,
            completed_at=None,
        ),
    )

    jobs = await jobs_dal.list(
        db_session,
        filters={"status": (FilterOp.EQ, "queued")},
        order_by=[("job_type", OrderDirection.ASC)],
    )
    assert len(jobs) == 2
    assert jobs[0].job_type == "a"
    assert jobs[1].job_type == "b"


@pytest.mark.asyncio
async def test_count_and_exists(db_session: AsyncSession, jobs_dal: JobsDAL) -> None:
    assert await jobs_dal.count(db_session) == 0
    assert not await jobs_dal.exists(db_session)

    await jobs_dal.create(
        db_session,
        JobsCreate(
            job_type="a",
            status="queued",
            input_payload=None,
            result_payload=None,
            error_message=None,
            user_id=None,
            photobook_id=None,
            started_at=None,
            completed_at=None,
        ),
    )
    assert await jobs_dal.count(db_session) == 1
    assert await jobs_dal.exists(db_session)

    assert await jobs_dal.exists(
        db_session, filters={"status": (FilterOp.EQ, "queued")}
    )


@pytest.mark.asyncio
async def test_get_returns_none_if_not_found(
    db_session: AsyncSession, jobs_dal: JobsDAL
) -> None:
    non_existent_id = uuid4()
    result = await jobs_dal.get(db_session, non_existent_id)
    assert result is None


@pytest.mark.asyncio
async def test_update_by_id_returns_none_if_not_found(
    db_session: AsyncSession, jobs_dal: JobsDAL
) -> None:
    result = await jobs_dal.update_by_id(
        db_session,
        uuid4(),
        JobsUpdate(status="error"),
    )
    assert result is None


@pytest.mark.asyncio
async def test_list_limit_offset(db_session: AsyncSession, jobs_dal: JobsDAL) -> None:
    for letter in ["a", "b", "c"]:
        await jobs_dal.create(
            db_session,
            JobsCreate(
                job_type=letter,
                status="queued",
                input_payload=None,
                result_payload=None,
                error_message=None,
                user_id=None,
                photobook_id=None,
                started_at=None,
                completed_at=None,
            ),
        )

    jobs = await jobs_dal.list(
        db_session,
        filters={"status": (FilterOp.EQ, "queued")},
        order_by=[("job_type", OrderDirection.ASC)],
        limit=2,
        offset=1,
    )

    assert len(jobs) == 2
    assert [job.job_type for job in jobs] == ["b", "c"]


@pytest.mark.asyncio
async def test_invalid_filter_field_raises(
    db_session: AsyncSession, jobs_dal: JobsDAL
) -> None:
    with pytest.raises(InvalidFilterFieldError):
        await jobs_dal.list(
            db_session,
            filters={"not_a_field": (FilterOp.EQ, "some_value")},
        )


@pytest.mark.asyncio
async def test_invalid_order_field_raises(
    db_session: AsyncSession, jobs_dal: JobsDAL
) -> None:
    with pytest.raises(InvalidFilterFieldError):
        await jobs_dal.list(
            db_session,
            order_by=[("bad_field", OrderDirection.ASC)],
        )


@pytest.mark.asyncio
async def test_exists_works_without_filters(
    db_session: AsyncSession, jobs_dal: JobsDAL
) -> None:
    assert not await jobs_dal.exists(db_session)

    await jobs_dal.create(
        db_session,
        JobsCreate(
            job_type="x",
            status="queued",
            input_payload=None,
            result_payload=None,
            error_message=None,
            user_id=None,
            photobook_id=None,
            started_at=None,
            completed_at=None,
        ),
    )
    assert await jobs_dal.exists(db_session)


@pytest.mark.asyncio
async def test_count_with_filters(db_session: AsyncSession, jobs_dal: JobsDAL) -> None:
    await jobs_dal.create(
        db_session,
        JobsCreate(
            job_type="a",
            status="done",
            input_payload=None,
            result_payload=None,
            error_message=None,
            user_id=None,
            photobook_id=None,
            started_at=None,
            completed_at=None,
        ),
    )
    await jobs_dal.create(
        db_session,
        JobsCreate(
            job_type="b",
            status="queued",
            input_payload=None,
            result_payload=None,
            error_message=None,
            user_id=None,
            photobook_id=None,
            started_at=None,
            completed_at=None,
        ),
    )

    count = await jobs_dal.count(
        db_session,
        filters={"status": (FilterOp.EQ, "queued")},
    )
    assert count == 1
