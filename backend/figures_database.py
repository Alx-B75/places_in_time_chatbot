from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Path to your historical data DB
FIGURE_DB_URL = "sqlite:///./data/figures.db"

figure_engine = create_engine(
    FIGURE_DB_URL, connect_args={"check_same_thread": False}
)

FigureSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=figure_engine
)

FigureBase = declarative_base()
