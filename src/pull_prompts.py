"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()


#def pull_prompts_from_langsmith():
#    ...


#def main():
#    """Função principal"""
#    ...

def pull_prompts_from_langsmith():
    """Faz pull de um prompt do LangSmith Hub"""

    print_section_header("Pull de prompt do LangSmith")

    # garante que as variáveis necessárias existem
    check_env_vars([
        "LANGSMITH_ENDPOINT",
        "LANGSMITH_API_KEY"
    ])

    try:
        # 👇 IMPORTANTE: substitua pelo nome do seu prompt no hub
        # formato comum: "owner/nome_prompt"
        prompt_id = "leonanluppi/bug_to_user_story_v1"

        print(f"Buscando prompt: {prompt_id}")

        # 🔥 pull do prompt
        prompt = hub.pull(prompt_id)

        if not prompt:
            raise Exception("Prompt não encontrado no LangSmith Hub")

        # 📦 serialização nativa do LangChain
        prompt_dict = prompt.dict()

        print("Prompt carregado com sucesso!")

        return prompt_dict

    except Exception as e:
        print(f"Erro ao buscar prompt: {e}")
        raise


def main():
    """Função principal"""

    try:
        print_section_header("Início do processo")

        prompt_data = pull_prompts_from_langsmith()

        # 📁 caminho de saída
        output_dir = Path("prompts")
        output_dir.mkdir(exist_ok=True)

        output_file = output_dir / "bug_to_user_story_v1.yml"

        # 💾 salvar YAML
        save_yaml(prompt_data, output_file)

        print(f"Prompt salvo em: {output_file}")

        print_section_header("Finalizado com sucesso")

        return 0

    except Exception as e:
        print(f"Erro geral: {e}")
        return 1



if __name__ == "__main__":
    sys.exit(main())
