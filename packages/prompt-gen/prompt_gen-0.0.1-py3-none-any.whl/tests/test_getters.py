import pytest
from prompt_generator.generator import PromptGenerator


@pytest.fixture
def get_prompt_model():
    return PromptGenerator()


def test_get_random_style(get_prompt_model):
    assert get_prompt_model.get_random_style() in get_prompt_model.styles
