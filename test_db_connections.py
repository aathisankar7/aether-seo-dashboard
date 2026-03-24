import asyncio
import sys
import os

# Path setup for imports
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from core.database_manager import db_manager

async def verify():
    print("🚀 Starting Database Connectivity Verification...")
    
    # Initialize engines
    print("📦 Initializing engines...")
    await db_manager.initialize()
    
    # Test connections
    print("🔍 Testing connections...")
    results = await db_manager.test_connections()
    
    print("\n--- Connection Results ---")
    print(f"MySQL: {results['mysql']}")
    print(f"PostgreSQL: {results['postgres']}")
    print("--------------------------\n")
    
    if "Successfully" in results["mysql"] or "Successfully" in results["postgres"]:
        print("✅ At least one database is reachable!")
    else:
        print("⚠️ No databases reachable. (Expected if local servers are not running or credentials are placeholders)")

    # Close engines
    await db_manager.close()
    print("🏁 Verification complete.")

if __name__ == "__main__":
    asyncio.run(verify())
