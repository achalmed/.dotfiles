"""studio/dotfiles_app/__init__.py — paquete de Dotfiles Studio.

La ventana es opcional: el repo se instala antes que cualquier otra cosa y `main.sh` no depende de ella. Necesita
PySide6 y `gui-comun` como paquete de pip (nunca se busca en otra carpeta: el repo no depende de ningún espacio de
trabajo). Sin ellos, `main.py` dice cómo instalarlos y sale.
"""

INSTALAR = ('python3 -m pip install --user PySide6 "git+https://github.com/achalmed/gui-comun@v1.3.0"\n'
            "  (o: ./main.sh instalar-deps, que lo ofrece como opcional)")


def faltan() -> list[str]:
    """Los módulos que faltan para abrir la ventana (vacío si están todos)."""
    import importlib.util
    return [m for m in ("PySide6", "gui_comun") if importlib.util.find_spec(m) is None]
