from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "OpenDomain"
    app_url: str = "http://localhost:3000"
    api_url: str = "http://localhost:8000"
    debug: bool = False

    database_url: str = "postgresql+asyncpg://opendomain:opendomain@localhost:5432/opendomain"
    redis_url: str = "redis://localhost:6379/0"

    secret_key: str = "change-me-to-a-random-secret-key"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    cors_origins: list[str] = ["http://localhost:3000"]

    anthropic_model: str = "anthropic.claude-fable-5"
    aws_region: str = "ap-southeast-2"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""

    epp_host: str = "epp.registry.example"
    epp_port: int = 700
    epp_client_id: str = ""
    epp_password: str = ""
    epp_cert_path: str = "./certs/epp-client.pem"
    epp_key_path: str = "./certs/epp-client-key.pem"
    epp_simulate: bool = True

    dns_provider: str = "powerdns"
    powerdns_api_url: str = "http://localhost:8081"
    powerdns_api_key: str = "change-me"

    whois_privacy_default: bool = True

    model_config = {"env_file": ".env", "case_sensitive": False}


settings = Settings()
