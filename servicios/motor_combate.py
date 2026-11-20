"""Motor de combate por turnos que coordina reglas, acciones e IA rival."""

from __future__ import annotations

import random

from modelos.habilidad import Curacion, PosturaDefensiva
from modelos.personaje import Personaje


class MotorCombate:
    """Coordina un combate por turnos entre el jugador y un enemigo."""

    ENERGIA_POR_DEFENSA: int = 12

    def __init__(self, jugador: Personaje, enemigo: Personaje) -> None:
        if jugador is enemigo:
            raise ValueError("El jugador y el enemigo deben ser instancias distintas.")
        self._jugador: Personaje = jugador
        self._enemigo: Personaje = enemigo
        self._turno: int = 1
        self._historial: list[str] = [
            f"¡Comienza el combate! {jugador.nombre} ({jugador.tipo_clase}) "
            f"vs {enemigo.nombre} ({enemigo.tipo_clase})."
        ]

    @property
    def jugador(self) -> Personaje:
        return self._jugador

    @property
    def enemigo(self) -> Personaje:
        return self._enemigo

    @property
    def turno(self) -> int:
        return self._turno

    @property
    def historial(self) -> tuple[str, ...]:
        return tuple(self._historial)

    @property
    def combate_terminado(self) -> bool:
        return not (self._jugador.esta_vivo and self._enemigo.esta_vivo)

    @property
    def ganador(self) -> Personaje | None:
        if not self.combate_terminado:
            return None
        return self._jugador if self._jugador.esta_vivo else self._enemigo

    def _verificar_combate_activo(self) -> None:
        if self.combate_terminado:
            raise RuntimeError("El combate ya ha finalizado.")

    def _ejecutar_ataque_basico(self, atacante: Personaje, defensor: Personaje) -> str:
        danio_bruto, detalle = atacante.calcular_ataque_basico()
        danio_final = defensor.recibir_danio(danio_bruto)
        sufijo = f" ({detalle})" if detalle else ""
        return (
            f"{atacante.nombre} realiza un ataque básico{sufijo} "
            f"e inflige {danio_final} de daño a {defensor.nombre}."
        )

    def _ejecutar_defensa(self, personaje: Personaje) -> str:
        personaje.activar_defensa()
        recuperada = personaje.recuperar_energia(self.ENERGIA_POR_DEFENSA)
        return (
            f"{personaje.nombre} se defiende (mitiga 50% del próximo ataque) "
            f"y recupera {recuperada} EN."
        )

    def _registrar_resultado_si_termino(self) -> None:
        if self.combate_terminado and self.ganador is not None:
            self._historial.append(f"¡{self.ganador.nombre} ha ganado el combate!")

    def turno_jugador_ataque(self) -> list[str]:
        """Ejecuta el ataque básico del jugador y, si sigue en pie, el turno rival."""
        self._verificar_combate_activo()
        eventos = [f"[Turno {self._turno}] {self._ejecutar_ataque_basico(self._jugador, self._enemigo)}"]
        self._avanzar_tras_accion_jugador(eventos)
        return eventos

    def turno_jugador_habilidad(self, indice_habilidad: int) -> list[str]:
        """Ejecuta una habilidad del jugador y, si sigue en pie, el turno rival."""
        self._verificar_combate_activo()
        mensaje = self._jugador.usar_habilidad(indice_habilidad, self._enemigo)
        eventos = [f"[Turno {self._turno}] {mensaje}"]
        self._avanzar_tras_accion_jugador(eventos)
        return eventos

    def turno_jugador_defender(self) -> list[str]:
        """Pone al jugador en defensa y ejecuta el turno rival."""
        self._verificar_combate_activo()
        eventos = [f"[Turno {self._turno}] {self._ejecutar_defensa(self._jugador)}"]
        self._avanzar_tras_accion_jugador(eventos)
        return eventos

    def _avanzar_tras_accion_jugador(self, eventos: list[str]) -> None:
        self._historial.extend(eventos)
        if self.combate_terminado:
            self._registrar_resultado_si_termino()
            return

        evento_enemigo = self._ejecutar_ia_enemigo()
        eventos.append(evento_enemigo)
        self._historial.append(evento_enemigo)

        if self.combate_terminado:
            self._registrar_resultado_si_termino()
        else:
            self._turno += 1

    def _ejecutar_ia_enemigo(self) -> str:
        """Selecciona una acción táctica para el enemigo según su estado actual."""
        habilidades = self._enemigo.habilidades
        disponibles = [
            (idx, hab)
            for idx, hab in enumerate(habilidades)
            if hab.puede_usarse(self._enemigo)
        ]

        if self._enemigo.porcentaje_vida < 0.45:
            soporte = [
                (idx, hab)
                for idx, hab in disponibles
                if isinstance(hab, (Curacion, PosturaDefensiva))
            ]
            if soporte and random.random() < 0.7:
                idx, _ = soporte[0]
                return f"[IA] {self._enemigo.usar_habilidad(idx, self._jugador)}"

        ofensivas = [
            (idx, hab)
            for idx, hab in disponibles
            if not isinstance(hab, (Curacion, PosturaDefensiva))
        ]
        if ofensivas and random.random() < 0.55:
            idx, _ = random.choice(ofensivas)
            return f"[IA] {self._enemigo.usar_habilidad(idx, self._jugador)}"

        if self._enemigo.energia_actual < 15 and random.random() < 0.35:
            return f"[IA] {self._ejecutar_defensa(self._enemigo)}"

        return f"[IA] {self._ejecutar_ataque_basico(self._enemigo, self._jugador)}"
