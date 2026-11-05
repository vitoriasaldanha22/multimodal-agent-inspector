import sys
from src.agent import InspectionAgent

def run_inspection_pipeline(user_query: str, visual_info: dict):
    print("=" * 60)
    print("Iniciando Pipeline do Multimodal Agent Inspector...")
    print(f"Texto do Operador: {user_query}")
    print(f"Evidências Visuais: {visual_info}")
    print("=" * 60)

    agent = InspectionAgent()
    result = agent.run(raw_input=user_query, visual_data=visual_info)

    print(f"STATUS DO AGENTE: {result.status}")
    print(f"FEEDBACK AO USUÁRIO: {result.feedback_to_operator}")
    print(f"AÇÃO EXECUTADA: {result.action_taken}")
    print("
PAYLOAD JSON VALIDADO (Pydantic):")
    if result.report:
        print(result.report.model_dump_json(indent=2))
    print("=" * 60)
    return result

if __name__ == "__main__":
    # Caso 1: Entrada incompleta (bloqueio por falta de dados)
    print("\n>>> CENÁRIO 1: Descrição incompleta")
    run_inspection_pipeline(
        user_query="Notei uma trinca na asa durante a vistoria",
        visual_info={"features": "Linha de fratura identificada a 45 graus"}
    )

    # Caso 2: Entrada completa (aprovação e chamada de Tool)
    print("\n>>> CENÁRIO 2: Descrição técnica completa")
    run_inspection_pipeline(
        user_query="Trinca identificada na peça PN-A320-BRG na posição estação 42",
        visual_info={"features": "Linha de fratura identificada a 45 graus"}
    )
