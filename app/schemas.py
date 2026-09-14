from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AssetType(str, Enum):
    SERVER = "Server"
    LAPTOP = "Laptop"
    DESKTOP = "Desktop"
    APPLICATION = "Application"
    DATABASE = "Database"


class Environment(str, Enum):
    PRODUCTION = "Production"
    TEST = "Test"
    DEVELOPMENT = "Development"
    CORPORATE = "Corporate"


class AssetStatus(str, Enum):
    ACTIVE = "Active"
    MAINTENANCE = "Maintenance"
    RETIRED = "Retired"


class AssetBase(BaseModel):
    asset_tag: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=150)
    asset_type: AssetType
    owner: str = Field(min_length=1, max_length=100)
    environment: Environment
    status: AssetStatus
    location: str = Field(min_length=1, max_length=150)
    operating_system: str = Field(min_length=1, max_length=100)

    @field_validator("asset_tag", "name", "owner", "location", "operating_system")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value


class AssetCreate(AssetBase):
    pass


class AssetUpdate(AssetBase):
    pass


class AssetRead(AssetBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
