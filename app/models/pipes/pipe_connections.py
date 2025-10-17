from sqlalchemy import Table, Column, Integer, ForeignKey
from app.db.database import Base

pipe_connections = Table(
    "pipe_connections",
    Base.metadata,
    Column("pipe_id", Integer, ForeignKey("pipes.id_pipes", ondelete="CASCADE"), primary_key=True),
    Column("connection_id", Integer, ForeignKey("connections.id_connection", ondelete="CASCADE"), primary_key=True)
)
