from app.proxy import apply_clash_proxy_env


def test_apply_clash_proxy_env_sets_defaults_when_enabled():
    env = apply_clash_proxy_env({"USE_CLASH_PROXY": "1"})

    assert env["HTTP_PROXY"] == "http://127.0.0.1:7890"
    assert env["HTTPS_PROXY"] == "http://127.0.0.1:7890"
    assert env["ALL_PROXY"] == "socks5h://127.0.0.1:7891"
    assert env["NO_PROXY"] == "localhost,127.0.0.1,::1"
    assert env["http_proxy"] == "http://127.0.0.1:7890"
    assert env["https_proxy"] == "http://127.0.0.1:7890"
    assert env["all_proxy"] == "socks5h://127.0.0.1:7891"
    assert env["no_proxy"] == "localhost,127.0.0.1,::1"


def test_apply_clash_proxy_env_preserves_existing_values():
    env = apply_clash_proxy_env(
        {
            "USE_CLASH_PROXY": "1",
            "HTTP_PROXY": "http://proxy.example:8080",
        }
    )

    assert env["HTTP_PROXY"] == "http://proxy.example:8080"
    assert env["HTTPS_PROXY"] == "http://127.0.0.1:7890"
