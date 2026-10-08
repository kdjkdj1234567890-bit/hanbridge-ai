"""Offline smoke tests for HanBridge AI (no network, no API key needed)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from hanbridge import llm, prompts  # noqa: E402


def test_extract_json_plain():
    d = llm.extract_json('{"a": 1}')
    assert d == {"a": 1}, d


def test_extract_json_fenced():
    d = llm.extract_json('```json\n{"translation": "hi"}\n```')
    assert d == {"translation": "hi"}, d


def test_extract_json_noisy():
    d = llm.extract_json('Sure! Here it is:\n{"x": [1, 2]}\nDone.')
    assert d == {"x": [1, 2]}, d


def test_extract_json_invalid_raises():
    try:
        llm.extract_json("no json here")
    except Exception:
        return
    raise AssertionError("expected an exception for non-JSON input")


class _FakeMsg:
    def __init__(self, content):
        self.content = content


class _FakeChoice:
    def __init__(self, content):
        self.message = _FakeMsg(content)


class _FakeResp:
    def __init__(self, content):
        self.choices = [_FakeChoice(content)]


class _FakeCompletions:
    def __init__(self, content):
        self._content = content
        self.last_kwargs = None

    def create(self, **kwargs):
        self.last_kwargs = kwargs
        return _FakeResp(self._content)


class _FakeChat:
    def __init__(self, content):
        self.completions = _FakeCompletions(content)


class _FakeClient:
    def __init__(self, content):
        self.chat = _FakeChat(content)


def test_translate_json_uses_json_mode_and_parses():
    client = _FakeClient('{"translation": "Hello", "tone_adjustments": []}')
    out = llm.translate_json(client, "some-model", "sys", "user")
    assert out["translation"] == "Hello", out
    assert client.chat.completions.last_kwargs["response_format"] == {
        "type": "json_object"
    }
    assert client.chat.completions.last_kwargs["model"] == "some-model"


def test_translate_text_returns_stripped():
    client = _FakeClient("  hello world\n")
    assert llm.translate_text(client, "m", "sys", "u") == "hello world"


def test_pick_nvidia_model_prefers_nemotron():
    ids = ["a/b", "nvidia/Nemotron-X", "c/d"]
    assert llm.pick_nvidia_model(ids) == "nvidia/Nemotron-X"


def test_pick_nvidia_model_falls_back():
    assert llm.pick_nvidia_model(["x", "y"]) == "x"
    assert llm.pick_nvidia_model([]) == ""


def test_prompts_format():
    kr = prompts.KR_TO_EN_SYSTEM.format(tone_guidance=prompts.TONE_GUIDANCE[3])
    assert "translation" in kr and "cultural_notes" in kr
    en = prompts.EN_TO_KR_SYSTEM.format(formality="Auto")
    assert "honorific_notes" in en
    chat = prompts.CHAT_SYSTEM.format(target_language="English", tone_guidance="x")
    assert "ONLY the translated message" in chat


def test_missing_key_error():
    old = llm.config.NEBIUS_API_KEY
    llm.config.NEBIUS_API_KEY = ""
    try:
        try:
            llm.get_client("")
        except llm.MissingApiKeyError:
            return
        raise AssertionError("expected MissingApiKeyError")
    finally:
        llm.config.NEBIUS_API_KEY = old


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"FAIL {t.__name__}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
