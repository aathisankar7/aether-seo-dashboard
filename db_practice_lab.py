import asyncio
import pandas as pd
from sqlalchemy import text
from core.database_manager import db_manager

# =================================================================
# 🧬 SQL MASTERCLASS PRACTICE LAB 🧬
# Similar to a Jupyter Notebook, run "cells" by calling functions.
# =================================================================

async def run_sql(db_type: str, query: str):
    """
    Helper to execute and format SQL results.
    db_type: 'mysql' or 'postgres'
    """
    print(f"\n🚀 Running on {db_type.upper()}...")
    try:
        if db_type == "mysql":
            session_factory = await db_manager.get_mysql_session()
        else:
            session_factory = await db_manager.get_postgres_session()
        
        if not session_factory:
            print(f"❌ {db_type.upper()} session not available. Check your .env file.")
            return

        async with session_factory as session:
            result = await session.execute(text(query))
            
            # If it's a SELECT query, show results with Pandas
            if query.strip().lower().startswith("select"):
                columns = result.keys()
                data = result.fetchall()
                df = pd.DataFrame(data, columns=columns)
                print(df.to_string(index=False))
            else:
                await session.commit()
                print("✅ Command executed and committed successfully.")
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")

# -----------------------------------------------------------------
# CELL 1: SETUP - Create Practice Tables
# -----------------------------------------------------------------
async def cell_setup_tables(db_type):
    sql = """
    CREATE TABLE IF NOT EXISTS seo_keywords (
        id SERIAL PRIMARY KEY,
        keyword VARCHAR(255) NOT NULL,
        volume INT,
        difficulty FLOAT,
        intent VARCHAR(50)
    );
    """
    # Note: MySQL uses AUTO_INCREMENT, Postgres uses SERIAL/IDENTITY. 
    # This example uses SERIAL-ish syntax (MySQL might need a tweak if not using standard SQL).
    if db_type == "mysql":
        sql = sql.replace("SERIAL PRIMARY KEY", "INT AUTO_INCREMENT PRIMARY KEY")
    
    await run_sql(db_type, sql)

# -----------------------------------------------------------------
# CELL 2: INSERT - Add Sample Data
# -----------------------------------------------------------------
async def cell_insert_data(db_type):
    sql = """
    INSERT INTO seo_keywords (keyword, volume, difficulty, intent) VALUES 
    ('best seo tools', 1500, 0.45, 'commercial'),
    ('how to do seo', 5000, 0.25, 'informational'),
    ('ai content generator', 12000, 0.65, 'commercial'),
    ('local seo strategies', 800, 0.35, 'transactional');
    """
    await run_sql(db_type, sql)

# -----------------------------------------------------------------
# CELL 3: SELECT - Query Data
# -----------------------------------------------------------------
async def cell_query_high_volume(db_type):
    sql = "SELECT * FROM seo_keywords WHERE volume > 1000 ORDER BY volume DESC;"
    await run_sql(db_type, sql)

# -----------------------------------------------------------------
# CELL 4: PRACTICE AREA - Write your own here!
# -----------------------------------------------------------------
async def my_practice_cell(db_type):
    # WRITE YOUR CUSTOM SQL HERE
    sql = """
    SELECT intent, AVG(volume) as avg_volume 
    FROM seo_keywords 
    GROUP BY intent;
    """
    await run_sql(db_type, sql)

# =================================================================
# 🏁 LAB EXECUTION
# =================================================================
async def main():
    db = "mysql" # Change this to "postgres" to switch environments
    
    # 1. Initialize
    await db_manager.initialize()
    
    print(f"--- Welcome to the {db.upper()} Lab ---")
    
    # Uncomment the cells you want to run!
    await cell_setup_tables(db)
    await cell_insert_data(db)
    await cell_query_high_volume(db)
    await my_practice_cell(db)
    
    # Close
    await db_manager.close()

if __name__ == "__main__":
    asyncio.run(main())
