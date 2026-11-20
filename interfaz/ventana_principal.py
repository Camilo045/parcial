"""Ventana principal de la aplicación construida con CustomTkinter."""

from __future__ import annotations

from tkinter import messagebox

import customtkinter as ctk

from modelos.personaje import Personaje
from servicios.fabrica import (
    CLASES_JUGADOR,
    RIVALES_DISPONIBLES,
    crear_personaje,
    crear_rival,
)
from servicios.motor_combate import MotorCombate


class TarjetaCombatiente(ctk.CTkFrame):
    """Componente visual reutilizable que muestra el estado de un combatiente."""

    def __init__(self, master: ctk.CTkBaseClass, titulo_rol: str) -> None:
        super().__init__(master, corner_radius=12)
        self._titulo_rol = titulo_rol

        self._lbl_rol = ctk.CTkLabel(
            self, text=titulo_rol, font=ctk.CTkFont(size=12, weight="bold")
        )
        self._lbl_rol.pack(anchor="w", padx=14, pady=(10, 0))

        self._lbl_nombre = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=18, weight="bold")
        )
        self._lbl_nombre.pack(anchor="w", padx=14, pady=(2, 4))

        self._lbl_estado = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=12), text_color="#60A5FA"
        )
        self._lbl_estado.pack(anchor="w", padx=14, pady=(0, 6))

        self._lbl_vida = ctk.CTkLabel(self, text="PV: 0 / 0", font=ctk.CTkFont(size=13))
        self._lbl_vida.pack(anchor="w", padx=14)
        self._barra_vida = ctk.CTkProgressBar(self, height=14)
        self._barra_vida.pack(fill="x", padx=14, pady=(2, 8))

        self._lbl_energia = ctk.CTkLabel(
            self, text="EN: 0 / 0", font=ctk.CTkFont(size=13)
        )
        self._lbl_energia.pack(anchor="w", padx=14)
        self._barra_energia = ctk.CTkProgressBar(
            self, height=12, progress_color="#3B82F6"
        )
        self._barra_energia.pack(fill="x", padx=14, pady=(2, 8))

        self._lbl_pasiva = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=11),
            wraplength=310,
            justify="left",
            text_color="#9CA3AF",
        )
        self._lbl_pasiva.pack(anchor="w", padx=14, pady=(0, 12))

    def actualizar(self, personaje: Personaje) -> None:
        """Sincroniza los controles de la tarjeta con el estado del personaje."""
        self._lbl_nombre.configure(text=f"{personaje.nombre} ({personaje.tipo_clase})")

        if not personaje.esta_vivo:
            self._lbl_estado.configure(text="Estado: Derrotado", text_color="#EF4444")
        elif personaje.defendiendo:
            self._lbl_estado.configure(text="Estado: En guardia (-50% daño)", text_color="#60A5FA")
        else:
            self._lbl_estado.configure(
                text=f"ATQ: {personaje.ataque_base} | DEF: {personaje.defensa}",
                text_color="#D1D5DB",
            )

        self._lbl_vida.configure(
            text=f"PV: {personaje.vida_actual} / {personaje.vida_maxima}"
        )
        pct_vida = personaje.porcentaje_vida
        self._barra_vida.set(pct_vida)
        if pct_vida > 0.5:
            self._barra_vida.configure(progress_color="#22C55E")
        elif pct_vida > 0.25:
            self._barra_vida.configure(progress_color="#EAB308")
        else:
            self._barra_vida.configure(progress_color="#EF4444")

        self._lbl_energia.configure(
            text=f"EN: {personaje.energia_actual} / {personaje.energia_maxima}"
        )
        self._barra_energia.set(personaje.porcentaje_energia)
        self._lbl_pasiva.configure(text=f"Pasiva: {personaje.descripcion_pasiva()}")


class VentanaPrincipal(ctk.CTk):
    """Ventana principal que coordina las pantallas de configuración y combate."""

    def __init__(self) -> None:
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("Arena RPG — Simulador de Combate por Turnos")
        self.geometry("820x650")
        self.minsize(760, 600)

        self._motor: MotorCombate | None = None
        self._botones_habilidad: list[ctk.CTkButton] = []

        self._contenedor = ctk.CTkFrame(self, fg_color="transparent")
        self._contenedor.pack(fill="both", expand=True, padx=18, pady=18)

        self._panel_config = ctk.CTkFrame(self._contenedor, corner_radius=14)
        self._panel_combate = ctk.CTkFrame(self._contenedor, fg_color="transparent")

        self._construir_panel_configuracion()
        self._construir_panel_combate()
        self._mostrar_configuracion()

    def _construir_panel_configuracion(self) -> None:
        titulo = ctk.CTkLabel(
            self._panel_config,
            text="Arena RPG — Preparación de Combate",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        titulo.pack(pady=(28, 8))

        subtitulo = ctk.CTkLabel(
            self._panel_config,
            text="Personaliza tu héroe y selecciona un oponente para iniciar.",
            font=ctk.CTkFont(size=14),
            text_color="#9CA3AF",
        )
        subtitulo.pack(pady=(0, 24))

        formulario = ctk.CTkFrame(self._panel_config, fg_color="transparent")
        formulario.pack(fill="x", padx=60)

        ctk.CTkLabel(
            formulario, text="Nombre del héroe:", font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(0, 4))
        self._entrada_nombre = ctk.CTkEntry(
            formulario, placeholder_text="Ej. Arturo, Lyra, Kael...", height=38
        )
        self._entrada_nombre.pack(fill="x", pady=(0, 14))
        self._entrada_nombre.insert(0, "Aventurero")

        ctk.CTkLabel(
            formulario, text="Clase del héroe:", font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(0, 4))
        self._var_clase = ctk.StringVar(value=CLASES_JUGADOR[0])
        self._selector_clase = ctk.CTkSegmentedButton(
            formulario,
            values=list(CLASES_JUGADOR),
            variable=self._var_clase,
            command=self._actualizar_preview_clase,
            height=36,
        )
        self._selector_clase.pack(fill="x", pady=(0, 8))

        self._lbl_preview_clase = ctk.CTkLabel(
            formulario,
            text="",
            font=ctk.CTkFont(size=12),
            justify="left",
            wraplength=580,
            text_color="#D1D5DB",
        )
        self._lbl_preview_clase.pack(anchor="w", pady=(0, 16))
        self._actualizar_preview_clase(CLASES_JUGADOR[0])

        ctk.CTkLabel(
            formulario, text="Rival:", font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(0, 4))
        rivales = list(RIVALES_DISPONIBLES.keys())
        self._var_rival = ctk.StringVar(value=rivales[0])
        self._menu_rival = ctk.CTkOptionMenu(
            formulario, values=rivales, variable=self._var_rival, height=38
        )
        self._menu_rival.pack(fill="x", pady=(0, 22))

        self._btn_iniciar = ctk.CTkButton(
            self._panel_config,
            text="Iniciar Combate",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=44,
            width=220,
            command=self._on_iniciar_combate,
        )
        self._btn_iniciar.pack(pady=(4, 24))

    def _construir_panel_combate(self) -> None:
        barra_superior = ctk.CTkFrame(self._panel_combate, fg_color="transparent")
        barra_superior.pack(fill="x", pady=(0, 10))

        self._lbl_turno = ctk.CTkLabel(
            barra_superior,
            text="Turno 1",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        self._lbl_turno.pack(side="left")

        btn_nueva = ctk.CTkButton(
            barra_superior,
            text="Nueva Partida",
            width=130,
            fg_color="#374151",
            hover_color="#4B5563",
            command=self._mostrar_configuracion,
        )
        btn_nueva.pack(side="right")

        tarjetas = ctk.CTkFrame(self._panel_combate, fg_color="transparent")
        tarjetas.pack(fill="x", pady=(0, 12))
        tarjetas.grid_columnconfigure(0, weight=1, uniform="col")
        tarjetas.grid_columnconfigure(1, weight=1, uniform="col")

        self._tarjeta_jugador = TarjetaCombatiente(tarjetas, "TU HÉROE")
        self._tarjeta_jugador.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        self._tarjeta_enemigo = TarjetaCombatiente(tarjetas, "OPONENTE")
        self._tarjeta_enemigo.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        self._panel_acciones = ctk.CTkFrame(self._panel_combate, corner_radius=12)
        self._panel_acciones.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            self._panel_acciones,
            text="Acciones disponibles:",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(anchor="w", padx=14, pady=(10, 6))

        self._contenedor_botones = ctk.CTkFrame(
            self._panel_acciones, fg_color="transparent"
        )
        self._contenedor_botones.pack(fill="x", padx=14, pady=(0, 12))

        self._btn_atacar = ctk.CTkButton(
            self._contenedor_botones,
            text="Ataque Básico",
            height=38,
            command=self._on_ataque_basico,
        )
        self._btn_atacar.pack(side="left", expand=True, fill="x", padx=(0, 6))

        self._frame_habilidades = ctk.CTkFrame(
            self._contenedor_botones, fg_color="transparent"
        )
        self._frame_habilidades.pack(side="left", expand=True, fill="x", padx=3)

        self._btn_defender = ctk.CTkButton(
            self._contenedor_botones,
            text="Defender (+12 EN)",
            height=38,
            fg_color="#0F766E",
            hover_color="#115E59",
            command=self._on_defender,
        )
        self._btn_defender.pack(side="left", expand=True, fill="x", padx=(6, 0))

        ctk.CTkLabel(
            self._panel_combate,
            text="Registro de batalla:",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(anchor="w", pady=(0, 4))

        self._log_combate = ctk.CTkTextbox(
            self._panel_combate, height=180, font=ctk.CTkFont(size=13), state="disabled"
        )
        self._log_combate.pack(fill="both", expand=True)

    def _actualizar_preview_clase(self, clase: str) -> None:
        ejemplo = crear_personaje(clase, "Vista Previa")
        habilidades = ", ".join(
            f"{h.nombre} ({h.costo_energia} EN)" for h in ejemplo.habilidades
        )
        self._lbl_preview_clase.configure(
            text=(
                f"PV: {ejemplo.vida_maxima} | EN: {ejemplo.energia_maxima} | "
                f"ATQ: {ejemplo.ataque_base} | DEF: {ejemplo.defensa}\n"
                f"Pasiva: {ejemplo.descripcion_pasiva()}\n"
                f"Habilidades: {habilidades}"
            )
        )

    def _mostrar_configuracion(self) -> None:
        self._panel_combate.pack_forget()
        self._panel_config.pack(fill="both", expand=True)

    def _mostrar_combate(self) -> None:
        self._panel_config.pack_forget()
        self._panel_combate.pack(fill="both", expand=True)

    def _on_iniciar_combate(self) -> None:
        nombre = self._entrada_nombre.get().strip()
        if not nombre:
            messagebox.showwarning(
                "Nombre requerido",
                "Por favor ingresa un nombre válido para tu héroe.",
            )
            return

        try:
            jugador = crear_personaje(self._var_clase.get(), nombre)
            enemigo = crear_rival(self._var_rival.get())
            self._motor = MotorCombate(jugador, enemigo)
        except ValueError as err:
            messagebox.showerror("Error de configuración", str(err))
            return

        self._reconstruir_botones_habilidades(jugador)
        self._limpiar_log()
        for linea in self._motor.historial:
            self._agregar_al_log(linea)
        self._sincronizar_vista()
        self._mostrar_combate()

    def _reconstruir_botones_habilidades(self, jugador: Personaje) -> None:
        for btn in self._botones_habilidad:
            btn.destroy()
        self._botones_habilidad.clear()

        for idx, hab in enumerate(jugador.habilidades):
            btn = ctk.CTkButton(
                self._frame_habilidades,
                text=f"{hab.nombre} ({hab.costo_energia} EN)",
                height=38,
                fg_color="#6D28D9",
                hover_color="#5B21B6",
                command=lambda i=idx: self._on_usar_habilidad(i),
            )
            btn.pack(side="left", expand=True, fill="x", padx=3)
            self._botones_habilidad.append(btn)

    def _on_ataque_basico(self) -> None:
        if self._motor is None:
            return
        self._ejecutar_accion(self._motor.turno_jugador_ataque)

    def _on_defender(self) -> None:
        if self._motor is None:
            return
        self._ejecutar_accion(self._motor.turno_jugador_defender)

    def _on_usar_habilidad(self, indice: int) -> None:
        if self._motor is None:
            return
        self._ejecutar_accion(lambda: self._motor.turno_jugador_habilidad(indice))

    def _ejecutar_accion(self, accion) -> None:
        if self._motor is None:
            return
        try:
            eventos = accion()
        except (ValueError, RuntimeError) as err:
            messagebox.showwarning("Acción no disponible", str(err))
            return

        for evento in eventos:
            self._agregar_al_log(evento)

        if self._motor.combate_terminado and self._motor.ganador is not None:
            self._agregar_al_log(f"=== FIN DEL COMBATE: Ganó {self._motor.ganador.nombre} ===")
            self._sincronizar_vista()
            victoria = self._motor.ganador is self._motor.jugador
            titulo = "¡Victoria!" if victoria else "Derrota"
            mensaje = (
                f"¡{self._motor.jugador.nombre} ha vencido a {self._motor.enemigo.nombre}!"
                if victoria
                else f"{self._motor.enemigo.nombre} ha derrotado a {self._motor.jugador.nombre}."
            )
            messagebox.showinfo(titulo, mensaje)
            return

        self._sincronizar_vista()

    def _sincronizar_vista(self) -> None:
        if self._motor is None:
            return
        self._lbl_turno.configure(text=f"Turno {self._motor.turno}")
        self._tarjeta_jugador.actualizar(self._motor.jugador)
        self._tarjeta_enemigo.actualizar(self._motor.enemigo)

        activo = not self._motor.combate_terminado
        estado_base = "normal" if activo else "disabled"
        self._btn_atacar.configure(state=estado_base)
        self._btn_defender.configure(state=estado_base)

        for idx, btn in enumerate(self._botones_habilidad):
            hab = self._motor.jugador.habilidades[idx]
            habilitado = activo and hab.puede_usarse(self._motor.jugador)
            btn.configure(state="normal" if habilitado else "disabled")

    def _limpiar_log(self) -> None:
        self._log_combate.configure(state="normal")
        self._log_combate.delete("1.0", "end")
        self._log_combate.configure(state="disabled")

    def _agregar_al_log(self, texto: str) -> None:
        self._log_combate.configure(state="normal")
        self._log_combate.insert("end", f"{texto}\n")
        self._log_combate.see("end")
        self._log_combate.configure(state="disabled")
