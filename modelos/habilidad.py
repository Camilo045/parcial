"""Módulo de habilidades especiales para los combatientes del RPG."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modelos.personaje import Personaje


class Habilidad(ABC):
    """Clase abstracta base que define el contrato de una habilidad de combate."""

    def __init__(self, nombre: str, costo_energia: int, descripcion: str) -> None:
        if not nombre or not nombre.strip():
            raise ValueError("El nombre de la habilidad no puede estar vacío.")
        if costo_energia < 0:
            raise ValueError("El costo de energía no puede ser negativo.")

        self._nombre: str = nombre.strip()
        self._costo_energia: int = costo_energia
        self._descripcion: str = descripcion.strip()

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def costo_energia(self) -> int:
        return self._costo_energia

    @property
    def descripcion(self) -> str:
        return self._descripcion

    def puede_usarse(self, usuario: Personaje) -> bool:
        """Verifica si el usuario cuenta con energía suficiente para usar la habilidad."""
        return usuario.esta_vivo and usuario.energia_actual >= self._costo_energia

    @abstractmethod
    def ejecutar(self, usuario: Personaje, objetivo: Personaje) -> str:
        """Ejecuta el efecto de la habilidad y retorna un mensaje descriptivo."""


class AtaquePotente(Habilidad):
    """Habilidad física que multiplica el ataque base del usuario."""

    def __init__(
        self,
        nombre: str,
        costo_energia: int,
        multiplicador: float,
        descripcion: str = "",
    ) -> None:
        super().__init__(
            nombre,
            costo_energia,
            descripcion or f"Golpe físico con multiplicador x{multiplicador:.1f}.",
        )
        if multiplicador <= 1.0:
            raise ValueError("El multiplicador de un ataque potente debe ser mayor a 1.0.")
        self._multiplicador: float = multiplicador

    def ejecutar(self, usuario: Personaje, objetivo: Personaje) -> str:
        usuario.consumir_energia(self._costo_energia)
        danio_bruto = int(round(usuario.ataque_base * self._multiplicador))
        danio_final = objetivo.recibir_danio(danio_bruto)
        return (
            f"{usuario.nombre} usa {self._nombre} contra {objetivo.nombre} "
            f"e inflige {danio_final} de daño."
        )


class HechizoOfensivo(Habilidad):
    """Habilidad mágica que ignora parcialmente la defensa del objetivo."""

    def __init__(
        self,
        nombre: str,
        costo_energia: int,
        poder_magico: int,
        penetracion_defensa: float = 0.5,
        descripcion: str = "",
    ) -> None:
        super().__init__(
            nombre,
            costo_energia,
            descripcion or f"Hechizo de {poder_magico} de poder que ignora parte de la defensa.",
        )
        if poder_magico <= 0:
            raise ValueError("El poder mágico debe ser mayor a cero.")
        if not 0.0 <= penetracion_defensa <= 1.0:
            raise ValueError("La penetración de defensa debe estar entre 0.0 y 1.0.")
        self._poder_magico: int = poder_magico
        self._penetracion_defensa: float = penetracion_defensa

    def ejecutar(self, usuario: Personaje, objetivo: Personaje) -> str:
        usuario.consumir_energia(self._costo_energia)
        danio_bruto = usuario.ataque_base + self._poder_magico
        danio_final = objetivo.recibir_danio(
            danio_bruto, ignorar_defensa=self._penetracion_defensa
        )
        return (
            f"{usuario.nombre} lanza {self._nombre} sobre {objetivo.nombre} "
            f"causando {danio_final} de daño mágico."
        )


class Curacion(Habilidad):
    """Habilidad de soporte que restaura puntos de vida del propio usuario."""

    def __init__(
        self,
        nombre: str,
        costo_energia: int,
        cantidad_curacion: int,
        descripcion: str = "",
    ) -> None:
        super().__init__(
            nombre,
            costo_energia,
            descripcion or f"Restaura hasta {cantidad_curacion} puntos de vida.",
        )
        if cantidad_curacion <= 0:
            raise ValueError("La cantidad de curación debe ser positiva.")
        self._cantidad_curacion: int = cantidad_curacion

    def ejecutar(self, usuario: Personaje, objetivo: Personaje) -> str:
        usuario.consumir_energia(self._costo_energia)
        curado = usuario.curar(self._cantidad_curacion)
        return f"{usuario.nombre} usa {self._nombre} y recupera {curado} PV."


class PosturaDefensiva(Habilidad):
    """Habilidad táctica que activa guardia reforzada y restaura algo de vida."""

    def __init__(
        self,
        nombre: str,
        costo_energia: int,
        curacion_menor: int = 10,
        descripcion: str = "",
    ) -> None:
        super().__init__(
            nombre,
            costo_energia,
            descripcion or "Adopta una guardia firme para reducir el próximo impacto.",
        )
        self._curacion_menor: int = max(0, curacion_menor)

    def ejecutar(self, usuario: Personaje, objetivo: Personaje) -> str:
        usuario.consumir_energia(self._costo_energia)
        usuario.activar_defensa()
        curado = usuario.curar(self._curacion_menor) if self._curacion_menor > 0 else 0
        extra = f" y recupera {curado} PV" if curado > 0 else ""
        return f"{usuario.nombre} ejecuta {self._nombre}, refuerza su guardia{extra}."
