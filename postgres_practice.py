import asyncio
import pandas as pd
from sqlalchemy import text
from core.database_manager import db_manager

# =================================================================
# 🐘 POSTGRESQL REPLICATION & PRACTICE WORKSPACE 🐘
# This file is dedicated to Postgres. Run it with: python3 postgres_practice.py
# =================================================================

async def execute(sql: str):
    """Run a Postgres query and show results."""
    print(f"\n⚡ Executing Postgres...")
    try:
        session_factory = await db_manager.get_postgres_session()
        if not session_factory:
            print("❌ Postgres not configured in .env")
            return

        async with session_factory as session:
            result = await session.execute(text(sql))
            if sql.strip().lower().startswith("select"):
                data = result.fetchall()
                df = pd.DataFrame(data, columns=result.keys())
                print(df.to_string(index=False))
            else:
                await session.commit()
                print("✅ Success.")
    except Exception as e:
        print(f"❌ Error: {e}")

async def my_postgres_work():
    # Example: Create a simple projects table
    await execute("""
    CREATE TABLE IF NOT EXISTS seo_projects (
        id SERIAL PRIMARY KEY,
        project_name TEXT UNIQUE,
        target_vibe TEXT,
        created_at TIMESTAMPTZ DEFAULT NOW()
    )
    """)

    # Example: Insert a project
    await execute("INSERT INTO seo_projects (project_name, target_vibe) VALUES ('Project Alpha', 'Elite SEO') ON CONFLICT DO NOTHING")

    # Example: Query projects
    await execute("SELECT * FROM seo_projects")

async def main():
    await db_manager.initialize()
    print("--- 🐘 Postgres Practice Session Started ---")
    
    await my_postgres_work()
    
    await db_manager.close()
    print("\n--- 🏁 Practice Finished ---")

if __name__ == "__main__":
    asyncio.run(main())
