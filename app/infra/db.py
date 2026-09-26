#Create an Engine
#Engine is a factory that can create a new database connection for us, which holds onto connections inside of a connection pool for fast reuse

from sqlalchemy.ext.asyncio import create_async_engine,AsyncEngine,async_sessionmaker

from app.infra.models import Base
from app.config import Settings

def make_engine(settings:Settings) -> AsyncEngine:
    return create_async_engine(settings.database_url)

def make_session_factory(engine:AsyncEngine):
    async_sessionmaker(engine,expire_on_commit=False)  
    # expire_on_commit=False means that keep the values on the Python objects available and not expire them after every session  

async def init_db(engine:AsyncEngine)-> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all) # Run this normal synchronous SQLAlchemy operation using my async connection

# Job of the function is to initialize the database
"""
Why a separate make_session_factory function instead of just using the engine directly everywhere ? 

Engine = manages connection to the databases
Session = actually works with database objects

We generally work with the engine. But I dont want different parts of the application to manipulate the engine directly. The engine gives the db connection.

So session is created. Its the workspace to perform various db operations.

Why do we need the session factory? To create various sessions.
"""