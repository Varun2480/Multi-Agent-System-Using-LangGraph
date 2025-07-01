from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL

class ApplicationSettings(BaseSettings):
    google_api_key: str
    # langchain_api_key: str
    # langchain_tracing_v2: str
    # langchain_project: str
    new_db_host: str
    new_db_port: int
    new_db_username: str
    new_db_password: str
    new_db_name: str
    new_db_pool: int = 5
    # gcp_region: str
    gcp_project_id: str
    gcp_location: str
    google_cloud_project: str
    google_cloud_location: str
    google_genai_use_vertexai: bool
    google_application_credentials: str



    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def postgres_connection_string(self):
        """
        Generate secure database connection string
        """
        connection_string = URL.create(
            drivername="postgresql",
            username=self.new_db_username,
            password=self.new_db_password,
            host=self.new_db_host,
            port=self.new_db_port,
            database=self.new_db_name,
        )

        return connection_string
    
SETTINGS = ApplicationSettings()