"""Fábrica de personajes y enemigos con sus habilidades asignadas."""

from __future__ import annotations

from modelos.habilidad import (
    AtaquePotente,
    Curacion,
    HechizoOfensivo,
    PosturaDefensiva,
)
from modelos.personaje import Arquero, EnemigoJefe, Guerrero, Mago, Personaje


CLASES_JUGADOR: tuple[str, ...] = ("Guerrero", "Mago", "Arquero")

RIVALES_DISPONIBLES: dict[str, tuple[str, str]] = {
    "Guerrero Oscuro": ("Guerrero", "Guerrero Oscuro"),
    "Archimago del Caos": ("Mago", "Archimago del Caos"),
    "Cazador Sombrío": ("Arquero", "Cazador Sombrío"),
    "Señor de las Sombras (Jefe)": ("Jefe", "Señor de las Sombras"),
}


def crear_personaje(clase: str, nombre: str) -> Personaje:
    """Crea una instancia de Personaje según su clase y le asigna sus habilidades."""
    clase_norm = clase.strip()
    if clase_norm == "Guerrero":
        personaje: Personaje = Guerrero(nombre)
        personaje.agregar_habilidad(
            AtaquePotente("Tajo Brutal", costo_energia=20, multiplicador=1.7)
        )
        personaje.agregar_habilidad(
            PosturaDefensiva("Muro de Escudo", costo_energia=15, curacion_menor=14)
        )
        return personaje

    if clase_norm == "Mago":
        personaje = Mago(nombre)
        personaje.agregar_habilidad(
            HechizoOfensivo(
                "Bola de Fuego", costo_energia=25, poder_magico=22, penetracion_defensa=0.6
            )
        )
        personaje.agregar_habilidad(
            Curacion("Luz Restauradora", costo_energia=22, cantidad_curacion=32)
        )
        return personaje

    if clase_norm == "Arquero":
        personaje = Arquero(nombre)
        personaje.agregar_habilidad(
            AtaquePotente("Flecha Perforante", costo_energia=20, multiplicador=1.65)
        )
        personaje.agregar_habilidad(
            Curacion("Vendaje Rápido", costo_energia=18, cantidad_curacion=22)
        )
        return personaje

    if clase_norm == "Jefe":
        personaje = EnemigoJefe(nombre)
        personaje.agregar_habilidad(
            HechizoOfensivo(
                "Descarga Abisal", costo_energia=25, poder_magico=20, penetracion_defensa=0.5
            )
        )
        personaje.agregar_habilidad(
            PosturaDefensiva("Égida Oscura", costo_energia=18, curacion_menor=18)
        )
        return personaje

    raise ValueError(f"Clase de personaje desconocida: '{clase}'.")


def crear_rival(clave_rival: str) -> Personaje:
    """Crea un rival predefinido a partir de su identificador."""
    if clave_rival not in RIVALES_DISPONIBLES:
        raise ValueError(f"Rival desconocido: '{clave_rival}'.")
    clase, nombre = RIVALES_DISPONIBLES[clave_rival]
    return crear_personaje(clase, nombre)
