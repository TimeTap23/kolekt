"""
Supabase service for ThreadStorm
Handles database operations, authentication, and file storage
"""

import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from supabase import create_client, Client
from src.core.config import settings

logger = logging.getLogger(__name__)


class SupabaseService:
    """Supabase service for ThreadStorm"""
    
    def __init__(self):
        self.client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        self.anon_client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
    
    # Expose table method for compatibility
    def table(self, table_name: str):
        """Get a table reference for database operations"""
        return self.client.table(table_name)
    
    def raw(self, query: str):
        """Execute raw SQL query"""
        return self.client.rpc('exec_sql', {'query': query})
    
    # Authentication Methods
    async def sign_up(self, email: str, password: str, user_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Sign up a new user"""
        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": user_data or {}
                }
            })
            return {"success": True, "user": response.user, "session": response.session}
        except Exception as e:
            logger.error(f"Sign up error: {e}")
            return {"success": False, "error": str(e)}
    
    async def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """Sign in a user"""
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            return {"success": True, "user": response.user, "session": response.session}
        except Exception as e:
            logger.error(f"Sign in error: {e}")
            return {"success": False, "error": str(e)}
    
    async def sign_out(self) -> Dict[str, Any]:
        """Sign out the current user"""
        try:
            self.client.auth.sign_out()
            return {"success": True}
        except Exception as e:
            logger.error(f"Sign out error: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get the current authenticated user"""
        try:
            user = self.client.auth.get_user()
            return user.user if user else None
        except Exception as e:
            logger.error(f"Get current user error: {e}")
            return None
    
    # Template Management
    async def create_template(self, template_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Create a new template"""
        try:
            template_data.update({
                "user_id": user_id,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            })
            
            response = self.client.table("templates").insert(template_data).execute()
            return {"success": True, "template": response.data[0] if response.data else None}
        except Exception as e:
            logger.error(f"Create template error: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_templates(self, user_id: Optional[str] = None, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get templates, optionally filtered by user and category"""
        try:
            query = self.client.table("templates").select("*")
            
            if user_id:
                query = query.eq("user_id", user_id)
            
            if category:
                query = query.eq("category", category)
            
            response = query.execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Get templates error: {e}")
            return []
    
    async def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific template by ID"""
        try:
            response = self.client.table("templates").select("*").eq("id", template_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Get template error: {e}")
            return None
    
    async def update_template(self, template_id: str, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a template"""
        try:
            template_data["updated_at"] = datetime.utcnow().isoformat()
            
            response = self.client.table("templates").update(template_data).eq("id", template_id).execute()
            return {"success": True, "template": response.data[0] if response.data else None}
        except Exception as e:
            logger.error(f"Update template error: {e}")
            return {"success": False, "error": str(e)}
    
    async def delete_template(self, template_id: str) -> Dict[str, Any]:
        """Delete a template"""
        try:
            response = self.client.table("templates").delete().eq("id", template_id).execute()
            return {"success": True}
        except Exception as e:
            logger.error(f"Delete template error: {e}")
            return {"success": False, "error": str(e)}
    
    # Draft Management
    async def create_draft(self, draft_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Create a new draft"""
        try:
            draft_data.update({
                "user_id": user_id,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": "draft"
            })
            
            response = self.client.table("drafts").insert(draft_data).execute()
            return {"success": True, "draft": response.data[0] if response.data else None}
        except Exception as e:
            logger.error(f"Create draft error: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_drafts(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all drafts for a user"""
        try:
            response = self.client.table("drafts").select("*").eq("user_id", user_id).order("updated_at", desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Get drafts error: {e}")
            return []
    
    async def get_draft(self, draft_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific draft by ID"""
        try:
            response = self.client.table("drafts").select("*").eq("id", draft_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Get draft error: {e}")
            return None
    
    async def update_draft(self, draft_id: str, draft_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a draft"""
        try:
            draft_data["updated_at"] = datetime.utcnow().isoformat()
            
            response = self.client.table("drafts").update(draft_data).eq("id", draft_id).execute()
            return {"success": True, "draft": response.data[0] if response.data else None}
        except Exception as e:
            logger.error(f"Update draft error: {e}")
            return {"success": False, "error": str(e)}
    
    async def delete_draft(self, draft_id: str) -> Dict[str, Any]:
        """Delete a draft"""
        try:
            response = self.client.table("drafts").delete().eq("id", draft_id).execute()
            return {"success": True}
        except Exception as e:
            logger.error(f"Delete draft error: {e}")
            return {"success": False, "error": str(e)}
    
    # File Storage
    async def upload_file(self, file_path: str, file_name: str, bucket: str = None) -> Dict[str, Any]:
        """Upload a file to Supabase Storage"""
        try:
            bucket_name = bucket or settings.SUPABASE_STORAGE_BUCKET
            
            with open(file_path, "rb") as f:
                response = self.client.storage.from_(bucket_name).upload(
                    path=file_name,
                    file=f,
                    file_options={"content-type": "image/jpeg"}
                )
            
            # Get public URL
            public_url = self.client.storage.from_(bucket_name).get_public_url(file_name)
            
            return {"success": True, "url": public_url, "path": file_name}
        except Exception as e:
            logger.error(f"Upload file error: {e}")
            return {"success": False, "error": str(e)}
    
    async def delete_file(self, file_name: str, bucket: str = None) -> Dict[str, Any]:
        """Delete a file from Supabase Storage"""
        try:
            bucket_name = bucket or settings.SUPABASE_STORAGE_BUCKET
            response = self.client.storage.from_(bucket_name).remove([file_name])
            return {"success": True}
        except Exception as e:
            logger.error(f"Delete file error: {e}")
            return {"success": False, "error": str(e)}
    
    # Threadstorm History
    async def save_threadstorm(self, threadstorm_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Save a completed threadstorm"""
        try:
            threadstorm_data.update({
                "user_id": user_id,
                "created_at": datetime.utcnow().isoformat(),
                "status": "completed"
            })
            
            response = self.client.table("threadstorms").insert(threadstorm_data).execute()
            return {"success": True, "threadstorm": response.data[0] if response.data else None}
        except Exception as e:
            logger.error(f"Save threadstorm error: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_threadstorm_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get threadstorm history for a user"""
        try:
            response = self.client.table("threadstorms").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Get threadstorm history error: {e}")
            return []


# Global Supabase service instance
supabase_service = SupabaseService()
