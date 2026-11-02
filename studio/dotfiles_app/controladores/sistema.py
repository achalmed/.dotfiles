"""dotfiles_app/controladores/sistema.py — la página Sistema: lo que no es de un paquete. Las dependencias de la
distribución (`instalar-deps`, que pide `sudo` y por eso se aplica en una terminal) con su estado, las fuentes de
usuario (`instalar-fuentes`) y el respaldo manual (`backup`). Cada una se simula (`--dry-run`) o se aplica tras la
confirmación de su acción (`sistema.<nombre>`), con su estado de operación (instalación o escritura). El escáner de
credenciales tiene su página (`seguridad.py`)."""

from __future__ import annotations

from gui_comun.qt import QObject, Property, Signal, Slot

from dotfiles_app import estado as est

ESTADO_OPERACION = {"fuentes": "instalacion", "dependencias": "instalacion", "respaldo": "escritura"}

# nombre → (título, orden de main.sh, qué hace, pide sudo)
OPERACIONES = {
    "fuentes": ("Instalar fuentes de usuario", "instalar-fuentes", "Descarga las fuentes de USER_FONTS (config.sh) desde su release oficial a ~/.local/share/fonts, comprueba el sha256 y refresca fontconfig. Sin sudo.", False),
    "dependencias": ("Instalar dependencias", "instalar-deps", "Instala con el gestor de la distribución los paquetes que el repo necesita, configura la zram y, al final, las fuentes. Pide sudo: se aplica en una terminal.", True),
    "respaldo": ("Respaldo de la configuración", "backup", "Guarda en .backups/ un tarball con los archivos de HOME que tocan los paquetes (se conservan los últimos 15). Es un respaldo de emergencia, no del sistema.", False),
}


class Sistema(QObject):
    terminado = Signal(str, int)      # nombre, código
    aviso = Signal(str, str)

    def __init__(self, espacio, consola, tareas, parent=None):
        super().__init__(parent)
        self.espacio, self.consola, self.tareas = espacio, consola, tareas

    @Property("QVariantList", constant=True)
    def operaciones(self) -> list:
        return [{"nombre": n, "titulo": t, "orden": o, "texto": x, "sudo": s} for n, (t, o, x, s) in OPERACIONES.items()]

    @Slot(str, result="QVariantMap")
    def info(self, nombre: str) -> dict:
        t, o, x, s = OPERACIONES[nombre]
        return {"nombre": nombre, "titulo": t, "orden": f"./main.sh {o}", "ordenSimular": f"./main.sh {o} --dry-run", "texto": x,
                "sudo": s, "simulable": True, "operacion": ESTADO_OPERACION[nombre]}

    @Property("QVariantList", constant=True)
    def dependencias(self) -> list:
        """Lo que el gestor necesita de la distribución (`_install_deps_apt`) y si está."""
        return est.dependencias_sistema()

    def consecuencias(self, nombre: str) -> str:
        t, o, x, s = OPERACIONES[nombre]
        return x + f"\n\nOrden: ./main.sh {o}" + ("\n\nPide sudo: se abre en una terminal para escribir la contraseña." if s else "")

    @Slot(str, bool)
    def correr(self, nombre: str, simular: bool) -> None:
        """Simula o aplica una operación; lo que pide sudo se aplica en una terminal (la simulación, en el panel)."""
        if nombre not in OPERACIONES:
            return
        if self.tareas.activa:
            self.aviso.emit("Hay una operación en curso; espera a que termine.", "informacion")
            return
        titulo, orden, _texto, sudo = OPERACIONES[nombre]
        argv = est.orden_main(orden, *(["--dry-run"] if simular else []))
        etiqueta = f"{titulo}{' (simulación)' if simular else ''}"
        if sudo and not simular:
            self.espacio.enTerminal(argv, titulo)
            return
        self.tareas.proceso(etiqueta, argv, cwd=str(est.repo()), operacion="simulacion" if simular else ESTADO_OPERACION[nombre],
                            al_terminar=lambda c, n=nombre: self._fin(n, c),
                            error={"descripcion": f"«{titulo}» no terminó bien", "recurso": " ".join(["./main.sh", *argv[2:]]),
                                   "accion": "Lea la salida (F4); si faltó la red, vuelva a intentarlo."})

    def _fin(self, nombre: str, codigo: int) -> None:
        self.terminado.emit(nombre, codigo)
