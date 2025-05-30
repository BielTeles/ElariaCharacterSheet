import customtkinter as ctk
import tkinter
from typing import List, Dict, Any, Optional, Tuple
import random
from datetime import datetime
import json
import os
from core.dice_roller import roll_generic_dice

class ToolTip:
    """Classe para criar tooltips personalizados."""
    
    def __init__(self, widget: ctk.CTkBaseClass, text: str):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind('<Enter>', self.show_tooltip)
        self.widget.bind('<Leave>', self.hide_tooltip)
    
    def show_tooltip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        self.tooltip_window = tkinter.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        label = tkinter.Label(
            self.tooltip_window,
            text=self.text,
            justify='left',
            background="#34495e",
            foreground="#ecf0f1",
            relief='solid',
            borderwidth=1,
            font=("Helvetica", 10),
            wraplength=300
        )
        label.pack()
    
    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

class DiceRollerGenericTab:
    """
    Gerencia a aba do Rolador de Dados, permitindo diferentes tipos de rolagens
    com interface moderna e recursos avançados.
    """
    def __init__(self, tab_widget: ctk.CTkFrame):
        self.tab_widget = tab_widget
        self.history: List[Dict[str, Any]] = []
        self.favorites: List[Dict[str, Any]] = self.load_favorites()
        
        # Cores e Estilos
        self.colors = {
            "primary": "#3498db",
            "secondary": "#2ecc71",
            "danger": "#e74c3c",
            "warning": "#f1c40f",
            "info": "#3498db",
            "success": "#2ecc71",
            "background": "#2c3e50",
            "surface": "#34495e",
            "text": "#ecf0f1",
            "text_secondary": "#95a5a6"
        }

        # Frame Principal com Grid Layout
        self.main_frame = ctk.CTkFrame(self.tab_widget, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Layout em duas colunas
        self.main_frame.grid_columnconfigure(0, weight=2)  # Coluna da esquerda (rolagem e histórico)
        self.main_frame.grid_columnconfigure(1, weight=1)  # Coluna da direita (favoritos e rolagens rápidas)

        # Seção de Rolagem Principal
        self.setup_main_roller()
        
        # Seção de Histórico
        self.setup_history_section()
        
        # Seção de Favoritos
        self.setup_favorites_section()
        
        # Seção de Rolagens Rápidas
        self.setup_quick_rolls_section()

        # Label para animação do dado
        self.dice_animation_label = ctk.CTkLabel(
            self.main_frame,
            text="",
            font=ctk.CTkFont(size=48, weight="bold"),
            text_color=self.colors["primary"]
        )
        self.dice_animation_label.grid(row=2, column=0, columnspan=2, pady=10)

        # Caracteres de animação otimizados
        self.animation_chars = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]
        self._animation_timer = None

    def setup_main_roller(self):
        """Configura a seção principal de rolagem."""
        roller_frame = ctk.CTkFrame(self.main_frame, fg_color=self.colors["surface"])
        roller_frame.grid(row=0, column=0, padx=10, pady=(0,10), sticky="nsew")
        
        # Título
        title_label = ctk.CTkLabel(
            roller_frame,
            text="🎲 Rolador de Dados",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["text"]
        )
        title_label.pack(pady=10)

        # Frame para inputs
        input_frame = ctk.CTkFrame(roller_frame, fg_color="transparent")
        input_frame.pack(pady=10, padx=20)

        # Quantidade de dados
        num_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        num_frame.pack(side="left", padx=5)
        
        num_dice_label = ctk.CTkLabel(num_frame, text="Quantidade:", font=ctk.CTkFont(size=12))
        num_dice_label.pack(side="left", padx=5)
        
        self.num_dice_entry = ctk.CTkEntry(
            num_frame,
            width=60,
            height=32,
            placeholder_text="1",
            font=ctk.CTkFont(size=12)
        )
        self.num_dice_entry.insert(0, "1")
        self.num_dice_entry.pack(side="left", padx=5)
        ToolTip(self.num_dice_entry, "Número de dados a serem rolados")

        # Tipo de dado
        type_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        type_frame.pack(side="left", padx=5)
        
        type_label = ctk.CTkLabel(type_frame, text="d", font=ctk.CTkFont(size=14, weight="bold"))
        type_label.pack(side="left", padx=5)
        
        self.dice_type_var = ctk.StringVar(value="20")
        self.dice_type_menu = ctk.CTkOptionMenu(
            type_frame,
            values=["4", "6", "8", "10", "12", "20", "100"],
            variable=self.dice_type_var,
            width=70,
            height=32,
            font=ctk.CTkFont(size=12)
        )
        self.dice_type_menu.pack(side="left", padx=5)
        ToolTip(self.dice_type_menu, "Tipo de dado")

        # Modificador
        mod_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        mod_frame.pack(side="left", padx=5)
        
        mod_label = ctk.CTkLabel(mod_frame, text="Mod:", font=ctk.CTkFont(size=12))
        mod_label.pack(side="left", padx=5)
        
        self.mod_entry = ctk.CTkEntry(
            mod_frame,
            width=60,
            height=32,
            placeholder_text="0",
            font=ctk.CTkFont(size=12)
        )
        self.mod_entry.insert(0, "0")
        self.mod_entry.pack(side="left", padx=5)
        ToolTip(self.mod_entry, "Modificador a ser somado ao resultado")

        # Frame para opções adicionais
        options_frame = ctk.CTkFrame(roller_frame, fg_color="transparent")
        options_frame.pack(pady=5)

        # Checkbox para vantagem/desvantagem
        self.advantage_var = ctk.StringVar(value="normal")
        
        adv_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        adv_frame.pack(pady=5)
        
        normal_radio = ctk.CTkRadioButton(
            adv_frame,
            text="Normal",
            variable=self.advantage_var,
            value="normal",
            font=ctk.CTkFont(size=12)
        )
        normal_radio.pack(side="left", padx=10)
        
        advantage_radio = ctk.CTkRadioButton(
            adv_frame,
            text="Vantagem",
            variable=self.advantage_var,
            value="advantage",
            font=ctk.CTkFont(size=12)
        )
        advantage_radio.pack(side="left", padx=10)
        
        disadvantage_radio = ctk.CTkRadioButton(
            adv_frame,
            text="Desvantagem",
            variable=self.advantage_var,
            value="disadvantage",
            font=ctk.CTkFont(size=12)
        )
        disadvantage_radio.pack(side="left", padx=10)

        # Botão de rolagem
        self.roll_button = ctk.CTkButton(
            roller_frame,
            text="🎲 Rolar!",
            command=self.perform_roll,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            fg_color=self.colors["primary"],
            hover_color="#2980b9"
        )
        self.roll_button.pack(pady=10)
        
        # Frame para resultado
        self.result_frame = ctk.CTkFrame(roller_frame, fg_color=self.colors["background"])
        self.result_frame.pack(fill="x", padx=20, pady=10)
        
        self.result_label = ctk.CTkLabel(
            self.result_frame,
            text="Aguardando rolagem...",
            font=ctk.CTkFont(size=14),
            wraplength=400
        )
        self.result_label.pack(pady=10)
        
        # Botão para salvar como favorito
        save_fav_button = ctk.CTkButton(
            roller_frame,
            text="⭐ Salvar como Favorito",
            command=self.save_current_as_favorite,
            font=ctk.CTkFont(size=12),
            height=32,
            fg_color=self.colors["warning"],
            hover_color="#f39c12"
        )
        save_fav_button.pack(pady=(0,10))

    def setup_history_section(self):
        """Configura a seção de histórico de rolagens."""
        history_frame = ctk.CTkFrame(self.main_frame, fg_color=self.colors["surface"])
        history_frame.grid(row=1, column=0, padx=10, pady=(0,10), sticky="nsew")
        
        # Título do histórico
        history_title = ctk.CTkLabel(
            history_frame,
            text="📜 Histórico de Rolagens",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        history_title.pack(pady=5)
        
        # Lista de histórico com scroll
        self.history_text = ctk.CTkTextbox(
            history_frame,
            height=150,
            font=ctk.CTkFont(size=12),
            wrap="word"
        )
        self.history_text.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Botão para limpar histórico
        clear_history_button = ctk.CTkButton(
            history_frame,
            text="🗑️ Limpar Histórico",
            command=self.clear_history,
            font=ctk.CTkFont(size=12),
            height=32,
            fg_color=self.colors["danger"],
            hover_color="#c0392b"
        )
        clear_history_button.pack(pady=5)

    def setup_favorites_section(self):
        """Configura a seção de rolagens favoritas."""
        favorites_frame = ctk.CTkFrame(self.main_frame, fg_color=self.colors["surface"])
        favorites_frame.grid(row=0, column=1, padx=10, pady=(0,10), sticky="nsew")
        
        # Título dos favoritos
        favorites_title = ctk.CTkLabel(
            favorites_frame,
            text="⭐ Rolagens Favoritas",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        favorites_title.pack(pady=5)
        
        # Frame scrollável para favoritos
        self.favorites_scroll = ctk.CTkScrollableFrame(
            favorites_frame,
            height=200,
            fg_color="transparent"
        )
        self.favorites_scroll.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.update_favorites_display()

    def setup_quick_rolls_section(self):
        """Configura a seção de rolagens rápidas."""
        quick_rolls_frame = ctk.CTkFrame(self.main_frame, fg_color=self.colors["surface"])
        quick_rolls_frame.grid(row=1, column=1, padx=10, pady=(0,10), sticky="nsew")
        
        # Título
        quick_rolls_title = ctk.CTkLabel(
            quick_rolls_frame,
            text="⚡ Rolagens Rápidas",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        quick_rolls_title.pack(pady=5)
        
        # Grid de botões para rolagens rápidas
        quick_buttons_frame = ctk.CTkFrame(quick_rolls_frame, fg_color="transparent")
        quick_buttons_frame.pack(pady=5)
        
        quick_rolls = [
            ("d20", "1d20"),
            ("2d20", "2d20"),
            ("d6", "1d6"),
            ("2d6", "2d6"),
            ("d100", "1d100"),
            ("4d6", "4d6")
        ]
        
        for i, (text, roll) in enumerate(quick_rolls):
            row = i // 3
            col = i % 3
            
            quick_button = ctk.CTkButton(
                quick_buttons_frame,
                text=text,
                command=lambda r=roll: self.perform_quick_roll(r),
                width=70,
                height=32,
                font=ctk.CTkFont(size=12),
                fg_color=self.colors["primary"],
                hover_color="#2980b9"
            )
            quick_button.grid(row=row, column=col, padx=5, pady=5)

    def animate_dice(self, frame: int, num_dice: int, dice_type: int, modifier: int, advantage_type: str):
        """Animação otimizada de rolagem."""
        if frame >= 8:  # Reduzir número de frames para melhor performance
            if self._animation_timer:
                self.tab_widget.after_cancel(self._animation_timer)
                self._animation_timer = None
            self.perform_final_roll(num_dice, dice_type, modifier, advantage_type)
            return
        
        # Usar menos caracteres na animação
        self.dice_animation_label.configure(
            text=random.choice(self.animation_chars)
        )
        
        self._animation_timer = self.tab_widget.after(
            50,  # Intervalo menor para animação mais suave
            self.animate_dice,
            frame + 1,
            num_dice,
            dice_type,
            modifier,
            advantage_type
        )

    def perform_roll(self) -> None:
        """Executa a rolagem de dados com as configurações atuais."""
        try:
            # Obtém valores dos inputs
            num_dice = int(self.num_dice_entry.get() or "1")
            dice_type = int(self.dice_type_var.get())
            modifier = int(self.mod_entry.get() or "0")
            advantage_type = self.advantage_var.get()

            if num_dice <= 0 or dice_type <= 0:
                self.show_result("Erro: valores devem ser positivos", "error")
                return

            # Cancela animação anterior se existir
            if self._animation_timer:
                self.tab_widget.after_cancel(self._animation_timer)
                self._animation_timer = None

            # Desabilita o botão de rolagem durante a animação
            self.roll_button.configure(state="disabled")
            
            # Inicia a animação
            self.animate_dice(0, num_dice, dice_type, modifier, advantage_type)

        except ValueError as e:
            self.show_result(f"Erro: entrada inválida - {str(e)}", "error")
        except Exception as e:
            self.show_result(f"Erro inesperado: {str(e)}", "error")

    def perform_final_roll(self, num_dice: int, dice_type: int, modifier: int, advantage_type: str) -> None:
        """Executa a rolagem real após a animação."""
        if advantage_type == "normal":
            rolls, total = roll_generic_dice(num_dice, dice_type)
            total += modifier
            result_text = f"🎲 Rolagem {num_dice}d{dice_type}"
            if modifier != 0:
                result_text += f" {'+' if modifier > 0 else ''}{modifier}"
            result_text += f"\nRolagens: {rolls}\nTotal: {total}"
        else:
            if num_dice == 1:
                # Para 1 dado com vantagem/desvantagem, rola 2 dados e pega o maior/menor
                rolls1, _ = roll_generic_dice(1, dice_type)
                rolls2, _ = roll_generic_dice(1, dice_type)
                
                if advantage_type == "advantage":
                    chosen_roll = max(rolls1[0], rolls2[0])
                else:  # disadvantage
                    chosen_roll = min(rolls1[0], rolls2[0])
                
                total = chosen_roll + modifier
                result_text = f"🎲 Rolagem com {'Vantagem' if advantage_type == 'advantage' else 'Desvantagem'}\n"
                result_text += f"Rolagem 1: {rolls1}\nRolagem 2: {rolls2}\n"
                result_text += f"Escolhido: {chosen_roll}"
            else:
                # Para 2+ dados, rola normalmente e pega o maior/menor
                rolls, _ = roll_generic_dice(num_dice, dice_type)
                
                if advantage_type == "advantage":
                    chosen_roll = max(rolls)
                else:  # disadvantage
                    chosen_roll = min(rolls)
                
                total = chosen_roll + modifier
                result_text = f"🎲 Rolagem com {'Vantagem' if advantage_type == 'advantage' else 'Desvantagem'}\n"
                result_text += f"Rolagens: {rolls}\n"
                result_text += f"Escolhido: {chosen_roll}"

            if modifier != 0:
                result_text += f"\nModificador: {'+' if modifier > 0 else ''}{modifier}"
            result_text += f"\nTotal: {total}"

        # Limpa a animação
        self.dice_animation_label.configure(text="")
        
        # Reativa o botão de rolagem
        self.roll_button.configure(state="normal")

        # Exibe o resultado
        self.show_result(result_text, "success")
        
        # Adiciona ao histórico
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.add_to_history({
            "timestamp": timestamp,
            "rolls": rolls if advantage_type == "normal" else [chosen_roll],
            "total": total,
            "config": f"{num_dice}d{dice_type}{'+' + str(modifier) if modifier > 0 else str(modifier) if modifier < 0 else ''}",
            "advantage_type": advantage_type
        })

    def perform_quick_roll(self, roll_config: str) -> None:
        """Executa uma rolagem rápida predefinida."""
        try:
            num_dice = int(roll_config.split('d')[0])
            dice_type = int(roll_config.split('d')[1])
            
            self.num_dice_entry.delete(0, "end")
            self.num_dice_entry.insert(0, str(num_dice))
            self.dice_type_var.set(str(dice_type))
            self.mod_entry.delete(0, "end")
            self.mod_entry.insert(0, "0")
            self.advantage_var.set("normal")
            
            self.perform_roll()
            
        except Exception as e:
            self.show_result(f"Erro na rolagem rápida: {str(e)}", "error")

    def show_result(self, text: str, result_type: str = "normal") -> None:
        """Exibe o resultado da rolagem com animação e cores."""
        colors = {
            "success": self.colors["success"],
            "error": self.colors["danger"],
            "normal": self.colors["text"]
        }
        
        self.result_label.configure(
            text=text,
            text_color=colors.get(result_type, self.colors["text"])
        )

    def add_to_history(self, roll_data: Dict[str, Any]) -> None:
        """Adiciona uma rolagem ao histórico."""
        self.history.append(roll_data)
        
        # Atualiza o display do histórico
        self.history_text.configure(state="normal")
        self.history_text.delete("1.0", "end")
        
        for roll in reversed(self.history[-10:]):  # Mostra apenas as últimas 10 rolagens
            entry = f"[{roll['timestamp']}] {roll['config']}"
            if roll['advantage_type'] != "normal":
                entry += f" ({roll['advantage_type']})"
            entry += f" = {roll['total']}\n"
            
            self.history_text.insert("1.0", entry)
        
        self.history_text.configure(state="disabled")

    def clear_history(self) -> None:
        """Limpa o histórico de rolagens."""
        self.history = []
        self.history_text.configure(state="normal")
        self.history_text.delete("1.0", "end")
        self.history_text.configure(state="disabled")
        self.show_result("Histórico limpo!", "normal")

    def save_current_as_favorite(self) -> None:
        """Salva a configuração atual como favorito."""
        current_config = {
            "name": f"{self.num_dice_entry.get()}d{self.dice_type_var.get()}",
            "num_dice": self.num_dice_entry.get(),
            "dice_type": self.dice_type_var.get(),
            "modifier": self.mod_entry.get(),
            "advantage_type": self.advantage_var.get()
        }
        
        if current_config not in self.favorites:
            self.favorites.append(current_config)
            self.save_favorites()
            self.update_favorites_display()
            self.show_result("Configuração salva nos favoritos!", "success")
        else:
            self.show_result("Esta configuração já está nos favoritos!", "warning")

    def load_favorites(self) -> List[Dict[str, Any]]:
        """Carrega as rolagens favoritas do arquivo."""
        try:
            if os.path.exists("data/dice_favorites.json"):
                with open("data/dice_favorites.json", "r") as f:
                    return json.load(f)
        except Exception:
            pass
        return []

    def save_favorites(self) -> None:
        """Salva as rolagens favoritas em arquivo."""
        try:
            os.makedirs("data", exist_ok=True)
            with open("data/dice_favorites.json", "w") as f:
                json.dump(self.favorites, f)
        except Exception as e:
            self.show_result(f"Erro ao salvar favoritos: {str(e)}", "error")

    def update_favorites_display(self) -> None:
        """Atualiza a exibição das rolagens favoritas."""
        # Limpa os widgets existentes
        for widget in self.favorites_scroll.winfo_children():
            widget.destroy()
        
        # Adiciona os favoritos
        for i, fav in enumerate(self.favorites):
            fav_frame = ctk.CTkFrame(self.favorites_scroll, fg_color=self.colors["background"])
            fav_frame.pack(fill="x", padx=5, pady=2)
            
            # Nome/configuração do favorito
            name_label = ctk.CTkLabel(
                fav_frame,
                text=f"🎲 {fav['name']}",
                font=ctk.CTkFont(size=12)
            )
            name_label.pack(side="left", padx=5)
            
            # Botões de ação
            buttons_frame = ctk.CTkFrame(fav_frame, fg_color="transparent")
            buttons_frame.pack(side="right", padx=5)
            
            # Botão de rolagem
            roll_button = ctk.CTkButton(
                buttons_frame,
                text="Rolar",
                command=lambda f=fav: self.roll_favorite(f),
                width=60,
                height=24,
                font=ctk.CTkFont(size=11),
                fg_color=self.colors["primary"],
                hover_color="#2980b9"
            )
            roll_button.pack(side="left", padx=2)
            
            # Botão de remoção
            remove_button = ctk.CTkButton(
                buttons_frame,
                text="❌",
                command=lambda f=fav: self.remove_favorite(f),
                width=30,
                height=24,
                font=ctk.CTkFont(size=11),
                fg_color=self.colors["danger"],
                hover_color="#c0392b"
            )
            remove_button.pack(side="left", padx=2)

    def roll_favorite(self, favorite: Dict[str, Any]) -> None:
        """Executa uma rolagem favorita."""
        self.num_dice_entry.delete(0, "end")
        self.num_dice_entry.insert(0, favorite["num_dice"])
        self.dice_type_var.set(favorite["dice_type"])
        self.mod_entry.delete(0, "end")
        self.mod_entry.insert(0, favorite["modifier"])
        self.advantage_var.set(favorite["advantage_type"])
        
        self.perform_roll()

    def remove_favorite(self, favorite: Dict[str, Any]) -> None:
        """Remove uma rolagem dos favoritos."""
        self.favorites.remove(favorite)
        self.save_favorites()
        self.update_favorites_display()
        self.show_result("Favorito removido!", "normal")