from pydantic_settings import BaseSettings
from functools import lru_cache
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.keyvault.secrets import SecretClient
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    APP_NAME: str = "MoI Digital Reporting System"
    API_VERSION: str = "v1"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Azure Key Vault
    AZURE_KEY_VAULT_NAME: str
    AZURE_TENANT_ID: Optional[str] = None
    AZURE_CLIENT_ID: Optional[str] = None
    AZURE_CLIENT_SECRET: Optional[str] = None
    
    # =========================================================
    # 🔐 Secrets (Loaded from Key Vault)
    # =========================================================
    
    # 1. Databases (Hot & Cold)
    SQLALCHEMY_DATABASE_URI_OPS: Optional[str] = None      # Operations DB (Hot)
    SQLALCHEMY_DATABASE_URI_ANALYTICS: Optional[str] = None # Analytics DB (Cold)
    
    # 2. Storage
    BLOB_STORAGE_CONNECTION_STRING: Optional[str] = None
    
    # 3. Security
    SECRET_KEY: Optional[str] = None
    
    # 4. Hot Path Integration (Queue)
    AZURE_SERVICE_BUS_CONNECTION_STRING: Optional[str] = None
    
    # 5. AI Services
    AZURE_SPEECH_KEY: Optional[str] = None
    AZURE_SPEECH_REGION: str = "eastus" # Can be overridden by env var
    AZURE_ML_ENDPOINT: Optional[str] = None
    AZURE_ML_API_KEY: Optional[str] = None
    
    # =========================================================
    # ⚙️ Static Config
    # =========================================================
    BLOB_CONTAINER_NAME: str = "report-attachments"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://localhost:8080", "capacitor://localhost"]
    RATE_LIMIT_PER_MINUTE: int = 60

    class Config:
        case_sensitive = True
        env_file = ".env" if os.getenv("ENVIRONMENT", "development") == "development" else None


class AzureKeyVaultManager:
    def __init__(self, settings: Settings):
        self.settings = settings
        # In local dev, we might skip KV if env vars are present, 
        # but this ensures we can connect if needed.
        if self.settings.AZURE_KEY_VAULT_NAME:
            self.key_vault_url = f"https://{settings.AZURE_KEY_VAULT_NAME}.vault.azure.net/"
            self.credential = self._get_credential()
            self.secret_client = SecretClient(vault_url=self.key_vault_url, credential=self.credential)
    
    def _get_credential(self):
        if self.settings.ENVIRONMENT == "development":
            if all([self.settings.AZURE_TENANT_ID, self.settings.AZURE_CLIENT_ID, self.settings.AZURE_CLIENT_SECRET]):
                return ClientSecretCredential(
                    tenant_id=self.settings.AZURE_TENANT_ID,
                    client_id=self.settings.AZURE_CLIENT_ID,
                    client_secret=self.settings.AZURE_CLIENT_SECRET
                )
        return DefaultAzureCredential()

    def get_secret(self, secret_name: str) -> str:
        try:
            secret = self.secret_client.get_secret(secret_name)
            return secret.value
        except Exception as e:
            logger.error(f"Error retrieving secret '{secret_name}': {e}")
            raise

    def load_secrets_to_settings(self, settings: Settings) -> Settings:
        """
        Maps Azure Key Vault secret names (Kebab-Case or CamelCase) 
        to Pydantic Settings (SNAKE_CASE).
        """
        # Format: "NameInKeyVault": "NameInSettings"
        secrets_mapping = {
            # Databases
            "SqlOpsConnectionString": "SQLALCHEMY_DATABASE_URI_OPS",
            "SqlAnalyticsConnectionString": "SQLALCHEMY_DATABASE_URI_ANALYTICS",
            
            # Storage & Security
            "BlobStorageConnectionString": "BLOB_STORAGE_CONNECTION_STRING",
            "JwtSecretKey": "SECRET_KEY",
            
            # Hot Path Queue
            "ServiceBusConnectionString": "AZURE_SERVICE_BUS_CONNECTION_STRING",
            
            # AI Services
            "SpeechServiceKey": "AZURE_SPEECH_KEY",
            "AzureMlEndpoint": "AZURE_ML_ENDPOINT",
            "AzureMlApiKey": "AZURE_ML_API_KEY",
        }

        for kv_name, setting_name in secrets_mapping.items():
            # Only fetch from KV if not already set via Environment Variable
            if getattr(settings, setting_name) is None:
                try:
                    value = self.get_secret(kv_name)
                    setattr(settings, setting_name, value)
                    logger.info(f"✓ Loaded secret: {kv_name}")
                except Exception as e:
                    logger.error(f"✗ Failed to load secret '{kv_name}': {e}")
                    # Fail fast in production
                    if settings.ENVIRONMENT == "production":
                        raise RuntimeError(f"Critical secret '{kv_name}' missing in production")
        
        return settings


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    
    # If critical DB connection is missing, attempt to load from Key Vault
    if settings.SQLALCHEMY_DATABASE_URI_OPS is None and settings.AZURE_KEY_VAULT_NAME:
        try:
            kv_manager = AzureKeyVaultManager(settings)
            settings = kv_manager.load_secrets_to_settings(settings)
        except Exception as e:
            logger.warning(f"Could not load secrets from Key Vault: {e}")
            
    return settings