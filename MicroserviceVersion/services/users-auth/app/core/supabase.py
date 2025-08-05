"""
Basic Supabase client for authentication only
"""
import logging
from supabase import create_client, Client
from app.config import get_config

logger = logging.getLogger(__name__)


class SupabaseAuthClient:
    """Basic Supabase client for authentication operations"""
    
    def __init__(self):
        self.config = get_config()
        self._validate_auth_config()
        
        # Initialize clients
        self.client = create_client(
            self.config.SUPABASE_URL,
            self.config.SUPABASE_ANON_KEY
        )
        
        self.admin_client = create_client(
            self.config.SUPABASE_URL,
            self.config.SUPABASE_SERVICE_ROLE_KEY
        )
        
        logger.info("Supabase auth client initialized")
    
    def _validate_auth_config(self):
        """Validate required auth configuration"""
        required = ['SUPABASE_URL', 'SUPABASE_ANON_KEY', 'SUPABASE_SERVICE_ROLE_KEY']
        missing = [var for var in required if not getattr(self.config, var)]
        
        if missing:
            raise ValueError(f"Missing Supabase config: {', '.join(missing)}")
    
    @property
    def jwt_secret(self):
        """Get JWT secret"""
        return self.config.SUPABASE_JWT_SECRET


# Global instance
_auth_client = None

def get_auth_client():
    """Get global auth client instance"""
    global _auth_client
    if _auth_client is None:
        _auth_client = SupabaseAuthClient()
    return _auth_client

def get_supabase():
    """Get Supabase client for user operations"""
    return get_auth_client().client

def get_supabase_admin():
    """Get Supabase admin client"""
    return get_auth_client().admin_client

def get_jwt_secret():
    """Get JWT secret"""
    return get_auth_client().jwt_secret