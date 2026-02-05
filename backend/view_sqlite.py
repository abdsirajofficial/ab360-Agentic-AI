"""
SQLite Database Viewer
View all structured data
"""
import sys
from pathlib import Path
import sqlite3

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import db

def print_table(title, rows, columns):
    """Print a formatted table"""
    if not rows:
        print(f"❌ No {title.lower()} found\n")
        return
    
    print(f"Total {title.lower()}: {len(rows)}\n")
    
    # Print headers
    header = " | ".join(columns)
    print(header)
    print("-" * len(header))
    
    # Print rows
    for row in rows[:10]:  # Show first 10
        values = [str(row.get(col, ''))[:30] for col in columns]
        print(" | ".join(values))
    
    if len(rows) > 10:
        print(f"... and {len(rows) - 10} more")
    print()

def main():
    print("=" * 80)
    print(" " * 28 + "SQLite Data Viewer")
    print("=" * 80)
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        # Tasks
        print("\n📋 TASKS")
        print("-" * 80)
        cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
        tasks = [dict(row) for row in cursor.fetchall()]
        print_table("Tasks", tasks, ['id', 'title', 'status', 'priority', 'due_date'])
        
        # Goals
        print("🎯 GOALS")
        print("-" * 80)
        cursor.execute("SELECT * FROM goals ORDER BY created_at DESC")
        goals = [dict(row) for row in cursor.fetchall()]
        print_table("Goals", goals, ['id', 'title', 'category', 'status', 'target_date'])
        
        # Preferences
        print("⚙️  PREFERENCES")
        print("-" * 80)
        cursor.execute("SELECT * FROM preferences ORDER BY updated_at DESC")
        prefs = [dict(row) for row in cursor.fetchall()]
        print_table("Preferences", prefs, ['id', 'key', 'value', 'updated_at'])
        
        # Learning Progress
        print("📚 LEARNING PROGRESS")
        print("-" * 80)
        cursor.execute("SELECT * FROM learning_progress ORDER BY updated_at DESC")
        learning = [dict(row) for row in cursor.fetchall()]
        print_table("Learning Progress", learning, ['id', 'topic', 'subtopic', 'status', 'progress'])
        
        # Decisions
        print("🤔 DECISIONS")
        print("-" * 80)
        cursor.execute("SELECT * FROM decisions ORDER BY created_at DESC")
        decisions = [dict(row) for row in cursor.fetchall()]
        print_table("Decisions", decisions, ['id', 'question', 'decision', 'created_at'])
        
        # Conversations
        print("💬 CONVERSATIONS")
        print("-" * 80)
        cursor.execute("SELECT * FROM conversations ORDER BY created_at DESC LIMIT 10")
        convos = [dict(row) for row in cursor.fetchall()]
        if convos:
            print(f"Total conversations: {len(convos)}\n")
            for i, convo in enumerate(convos, 1):
                print(f"[{i}] {convo.get('created_at', 'N/A')}")
                print(f"    Intent: {convo.get('intent', 'N/A')}")
                print(f"    User: {convo.get('user_input', '')[:100]}...")
                print(f"    Agent: {convo.get('agent_response', '')[:100]}...")
                print()
        else:
            print("❌ No conversations yet\n")
        
        # Statistics
        print("📊 STATISTICS")
        print("-" * 80)
        cursor.execute("SELECT COUNT(*) FROM tasks")
        task_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status='completed'")
        completed_tasks = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM goals WHERE status='active'")
        active_goals = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM conversations")
        convo_count = cursor.fetchone()[0]
        
        print(f"Tasks: {task_count} total, {completed_tasks} completed")
        print(f"Active Goals: {active_goals}")
        print(f"Conversations: {convo_count}")
        print()
    
    print("=" * 80)
    print("✅ SQLite viewing complete!")
    print("=" * 80)
    print("\nDatabase location: D:\\Gen_AI_Poc\\ab360\\backend\\data\\ab360.db")

if __name__ == "__main__":
    main()
