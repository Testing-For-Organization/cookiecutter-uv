"""Integration checks for Felix upgrade-PR CI monitoring on this Python repo.

These tests exercise runtime dependencies Felix may upgrade. If an upgrade
breaks imports or basic APIs, CI fails and Dash can spawn remediate_pr_checks.
"""

from __future__ import annotations

import click
import cookiecutter
import pytest
import requests


def test_click_runtime_api() -> None:
    """click must remain importable and expose a working CLI Context."""
    ctx = click.Context(click.Command("felix-smoke"))
    assert ctx.command.name == "felix-smoke"
    assert isinstance(click.__version__, str)
    assert click.__version__


def test_cookiecutter_runtime_api() -> None:
    """cookiecutter package must remain importable after dependency upgrades."""
    assert cookiecutter is not None
    # Version attribute varies across releases; presence of generate module is stable.
    import cookiecutter.generate as generate

    assert hasattr(generate, "generate_files") or hasattr(generate, "generate_context")


def test_requests_runtime_api() -> None:
    """Pinned requests must stay compatible with Session usage Felix upgrades touch."""
    session = requests.Session()
    assert session.headers is not None
    # urllib3 is a transitive dep; broken upgrades often fail here.
    prepared = requests.Request("GET", "https://example.com").prepare()
    assert prepared.method == "GET"
    assert prepared.url == "https://example.com/"


@pytest.mark.integration
def test_dependency_versions_are_reported() -> None:
    """Helpful failure output when remediation inspects CI logs."""
    versions = {
        "click": getattr(click, "__version__", "unknown"),
        "requests": getattr(requests, "__version__", "unknown"),
        "cookiecutter": getattr(cookiecutter, "__version__", "unknown"),
    }
    for name, version in versions.items():
        assert version, f"{name} version missing"
    print(versions)
