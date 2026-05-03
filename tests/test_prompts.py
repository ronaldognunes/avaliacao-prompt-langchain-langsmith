"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

PROMPTS_FILE = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"
PROMPT_KEY = "bug_to_user_story_v2"


def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def prompt_data():
    """Carrega e retorna os dados do prompt uma única vez por sessão de testes."""
    assert PROMPTS_FILE.exists(), f"Arquivo de prompt não encontrado: {PROMPTS_FILE}"
    raw = load_prompts(PROMPTS_FILE)
    assert raw is not None, f"Falha ao parsear YAML: {PROMPTS_FILE}"
    assert PROMPT_KEY in raw, (
        f"Chave '{PROMPT_KEY}' não encontrada no YAML. "
        f"Chaves disponíveis: {list(raw.keys())}"
    )
    return raw[PROMPT_KEY]


class TestPrompts:
    def test_prompt_has_system_prompt(self, prompt_data):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert "system_prompt" in prompt_data, (
            "Campo obrigatório 'system_prompt' não encontrado no YAML"
        )
        assert prompt_data["system_prompt"].strip(), (
            "Campo 'system_prompt' existe mas está vazio"
        )

    def test_prompt_has_role_definition(self, prompt_data):
        """Verifica se o prompt define uma persona (ex: 'Você é um Product Manager')."""
        system_prompt = prompt_data["system_prompt"]
        assert "Você é" in system_prompt, (
            "O system_prompt deve definir uma persona começando com 'Você é ...'"
        )

    def test_prompt_mentions_format(self, prompt_data):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        system_prompt = prompt_data["system_prompt"]
        format_keywords = ["Markdown", "User Story", "Como <ator>", "eu quero", "para que"]
        assert any(kw in system_prompt for kw in format_keywords), (
            f"O system_prompt deve mencionar o formato esperado. "
            f"Esperado pelo menos um de: {format_keywords}"
        )

    def test_prompt_has_few_shot_examples(self, prompt_data):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        system_prompt = prompt_data["system_prompt"]
        has_example_marker = "Exemplo" in system_prompt
        has_io_pair = "Entrada:" in system_prompt and "Saída:" in system_prompt
        assert has_example_marker and has_io_pair, (
            "O system_prompt deve conter exemplos few-shot com as marcações "
            "'Exemplo', 'Entrada:' e 'Saída:'"
        )

    def test_prompt_no_todos(self, prompt_data):
        """Garante que não há [TODO] esquecido no texto do prompt."""
        system_prompt = prompt_data["system_prompt"]
        user_prompt = prompt_data.get("user_prompt", "")
        full_text = system_prompt + user_prompt
        assert "[TODO]" not in full_text, (
            "O prompt ainda contém marcadores [TODO] não resolvidos. "
            "Remova ou complete todos os TODOs antes de publicar."
        )

    def test_minimum_techniques(self, prompt_data):
        """Verifica se pelo menos 2 técnicas foram listadas nos metadados do YAML."""
        techniques = prompt_data.get("techniques", [])
        assert isinstance(techniques, list), (
            "O campo 'techniques' deve ser uma lista no YAML"
        )
        assert len(techniques) >= 2, (
            f"Mínimo de 2 técnicas requeridas, encontradas {len(techniques)}: {techniques}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
