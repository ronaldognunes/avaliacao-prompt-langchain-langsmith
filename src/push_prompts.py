"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    try:
        system_prompt = prompt_data["system_prompt"]
        user_prompt = prompt_data["user_prompt"]

        prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", user_prompt),
            ]
        )

        description = prompt_data.get("description", "Prompt otimizado")
        tags = list(prompt_data.get("tags", []))
        techniques = list(prompt_data.get("techniques", []))

        # Publicar técnicas como tags para facilitar rastreio no Hub.
        technique_tags = [f"technique:{tech}" for tech in techniques]
        all_tags = sorted(set(tags + technique_tags))

        version = prompt_data.get("version", "v2")
        readme = (
            f"# {prompt_name}\n\n"
            f"- Versão: {version}\n"
            f"- Técnicas: {', '.join(techniques) if techniques else 'não informadas'}\n"
        )

        result_url = hub.push(
            prompt_name,
            prompt_template,
            api_url=os.getenv("LANGSMITH_ENDPOINT"),
            api_key=os.getenv("LANGSMITH_API_KEY"),
            new_repo_is_public=True,
            new_repo_description=description,
            readme=readme,
            tags=all_tags,
        )

        print(f"   ✓ Push concluído: {result_url}")
        print(f"   ✓ Tags: {', '.join(all_tags) if all_tags else 'nenhuma'}")
        return True
    except Exception as e:
        print(f"   ❌ Erro no push de '{prompt_name}': {e}")
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    errors = []

    required_fields = [
        "description",
        "system_prompt",
        "user_prompt",
        "version",
        "tags",
        "techniques",
    ]

    for field in required_fields:
        if field not in prompt_data:
            errors.append(f"Campo obrigatório faltando: {field}")

    system_prompt = str(prompt_data.get("system_prompt", "")).strip()
    user_prompt = str(prompt_data.get("user_prompt", "")).strip()

    if not system_prompt:
        errors.append("system_prompt está vazio")
    if not user_prompt:
        errors.append("user_prompt está vazio")

    techniques = prompt_data.get("techniques", [])
    if not isinstance(techniques, list):
        errors.append("techniques deve ser uma lista")
    elif len(techniques) < 2:
        errors.append("Mínimo de 2 técnicas é obrigatório (Few-shot + 1 adicional)")

    tags = prompt_data.get("tags", [])
    if tags and not isinstance(tags, list):
        errors.append("tags deve ser uma lista")

    if "few-shot" not in system_prompt.lower() and "few-shot" not in " ".join(
        [str(t).lower() for t in techniques]
    ):
        errors.append("Few-shot Learning não foi identificado no prompt/metadados")

    return (len(errors) == 0, errors)


def main():
    """Função principal"""
    print_section_header("Push de prompts otimizados para o LangSmith")

    if not check_env_vars([
        "LANGSMITH_ENDPOINT",
        "LANGSMITH_API_KEY",
        "USERNAME_LANGSMITH_HUB",
    ]):
        return 1

    prompts_file = Path("prompts") / "bug_to_user_story_v2.yml"

    if not prompts_file.exists():
        print(f"❌ Arquivo não encontrado: {prompts_file}")
        return 1

    yaml_data = load_yaml(str(prompts_file))
    if not yaml_data:
        print("❌ Não foi possível carregar o YAML de prompts")
        return 1

    username = os.getenv("USERNAME_LANGSMITH_HUB", "").strip()
    if not username:
        print("❌ USERNAME_LANGSMITH_HUB está vazio no .env")
        return 1

    pushed_count = 0
    failed_count = 0

    for prompt_key, prompt_data in yaml_data.items():
        print(f"\nProcessando prompt: {prompt_key}")

        is_valid, errors = validate_prompt(prompt_data)
        if not is_valid:
            print("   ❌ Prompt inválido:")
            for err in errors:
                print(f"      - {err}")
            failed_count += 1
            continue

        remote_name = f"{username}/{prompt_key}"
        print(f"   Repositório remoto: {remote_name}")

        success = push_prompt_to_langsmith(remote_name, prompt_data)
        if success:
            pushed_count += 1
        else:
            failed_count += 1

    print_section_header("Resumo")
    print(f"Prompts publicados: {pushed_count}")
    print(f"Falhas: {failed_count}")

    if pushed_count == 0:
        print("\n❌ Nenhum prompt foi publicado com sucesso")
        return 1

    print("\n✅ Processo concluído")
    print("Próximo passo: execute `python src/evaluate.py` para avaliar as métricas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
