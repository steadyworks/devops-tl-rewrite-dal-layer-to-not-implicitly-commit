from backend.db.dal.base import AsyncPostgreSQLDAL
from backend.db.data_models import Assets, Jobs, Pages, PagesAssetsRel, Photobooks
from backend.db.schemas import (
    AssetsCreate,
    AssetsRead,
    AssetsUpdate,
    JobsCreate,
    JobsRead,
    JobsUpdate,
    PagesAssetsRelCreate,
    PagesAssetsRelRead,
    PagesAssetsRelUpdate,
    PagesCreate,
    PagesRead,
    PagesUpdate,
    PhotobooksCreate,
    PhotobooksRead,
    PhotobooksUpdate,
)


class AssetsDAL(AsyncPostgreSQLDAL[Assets, AssetsRead, AssetsCreate, AssetsUpdate]):
    pass


class JobsDAL(AsyncPostgreSQLDAL[Jobs, JobsRead, JobsCreate, JobsUpdate]):
    pass


class PagesDAL(AsyncPostgreSQLDAL[Pages, PagesRead, PagesCreate, PagesUpdate]):
    pass


class PagesAssetsRelDAL(
    AsyncPostgreSQLDAL[
        PagesAssetsRel, PagesAssetsRelRead, PagesAssetsRelCreate, PagesAssetsRelUpdate
    ]
):
    pass


class PhotobooksDAL(
    AsyncPostgreSQLDAL[Photobooks, PhotobooksRead, PhotobooksCreate, PhotobooksUpdate]
):
    pass
