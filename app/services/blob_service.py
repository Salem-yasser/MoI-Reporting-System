from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from azure.core.exceptions import AzureError
from datetime import datetime, timedelta, timezone
from typing import Optional
import uuid
import logging

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

class BlobStorageService:
    """Azure Blob Storage operations"""
    
    def __init__(self):
        if not settings.BLOB_STORAGE_CONNECTION_STRING:
            raise ValueError("BLOB_STORAGE_CONNECTION_STRING is not configured")
        
        self.blob_service_client = BlobServiceClient.from_connection_string(
            settings.BLOB_STORAGE_CONNECTION_STRING
        )
        self.container_name = getattr(settings, 'BLOB_CONTAINER_NAME', 'report-attachments')
        
        # Ensure container exists
        self._ensure_container_exists()
    
    def _ensure_container_exists(self):
        """Create container if it doesn't exist"""
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            if not container_client.exists():
                container_client.create_container()
                logger.info(f"Created container: {self.container_name}")
        except AzureError as e:
            logger.error(f"Error ensuring container exists: {e}")
    
    def upload_file(
        self, 
        file_content: bytes, 
        filename: str,
        content_type: str
    ) -> Optional[str]:
        """
        Upload file to Azure Blob Storage
        
        Args:
            file_content: File bytes
            filename: Original filename
            content_type: MIME type
        
        Returns:
            Blob URL if successful, None otherwise
        """
        try:
            # Generate unique blob name
            file_extension = filename.split('.')[-1] if '.' in filename else 'bin'
            blob_name = f"{uuid.uuid4()}.{file_extension}"
            
            # Get blob client
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            # Upload file with metadata
            blob_client.upload_blob(
                file_content,
                content_settings={
                    'content_type': content_type
                },
                overwrite=True,
                metadata={
                    'original_filename': filename,
                    'uploaded_at': datetime.now(timezone.utc).isoformat()
                }
            )
            
            logger.info(f"Uploaded file: {blob_name} ({len(file_content)} bytes)")
            
            # Return URL
            return blob_client.url
        
        except AzureError as e:
            logger.error(f"Error uploading file '{filename}': {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error uploading file '{filename}': {e}")
            return None
    
    def delete_file(self, blob_url: str) -> bool:
        """Delete file from storage"""
        try:
            # Extract blob name from URL
            blob_name = blob_url.split('/')[-1].split('?')[0]  # Remove SAS token if present
            
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            blob_client.delete_blob()
            logger.info(f"Deleted blob: {blob_name}")
            return True
            
        except AzureError as e:
            logger.error(f"Error deleting file from {blob_url}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting file: {e}")
            return False
    
    def generate_download_url(
        self, 
        blob_url: str,
        expiry_hours: int = 1
    ) -> Optional[str]:
        """Generate temporary download URL with SAS token"""
        try:
            # Extract blob name from URL
            blob_name = blob_url.split('/')[-1].split('?')[0]
            
            # Get account key from connection string
            account_key = self._get_account_key()
            
            if not account_key:
                logger.error("Could not extract account key from connection string")
                return None
            
            # Generate SAS token
            sas_token = generate_blob_sas(
                account_name=self.blob_service_client.account_name,
                container_name=self.container_name,
                blob_name=blob_name,
                account_key=account_key,
                permission=BlobSasPermissions(read=True),
                expiry=datetime.now(timezone.utc) + timedelta(hours=expiry_hours)
            )
            
            # Return URL with SAS token
            base_url = blob_url.split('?')[0]  # Remove existing SAS if any
            return f"{base_url}?{sas_token}"
        
        except AzureError as e:
            logger.error(f"Error generating SAS token for {blob_url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error generating SAS token: {e}")
            return None
    
    def _get_account_key(self) -> Optional[str]:
        """Extract account key from connection string"""
        try:
            conn_str = settings.BLOB_STORAGE_CONNECTION_STRING
            for part in conn_str.split(';'):
                if part.startswith('AccountKey='):
                    return part.replace('AccountKey=', '')
            return None
        except Exception:
            return None
    
    def get_file_metadata(self, blob_url: str) -> Optional[dict]:
        """Get file metadata"""
        try:
            blob_name = blob_url.split('/')[-1].split('?')[0]
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            properties = blob_client.get_blob_properties()
            
            return {
                'size': properties.size,
                'content_type': properties.content_settings.content_type,
                'created_on': properties.creation_time,
                'last_modified': properties.last_modified,
                'metadata': properties.metadata
            }
        except AzureError as e:
            logger.error(f"Error getting metadata for {blob_url}: {e}")
            return None