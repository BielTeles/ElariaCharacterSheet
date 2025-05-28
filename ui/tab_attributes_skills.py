import customtkinter as ctk
import random
from typing import Dict, Any, Optional
import tkinter

# Definição das cores do tema
COLORS = {
    "primary": "#3B82F6",      # Azul principal
    "primary_hover": "#2563EB",
    "secondary": "#6B7280",    # Cinza neutro
    "success": "#10B981",      # Verde
    "danger": "#EF4444",       # Vermelho
    "warning": "#F59E0B",      # Amarelo
    "surface": "#1F2937",      # Fundo de elementos
    "background": "#111827",   # Fundo geral
    "text": "#F9FAFB",         # Texto principal
    "text_secondary": "#9CA3AF" # Texto secundário
}

# Estilos comuns para widgets
STYLES = {
    "button": {
        "normal": {
            "width": 35,
            "height": 35,
            "corner_radius": 8,
            "border_width": 2,
            "font": ("Roboto", 14, "bold")
        },
        "small": {
            "width": 28,
            "height": 28,
            "corner_radius": 6,
            "border_width": 2,
            "font": ("Roboto", 12, "bold")
        }
    },
    "entry": {
        "normal": {
            "width": 60,
            "height": 35,
            "corner_radius": 8,
            "border_width": 2,
            "font": ("Roboto", 14),
            "justify": "center"
        },
        "small": {
            "width": 45,
            "height": 28,
            "corner_radius": 6,
            "border_width": 2,
            "font": ("Roboto", 12),
            "justify": "center"
        }
    },
    "label": {
        "title": {
            "font": ("Roboto", 20, "bold"),
            "text_color": COLORS["primary"]
        },
        "subtitle": {
            "font": ("Roboto", 16, "bold"),
            "text_color": COLORS["text"]
        },
        "normal": {
            "font": ("Roboto", 12),
            "text_color": COLORS["text"]
        },
        "small": {
            "font": ("Roboto", 11),
            "text_color": COLORS["text_secondary"]
        }
    },
    "checkbox": {
        "width": 24,
        "height": 24,
        "corner_radius": 6,
        "border_width": 2,
        "border_color": COLORS["primary"],
        "fg_color": COLORS["primary"],
        "hover_color": COLORS["primary_hover"]
    }
}

# Assumindo que Personagem e as funções de dice_roller estão acessíveis
# (serão importadas corretamente quando a AppUI for instanciada)
from core.character import Personagem 
from core.dice_roller import (
    perform_attribute_test_roll,
    check_success,
    get_dice_for_attribute_test,
    # Importando constantes de grau de sucesso para consistência
    SUCCESS_EXTREME, SUCCESS_GOOD, SUCCESS_NORMAL,
    FAILURE_NORMAL, FAILURE_EXTREME
)
from core.character import (
    Personagem,
    FORCA, DESTREZA, CONSTITUICAO, INTELIGENCIA, SABEDORIA, CARISMA  # Adicionado
)
from core.dice_roller import (
    perform_attribute_test_roll,
    check_success,
    get_dice_for_attribute_test,
    # Importando constantes de grau de sucesso para consistência
    SUCCESS_EXTREME, SUCCESS_GOOD, SUCCESS_NORMAL,
    FAILURE_NORMAL, FAILURE_EXTREME,
    ROLL_TYPE_ADVANTAGE, ROLL_TYPE_DISADVANTAGE, ROLL_TYPE_NORMAL # Adicionado ROLL_TYPE_NORMAL também, para completude
)

# Constantes para nomes de atributos (já definidas em character.py, usadas aqui para clareza conceitual)
# ATTR_FORCA = "Força" 
# ... (outros atributos)

# Lista de perícias do jogo
SKILLS_LIST = [
    "Acrobacia", "Adestramento", "Atletismo",
    "Atuação", "Bloqueio", "Cavalgar",
    "Conhecimento (Arcano)", "Conhecimento (História)",
    "Conhecimento (Natureza)", "Conhecimento (Religião)",
    "Conhecimento (Geografia)", "Conhecimento (Reinos)",
    "Corpo-a-Corpo", "Cura", "Diplomacia",
    "Elemental", "Enganação", "Esquiva",
    "Fortitude", "Furtividade", "Guerra",
    "Iniciativa", "Intimidação", "Intuição",
    "Investigação", "Jogatina", "Ladinagem",
    "Misticismo", "Nobreza", "Percepção",
    "Pontaria", "Reflexos", "Sobrevivência",
    "Vontade"
]

# Mapeamento de perícias para seus atributos chave
SKILL_ATTRIBUTE_MAP = {
    "Acrobacia": DESTREZA,
    "Adestramento": CARISMA,
    "Atletismo": FORCA,
    "Atuação": CARISMA,
    "Bloqueio": CONSTITUICAO,
    "Cavalgar": DESTREZA,
    "Conhecimento (Arcano)": INTELIGENCIA,
    "Conhecimento (História)": INTELIGENCIA,
    "Conhecimento (Natureza)": INTELIGENCIA,
    "Conhecimento (Religião)": INTELIGENCIA,
    "Conhecimento (Geografia)": INTELIGENCIA,
    "Conhecimento (Reinos)": INTELIGENCIA,
    "Corpo-a-Corpo": FORCA,  # Pode usar FOR ou DES, usando FOR como padrão
    "Cura": SABEDORIA,
    "Diplomacia": CARISMA,
    "Elemental": INTELIGENCIA,  # Pode usar INT ou SAB, usando INT como padrão
    "Enganação": CARISMA,
    "Esquiva": DESTREZA,
    "Fortitude": CONSTITUICAO,
    "Furtividade": DESTREZA,
    "Guerra": INTELIGENCIA,
    "Iniciativa": DESTREZA,
    "Intimidação": CARISMA,
    "Intuição": SABEDORIA,
    "Investigação": INTELIGENCIA,
    "Jogatina": CARISMA,
    "Ladinagem": DESTREZA,
    "Misticismo": INTELIGENCIA,
    "Nobreza": INTELIGENCIA,
    "Percepção": SABEDORIA,
    "Pontaria": DESTREZA,
    "Reflexos": DESTREZA,
    "Sobrevivência": SABEDORIA,
    "Vontade": SABEDORIA
}

class AttributesSkillsTab:
    """
    Gerencia a aba de Atributos e Perícias na interface do usuário.
    Permite a visualização e edição de atributos, PV, PM, Vigor e perícias,
    além de realizar testes de perícia.
    """
    personagem: Personagem # Referência ao objeto Personagem atual
    app_ui: Any  # Referência ao AppUI

    attribute_entries: Dict[str, ctk.CTkEntry]
    attribute_dice_labels: Dict[str, ctk.CTkLabel]
    attribute_stringvars: Dict[str, ctk.StringVar]

    skill_value_stringvars: Dict[str, ctk.StringVar]
    skill_trained_vars: Dict[str, ctk.BooleanVar]
    skill_widgets: Dict[str, ctk.CTkBaseClass] # Para botões, checkboxes, entries
    skill_key_attribute_map: Dict[str, str] # Mapeia nome da perícia para nome do atributo chave (lookup)

    pv_atuais_var: ctk.StringVar
    pv_max_var: ctk.StringVar
    pm_atuais_var: ctk.StringVar
    pm_max_var: ctk.StringVar
    vigor_atuais_var: ctk.StringVar
    vigor_max_var: ctk.StringVar

    dice_animation_label: ctk.CTkLabel
    roll_result_label: ctk.CTkLabel

    def __init__(self, tab_widget: ctk.CTkFrame, personagem: Personagem, app_ui_ref: Any):
        self.tab_widget = tab_widget
        self.personagem = personagem
        self.app_ui = app_ui_ref

        # Frame principal com melhor organização
        self.main_frame = ctk.CTkFrame(self.tab_widget, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configuração do grid principal para melhor distribuição
        self.main_frame.grid_columnconfigure(0, weight=1)  # Coluna dos atributos
        self.main_frame.grid_columnconfigure(1, weight=2)  # Coluna das perícias
        self.main_frame.grid_rowconfigure(0, weight=1)     # Linha principal expande
        self.main_frame.grid_rowconfigure(1, weight=0)     # Linha do resultado não expande

        # Frame para atributos e pontos
        self.attr_points_frame = ctk.CTkFrame(self.main_frame, fg_color=COLORS["surface"])
        self.attr_points_frame.grid(row=0, column=0, padx=(0, 5), pady=(0, 5), sticky="nsew")
        self.attr_points_frame.grid_rowconfigure(0, weight=1)
        self.attr_points_frame.grid_columnconfigure(0, weight=1)

        # Frame para perícias
        self.skills_frame_container = ctk.CTkFrame(self.main_frame, fg_color=COLORS["surface"])
        self.skills_frame_container.grid(row=0, column=1, padx=(5, 0), pady=(0, 5), sticky="nsew")
        self.skills_frame_container.grid_rowconfigure(0, weight=1)
        self.skills_frame_container.grid_columnconfigure(0, weight=1)

        # Inicialização dos dicionários
        self.attribute_entries = {}
        self.attribute_dice_labels = {}
        self.attribute_stringvars = {}
        self.skill_value_stringvars = {}
        self.skill_trained_vars = {}
        self.skill_widgets = {}
        self.skill_key_attribute_map = {}
        self.skill_value_entries = {}
        self.skill_dice_labels = {}

        # Inicialização das variáveis de pontos
        self.pv_atuais_var = ctk.StringVar()
        self.pv_max_var = ctk.StringVar()
        self.pm_atuais_var = ctk.StringVar()
        self.pm_max_var = ctk.StringVar()
        self.vigor_atuais_var = ctk.StringVar()
        self.vigor_max_var = ctk.StringVar()

        # Setup das seções
        self.setup_attributes_points_section()
        self.setup_skills_section()
        self.setup_dice_roll_result_display_section()

        # Carrega dados iniciais
        self.load_data_from_personagem()

    def load_data_from_personagem(self) -> None:
        """Carrega os dados do personagem para a UI."""
        # Atributos
        for attr_name in [FORCA, DESTREZA, CONSTITUICAO, INTELIGENCIA, SABEDORIA, CARISMA]:
            attr_value = self.personagem.atributos.get(attr_name, 0)
            self.attribute_stringvars[attr_name].set(str(attr_value))
            self._update_attribute_dice_display(attr_name)

            # Atualiza a cor do entry
            entry = self.attribute_entries[attr_name + "_val"]
            if attr_value >= 5:
                entry.configure(border_color=COLORS["success"], text_color=COLORS["success"])
            elif attr_value >= 3:
                entry.configure(border_color=COLORS["primary"], text_color=COLORS["primary"])
            elif attr_value >= 1:
                entry.configure(border_color=COLORS["warning"], text_color=COLORS["warning"])
            else:
                entry.configure(border_color=COLORS["danger"], text_color=COLORS["danger"])

        # Pontos
        self.pv_atuais_var.set(str(self.personagem.pv_atuais))
        self.pv_max_var.set(str(self.personagem.pv_maximo))
        self._update_stat_entry_color(self.pv_current_entry, self.personagem.pv_atuais, self.personagem.pv_maximo)

        self.pm_atuais_var.set(str(self.personagem.pm_atuais))
        self.pm_max_var.set(str(self.personagem.pm_maximo))
        self._update_stat_entry_color(self.pm_current_entry, self.personagem.pm_atuais, self.personagem.pm_maximo)

        self.vigor_atuais_var.set(str(self.personagem.vigor_atuais))
        self.vigor_max_var.set(str(self.personagem.vigor_maximo))
        self._update_stat_entry_color(self.vigor_current_entry, self.personagem.vigor_atuais, self.personagem.vigor_maximo)

        # Perícias
        for skill_name in SKILLS_LIST:
            # Valor numérico
            skill_value = self.personagem.pericias_valores.get(skill_name, 0)
            self.skill_value_stringvars[skill_name].set(str(skill_value))
            
            # Status de treinada
            is_trained = skill_name in self.personagem.pericias_treinadas
            self.skill_trained_vars[skill_name].set(is_trained)

            # Atualiza a cor do entry
            entry = self.skill_value_entries[skill_name]
            if skill_value >= 8:
                entry.configure(border_color=COLORS["success"], text_color=COLORS["success"])
            elif skill_value >= 5:
                entry.configure(border_color=COLORS["primary"], text_color=COLORS["primary"])
            elif skill_value >= 1:
                entry.configure(border_color=COLORS["warning"], text_color=COLORS["warning"])
            else:
                entry.configure(border_color=COLORS["danger"], text_color=COLORS["danger"])

    def atualizar_display_maximos(self) -> None:
        """Atualiza os valores máximos de PV, PM e Vigor na UI."""
        # Atualiza os valores máximos
        self.pv_max_var.set(str(self.personagem.pv_maximo))
        self.pm_max_var.set(str(self.personagem.pm_maximo))
        self.vigor_max_var.set(str(self.personagem.vigor_maximo))

        # Atualiza as cores dos entries baseado nos valores atuais vs máximos
        self._update_stat_entry_color(self.pv_current_entry, self.personagem.pv_atuais, self.personagem.pv_maximo)
        self._update_stat_entry_color(self.pm_current_entry, self.personagem.pm_atuais, self.personagem.pm_maximo)
        self._update_stat_entry_color(self.vigor_current_entry, self.personagem.vigor_atuais, self.personagem.vigor_maximo)

    def _adjust_attribute_value(self, attr_name: str, amount: int) -> None:
        """Ajusta o valor de um atributo."""
        try:
            current_val = int(self.attribute_stringvars[attr_name].get())
            new_val = current_val + amount  # Removida a restrição de valor mínimo
            self.attribute_stringvars[attr_name].set(str(new_val))
        except ValueError:
            self.attribute_stringvars[attr_name].set("0")

    def on_attribute_change(self, attr_name: str, attr_var: ctk.StringVar) -> None:
        """Manipula mudanças nos valores dos atributos."""
        try:
            new_val = int(attr_var.get())
            
            # Atualiza o personagem
            self.personagem.atributos[attr_name] = new_val
            
            # Atualiza o display dos dados
            self._update_attribute_dice_display(attr_name)
            
            # Atualiza a cor do entry
            entry = self.attribute_entries[attr_name + "_val"]
            if new_val >= 5:
                entry.configure(border_color=COLORS["success"], text_color=COLORS["success"])
            elif new_val >= 3:
                entry.configure(border_color=COLORS["primary"], text_color=COLORS["primary"])
            elif new_val >= 0:
                entry.configure(border_color=COLORS["warning"], text_color=COLORS["warning"])
            else:  # Valores negativos
                entry.configure(border_color=COLORS["danger"], text_color=COLORS["danger"])
                
        except ValueError:
            # Reverte para o valor anterior em caso de entrada inválida
            attr_var.set(str(self.personagem.atributos.get(attr_name, 0)))

    def _adjust_skill_value(self, skill_name: str, amount: int) -> None:
        """Ajusta o valor de uma perícia."""
        try:
            current_val = int(self.skill_value_stringvars[skill_name].get())
            new_val = max(0, current_val + amount)  # Não permite valores negativos
            self.skill_value_stringvars[skill_name].set(str(new_val))
        except ValueError:
            self.skill_value_stringvars[skill_name].set("0")

    def on_skill_value_change(self, skill_name: str, value_var: ctk.StringVar) -> None:
        """Manipula mudanças nos valores das perícias."""
        try:
            new_val = int(value_var.get())
            if new_val < 0:
                new_val = 0
                value_var.set("0")
            
            # Atualiza o personagem
            self.personagem.pericias_valores[skill_name] = new_val
            
            # Atualiza a cor do entry
            entry = self.skill_value_entries[skill_name]
            if new_val >= 8:
                entry.configure(border_color=COLORS["success"], text_color=COLORS["success"])
            elif new_val >= 5:
                entry.configure(border_color=COLORS["primary"], text_color=COLORS["primary"])
            elif new_val >= 1:
                entry.configure(border_color=COLORS["warning"], text_color=COLORS["warning"])
            else:
                entry.configure(border_color=COLORS["danger"], text_color=COLORS["danger"])
                
            # Notifica outras abas da mudança
            if skill_name in ["Corpo-a-Corpo", "Pontaria", "Elemental", "Esquiva", "Bloqueio", "Iniciativa"]:
                if hasattr(self.personagem, 'atualizar_pericia_valor'):
                    self.personagem.atualizar_pericia_valor(skill_name, new_val)
                    # Atualiza as abas que usam estas perícias
                    if hasattr(self.app_ui, 'combat_tab'):
                        self.app_ui.combat_tab.load_data_from_personagem()
                    if hasattr(self.app_ui, 'magic_tab') and skill_name == "Elemental":
                        self.app_ui.magic_tab.load_data_from_personagem()
                
        except ValueError:
            # Reverte para o valor anterior em caso de entrada inválida
            value_var.set(str(self.personagem.pericias_valores.get(skill_name, 0)))

    def on_skill_trained_change(self, skill_name: str, trained_var: tkinter.BooleanVar) -> None:
        """Manipula mudanças no status de treinamento das perícias."""
        is_trained = trained_var.get()
        
        # Atualiza o personagem
        if is_trained:
            self.personagem.pericias_treinadas.add(skill_name)
        else:
            self.personagem.pericias_treinadas.discard(skill_name)

    def _update_stat_entry_color(self, entry: ctk.CTkEntry, current: int, maximum: int) -> None:
        """Atualiza a cor do entry baseado no valor atual vs máximo."""
        if current <= 0:
            entry.configure(border_color=COLORS["danger"], text_color=COLORS["danger"])
        elif current <= maximum // 4:
            entry.configure(border_color=COLORS["warning"], text_color=COLORS["warning"])
        elif current <= maximum // 2:
            entry.configure(border_color=COLORS["primary"], text_color=COLORS["primary"])
        else:
            entry.configure(border_color=COLORS["success"], text_color=COLORS["success"])

    def _update_attribute_dice_display(self, attr_name: str) -> None:
        """Atualiza o display dos dados para um atributo."""
        try:
            attr_value = int(self.attribute_stringvars[attr_name].get())
            num_dice, roll_type = get_dice_for_attribute_test(attr_value)
            
            # Determina o texto do tipo de rolagem
            roll_type_text = ""
            if roll_type == ROLL_TYPE_ADVANTAGE:
                roll_type_text = "↑"  # Seta para cima indica vantagem
                text_color = COLORS["success"]
            elif roll_type == ROLL_TYPE_DISADVANTAGE:
                roll_type_text = "↓"  # Seta para baixo indica desvantagem
                text_color = COLORS["danger"]
            else:
                text_color = COLORS["text"]
            
            # Atualiza o label com a informação dos dados
            dice_label = self.attribute_dice_labels[attr_name + "_dice_label"]
            dice_text = f"{num_dice}d20{roll_type_text}"
            
            # Define a cor baseada no número de dados e tipo de rolagem
            if num_dice > 1 and roll_type == ROLL_TYPE_ADVANTAGE:
                text_color = COLORS["success"]
            elif num_dice > 1 and roll_type == ROLL_TYPE_DISADVANTAGE:
                text_color = COLORS["danger"]
            
            dice_label.configure(text=dice_text, text_color=text_color)
            
        except ValueError:
            # Em caso de erro, mostra o padrão de 1d20
            dice_label = self.attribute_dice_labels[attr_name + "_dice_label"]
            dice_label.configure(text="1d20", text_color=COLORS["text"])

    def setup_attributes_points_section(self) -> None:
        """Configura os widgets para Atributos, PV, PM e Vigor com visual aprimorado."""
        # Frame principal dos atributos
        attr_frame = ctk.CTkFrame(
            self.attr_points_frame,
            fg_color="transparent",
            border_width=2,
            border_color=COLORS["primary"],
            corner_radius=10
        )
        attr_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título da seção
        title_attr_label = ctk.CTkLabel(
            master=attr_frame,
            text="Atributos",
            **STYLES["label"]["title"]
        )
        title_attr_label.pack(pady=(15, 20))

        # Frame para os atributos
        attributes_frame = ctk.CTkFrame(attr_frame, fg_color="transparent")
        attributes_frame.pack(fill="x", padx=15, pady=5)
        
        # Grid para os atributos
        attributes_frame.columnconfigure(0, weight=0)  # Nome (fixo)
        attributes_frame.columnconfigure(1, weight=1)  # Controles (expansível)
        attributes_frame.columnconfigure(2, weight=0)  # Dados (fixo)

        # Lista de atributos com suas abreviações
        attributes = [
            (FORCA, "FOR"),
            (DESTREZA, "DES"),
            (CONSTITUICAO, "CON"),
            (INTELIGENCIA, "INT"),
            (SABEDORIA, "SAB"),
            (CARISMA, "CAR")
        ]

        for i, (attr_name, attr_abbrev) in enumerate(attributes):
            # Label do atributo com abreviação
            label = ctk.CTkLabel(
                master=attributes_frame,
                text=f"{attr_name} ({attr_abbrev}):",
                anchor="e",
                width=120,
                **STYLES["label"]["normal"]
            )
            label.grid(row=i, column=0, padx=(5, 10), pady=5, sticky="e")

            # Frame para os controles (-, entry, +)
            controls_frame = ctk.CTkFrame(attributes_frame, fg_color="transparent")
            controls_frame.grid(row=i, column=1, sticky="w", padx=5)

            # Botão de diminuir
            minus_button = ctk.CTkButton(
                master=controls_frame,
                text="-",
                width=25,
                height=25,
                fg_color="transparent",
                border_color=COLORS["danger"],
                hover_color=COLORS["surface"],
                text_color=COLORS["danger"],
                command=lambda name=attr_name: self._adjust_attribute_value(name, -1)
            )
            minus_button.pack(side="left", padx=2)

            # Entry do valor
            attr_var = ctk.StringVar()
            self.attribute_stringvars[attr_name] = attr_var
            attr_var.trace_add("write", lambda n, idx, mode, sv=attr_var, an=attr_name: self.on_attribute_change(an, sv))
            
            entry_val = ctk.CTkEntry(
                master=controls_frame,
                textvariable=attr_var,
                placeholder_text="0",
                width=50,
                border_color=COLORS["primary"]
            )
            entry_val.pack(side="left", padx=5)
            self.attribute_entries[attr_name + "_val"] = entry_val

            # Botão de aumentar
            plus_button = ctk.CTkButton(
                master=controls_frame,
                text="+",
                width=25,
                height=25,
                fg_color="transparent",
                border_color=COLORS["success"],
                hover_color=COLORS["surface"],
                text_color=COLORS["success"],
                command=lambda name=attr_name: self._adjust_attribute_value(name, 1)
            )
            plus_button.pack(side="left", padx=2)

            # Label dos dados
            dice_label = ctk.CTkLabel(
                master=attributes_frame,
                text="",
                width=100,
                anchor="w",
                **STYLES["label"]["small"]
            )
            dice_label.grid(row=i, column=2, padx=10, sticky="w")
            self.attribute_dice_labels[attr_name + "_dice_label"] = dice_label

        # Seção de Pontos
        points_frame = ctk.CTkFrame(
            attr_frame,
            fg_color="transparent",
            border_width=2,
            border_color=COLORS["secondary"],
            corner_radius=8
        )
        points_frame.pack(fill="x", padx=15, pady=(20, 15))

        # Título da seção de pontos
        points_title = ctk.CTkLabel(
            master=points_frame,
            text="Pontos",
            **STYLES["label"]["subtitle"]
        )
        points_title.pack(pady=(10, 15))

        # Frame interno para os pontos
        points_inner_frame = ctk.CTkFrame(points_frame, fg_color="transparent")
        points_inner_frame.pack(fill="x", padx=15, pady=(0, 15))

        # Configuração do grid para os pontos
        points_inner_frame.columnconfigure(0, weight=0)  # Label (fixo)
        points_inner_frame.columnconfigure(1, weight=1)  # Entry atual (expansível)
        points_inner_frame.columnconfigure(2, weight=0)  # Separador (fixo)
        points_inner_frame.columnconfigure(3, weight=0)  # Label máximo (fixo)

        # Pontos com suas cores específicas
        points_types = [
            ("PV", self.pv_atuais_var, self.pv_max_var, COLORS["danger"]),
            ("PM", self.pm_atuais_var, self.pm_max_var, COLORS["primary"]),
            ("Vigor", self.vigor_atuais_var, self.vigor_max_var, COLORS["success"])
        ]

        for i, (point_type, current_var, max_var, color) in enumerate(points_types):
            # Label
            ctk.CTkLabel(
                master=points_inner_frame,
                text=f"{point_type}:",
                anchor="e",
                width=60,
                **STYLES["label"]["normal"]
            ).grid(row=i, column=0, padx=(5, 10), pady=3, sticky="e")

            # Entry do valor atual
            current_entry = ctk.CTkEntry(
                master=points_inner_frame,
                textvariable=current_var,
                placeholder_text="Atual",
                width=70,
                border_color=color
            )
            current_entry.grid(row=i, column=1, padx=2, pady=3, sticky="w")

            # Configurar o callback para atualização do valor atual
            if point_type == "PV":
                self.pv_current_entry = current_entry
                current_var.trace_add("write", lambda n,i,m,sv=current_var: self._update_current_stat_pv(sv))
            elif point_type == "PM":
                self.pm_current_entry = current_entry
                current_var.trace_add("write", lambda n,i,m,sv=current_var: self._update_current_stat_pm(sv))
            else:  # Vigor
                self.vigor_current_entry = current_entry
                current_var.trace_add("write", lambda n,i,m,sv=current_var: self._update_current_stat_vigor(sv))

            # Separador
            ctk.CTkLabel(
                master=points_inner_frame,
                text="/",
                **STYLES["label"]["normal"]
            ).grid(row=i, column=2, padx=5, pady=3)

            # Label do valor máximo
            max_label = ctk.CTkLabel(
                master=points_inner_frame,
                textvariable=max_var,
                width=50,
                anchor="center",
                fg_color=COLORS["surface"],
                corner_radius=8,
                **STYLES["label"]["normal"]
            )
            max_label.grid(row=i, column=3, padx=2, pady=3, sticky="w")

    def setup_skills_section(self) -> None:
        """Configura a seção de perícias com visual aprimorado."""
        # Frame principal das perícias
        skills_frame = ctk.CTkFrame(
            self.skills_frame_container,
            fg_color="transparent",
            border_width=2,
            border_color=COLORS["primary"],
            corner_radius=10
        )
        skills_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Título da seção
        title_skills_label = ctk.CTkLabel(
            master=skills_frame,
            text="Perícias",
            **STYLES["label"]["title"]
        )
        title_skills_label.pack(pady=(15, 20))

        # Frame scrollável para as perícias
        self.skills_scroll_frame = ctk.CTkScrollableFrame(
            master=skills_frame,
            fg_color="transparent",
            height=400
        )
        self.skills_scroll_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Configuração do grid para as perícias
        self.skills_scroll_frame.columnconfigure(0, weight=1)  # Nome da perícia (expansível)
        self.skills_scroll_frame.columnconfigure(1, weight=0)  # Treinada (fixo)
        self.skills_scroll_frame.columnconfigure(2, weight=0)  # Controles de valor (fixo)
        self.skills_scroll_frame.columnconfigure(3, weight=0)  # Atributo (fixo)
        self.skills_scroll_frame.columnconfigure(4, weight=0)  # Rolar (fixo)

        # Cabeçalho das colunas
        headers = [
            ("Perícia", "w", 1), 
            ("Treinada", "center", 0),
            ("Valor", "center", 0),
            ("Atributo", "center", 0),
            ("", "center", 0)  # Coluna do botão de rolar
        ]
        
        for col, (text, align, weight) in enumerate(headers):
            self.skills_scroll_frame.columnconfigure(col, weight=weight)
            if text:  # Só cria label se houver texto
                ctk.CTkLabel(
                    self.skills_scroll_frame,
                    text=text,
                    anchor=align,
                    **STYLES["label"]["small"]
                ).grid(row=0, column=col, padx=5, pady=(0,10), sticky="ew")

        # Lista de perícias com seus atributos
        skills_data = [
            ("Acrobacia", "DES", DESTREZA),
            ("Adestramento", "CAR", CARISMA),
            ("Atletismo", "FOR", FORCA),
            ("Atuação", "CAR", CARISMA),
            ("Bloqueio", "CON", CONSTITUICAO),
            ("Cavalgar", "DES", DESTREZA),
            ("Conhecimento (Arcano)", "INT", INTELIGENCIA),
            ("Conhecimento (História)", "INT", INTELIGENCIA),
            ("Conhecimento (Natureza)", "INT", INTELIGENCIA),
            ("Conhecimento (Religião)", "INT", INTELIGENCIA),
            ("Conhecimento (Geografia)", "INT", INTELIGENCIA),
            ("Conhecimento (Reinos)", "INT", INTELIGENCIA),
            ("Corpo-a-Corpo", "FOR/DES", FORCA),
            ("Cura", "SAB", SABEDORIA),
            ("Diplomacia", "CAR", CARISMA),
            ("Elemental", "INT/SAB", INTELIGENCIA),
            ("Enganação", "CAR", CARISMA),
            ("Esquiva", "DES", DESTREZA),
            ("Fortitude", "CON", CONSTITUICAO),
            ("Furtividade", "DES", DESTREZA),
            ("Guerra", "INT", INTELIGENCIA),
            ("Iniciativa", "DES", DESTREZA),
            ("Intimidação", "CAR", CARISMA),
            ("Intuição", "SAB", SABEDORIA),
            ("Investigação", "INT", INTELIGENCIA),
            ("Jogatina", "CAR", CARISMA),
            ("Ladinagem", "DES", DESTREZA),
            ("Misticismo", "INT", INTELIGENCIA),
            ("Nobreza", "INT", INTELIGENCIA),
            ("Percepção", "SAB", SABEDORIA),
            ("Pontaria", "DES", DESTREZA),
            ("Reflexos", "DES", DESTREZA),
            ("Sobrevivência", "SAB", SABEDORIA),
            ("Vontade", "SAB", SABEDORIA)
        ]

        for i, (skill_name, attr_abbrev, attr_key) in enumerate(skills_data, start=1):
            # Nome da perícia
            name_label = ctk.CTkLabel(
                master=self.skills_scroll_frame,
                text=skill_name,
                anchor="w",
                **STYLES["label"]["normal"]
            )
            name_label.grid(row=i, column=0, padx=5, pady=2, sticky="ew")

            # Checkbox de treinada
            trained_var = tkinter.BooleanVar()
            trained_var.trace_add("write", lambda n,idx,m,bv=trained_var,sn=skill_name: self.on_skill_trained_change(sn,bv))
            trained_check = ctk.CTkCheckBox(
                master=self.skills_scroll_frame,
                text="",
                variable=trained_var,
                width=20
            )
            trained_check.grid(row=i, column=1, padx=5, pady=2)
            self.skill_trained_vars[skill_name] = trained_var

            # Frame para os controles de valor
            value_frame = ctk.CTkFrame(self.skills_scroll_frame, fg_color="transparent")
            value_frame.grid(row=i, column=2, padx=5, pady=2)

            # Botão de diminuir
            minus_button = ctk.CTkButton(
                master=value_frame,
                text="-",
                width=25,
                height=25,
                fg_color="transparent",
                border_color=COLORS["danger"],
                hover_color=COLORS["surface"],
                text_color=COLORS["danger"],
                command=lambda name=skill_name: self._adjust_skill_value(name, -1)
            )
            minus_button.pack(side="left", padx=2)

            # Entry do valor
            value_var = ctk.StringVar()
            self.skill_value_stringvars[skill_name] = value_var
            value_var.trace_add("write", lambda n,idx,m,sv=value_var,sn=skill_name: self.on_skill_value_change(sn,sv))

            value_entry = ctk.CTkEntry(
                master=value_frame,
                textvariable=value_var,
                placeholder_text="0",
                width=50,
                border_color=COLORS["primary"]
            )
            value_entry.pack(side="left", padx=2)
            self.skill_value_entries[skill_name] = value_entry

            # Botão de aumentar
            plus_button = ctk.CTkButton(
                master=value_frame,
                text="+",
                width=25,
                height=25,
                fg_color="transparent",
                border_color=COLORS["success"],
                hover_color=COLORS["surface"],
                text_color=COLORS["success"],
                command=lambda name=skill_name: self._adjust_skill_value(name, 1)
            )
            plus_button.pack(side="left", padx=2)

            # Label do atributo
            attr_label = ctk.CTkLabel(
                master=self.skills_scroll_frame,
                text=f"({attr_abbrev})",
                anchor="center",
                width=60,
                **STYLES["label"]["small"]
            )
            attr_label.grid(row=i, column=3, padx=5, pady=2)
            self.skill_key_attribute_map[skill_name] = attr_key

            # Botão de rolagem
            roll_button = ctk.CTkButton(
                master=self.skills_scroll_frame,
                text="🎲",
                width=30,
                height=28,
                corner_radius=8,
                fg_color="transparent",
                border_color=COLORS["primary"],
                hover_color=COLORS["surface"],
                text_color=COLORS["primary"],
                command=lambda sn=skill_name: self.roll_specific_skill(sn)
            )
            roll_button.grid(row=i, column=4, padx=5, pady=2)
            self.skill_widgets[skill_name + "_roll_button"] = roll_button

    def setup_dice_roll_result_display_section(self) -> None:
        """Configura a seção de exibição do resultado da rolagem com visual aprimorado."""
        # Frame principal para o resultado da rolagem
        self.dice_result_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=COLORS["surface"],
            border_width=2,
            border_color=COLORS["secondary"],
            corner_radius=8
        )
        self.dice_result_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=(5, 0))

        # Centraliza o conteúdo
        self.dice_result_frame.grid_columnconfigure(0, weight=1)  # Espaço à esquerda
        self.dice_result_frame.grid_columnconfigure(1, weight=0)  # Animação (fixo)
        self.dice_result_frame.grid_columnconfigure(2, weight=0)  # Texto (fixo)
        self.dice_result_frame.grid_columnconfigure(3, weight=1)  # Espaço à direita

        # Label para animação do dado
        self.dice_animation_label = ctk.CTkLabel(
            master=self.dice_result_frame,
            text="",
            font=ctk.CTkFont(size=24, weight="bold"),
            width=60,
            anchor="center"
        )
        self.dice_animation_label.grid(row=0, column=1, padx=10, pady=10)

        # Label para o texto "Rolando..."
        self.roll_result_label = ctk.CTkLabel(
            master=self.dice_result_frame,
            text="",
            anchor="w",
            justify="left"
        )
        self.roll_result_label.grid(row=0, column=2, padx=10, pady=10)

        # Popup para resultado
        self.result_popup = None  # Será criado quando necessário

    def _create_result_popup(self, formatted_result: str, success_level: str) -> None:
        """Cria um popup com o resultado da rolagem."""
        # Se já existe um popup, destrói ele
        if self.result_popup is not None:
            self.result_popup.destroy()

        # Define cores baseadas no resultado
        result_colors = {
            "SUCESSO EXTREMO": COLORS["success"],
            "SUCESSO BOM": COLORS["primary"],
            "SUCESSO NORMAL": COLORS["secondary"],
            "FRACASSO": COLORS["warning"],
            "FRACASSO CRÍTICO": COLORS["danger"]
        }
        result_color = result_colors[success_level]

        # Cria um novo popup
        self.result_popup = ctk.CTkToplevel()
        self.result_popup.title("Resultado do Teste")
        self.result_popup.geometry("600x500")  # Aumentado a largura para 600
        
        # Configura o popup
        self.result_popup.transient(self.tab_widget.winfo_toplevel())
        self.result_popup.grab_set()
        
        # Centraliza o popup na tela
        window = self.tab_widget.winfo_toplevel()
        x = window.winfo_x() + (window.winfo_width() - 600) // 2  # Ajustado para a nova largura
        y = window.winfo_y() + (window.winfo_height() - 500) // 2
        self.result_popup.geometry(f"+{x}+{y}")

        # Frame interno com padding e borda colorida
        inner_frame = ctk.CTkFrame(
            self.result_popup,
            fg_color="transparent",
            border_width=2,
            border_color=result_color,
            corner_radius=10
        )
        inner_frame.pack(fill="both", expand=True, padx=35, pady=30)  # Aumentado o padding horizontal

        # Label com o resultado
        result_label = ctk.CTkLabel(
            inner_frame,
            text=formatted_result,
            justify="center",
            font=ctk.CTkFont(size=16),
            wraplength=520  # Aumentado para a nova largura
        )
        result_label.pack(fill="both", expand=True, padx=30, pady=25)  # Aumentado o padding horizontal

        # Frame para os botões
        button_frame = ctk.CTkFrame(inner_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(0, 15))

        # Botão de fechar
        close_button = ctk.CTkButton(
            button_frame,
            text="Fechar",
            command=self.result_popup.destroy,
            fg_color=result_color,
            hover_color=COLORS["surface"],
            width=140,  # Aumentado a largura do botão
            height=35
        )
        close_button.pack(pady=(20, 0))

    def _update_roll_result_display(self, formatted_result: str, success_level: str) -> None:
        """Atualiza o display do resultado da rolagem."""
        # Limpa o texto de "Rolando..."
        self.roll_result_label.configure(text="")
        
        # Cria o popup com o resultado
        self._create_result_popup(formatted_result, success_level)
        
        # Reativa todos os botões de rolagem após a animação
        for widget_key in self.skill_widgets:
            if widget_key.endswith("_roll_button"):
                widget = self.skill_widgets[widget_key]
                if isinstance(widget, ctk.CTkButton):
                    widget.configure(state="normal")

    def roll_specific_skill(self, skill_name: str) -> None:
        """Realiza um teste para uma perícia específica."""
        # Obtém o valor da perícia da UI
        skill_val_str = self.skill_value_stringvars.get(skill_name, ctk.StringVar(value="0")).get()
        try:
            skill_value = int(skill_val_str)
        except ValueError:
            skill_value = 0  # Valor padrão se inválido

        # Obtém o atributo base da perícia (usado apenas para determinar os dados)
        base_attribute = self.skill_key_attribute_map[skill_name]
        base_attribute_value = int(self.attribute_stringvars[base_attribute].get())

        # Desabilita todos os botões de rolagem durante a animação
        for widget_key in self.skill_widgets:
            if widget_key.endswith("_roll_button"):
                widget = self.skill_widgets[widget_key]
                if isinstance(widget, ctk.CTkButton):
                    widget.configure(state="disabled")

        # Inicia a animação, usando o atributo para dados e a perícia para o alvo
        self.start_dice_roll_animation(base_attribute_value, skill_value, skill_name)

    def start_dice_roll_animation(self, attribute_value: int, skill_value: int, skill_name: str) -> None:
        """Inicia a animação de rolagem de dados."""
        self.dice_animation_label.configure(text="")
        self.roll_result_label.configure(text=f"Rolando {skill_name}...")
        self.animate_dice(0, attribute_value, skill_value, skill_name)

    def animate_dice(self, step: int, attribute_value: int, skill_value: int, skill_name: str) -> None:
        """Executa um passo da animação de rolagem de dados."""
        if step < 8:  # 8 passos de animação
            # Gera um número aleatório para a animação
            num = random.randint(1, 20)
            self.dice_animation_label.configure(text=str(num))
            
            # Calcula o intervalo da animação (mais rápido no início, mais lento no final)
            animation_interval = 50 + (step * 25)  # 50ms -> 225ms
            
            # Agenda o próximo passo da animação
            self.tab_widget.after(animation_interval, self.animate_dice, step + 1, attribute_value, skill_value, skill_name)
        else:
            # Determina o tipo de rolagem baseado no valor do ATRIBUTO
            num_dice, roll_type = get_dice_for_attribute_test(attribute_value)
            
            # Realiza a rolagem final usando o valor do ATRIBUTO para determinar dados
            final_d20, all_rolls = perform_attribute_test_roll(attribute_value)
            
            # Usa o valor da PERÍCIA para verificar o sucesso
            success_level = check_success(skill_value, final_d20, final_d20)

            # Determina o texto do tipo de rolagem
            roll_type_text = ""
            if roll_type == ROLL_TYPE_ADVANTAGE:
                roll_type_text = " (Vantagem)"
            elif roll_type == ROLL_TYPE_DISADVANTAGE:
                roll_type_text = " (Desvantagem)"

            # Atualiza o label de animação com o resultado final
            self.dice_animation_label.configure(text=str(final_d20))

            # Formata e exibe o resultado
            formatted_result = self._format_roll_result(
                skill_name=skill_name,
                skill_value=skill_value,
                attribute_value=attribute_value,
                final_d20=final_d20,
                all_rolls=all_rolls,
                success_level=success_level,
                roll_type_text=roll_type_text
            )
            self._update_roll_result_display(formatted_result, success_level)

    def _format_roll_result(self, skill_name: str, skill_value: int, attribute_value: int, final_d20: int, 
                          all_rolls: list, success_level: str, roll_type_text: str = "") -> str:
        """Formata o resultado da rolagem com cores e estilos."""
        # Obtém os valores individuais
        base_attribute = self.skill_key_attribute_map[skill_name]
        is_trained = self.skill_trained_vars[skill_name].get()

        # Determina o símbolo e a mensagem baseado no resultado
        result_info = {
            "SUCESSO EXTREMO": ("⭐⭐", "Sucesso Extremo! Superou o alvo por 10 ou mais!"),
            "SUCESSO BOM": ("⭐", "Sucesso Bom! Superou o alvo por 5 a 9 pontos!"),
            "SUCESSO NORMAL": ("✓", "Sucesso Normal! Alcançou ou superou o alvo!"),
            "FRACASSO": ("✗", "Fracasso! Ficou abaixo do alvo!"),
            "FRACASSO CRÍTICO": ("✗✗", "Fracasso Crítico! Ficou 5 ou mais pontos abaixo do alvo!")
        }

        symbol, message = result_info.get(success_level, ("", ""))

        # Formata o texto do tipo de rolagem e detalhes
        if roll_type_text:
            dice_info = f"{len(all_rolls)}d20{roll_type_text}"
            if len(all_rolls) > 1:
                roll_details = f"\n→ Rolagens individuais: {', '.join(map(str, all_rolls))}"
            else:
                roll_details = ""
        else:
            dice_info = "1d20"
            roll_details = ""

        # Formata o status de treinamento
        training_status = "[Não Treinada]" if not is_trained else "[Treinada]"

        # Constrói o texto do resultado com mais clareza e organização
        lines = [
            "╔═══════════════════════════════╗",
            f"  {message}  {symbol}",
            "╚═══════════════════════════════╝",
            "",
            "▸ INFORMAÇÕES DO TESTE:",
            f"• Perícia: {skill_name} {training_status}",
            f"• Dificuldade do Teste: {skill_value}",
            "",
            "▸ DETALHES DA ROLAGEM:",
            f"• Atributo Base: {base_attribute} (nível {attribute_value})",
            f"• Dados Usados: {dice_info}"
        ]

        # Adiciona detalhes das rolagens se houver
        if roll_details:
            lines.append(roll_details)

        lines.extend([
            "",
            "▸ RESULTADO FINAL:",
            f"• Valor Obtido: {final_d20}",
            f"• Alvo Necessário: {skill_value}"
        ])

        return "\n".join(lines)

    def _update_current_stat_pv(self, string_var: ctk.StringVar) -> None:
        """Atualiza os PV atuais no objeto personagem."""
        try:
            new_val = int(string_var.get())
            self.personagem.pv_atuais = new_val  # O setter da property já faz a validação
            self._update_stat_entry_color(self.pv_current_entry, new_val, self.personagem.pv_maximo)
        except ValueError:
            # Reverte para o valor atual do personagem em caso de entrada inválida
            string_var.set(str(self.personagem.pv_atuais))

    def _update_current_stat_pm(self, string_var: ctk.StringVar) -> None:
        """Atualiza os PM atuais no objeto personagem."""
        try:
            new_val = int(string_var.get())
            self.personagem.pm_atuais = new_val  # O setter da property já faz a validação
            self._update_stat_entry_color(self.pm_current_entry, new_val, self.personagem.pm_maximo)
        except ValueError:
            # Reverte para o valor atual do personagem em caso de entrada inválida
            string_var.set(str(self.personagem.pm_atuais))

    def _update_current_stat_vigor(self, string_var: ctk.StringVar) -> None:
        """Atualiza os pontos de Vigor atuais no objeto personagem."""
        try:
            new_val = int(string_var.get())
            self.personagem.vigor_atuais = new_val  # O setter da property já faz a validação
            self._update_stat_entry_color(self.vigor_current_entry, new_val, self.personagem.vigor_maximo)
        except ValueError:
            # Reverte para o valor atual do personagem em caso de entrada inválida
            string_var.set(str(self.personagem.vigor_atuais))