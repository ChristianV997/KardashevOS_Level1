from pathlib import Path

SCRIPT_NAMES = ["start.bat", "stop.bat", "clean.bat"]

def test_batch_scripts_exist():
    for name in SCRIPT_NAMES:
        assert Path(name).is_file(), f"{name} script is missing"
