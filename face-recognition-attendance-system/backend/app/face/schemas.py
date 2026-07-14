import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class FaceRegisterResponse(BaseModel):
    id: uuid.UUID = Field(..., description="Unique face embedding identifier")
    model_name: str = Field(..., description="Face recognition model used for embedding")
    image_path: str = Field(..., description="Path to the stored face image")
    created_at: datetime = Field(..., description="Embedding creation timestamp")

    model_config = {"from_attributes": True}


class FaceResponse(BaseModel):
    id: uuid.UUID = Field(..., description="Unique face embedding identifier")
    model_name: str = Field(..., description="Face recognition model used for embedding")
    image_path: str = Field(..., description="Path to the stored face image")
    created_at: datetime = Field(..., description="Embedding creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {"from_attributes": True}



