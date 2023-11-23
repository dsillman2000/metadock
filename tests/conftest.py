from pathlib import Path

import pytest


@pytest.fixture
def empty_metadock_project_dir(tmp_path) -> Path:
    # Create a temporary directory for the Metadock project
    project_dir = tmp_path / ".metadock"
    project_dir.mkdir()

    # Create the necessary directories within the project
    (project_dir / "templated_documents").mkdir()
    (project_dir / "content_schematics").mkdir()
    (project_dir / "generated_documents").mkdir()

    return project_dir


@pytest.fixture
def capture_prints(monkeypatch):
    captured_print_args = []

    with monkeypatch.context() as m:
        m.setattr("builtins.print", lambda *args: captured_print_args.extend(args))
        yield captured_print_args

    return captured_print_args
