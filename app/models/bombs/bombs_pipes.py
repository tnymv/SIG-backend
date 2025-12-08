from sqlalchemy import Table, Column, Integer, ForeignKey
from app.db.database import Base

bombs_pipes = Table(
    "bombs_pipes",
    Base.metadata,
    Column("bombs_id", Integer, ForeignKey("bombs.id_bombs", ondelete="CASCADE"), primary_key=True),
    Column("pipe_id", Integer, ForeignKey("pipes.id_pipes", ondelete="CASCADE"),primary_key=True)
)