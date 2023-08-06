import datetime

from sqlalchemy import text

from fastapi_views.tests._tmp_db import (
    engine,
    TestingSessionLocal,
    Base,
    SimpleTestOrm,
    async_engine,
    TestingSessionLocalAsync,
)


class DatabaseSession:

    def __init__(self, number: int = 50):
        self._session = None
        self._engine = None
        self._number = number

    def init(self):
        self._engine = engine
        self._session = TestingSessionLocal()

    def create_all(self):
        Base.metadata.create_all(bind=engine)
        _now = datetime.datetime.now()
        for _id in range(0, self._number):
            t = _now + datetime.timedelta(minutes=_id)
            self._session.add(SimpleTestOrm(time_created=t))
        self._session.commit()

    def close_and_drop(self):
        self._session.close()
        Base.metadata.drop_all(bind=engine)

    @property
    def session(self):
        return self._session


class DatabaseSessionSameDateTime(DatabaseSession):

    def create_all(self):
        Base.metadata.create_all(bind=engine)
        _now = datetime.datetime.now()
        for _id in range(0, 50):
            self._session.add(SimpleTestOrm(time_created=_now))
        self._session.commit()


class AsyncDatabaseSession:

    def __init__(self):
        self._session = None
        self._engine = None

    async def init(self):
        self._engine = async_engine
        self._session = TestingSessionLocalAsync()

    async def create_all(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            ids = ', '.join(
                map(
                    lambda x: f'({x}, "{datetime.datetime.now()}")',
                    [x for x in range(1, 16)],
                ),
            )
            insert_txt = text(f"""
                INSERT INTO test_database (id, time_created)
                VALUES {ids}
            """)
            await conn.execute(insert_txt)

    async def delete_all(self):
        async with self._engine.begin() as conn:
            await conn.execute(text('DROP TABLE test_database'))

    @property
    def session(self):
        return self._session
