from collections.abc import Mapping
import os
import socket


DEFAULT_HTTP_PROXY = "http://127.0.0.1:7890"
DEFAULT_HTTPS_PROXY = "http://127.0.0.1:7890"
DEFAULT_ALL_PROXY = "socks5h://127.0.0.1:7891"
DEFAULT_NO_PROXY = "localhost,127.0.0.1,::1"


def apply_clash_proxy_env(env: Mapping[str, str]) -> dict:
    updated = dict(env)
    if updated.get("USE_CLASH_PROXY") not in {"1", "true", "yes", "on"}:
        return updated

    for key, value in (
        ("HTTP_PROXY", DEFAULT_HTTP_PROXY),
        ("HTTPS_PROXY", DEFAULT_HTTPS_PROXY),
        ("ALL_PROXY", DEFAULT_ALL_PROXY),
        ("NO_PROXY", DEFAULT_NO_PROXY),
        ("http_proxy", DEFAULT_HTTP_PROXY),
        ("https_proxy", DEFAULT_HTTPS_PROXY),
        ("all_proxy", DEFAULT_ALL_PROXY),
        ("no_proxy", DEFAULT_NO_PROXY),
    ):
        updated.setdefault(key, value)
    return updated


def _clash_port_open(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=0.2):
            return True
    except OSError:
        return False


def enable_clash_proxy_if_available() -> None:
    if os.environ.get("USE_CLASH_PROXY") in {"1", "true", "yes", "on"}:
        for key, value in (
            ("HTTP_PROXY", DEFAULT_HTTP_PROXY),
            ("HTTPS_PROXY", DEFAULT_HTTPS_PROXY),
            ("ALL_PROXY", DEFAULT_ALL_PROXY),
            ("NO_PROXY", DEFAULT_NO_PROXY),
            ("http_proxy", DEFAULT_HTTP_PROXY),
            ("https_proxy", DEFAULT_HTTPS_PROXY),
            ("all_proxy", DEFAULT_ALL_PROXY),
            ("no_proxy", DEFAULT_NO_PROXY),
        ):
            os.environ.setdefault(key, value)
        return

    if _clash_port_open("127.0.0.1", 7890) or _clash_port_open("::1", 7890):
        for key, value in (
            ("HTTP_PROXY", DEFAULT_HTTP_PROXY),
            ("HTTPS_PROXY", DEFAULT_HTTPS_PROXY),
            ("ALL_PROXY", DEFAULT_ALL_PROXY),
            ("NO_PROXY", DEFAULT_NO_PROXY),
            ("http_proxy", DEFAULT_HTTP_PROXY),
            ("https_proxy", DEFAULT_HTTPS_PROXY),
            ("all_proxy", DEFAULT_ALL_PROXY),
            ("no_proxy", DEFAULT_NO_PROXY),
        ):
            os.environ.setdefault(key, value)
