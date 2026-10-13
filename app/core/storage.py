import logging
from supabase import create_client, Client
from app.core.config import settings

logger = logging.getLogger(__name__)

def get_supabase_client() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def upload_file(file_content: bytes, file_name: str, content_type: str) -> str:
    """
    Uploads a file to Supabase Storage and returns the file path.
    """
    supabase = get_supabase_client()
    try:
        res = supabase.storage.from_(settings.STORAGE_BUCKET).upload(
            file_name, 
            file_content,
            file_options={"content-type": content_type}
        )
        return file_name
    except Exception as e:
        logger.error(f"Failed to upload to Supabase: {e}")
        raise e

def get_signed_url(file_name: str, expires_in: int = 3600) -> str:
    """
    Generates a signed URL for a file in Supabase Storage.
    """
    supabase = get_supabase_client()
    try:
        res = supabase.storage.from_(settings.STORAGE_BUCKET).create_signed_url(file_name, expires_in)
        return res['signedURL']
    except Exception as e:
        logger.error(f"Failed to get signed URL: {e}")
        return ""
