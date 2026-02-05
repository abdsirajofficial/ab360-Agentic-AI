"""ChromaDB vector store for memory"""

import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from app.core.config import settings


class VectorStore:
    """ChromaDB vector store manager"""
    
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=settings.vector_store_path,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # Create collections
        self.notes_collection = self.client.get_or_create_collection(
            name="notes",
            metadata={"description": "User notes and information"}
        )
        
        self.learning_collection = self.client.get_or_create_collection(
            name="learning",
            metadata={"description": "Learning summaries and progress"}
        )
        
        self.conversations_collection = self.client.get_or_create_collection(
            name="conversations",
            metadata={"description": "Important conversation history"}
        )
    
    def add_note(self, note_id: str, content: str, metadata: Optional[Dict] = None) -> None:
        """Add a note to vector store"""
        metadata = metadata or {}
        metadata["created_at"] = datetime.now().isoformat()
        metadata["type"] = "note"
        
        self.notes_collection.add(
            ids=[note_id],
            documents=[content],
            metadatas=[metadata]
        )
    
    def add_learning_summary(self, summary_id: str, content: str, metadata: Optional[Dict] = None) -> None:
        """Add a learning summary to vector store"""
        metadata = metadata or {}
        metadata["created_at"] = datetime.now().isoformat()
        metadata["type"] = "learning"
        
        self.learning_collection.add(
            ids=[summary_id],
            documents=[content],
            metadatas=[metadata]
        )
    
    def add_conversation(self, conv_id: str, content: str, metadata: Optional[Dict] = None) -> None:
        """Add important conversation to vector store"""
        metadata = metadata or {}
        metadata["created_at"] = datetime.now().isoformat()
        metadata["type"] = "conversation"
        
        self.conversations_collection.add(
            ids=[conv_id],
            documents=[content],
            metadatas=[metadata]
        )
    
    def search_notes(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant notes"""
        results = self.notes_collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return self._format_results(results)
    
    def search_learning(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant learning content"""
        results = self.learning_collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return self._format_results(results)
    
    def search_conversations(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant past conversations"""
        results = self.conversations_collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return self._format_results(results)
    
    def search_all(self, query: str, n_results: int = 3) -> Dict[str, List[Dict[str, Any]]]:
        """Search across all collections"""
        return {
            "notes": self.search_notes(query, n_results),
            "learning": self.search_learning(query, n_results),
            "conversations": self.search_conversations(query, n_results)
        }
    
    def delete_note(self, note_id: str) -> None:
        """Delete a note"""
        self.notes_collection.delete(ids=[note_id])
    
    def delete_learning(self, learning_id: str) -> None:
        """Delete a learning entry"""
        self.learning_collection.delete(ids=[learning_id])
    
    def delete_conversation(self, conv_id: str) -> None:
        """Delete a conversation"""
        self.conversations_collection.delete(ids=[conv_id])
    
    def _format_results(self, results: Dict) -> List[Dict[str, Any]]:
        """Format ChromaDB results into a clean list"""
        formatted = []
        if results["ids"] and len(results["ids"]) > 0:
            for i in range(len(results["ids"][0])):
                formatted.append({
                    "id": results["ids"][0][i],
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results.get("distances") else None
                })
        return formatted


# Global vector store instance
vector_store = VectorStore()
