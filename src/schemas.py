from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, field_validator

class SeverityLevel(str, Enum):
    LOW = "Baixa"
    MEDIUM = "Media"
    HIGH = "Alta"
    CRITICAL = "Critica"

class NonConformityReport(BaseModel):
    item_id: str = Field(
        ...,
        description="Identificador unico da peca, montagem ou lote (ex: ASY-7842)",
        min_length=3
    )
    defect_category: str = Field(
        ...,
        description="Classificacao tecnica do defeito (ex: Trinca estrutural, Falha de torque, Delaminacao)"
    )
    severity: SeverityLevel = Field(
        ...,
        description="Nivel de severidade tecnica da nao-conformidade"
    )
    detected_evidence: List[str] = Field(
        default_factory=list,
        description="Pontos factuais observados na imagem ou descricao"
    )
    missing_fields: List[str] = Field(
        default_factory=list,
        description="Campos mandatorios ausentes no relato inicial"
    )
    bilingual_summary: Dict[str, str] = Field(
        ...,
        description="Descricao tecnica padronizada em pt-BR e en-US"
    )
    is_valid_for_submission: bool = Field(
        default=False,
        description="Flag deterministica que autoriza ou bloqueia o envio ao sistema de qualidade"
    )

    @field_validator("bilingual_summary")
    @classmethod
    def validate_languages(cls, v: Dict[str, str]) -> Dict[str, str]:
        if "pt_BR" not in v or "en_US" not in v:
            raise ValueError("O resumo deve conter as chaves obrigatórias 'pt_BR' e 'en_US'.")
        if not v["pt_BR"].strip() or not v["en_US"].strip():
            raise ValueError("Os resumos bilingues nao podem ser vazios.")
        return v

class AgentExecutionResult(BaseModel):
    status: str
    report: Optional[NonConformityReport] = None
    action_taken: str
    feedback_to_operator: Optional[str] = None
