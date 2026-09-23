"""Smoke-test every Streamlit page headlessly with AppTest."""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
PAGES = sorted((ROOT / "app_pages").glob("*.py"))


@pytest.mark.parametrize("page", PAGES, ids=[p.stem for p in PAGES])
def test_page_renders(page, monkeypatch):
    monkeypatch.chdir(ROOT)
    at = AppTest.from_file(str(page), default_timeout=120)
    at.run()
    assert not at.exception, [e.value for e in at.exception]
