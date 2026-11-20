"""Punto de entrada principal del Simulador de Combate RPG."""

from interfaz.ventana_principal import VentanaPrincipal


def main() -> None:
    app = VentanaPrincipal()
    app.mainloop()


if __name__ == "__main__":
    main()
