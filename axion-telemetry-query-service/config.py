"""
Axion Telemetry Query Service - Configuration
"""

import os
from dataclasses import dataclass

@dataclass
class Settings:
    # PostgreSQL connection string
    # Format: postgresql://<user>:<password>@<host>:<port>/<database>
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        #"postgresql://axion_user:P%40ssw01rd%40123@localhost:5432/axion_db",
        "postgresql://Akkalkot:Akkalkot%40413216@postgresql-service-pod:5432/axiondb"
    )
    # Allows configuring a different port, e.g., if we run multiple services
    PORT: int = int(os.getenv("PORT", "8000"))

settings = Settings()
