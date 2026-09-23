"""Click through the Locker prototype like a user would."""
from pathlib import Path

from streamlit.testing.v1 import AppTest

PAGE = str(Path(__file__).resolve().parents[1] / "app_pages" / "locker.py")


def test_full_patient_journey(monkeypatch):
    monkeypatch.chdir(Path(PAGE).parents[1])
    at = AppTest.from_file(PAGE, default_timeout=60).run()
    for _ in range(3):  # wizard steps 1→4
        [b for b in at.button if b.label.startswith("Next")][0].click().run()
    [b for b in at.button if b.label.startswith("I agree")][0].click().run()
    assert not at.exception
    for _ in range(8):
        btn = [b for b in at.button if b.label.startswith("▶")]
        if not btn:
            break
        btn[0].click().run()
    assert any("Journey complete" in s.value for s in at.success)
    assert at.metric[2].value != "0"  # pharmacy/insurer attempts blocked
