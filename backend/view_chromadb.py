"""
ChromaDB Data Viewer
View all data stored in vector database
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.vector_store import vector_store

def main():
    print("=" * 80)
    print(" " * 25 + "ChromaDB Data Viewer")
    print("=" * 80)
    
    # Notes Collection
    print("\n📝 NOTES COLLECTION")
    print("-" * 80)
    notes = vector_store.notes_collection.get()
    if notes['ids']:
        print(f"Total notes: {len(notes['ids'])}\n")
        for i, note_id in enumerate(notes['ids'][:10]):  # Show first 10
            content = notes['documents'][i]
            metadata = notes['metadatas'][i] if notes['metadatas'] else {}
            print(f"[{i+1}] ID: {note_id}")
            print(f"    Content: {content[:150]}...")
            print(f"    Metadata: {metadata}")
            print()
    else:
        print("❌ No notes stored yet")
    
    # Learning Collection
    print("\n📚 LEARNING COLLECTION")
    print("-" * 80)
    learning = vector_store.learning_collection.get()
    if learning['ids']:
        print(f"Total learning items: {len(learning['ids'])}\n")
        for i, item_id in enumerate(learning['ids'][:10]):
            content = learning['documents'][i]
            metadata = learning['metadatas'][i] if learning['metadatas'] else {}
            print(f"[{i+1}] ID: {item_id}")
            print(f"    Content: {content[:150]}...")
            print(f"    Metadata: {metadata}")
            print()
    else:
        print("❌ No learning data stored yet")
    
    # Conversations Collection
    print("\n💬 CONVERSATIONS COLLECTION")
    print("-" * 80)
    conversations = vector_store.conversations_collection.get()
    if conversations['ids']:
        print(f"Total conversations: {len(conversations['ids'])}\n")
        for i, conv_id in enumerate(conversations['ids'][:10]):
            content = conversations['documents'][i]
            metadata = conversations['metadatas'][i] if conversations['metadatas'] else {}
            print(f"[{i+1}] ID: {conv_id}")
            print(f"    Content: {content[:150]}...")
            print(f"    Metadata: {metadata}")
            print()
    else:
        print("❌ No conversations stored yet")
    
    # Test Semantic Search
    print("\n🔍 SEMANTIC SEARCH TEST")
    print("-" * 80)
    test_query = "preferences"
    print(f"Query: '{test_query}'\n")
    
    results = vector_store.search_all(test_query, n_results=3)
    
    for collection_name, items in results.items():
        if items:
            print(f"{collection_name.upper()}:")
            for item in items:
                distance = item.get('distance', 'N/A')
                print(f"  • {item['content'][:100]}...")
                print(f"    (Similarity: {1 - distance:.2%})")
            print()
        else:
            print(f"{collection_name.upper()}: No matches")
    
    print("=" * 80)
    print("✅ ChromaDB viewing complete!")
    print("=" * 80)

if __name__ == "__main__":
    main()
