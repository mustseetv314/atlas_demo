import logging
from collections.abc import Generator

from sqlalchemy import create_engine, func, select, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


settings = get_settings()
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def check_database() -> bool:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError:
        logger.exception("Database connectivity check failed")
        return False


def initialize_database() -> None:
    from app.models import Asset
    from app.seed import SEED_ASSETS

    logger.info("Initializing database schema")
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        if session.scalar(select(func.count()).select_from(Asset)):
            logger.info("Asset seed data already present")
            return
        try:
            session.add_all(Asset(**item) for item in SEED_ASSETS)
            session.commit()
            logger.info("Inserted %d seed assets", len(SEED_ASSETS))
        except IntegrityError:
            # Another replica may have inserted the same unique asset tags first.
            session.rollback()
            logger.info("Seed data was initialized concurrently by another replica")
