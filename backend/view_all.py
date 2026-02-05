"""
Complete Data Viewer
View all ab360 data: SQLite + ChromaDB
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

import subprocess

def main():
    print("\n" + "=" * 80)
    print(" " * 30 + "ab360 Data Viewer")
    print(" " * 25 + "Complete Data Visualization")
    print("=" * 80)
    
    print("\n🔍 Viewing all stored data...")
    print("\n")
    
    # View SQLite
    print("🗄️  PART 1: STRUCTURED DATA (SQLite)")
    print("=" * 80)
    subprocess.run([sys.executable, "view_sqlite.py"])
    
    print("\n\n")
    
    # View ChromaDB
    print("🧠 PART 2: VECTOR MEMORY (ChromaDB)")
    print("=" * 80)
    subprocess.run([sys.executable, "view_chromadb.py"])
    
    print("\n\n")
    print("=" * 80)
    print("✅ Complete data visualization finished!")
    print("=" * 80)
    print("\nStorage Location:")
    print("  📁 D:\\Gen_AI_Poc\\ab360\\backend\\data\\")
    print("     ├── ab360.db (SQLite)")
    print("     └── chromadb\\ (Vector DB)")
    print("\nTo view specific data:")
    print("  • SQLite only:   poetry run python view_sqlite.py")
    print("  • ChromaDB only: poetry run python view_chromadb.py")
    print("  • Everything:    poetry run python view_all.py")
    print()

if __name__ == "__main__":
    main()
