from app.api.main import SpeechRequest, _generate_audio


def test_generate_audio_falls_back_on_gpu_memory_error(monkeypatch):
    request = SpeechRequest(text="hello world", voice="custom")

    def raise_gpu_error(*args, **kwargs):
        raise RuntimeError("CUDA out of memory")

    monkeypatch.setattr(
        "app.api.main.engine.generate_custom_voice",
        raise_gpu_error,
    )

    audio, sample_rate = _generate_audio(request, "hello world")

    assert sample_rate == 22050
    assert len(audio) > 0
