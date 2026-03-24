import asyncio
import pandas as pd
from sqlalchemy import text
from core.database_manager import db_manager

# =================================================================
# 🐬 MYSQL REPLICATION & PRACTICE WORKSPACE 🐬
# This file is dedicated to MySQL. Run it with: python mysql_practice.py
# =================================================================

async def execute(sql: str):
    """Run a MySQL query and show results."""
    print(f"\n⚡ Executing MySQL...")
    try:
        session_factory = await db_manager.get_mysql_session()
        if not session_factory:
            print("❌ MySQL not configured in .env")
            return

        async with session_factory as session:
            result = await session.execute(text(sql))
            if sql.strip().lower().startswith("select") or sql.strip().lower().startswith("show") or sql.strip().lower().startswith("desc"):
                data = result.fetchall()
                df = pd.DataFrame(data, columns=result.keys())
                print(df.to_string(index=False))
            else:
                await session.commit()
                print("✅ Success.")
    except Exception as e:
        print(f"❌ Error: {e}")

# -----------------------------------------------------------------
# 📝 WORK AREA - WRITE YOUR MYSQL CODE HERE
# -----------------------------------------------------------------

async def my_mysql_work():
    # Example: Create a simple users table
    await execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) UNIQUE,
        email VARCHAR(100),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Example: Insert a user
    await execute("INSERT IGNORE INTO users (username, email) VALUES ('admin', 'admin@example.com')")

    # Example: Query users
    await execute("SELECT * FROM users")

# -----------------------------------------------------------------

async def main():
    await db_manager.initialize()
    print("--- 🐬 MySQL Practice Session Started ---")
    
    await my_mysql_work()
    
    await db_manager.close()
    print("\n--- 🏁 Practice Finished ---")

if __name__ == "__main__":
    asyncio.run(main())
