from __future__ import annotations

import uuid
from pydantic import BaseModel, ConfigDict


class SupplierDirectoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    email: str
    city: str
    country_code: str
    material_categories: list[str]
