import pytest

from app.core.qwen3_engine import Qwen3Engine


@pytest.mark.integration
def test_qwen_model_loads():

    engine = Qwen3Engine()

    engine.load()

    assert (
        engine.model is not None
    )



@pytest.mark.unit
def test_qwen_character_methods_exist():

    engine = Qwen3Engine()


    methods = dir(engine)


    expected = [
        "clone_voice",
        "create_character",
        "generate_roleplay",
    ]


    for method in expected:

        assert method in methods