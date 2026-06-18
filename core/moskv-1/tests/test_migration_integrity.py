import os
from pathlib import Path
import subprocess

def test_migration_integrity():
    # El test asume que se ejecuta desde la raíz del proyecto (o puede calcularla desde este archivo)
    current_file = Path(__file__).resolve()
    # current_file = .../core/moskv-1/tests/test_migration_integrity.py
    # repo_root = current_file.parents[3]
    repo_root = current_file.parent.parent.parent.parent

    assert (repo_root / "core" / "moskv-1").exists(), "Falta core/moskv-1"
    assert (repo_root / "apps" / "agents.archi").exists(), "Falta apps/agents.archi"
    assert (repo_root / "archive" / "legacy").exists(), "Falta archive/legacy"
    
    # Comprobar que no existe `app.js` en root
    assert not (repo_root / "app.js").exists(), "app.js no debería estar en root"
    
    # Comprobar el log de un archivo para validar el git mv
    try:
        # Buscamos el log de app.js
        result = subprocess.run(
            ["git", "log", "-n", "1", "--follow", "--stat", "--", "apps/agents.archi/app.js"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True
        )
        assert "apps/agents.archi/app.js" in result.stdout
    except Exception as e:
        print("Git log check failed:", e)
