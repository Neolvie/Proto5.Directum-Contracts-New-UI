import os
import subprocess
import sys
import time
from pathlib import Path

import httpx
from playwright.sync_api import Page, expect


def wait_for_health(url: str, timeout: float = 20.0) -> None:
    start = time.time()
    while time.time() - start < timeout:
        try:
            response = httpx.get(url, timeout=2.0)
            if response.status_code == 200:
                return
        except httpx.HTTPError:
            time.sleep(0.5)
    raise RuntimeError("Сервер не поднялся вовремя.")


def test_ui_flow(tmp_path: Path, page: Page) -> None:
    env = os.environ.copy()
    env["LLM_STUB"] = "1"
    env["PORT"] = "8001"
    project_root = Path(__file__).resolve().parents[2]
    env["PYTHONPATH"] = str(project_root)

    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.app:app", "--port", "8001"],
        env=env,
        cwd=project_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        wait_for_health("http://127.0.0.1:8001/api/health")
        page.goto("http://127.0.0.1:8001/")

        page.get_by_role("button", name="Руководитель БЕ").click()
        expect(page.get_by_text("Роль: Руководитель БЕ")).to_be_visible()

        sample = tmp_path / "sample.md"
        sample.write_text("Тестовый документ", encoding="utf-8")
        page.set_input_files("#fileInput", str(sample))
        page.get_by_role("button", name="Загрузить").click()
        expect(page.get_by_text("sample.md")).to_be_visible()

        page.get_by_role("button", name="Запустить").first.click()
        expect(page.get_by_text("Тестовый ответ.")).to_be_visible()

        page.get_by_role("button", name="👍").first.click()
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
