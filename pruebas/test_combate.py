"""Pruebas unitarias para modelos, habilidades y motor de combate."""

from __future__ import annotations

import unittest

from modelos.habilidad import AtaquePotente, Curacion, Habilidad
from modelos.personaje import Arquero, EnemigoJefe, Guerrero, Mago, Personaje
from servicios.fabrica import crear_personaje, crear_rival
from servicios.motor_combate import MotorCombate


class TestAbstraccionYEncapsulamiento(unittest.TestCase):
    """Verifica que las clases abstractas y las invariantes de estado se cumplan."""

    def test_no_se_puede_instanciar_personaje_abstracto(self) -> None:
        with self.assertRaises(TypeError):
            Personaje("Base", 100, 50, 10, 5)  # type: ignore[abstract]

    def test_no_se_puede_instanciar_habilidad_abstracta(self) -> None:
        with self.assertRaises(TypeError):
            Habilidad("Base", 10, "Desc")  # type: ignore[abstract]

    def test_nombre_vacio_lanza_error(self) -> None:
        with self.assertRaises(ValueError):
            Guerrero("   ")

    def test_vida_no_baja_de_cero_ni_supera_maximo(self) -> None:
        mago = Mago("Merlín")
        mago.recibir_danio(9999)
        self.assertEqual(mago.vida_actual, 0)
        self.assertFalse(mago.esta_vivo)

        guerrero = Guerrero("Arturo")
        guerrero.recibir_danio(30)
        curado = guerrero.curar(999)
        self.assertEqual(guerrero.vida_actual, guerrero.vida_maxima)
        self.assertGreater(curado, 0)


class TestHerenciaYPolimorfismo(unittest.TestCase):
    """Verifica el comportamiento polimórfico de cada subclase."""

    def test_guerrero_mitiga_danio_adicional_por_armadura(self) -> None:
        guerrero = Guerrero("Tanque")
        danio_recibido = guerrero.recibir_danio(30)
        # 30 - 3 (armadura) = 27; 27 - 10 (defensa) = 17
        self.assertEqual(danio_recibido, 17)

    def test_mago_regenera_energia_en_ataque_basico(self) -> None:
        mago = Mago("Gandalf")
        mago.consumir_energia(20)
        energia_previa = mago.energia_actual
        danio, detalle = mago.calcular_ataque_basico()
        self.assertEqual(danio, mago.ataque_base)
        self.assertEqual(mago.energia_actual, energia_previa + 6)
        self.assertIn("+6 EN", detalle)

    def test_arquero_golpe_critico_garantizado(self) -> None:
        arquero = Arquero("Legolas", prob_critico=1.0)
        danio, detalle = arquero.calcular_ataque_basico()
        self.assertEqual(danio, int(round(arquero.ataque_base * 1.75)))
        self.assertIn("CRÍTICO", detalle)

    def test_jefe_entra_en_furia_bajo_40_por_ciento_vida(self) -> None:
        jefe = EnemigoJefe("Jefe")
        danio_normal, _ = jefe.calcular_ataque_basico()
        jefe.recibir_danio(120)
        self.assertLess(jefe.porcentaje_vida, 0.40)
        danio_furia, detalle = jefe.calcular_ataque_basico()
        self.assertGreater(danio_furia, danio_normal)
        self.assertIn("FURIA", detalle)


class TestMotorCombateYErrores(unittest.TestCase):
    """Verifica el flujo de turnos, habilidades y manejo de errores."""

    def test_error_energia_insuficiente_al_usar_habilidad(self) -> None:
        jugador = crear_personaje("Guerrero", "Héroe")
        enemigo = crear_rival("Archimago del Caos")
        jugador.consumir_energia(jugador.energia_actual)

        with self.assertRaises(ValueError):
            jugador.usar_habilidad(0, enemigo)

    def test_clase_invalida_en_fabrica(self) -> None:
        with self.assertRaises(ValueError):
            crear_personaje("Paladín", "Nombre")

    def test_combate_completo_hasta_ganador(self) -> None:
        jugador = Guerrero("Campeón")
        jugador.agregar_habilidad(AtaquePotente("Ejecución", 10, 5.0))
        enemigo = Mago("Aprendiz")
        motor = MotorCombate(jugador, enemigo)

        while not motor.combate_terminado:
            if jugador.habilidades[0].puede_usarse(jugador):
                motor.turno_jugador_habilidad(0)
            else:
                motor.turno_jugador_ataque()

        self.assertTrue(motor.combate_terminado)
        self.assertIsNotNone(motor.ganador)
        with self.assertRaises(RuntimeError):
            motor.turno_jugador_ataque()

    def test_curacion_restaura_vida_y_consume_energia(self) -> None:
        mago = Mago("Sanador")
        curacion = Curacion("Plegaria", costo_energia=15, cantidad_curacion=25)
        mago.agregar_habilidad(curacion)
        mago.recibir_danio(40)
        vida_antes = mago.vida_actual
        energia_antes = mago.energia_actual

        mensaje = mago.usar_habilidad(0, mago)
        self.assertGreater(mago.vida_actual, vida_antes)
        self.assertEqual(mago.energia_actual, energia_antes - 15)
        self.assertIn("recupera", mensaje)


if __name__ == "__main__":
    unittest.main()
