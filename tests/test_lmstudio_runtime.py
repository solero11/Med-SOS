from unittest.mock import Mock, patch

from src.llm.lmstudio_runtime import LMStudioRuntime


def make_response(json_payload, status_code=200):
    resp = Mock()
    resp.status_code = status_code
    resp.json.return_value = json_payload
    return resp


@patch("src.llm.lmstudio_runtime.requests.post")
@patch("src.llm.lmstudio_runtime.requests.get")
def test_ensure_model_loaded_when_already_active(mock_get, mock_post):
    def fake_get(url, timeout):
        if url.endswith("/v1/models/active"):
            return make_response({"data": [{"id": "medicine-llm-13b"}]})
        return make_response({"data": [{"id": "medicine-llm-13b"}]})

    mock_get.side_effect = fake_get

    runtime = LMStudioRuntime()
    active = runtime.ensure_model_loaded()

    assert active == "medicine-llm-13b"
    mock_post.assert_not_called()


@patch("src.llm.lmstudio_runtime.requests.post")
@patch("src.llm.lmstudio_runtime.requests.get")
def test_ensure_model_loaded_swaps_out_other_model(mock_get, mock_post):
    calls = []

    def fake_get(url, timeout):
        calls.append(url)
        if url.endswith("/v1/models/active"):
            if mock_post.call_count >= 2:
                return make_response({"data": [{"id": "medicine-llm-13b"}]})
            return make_response({"data": [{"id": "other-model"}]})
        # After load we want target reported
        if mock_post.call_count >= 2:
            return make_response({"data": [{"id": "medicine-llm-13b"}]})
        return make_response({"data": [{"id": "other-model"}]})

    mock_get.side_effect = fake_get

    def fake_post(url, json, timeout):
        if json.get("action") == "unload" or json.get("model") == "other-model":
            return make_response({"status": "unsupported"}, status_code=400)
        return make_response({"status": "ok"})

    mock_post.side_effect = fake_post

    runtime = LMStudioRuntime()
    active = runtime.ensure_model_loaded()

    assert active == "medicine-llm-13b"
    # Ensure we attempted to unload but tolerated failure.
    unload_calls = [
        call for call in mock_post.call_args_list
        if call.kwargs["json"].get("action") == "unload" or call.kwargs["json"].get("model") == "other-model"
    ]
    assert unload_calls
