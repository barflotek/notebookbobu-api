"""
Database service for Supabase operations
"""

from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
from supabase import create_client, Client

from app.core.config import settings


class DatabaseService:
    """Supabase database operations"""
    
    def __init__(self):
        if settings.SUPABASE_URL and settings.SUPABASE_SERVICE_ROLE_KEY:
            self.supabase: Client = create_client(
                settings.SUPABASE_URL, 
                settings.SUPABASE_SERVICE_ROLE_KEY
            )
            self.connected = True
        else:
            self.supabase = None
            self.connected = False
    
    async def store_document(
        self,
        document_id: str,
        user_id: str,
        title: str,
        content: bytes,
        summary: Optional[str] = None,
        bullet_points: Optional[str] = None,
        q_and_a: Optional[str] = None,
        mindmap_html: Optional[str] = None
    ) -> str:
        """Store processed document in database"""
        
        if not self.connected:
            print("⚠️  Database not connected - using mock storage")
            return document_id
        
        try:
            # Store document metadata
            result = self.supabase.table(settings.DOCUMENTS_TABLE).insert({
                "id": document_id,
                "user_id": user_id,
                "title": title,
                "summary": summary,
                "bullet_points": bullet_points,
                "q_and_a": q_and_a,
                "mindmap_html": mindmap_html,
                "file_size": len(content),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }).execute()
            
            # Store file content in Supabase Storage
            file_path = f"{user_id}/{document_id}/document.pdf"
            try:
                self.supabase.storage.from_(settings.STORAGE_BUCKET).upload(
                    file_path, content
                )
            except Exception as storage_error:
                print(f"⚠️  Storage upload failed: {storage_error}")
                # Continue without storage - metadata is still saved
            
            return document_id
            
        except Exception as e:
            print(f"❌ Database error storing document: {e}")
            raise e
    
    async def get_user_documents(
        self, 
        user_id: str, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get user's documents"""
        
        if not self.connected:
            return []  # Mock empty list
        
        try:
            result = self.supabase.table(settings.DOCUMENTS_TABLE)\
                .select("*")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()
            
            return result.data
        except Exception as e:
            print(f"❌ Database error fetching user documents: {e}")
            return []
    
    async def get_document(self, document_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific document"""
        
        if not self.connected:
            return None
        
        try:
            result = self.supabase.table(settings.DOCUMENTS_TABLE)\
                .select("*")\
                .eq("id", document_id)\
                .eq("user_id", user_id)\
                .execute()
            
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"❌ Database error fetching document: {e}")
            return None
    
    async def get_documents_by_ids(
        self, 
        document_ids: List[str], 
        user_id: str
    ) -> List[Dict[str, Any]]:
        """Get multiple documents by IDs"""
        
        if not self.connected:
            return []
        
        try:
            result = self.supabase.table(settings.DOCUMENTS_TABLE)\
                .select("*")\
                .in_("id", document_ids)\
                .eq("user_id", user_id)\
                .execute()
            
            return result.data
        except Exception as e:
            print(f"❌ Database error fetching documents by IDs: {e}")
            return []
    
    async def delete_document(self, document_id: str, user_id: str) -> bool:
        """Delete a document"""
        
        if not self.connected:
            return True  # Mock success
        
        try:
            # Delete from database
            result = self.supabase.table(settings.DOCUMENTS_TABLE)\
                .delete()\
                .eq("id", document_id)\
                .eq("user_id", user_id)\
                .execute()
            
            # Delete from storage
            try:
                file_path = f"{user_id}/{document_id}/document.pdf"
                self.supabase.storage.from_(settings.STORAGE_BUCKET).remove([file_path])
            except:
                pass  # File might not exist
            
            return len(result.data) > 0
        except Exception as e:
            print(f"❌ Database error deleting document: {e}")
            return False
    
    async def store_chat(
        self,
        user_id: str,
        document_ids: List[str],
        question: str,
        answer: str,
        sources: List[str]
    ) -> str:
        """Store chat interaction"""
        
        if not self.connected:
            return str(uuid.uuid4())  # Mock ID
        
        try:
            chat_id = str(uuid.uuid4())
            result = self.supabase.table(settings.CHATS_TABLE).insert({
                "id": chat_id,
                "user_id": user_id,
                "document_ids": document_ids,
                "question": question,
                "answer": answer,
                "sources": sources,
                "created_at": datetime.utcnow().isoformat()
            }).execute()
            
            return chat_id
        except Exception as e:
            print(f"❌ Database error storing chat: {e}")
            return str(uuid.uuid4())  # Return mock ID
    
    async def get_chat_history(
        self, 
        user_id: str, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get user's chat history"""
        
        if not self.connected:
            return []
        
        try:
            result = self.supabase.table(settings.CHATS_TABLE)\
                .select("*")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()
            
            return result.data
        except Exception as e:
            print(f"❌ Database error fetching chat history: {e}")
            return []

    # Domain-driven methods for enhanced document management
    async def create_document(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create document with domain entity data"""
        
        if not self.connected:
            print("⚠️  Database not connected - using mock data")
            return data
        
        try:
            result = self.supabase.table(settings.DOCUMENTS_TABLE).insert(data).execute()
            return result.data[0] if result.data else data
        except Exception as e:
            print(f"❌ Failed to create document: {e}")
            return data
    
    async def get_document_by_filters(self, filters: Dict[str, Any], limit: int = 1) -> Optional[Dict[str, Any]]:
        """Get document by filters"""
        
        if not self.connected:
            return None
        
        try:
            query = self.supabase.table(settings.DOCUMENTS_TABLE).select("*")
            for key, value in filters.items():
                query = query.eq(key, value)
            
            result = query.limit(limit).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"❌ Failed to get document: {e}")
            return None
    
    async def update_document(self, document_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update document"""
        
        if not self.connected:
            return data
        
        try:
            result = self.supabase.table(settings.DOCUMENTS_TABLE).update(data).eq(
                "id", document_id
            ).execute()
            
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"❌ Failed to update document: {e}")
            return None
    
    # Document chunks methods
    async def create_document_chunks(self, chunks_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create document chunks"""
        
        if not self.connected:
            return chunks_data
        
        try:
            # Create chunks table name
            chunks_table = "notebookbobu_document_chunks"
            result = self.supabase.table(chunks_table).insert(chunks_data).execute()
            return result.data
        except Exception as e:
            print(f"❌ Failed to create document chunks: {e}")
            return chunks_data
    
    async def get_document_chunks(self, document_id: str) -> List[Dict[str, Any]]:
        """Get document chunks"""
        
        if not self.connected:
            return []
        
        try:
            chunks_table = "notebookbobu_document_chunks"
            result = self.supabase.table(chunks_table).select("*").eq(
                "document_id", document_id
            ).order("chunk_index").execute()
            
            return result.data
        except Exception as e:
            print(f"❌ Failed to get document chunks: {e}")
            return []
    
    async def delete_document_chunks(self, document_id: str) -> bool:
        """Delete document chunks"""
        
        if not self.connected:
            return True
        
        try:
            chunks_table = "notebookbobu_document_chunks"
            result = self.supabase.table(chunks_table).delete().eq(
                "document_id", document_id
            ).execute()
            
            return True
        except Exception as e:
            print(f"❌ Failed to delete document chunks: {e}")
            return False
    
    async def search_document_chunks_by_content(self, query: str, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search document chunks by content"""
        
        if not self.connected:
            return []
        
        try:
            # This would need proper full-text search or vector search implementation
            chunks_table = "notebookbobu_document_chunks"
            documents_table = settings.DOCUMENTS_TABLE
            
            # Join with documents to ensure user ownership
            result = self.supabase.table(chunks_table).select(
                f"*, {documents_table}!inner(user_id)"
            ).ilike("content", f"%{query}%").eq(
                f"{documents_table}.user_id", user_id
            ).limit(limit).execute()
            
            return result.data
        except Exception as e:
            print(f"❌ Failed to search document chunks: {e}")
            return []