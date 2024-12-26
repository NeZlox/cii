from typing import Optional
from pydantic import BaseModel, Field


class StartParsingRequestSchema(BaseModel):
    start_id: Optional[int] = Field(default=None, description="Начальный ID поста для парсинга", ge=1)
    end_id: Optional[int] = Field(default=None, description="Конечный ID поста для парсинга", ge=1)


class StartParsingResponseSchema(BaseModel):
    status: str = Field(..., description="Статус запуска парсера")
    start_id: Optional[int] = Field(..., description="Начальный ID поста")
    end_id: Optional[int] = Field(..., description="Конечный ID поста")


class ParsingResultSchema(BaseModel):
    start_id: int = Field(..., description="Начальный ID поста")
    end_id: int = Field(..., description="Конечный ID поста")
