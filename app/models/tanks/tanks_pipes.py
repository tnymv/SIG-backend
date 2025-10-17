# models/tanks/tank_pipes.py
from sqlalchemy import Table, Column, Integer, ForeignKey
from app.db.database import Base

tank_pipes = Table(
    "tank_pipes",
    Base.metadata,
    Column("tank_id", Integer, ForeignKey("tanks.id_tank", ondelete="CASCADE"), primary_key=True),
    Column("pipe_id", Integer, ForeignKey("pipes.id_pipes", ondelete="CASCADE"), primary_key=True)
)

# # Obtener un tanque y sus tuberías
# tank = db.query(Tank).filter(Tank.id_tank == 1).first()
# for pipe in tank.pipes:
#     print(pipe.id_pipes, pipe.material)

# # Obtener una tubería y todos sus tanques
# pipe = db.query(Pipes).filter(Pipes.id_pipes == 1).first()
# for tank in pipe.tanks:
#     print(tank.id_tank, tank.name)
