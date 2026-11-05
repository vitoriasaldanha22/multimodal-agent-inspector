import json
from typing import Any, Callable, Dict, List, Optional
from src.schemas import NonConformityReport, SeverityLevel, AgentExecutionResult

# Simulação de Tool Calling / Function Calling para persistência em ERP/MES
def dispatch_quality_notification(report_data: Dict[str, Any]) -> str:
    """Ferramenta chamada pelo agente quando o relatório está 100% validado."""
    return f"SUCESSO: Notificacao CD-{report_data['item_id']} registrada no sistema central com status APROVADO."

class InspectionAgent:
    """
    Agente responsável por orquestrar a extração estruturada (Structured Output),
    verificação determinística de integridade e Tool Calling.
    """
    def __init__(self, system_prompt: Optional[str] = None):
        self.system_prompt = system_prompt or self._default_prompt()
        self.tools: Dict[str, Callable] = {
            "dispatch_quality_notification": dispatch_quality_notification
        }

    def _default_prompt(self) -> str:
        return (
            "Você é um Especialista de Engenharia da Qualidade Aeronáutica e Manufatura. "
            "Sua função é analisar a descrição do operador e os metadados visuais, "
            "extraindo estritamente um JSON que obedeça ao contrato NonConformityReport. "
            "Se faltarem informações cruciais para a auditoria, identifique-as no campo 'missing_fields'."
        )

    def mock_llm_inference(self, raw_text: str, visual_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Simula a chamada de LLM multimodal com Structured Output (JSON Schema garantido).
        Permite testar o fluxo end-to-end sem expor credenciais ou chaves corporativas.
        """
        lower_text = raw_text.lower()
        missing = []
        
        # Regras de integridade técnica
        if "peça" not in lower_text and "item" not in lower_text and "pn" not in lower_text:
            missing.append("Part Number / Identificador do Item")
        if "local" not in lower_text and "posição" not in lower_text and "estação" not in lower_text:
            missing.append("Localização/Estação de Montagem")

        is_valid = len(missing) == 0
        severity = SeverityLevel.CRITICAL if "trinca" in lower_text or "rachadura" in lower_text else SeverityLevel.MEDIUM

        return {
            "item_id": "PN-A320-BRG" if "pn" in lower_text or "peça" in lower_text else "UNKNOWN-ITEM",
            "defect_category": "Fadiga Mecânica / Fissura Superficial" if "trinca" in lower_text else "Desvio Dimensional",
            "severity": severity.value,
            "detected_evidence": [
                f"Input textual: '{raw_text}'",
                f"Análise visual detectada: {visual_metadata.get('features', 'Sem anomalia geométrica') if visual_metadata else 'Sem imagem'}"
            ],
            "missing_fields": missing,
            "bilingual_summary": {
                "pt_BR": f"Identificado defeito do tipo {severity.value}: {raw_text}",
                "en_US": f"Identified {severity.value} defect: translated summary of '{raw_text}'"
            },
            "is_valid_for_submission": is_valid
        }

    def run(self, raw_input: str, visual_data: Optional[Dict[str, Any]] = None) -> AgentExecutionResult:
        # 1. Inferência com Structured Output
        raw_llm_payload = self.mock_llm_inference(raw_input, visual_data)

        # 2. Validação determinística de Schema com Pydantic
        report = NonConformityReport.model_validate(raw_llm_payload)

        # 3. Tomada de Decisão baseada em Guardrails
        if report.is_valid_for_submission:
            tool_output = self.tools["dispatch_quality_notification"](report.model_dump())
            return AgentExecutionResult(
                status="DISPATCHED",
                report=report,
                action_taken=f"Tool executada: {tool_output}",
                feedback_to_operator="Relatório aceito e registrado com sucesso no sistema central."
            )
        else:
            missing_items = ", ".join(report.missing_fields)
            return AgentExecutionResult(
                status="ACTION_REQUIRED",
                report=report,
                action_taken="Registro bloqueado pelo guardrail de integridade.",
                feedback_to_operator=f"Informações incompletas. Por favor, forneça: {missing_items}"
            )
