from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

class PagamentoCreate(BaseModel):
    id_os: int = Field(..., gt=0)
    valor: float = Field(..., gt=0)
    forma_pagamento: str = Field(min_length=1, max_length=50)

class PagamentoUpdate(BaseModel):
    valor: float = Field(..., gt=0)
    forma_pagamento: str = Field(min_length=1, max_length=50)
    status: str = Field(default="pendente")

class PagamentoStatusUpdate(BaseModel):
    status: str

class PagamentoPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_pagamento: int
    id_os: int
    valor: float
    forma_pagamento: str
    status: str
    data_pagamento: datetime | None = None
    created_at: datetime
    updated_at: datetime | None = None
