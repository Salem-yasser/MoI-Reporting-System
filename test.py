import asyncio
from sqlalchemy import text
from app.core.database import engine

async def test_connection():
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            val = result.scalar_one()
            print(f"✅ Database connection successful, test query returned: {val}")
    except Exception as e:
        print(f"✗ Database connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
