"""Módulo de entidades de personajes del simulador RPG."""

from __future__ import annotations

import random
from abc import ABC, abstractmethod

from modelos.habilidad import Habilidad


class Personaje(ABC):
    """Clase abstracta base para todos los combatientes del juego."""

    def __init__(
        self,
        nombre: str,
        vida_maxima: int,
        energia_maxima: int,
        ataque_base: int,
        defensa: int,
    ) -> None:
        if not nombre or not nombre.strip():
            raise ValueError("El nombre del personaje no puede estar vacío.")
        if vida_maxima <= 0:
            raise ValueError("La vida máxima debe ser mayor a cero.")
        if energia_maxima < 0:
            raise ValueError("La energía máxima no puede ser negativa.")
        if ataque_base <= 0:
            raise ValueError("El ataque base debe ser mayor a cero.")
        if defensa < 0:
            raise ValueError("La defensa no puede ser negativa.")

        self._nombre: str = nombre.strip()
        self._vida_maxima: int = vida_maxima
        self._vida_actual: int = vida_maxima
        self._energia_maxima: int = energia_maxima
        self._energia_actual: int = energia_maxima
        self._ataque_base: int = ataque_base
        self._defensa: int = defensa
        self._defendiendo: bool = False
        self._habilidades: list[Habilidad] = []

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def vida_actual(self) -> int:
        return self._vida_actual

    @property
    def vida_maxima(self) -> int:
        return self._vida_maxima

    @property
    def energia_actual(self) -> int:
        return self._energia_actual

    @property
    def energia_maxima(self) -> int:
        return self._energia_maxima

    @property
    def ataque_base(self) -> int:
        return self._ataque_base

    @property
    def defensa(self) -> int:
        return self._defensa

    @property
    def defendiendo(self) -> bool:
        return self._defendiendo

    @property
    def esta_vivo(self) -> bool:
        return self._vida_actual > 0

    @property
    def porcentaje_vida(self) -> float:
        return self._vida_actual / self._vida_maxima

    @property
    def porcentaje_energia(self) -> float:
        if self._energia_maxima == 0:
            return 0.0
        return self._energia_actual / self._energia_maxima

    @property
    def habilidades(self) -> tuple[Habilidad, ...]:
        return tuple(self._habilidades)

    @property
    @abstractmethod
    def tipo_clase(self) -> str:
        """Nombre de la clase o arquetipo del personaje."""

    @abstractmethod
    def descripcion_pasiva(self) -> str:
        """Descripción de la habilidad pasiva característica de la clase."""

    @abstractmethod
    def calcular_ataque_basico(self) -> tuple[int, str]:
        """Calcula el daño bruto del ataque básico y un detalle opcional."""

    def agregar_habilidad(self, habilidad: Habilidad) -> None:
        """Asocia una habilidad al repertorio del personaje."""
        self._habilidades.append(habilidad)

    def activar_defensa(self) -> None:
        """Activa la postura defensiva hasta recibir el próximo ataque."""
        self._defendiendo = True

    def consumir_energia(self, cantidad: int) -> None:
        """Descuenta energía validando disponibilidad."""
        if cantidad < 0:
            raise ValueError("La cantidad de energía a consumir no puede ser negativa.")
        if cantidad > self._energia_actual:
            raise ValueError(
                f"{self._nombre} no tiene energía suficiente "
                f"({self._energia_actual}/{cantidad})."
            )
        self._energia_actual -= cantidad

    def recuperar_energia(self, cantidad: int) -> int:
        """Recupera energía sin superar el máximo y retorna lo recuperado."""
        if cantidad <= 0 or not self.esta_vivo:
            return 0
        anterior = self._energia_actual
        self._energia_actual = min(self._energia_maxima, self._energia_actual + cantidad)
        return self._energia_actual - anterior

    def curar(self, cantidad: int) -> int:
        """Restaura vida sin exceder el máximo y retorna los PV curados."""
        if cantidad <= 0 or not self.esta_vivo:
            return 0
        anterior = self._vida_actual
        self._vida_actual = min(self._vida_maxima, self._vida_actual + cantidad)
        return self._vida_actual - anterior

    def recibir_danio(self, danio_bruto: int, ignorar_defensa: float = 0.0) -> int:
        """Aplica mitigación por defensa/postura y reduce la vida con límite en 0."""
        if danio_bruto < 0:
            raise ValueError("El daño bruto no puede ser negativo.")
        if not self.esta_vivo:
            return 0

        defensa_efectiva = int(round(self._defensa * (1.0 - ignorar_defensa)))
        danio_mitigado = max(1, danio_bruto - defensa_efectiva)

        if self._defendiendo:
            danio_mitigado = max(1, danio_mitigado // 2)
            self._defendiendo = False

        self._vida_actual = max(0, self._vida_actual - danio_mitigado)
        return danio_mitigado

    def usar_habilidad(self, indice: int, objetivo: Personaje) -> str:
        """Ejecuta una habilidad por índice sobre el objetivo indicado."""
        if not self.esta_vivo:
            raise RuntimeError(f"{self._nombre} no puede actuar porque ha sido derrotado.")
        if indice < 0 or indice >= len(self._habilidades):
            raise IndexError("Índice de habilidad fuera de rango.")

        habilidad = self._habilidades[indice]
        if not habilidad.puede_usarse(self):
            raise ValueError(
                f"Energía insuficiente para usar {habilidad.nombre} "
                f"(requiere {habilidad.costo_energia})."
            )
        return habilidad.ejecutar(self, objetivo)


class Guerrero(Personaje):
    """Combatiente resistente especializado en defensa y daño físico sostenido."""

    def __init__(self, nombre: str) -> None:
        super().__init__(
            nombre=nombre,
            vida_maxima=140,
            energia_maxima=60,
            ataque_base=22,
            defensa=10,
        )
        self._mitigacion_armadura: int = 3

    @property
    def tipo_clase(self) -> str:
        return "Guerrero"

    def descripcion_pasiva(self) -> str:
        return "Armadura pesada: reduce en 3 puntos adicionales cualquier daño recibido."

    def calcular_ataque_basico(self) -> tuple[int, str]:
        return self._ataque_base, ""

    def recibir_danio(self, danio_bruto: int, ignorar_defensa: float = 0.0) -> int:
        danio_reducido = max(1, danio_bruto - self._mitigacion_armadura)
        return super().recibir_danio(danio_reducido, ignorar_defensa)


class Mago(Personaje):
    """Lanzador de hechizos con alta reserva de energía y regeneración arcana."""

    def __init__(self, nombre: str) -> None:
        super().__init__(
            nombre=nombre,
            vida_maxima=100,
            energia_maxima=100,
            ataque_base=18,
            defensa=5,
        )
        self._regeneracion_arcana: int = 6

    @property
    def tipo_clase(self) -> str:
        return "Mago"

    def descripcion_pasiva(self) -> str:
        return "Flujo arcano: regenera 6 de energía cada vez que realiza un ataque básico."

    def calcular_ataque_basico(self) -> tuple[int, str]:
        recuperada = self.recuperar_energia(self._regeneracion_arcana)
        detalle = f"+{recuperada} EN" if recuperada > 0 else ""
        return self._ataque_base, detalle


class Arquero(Personaje):
    """Combatiente ágil capaz de asestar golpes críticos devastadores."""

    def __init__(self, nombre: str, prob_critico: float = 0.30) -> None:
        super().__init__(
            nombre=nombre,
            vida_maxima=115,
            energia_maxima=75,
            ataque_base=20,
            defensa=7,
        )
        if not 0.0 <= prob_critico <= 1.0:
            raise ValueError("La probabilidad de crítico debe estar entre 0.0 y 1.0.")
        self._prob_critico: float = prob_critico

    @property
    def tipo_clase(self) -> str:
        return "Arquero"

    def descripcion_pasiva(self) -> str:
        porcentaje = int(self._prob_critico * 100)
        return f"Puntería letal: {porcentaje}% de probabilidad de golpe crítico (x1.75)."

    def calcular_ataque_basico(self) -> tuple[int, str]:
        if random.random() < self._prob_critico:
            return int(round(self._ataque_base * 1.75)), "¡GOLPE CRÍTICO!"
        return self._ataque_base, ""


class EnemigoJefe(Personaje):
    """Adversario poderoso que entra en furia cuando su vida cae bajo el 40%."""

    def __init__(self, nombre: str = "Señor de las Sombras") -> None:
        super().__init__(
            nombre=nombre,
            vida_maxima=160,
            energia_maxima=80,
            ataque_base=21,
            defensa=8,
        )

    @property
    def tipo_clase(self) -> str:
        return "Jefe"

    def descripcion_pasiva(self) -> str:
        return "Furia abisal: inflige +35% de daño básico cuando tiene menos de 40% de vida."

    def calcular_ataque_basico(self) -> tuple[int, str]:
        if self.porcentaje_vida < 0.40:
            return int(round(self._ataque_base * 1.35)), "¡EN FURIA!"
        return self._ataque_base, ""
