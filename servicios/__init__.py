"""Paquete de servicios y lógica de coordinación del combate."""

from servicios.fabrica import CLASES_JUGADOR, RIVALES_DISPONIBLES, crear_personaje, crear_rival
from servicios.motor_combate import MotorCombate

__all__ = [
    "CLASES_JUGADOR",
    "RIVALES_DISPONIBLES",
    "crear_personaje",
    "crear_rival",
    "MotorCombate",
]
