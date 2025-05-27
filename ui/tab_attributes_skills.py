import customtkinter as ctk
import random
from typing import Dict, Any, Optional
import tkinter

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

class AttributesSkillsTab:
    """
    Gerencia a aba de Atributos e Perícias na interface do usuário.
    Permite a visualização e edição de atributos, PV, PM, Vigor e perícias,
    além de realizar testes de perícia.
    """
    personagem: Personagem # Referência ao objeto Personagem atual

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

    def __init__(self, tab_widget: ctk.CTkFrame, personagem: Personagem):
        self.tab_widget = tab_widget
        self.personagem = personagem

        self.main_frame = ctk.CTkFrame(self.tab_widget)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=2)
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=0)

        self.attr_points_frame = ctk.CTkFrame(self.main_frame)
        self.attr_points_frame.grid(row=0, column=0, padx=(0, 5), pady=(0, 10), sticky="nsew")
        self.attr_points_frame.columnconfigure(0, weight=0)
        self.attr_points_frame.columnconfigure(1, weight=0)
        self.attr_points_frame.columnconfigure(2, weight=1)

        self.attribute_entries = {}
        self.attribute_dice_labels = {}
        self.attribute_stringvars = {}

        self.skill_value_stringvars = {}
        self.skill_trained_vars = {}
        self.skill_widgets = {}
        self.skill_key_attribute_map = {}

        self.pv_atuais_var = ctk.StringVar()
        self.pv_max_var = ctk.StringVar()
        self.pm_atuais_var = ctk.StringVar()
        self.pm_max_var = ctk.StringVar()
        self.vigor_atuais_var = ctk.StringVar()
        self.vigor_max_var = ctk.StringVar()

        self.setup_attributes_points_section()
        self.skills_frame_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.skills_frame_container.grid(row=0, column=1, padx=(5, 0), pady=0, sticky="nsew")
        self.skills_frame_container.rowconfigure(0, weight=1)
        self.setup_skills_section()
        self.setup_dice_roll_result_display_section()

        self.load_data_from_personagem()

    def load_data_from_personagem(self) -> None:
        """
        Carrega os dados do objeto Personagem para os widgets da UI desta aba.
        Este método é chamado quando uma nova ficha é carregada ou criada.
        """
        # Carrega Atributos
        for attr_name_key, string_var in self.attribute_stringvars.items():
            val_personagem = str(self.personagem.atributos.get(attr_name_key, 0))
            string_var.set(val_personagem) # Dispara o callback on_attribute_change que atualiza o dice_label

        # Carrega PV, PM, Vigor (atuais e máximos)
        self.personagem.recalcular_maximos() # Garante que máximos estão atualizados no modelo
        self.atualizar_display_maximos() # Atualiza os labels de máximos na UI

        self.pv_atuais_var.set(str(self.personagem.pv_atuais))
        self.pm_atuais_var.set(str(self.personagem.pm_atuais))
        self.vigor_atuais_var.set(str(self.personagem.vigor_atuais))

        # Carrega Perícias (Treinadas e Valores)
        for skill_name, trained_var in self.skill_trained_vars.items():
            is_trained_in_model = skill_name in self.personagem.pericias_treinadas
            trained_var.set(is_trained_in_model) # Dispara on_skill_trained_change

        for skill_name, value_var in self.skill_value_stringvars.items():
            # O callback on_skill_trained_change já ajusta o valor se necessário,
            # mas garantimos que o valor carregado do personagem seja refletido.
            is_trained = skill_name in self.personagem.pericias_treinadas
            default_val_if_not_found = 1 if is_trained and self.personagem.pericias_valores.get(skill_name) is None else 0
            val_personagem_pericia = str(self.personagem.pericias_valores.get(skill_name, default_val_if_not_found))
            value_var.set(val_personagem_pericia) # Dispara on_skill_value_change

    def atualizar_display_maximos(self) -> None:
        """Atualiza os labels da UI que exibem os valores máximos de PV, PM e Vigor."""
        if hasattr(self, 'personagem'): # Garante que personagem existe
            self.pv_max_var.set(str(self.personagem.pv_maximo))
            self.pm_max_var.set(str(self.personagem.pm_maximo))
            self.vigor_max_var.set(str(self.personagem.vigor_maximo))

    def _adjust_attribute_value(self, attr_name: str, amount: int) -> None:
        """Ajusta o valor de um atributo (usado pelos botões +/-) e atualiza a StringVar."""
        try:
            current_val_str = self.attribute_stringvars[attr_name].get()
            current_val = int(current_val_str) if current_val_str.lstrip('-').isdigit() else 0
            new_val = current_val + amount
            if new_val < -1: # Limite inferior para atributos (exemplo)
                new_val = -1
            self.attribute_stringvars[attr_name].set(str(new_val))
            # O trace na StringVar chamará on_attribute_change
        except ValueError:
            # Se o valor atual na UI for inválido, redefina para o valor do modelo
            self.attribute_stringvars[attr_name].set(str(self.personagem.atributos.get(attr_name, 0)))
        except KeyError:
            print(f"Erro: Stringvar para atributo {attr_name} não encontrada.") # Para debug

    def on_attribute_change(self, attr_name_key: str, string_var_instance: ctk.StringVar, *args) -> None:
        """
        Callback acionado quando o valor de uma StringVar de atributo muda.
        Atualiza o modelo do personagem e o display de dados do atributo (vantagem/desvantagem).
        """
        attr_val_str = string_var_instance.get().strip()
        attr_value_for_model: int
        attr_value_for_dice_label: int # Valor usado para calcular os dados (pode ser 0 se inválido)

        if not attr_val_str or attr_val_str == "-":
            attr_value_for_model = 0
            attr_value_for_dice_label = 0
        elif attr_val_str.lstrip('-').isdigit():
            try:
                attr_value_for_model = int(attr_val_str)
                attr_value_for_dice_label = attr_value_for_model
            except ValueError: # Não deveria acontecer se a validação de entrada for boa
                attr_value_for_model = self.personagem.atributos.get(attr_name_key, 0)
                attr_value_for_dice_label = attr_value_for_model
                string_var_instance.set(str(attr_value_for_model)) # Reverte na UI
        else: # Entrada inválida não numérica
            attr_value_for_model = self.personagem.atributos.get(attr_name_key, 0)
            attr_value_for_dice_label = attr_value_for_model
            string_var_instance.set(str(attr_value_for_model)) # Reverte na UI

        # Atualiza o modelo Personagem apenas se o valor realmente mudou
        if self.personagem.atributos.get(attr_name_key) != attr_value_for_model:
            self.personagem.atualizar_atributo(attr_name_key, attr_value_for_model)
            self.atualizar_display_maximos() # PV/PM/Vigor podem depender de atributos

        # Sempre atualiza o display de dados do atributo na UI
        num_dice, roll_type_key = get_dice_for_attribute_test(attr_value_for_dice_label)
        roll_type_text = ""
        if roll_type_key == ROLL_TYPE_ADVANTAGE:
            roll_type_text = " (Maior)"
        elif roll_type_key == ROLL_TYPE_DISADVANTAGE:
            roll_type_text = " (Menor)"
        dice_text = f" ({num_dice}d20{roll_type_text})"
        
        dice_label_key = attr_name_key + "_dice_label"
        if dice_label_key in self.attribute_dice_labels:
            self.attribute_dice_labels[dice_label_key].configure(text=dice_text)

    def setup_attributes_points_section(self) -> None:
        """Configura os widgets para Atributos, PV, PM e Vigor."""
        title_attr_label = ctk.CTkLabel(master=self.attr_points_frame, text="Atributos", font=ctk.CTkFont(size=16, weight="bold"))
        title_attr_label.grid(row=0, column=0, columnspan=3, padx=5, pady=(5,10), sticky="n")
        
        # Usando as constantes definidas em character.py (ou que poderiam ser importadas)
        attributes_order = [FORCA, DESTREZA, CONSTITUICAO, INTELIGENCIA, SABEDORIA, CARISMA]

        for i, attr_name in enumerate(attributes_order):
            label = ctk.CTkLabel(master=self.attr_points_frame, text=f"{attr_name}:")
            label.grid(row=i + 1, column=0, padx=(10,2), pady=5, sticky="e")
            
            attr_input_frame = ctk.CTkFrame(self.attr_points_frame, fg_color="transparent")
            attr_input_frame.grid(row=i + 1, column=1, padx=0, pady=2, sticky="w")
            
            attr_var = ctk.StringVar()
            self.attribute_stringvars[attr_name] = attr_var
            # O lambda agora passa a instância da StringVar diretamente
            attr_var.trace_add("write", lambda n, idx, mode, sv=attr_var, an=attr_name: self.on_attribute_change(an, sv))
            
            minus_button = ctk.CTkButton(master=attr_input_frame, text="-", width=28, height=28,
                                         command=lambda name=attr_name: self._adjust_attribute_value(name, -1))
            minus_button.pack(side="left", padx=(0,1))
            
            entry_val = ctk.CTkEntry(master=attr_input_frame, width=40, textvariable=attr_var,
                                     justify="center", placeholder_text="0")
            entry_val.pack(side="left", padx=1)
            self.attribute_entries[attr_name + "_val"] = entry_val # Ainda pode ser útil para referenciar o widget
            
            plus_button = ctk.CTkButton(master=attr_input_frame, text="+", width=28, height=28,
                                        command=lambda name=attr_name: self._adjust_attribute_value(name, 1))
            plus_button.pack(side="left", padx=(1,0))
            
            dice_label = ctk.CTkLabel(master=self.attr_points_frame, text="", width=120, anchor="w")
            dice_label.grid(row=i + 1, column=2, padx=(5,0), pady=5, sticky="w")
            self.attribute_dice_labels[attr_name + "_dice_label"] = dice_label
            
        # Seção de Pontos (PV, PM, Vigor)
        points_frame = ctk.CTkFrame(self.attr_points_frame)
        points_frame.grid(row=len(attributes_order) + 1, column=0, columnspan=3, padx=5, pady=(15,5), sticky="ew")
        points_frame.columnconfigure(0, weight=1); points_frame.columnconfigure(1, weight=1)
        points_frame.columnconfigure(2, weight=0); points_frame.columnconfigure(3, weight=1)

        # PV
        pv_label = ctk.CTkLabel(master=points_frame, text="PV:")
        pv_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.pv_current_entry = ctk.CTkEntry(master=points_frame, placeholder_text="Atual", width=60, textvariable=self.pv_atuais_var)
        self.pv_current_entry.grid(row=0, column=1, padx=2, pady=5, sticky="ew")
        self.pv_atuais_var.trace_add("write", lambda n,i,m, sv=self.pv_atuais_var: self._update_current_stat_pv(sv))
        ctk.CTkLabel(master=points_frame, text="/").grid(row=0, column=2, padx=0, pady=5)
        self.pv_max_label = ctk.CTkLabel(master=points_frame, textvariable=self.pv_max_var, width=60)
        self.pv_max_label.grid(row=0, column=3, padx=2, pady=5, sticky="ew")

        # PM
        pm_label = ctk.CTkLabel(master=points_frame, text="PM:")
        pm_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.pm_current_entry = ctk.CTkEntry(master=points_frame, placeholder_text="Atual", width=60, textvariable=self.pm_atuais_var)
        self.pm_current_entry.grid(row=1, column=1, padx=2, pady=5, sticky="ew")
        self.pm_atuais_var.trace_add("write", lambda n,i,m, sv=self.pm_atuais_var: self._update_current_stat_pm(sv))
        ctk.CTkLabel(master=points_frame, text="/").grid(row=1, column=2, padx=0, pady=5)
        self.pm_max_label = ctk.CTkLabel(master=points_frame, textvariable=self.pm_max_var, width=60)
        self.pm_max_label.grid(row=1, column=3, padx=2, pady=5, sticky="ew")

        # Vigor
        vigor_label = ctk.CTkLabel(master=points_frame, text="Vigor (V):")
        vigor_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.vigor_current_entry = ctk.CTkEntry(master=points_frame, placeholder_text="Atual", width=60, textvariable=self.vigor_atuais_var)
        self.vigor_current_entry.grid(row=2, column=1, padx=2, pady=5, sticky="ew")
        self.vigor_atuais_var.trace_add("write", lambda n,i,m, sv=self.vigor_atuais_var: self._update_current_stat_vigor(sv))
        ctk.CTkLabel(master=points_frame, text="/").grid(row=2, column=2, padx=0, pady=5)
        self.vigor_max_label = ctk.CTkLabel(master=points_frame, textvariable=self.vigor_max_var, width=60)
        self.vigor_max_label.grid(row=2, column=3, padx=2, pady=5, sticky="ew")

    # Callbacks específicos para PV, PM, Vigor para usar os setters do Personagem
    def _update_current_stat_pv(self, current_val_var: ctk.StringVar) -> None:
        try:
            current_val = int(current_val_var.get())
            if self.personagem.pv_atuais != current_val: # Evita loop se o setter redefinir a stringvar
                self.personagem.pv_atuais = current_val
                # Se o setter do personagem ajustar o valor, precisamos garantir que a stringvar reflita isso.
                # A property Personagem.pv_atuais já faz a validação, então aqui só precisamos ler de volta se necessário.
                if str(self.personagem.pv_atuais) != current_val_var.get():
                    current_val_var.set(str(self.personagem.pv_atuais))
        except ValueError:
            current_val_var.set(str(self.personagem.pv_atuais)) # Reverte para o valor do modelo

    def _update_current_stat_pm(self, current_val_var: ctk.StringVar) -> None:
        try:
            current_val = int(current_val_var.get())
            if self.personagem.pm_atuais != current_val:
                self.personagem.pm_atuais = current_val
                if str(self.personagem.pm_atuais) != current_val_var.get():
                    current_val_var.set(str(self.personagem.pm_atuais))
        except ValueError:
            current_val_var.set(str(self.personagem.pm_atuais))

    def _update_current_stat_vigor(self, current_val_var: ctk.StringVar) -> None:
        try:
            current_val = int(current_val_var.get())
            if self.personagem.vigor_atuais != current_val:
                self.personagem.vigor_atuais = current_val
                if str(self.personagem.vigor_atuais) != current_val_var.get():
                    current_val_var.set(str(self.personagem.vigor_atuais))
        except ValueError:
            current_val_var.set(str(self.personagem.vigor_atuais))

    def _adjust_skill_value(self, skill_name: str, amount: int) -> None:
        """Ajusta o valor de uma perícia (usado pelos botões +/-) e atualiza a StringVar."""
        try:
            value_var = self.skill_value_stringvars[skill_name]
            current_val_str = value_var.get()
            current_val = int(current_val_str) if current_val_str.strip().lstrip('-').isdigit() else 0
            
            new_val = current_val + amount
            
            is_trained = self.skill_trained_vars.get(skill_name, ctk.BooleanVar(value=False)).get()
            min_val = 1 if is_trained and new_val < 1 else 0
            if not is_trained and new_val < 0: # Não treinado não pode ser < 0
                min_val = 0
                
            if new_val < min_val:
                new_val = min_val
            
            value_var.set(str(new_val))
            # O trace na StringVar chamará on_skill_value_change
        except ValueError:
            is_trained_check = self.skill_trained_vars.get(skill_name, ctk.BooleanVar(value=False)).get()
            default_revert_val = 1 if is_trained_check else 0
            self.skill_value_stringvars[skill_name].set(str(self.personagem.pericias_valores.get(skill_name, default_revert_val)))
        except KeyError:
            print(f"Erro: Stringvar para perícia {skill_name} não encontrada.") # Para debug

    def on_skill_value_change(self, skill_name: str, string_var_instance: ctk.StringVar, *args) -> None:
        """
        Callback acionado quando o valor de uma StringVar de perícia muda.
        Atualiza o modelo do personagem.
        """
        skill_val_str = string_var_instance.get().strip()
        new_value_for_model: int
        
        is_trained = self.skill_trained_vars.get(skill_name, ctk.BooleanVar(value=False)).get()
        
        if skill_val_str.lstrip('-').isdigit(): # Permite números negativos, mas a lógica abaixo corrige
            new_value_for_model = int(skill_val_str)
            if is_trained and new_value_for_model < 1:
                new_value_for_model = 1
            elif not is_trained and new_value_for_model < 0: # Se não treinado, valor mínimo é 0
                new_value_for_model = 0
        elif skill_val_str == "": # Campo vazio
            new_value_for_model = 1 if is_trained else 0
        else: # Entrada inválida
            current_val_in_obj = self.personagem.pericias_valores.get(skill_name, 1 if is_trained else 0)
            string_var_instance.set(str(current_val_in_obj))
            return

        # Garante que a UI reflita o valor corrigido se necessário
        if str(new_value_for_model) != skill_val_str:
            string_var_instance.set(str(new_value_for_model))
            # O set() acima irá re-disparar este callback, mas a condição abaixo evitará loop infinito.

        # Atualiza o modelo Personagem apenas se o valor realmente mudou
        if self.personagem.pericias_valores.get(skill_name) != new_value_for_model:
            self.personagem.atualizar_pericia_valor(skill_name, new_value_for_model)

    def on_skill_trained_change(self, skill_name: str, boolean_var_instance: tkinter.BooleanVar, *args) -> None:
        """
        Callback acionado quando o checkbox "treinada" de uma perícia muda.
        Atualiza o modelo e o valor da perícia na UI (mínimo 1 se treinada, 0 se não).
        """
        is_trained_ui = boolean_var_instance.get()

        if (skill_name in self.personagem.pericias_treinadas) != is_trained_ui:
            self.personagem.marcar_pericia_treinada(skill_name, is_trained_ui)

        value_var = self.skill_value_stringvars.get(skill_name)
        if value_var:
            current_skill_val_str = value_var.get()
            try:
                current_skill_val = int(current_skill_val_str)
            except ValueError:
                current_skill_val = 0

            new_val_for_ui: Optional[str] = None
            if is_trained_ui and current_skill_val < 1:
                new_val_for_ui = "1"
            elif not is_trained_ui and current_skill_val != 0:
                new_val_for_ui = "0"
            
            if new_val_for_ui is not None and value_var.get() != new_val_for_ui:
                value_var.set(new_val_for_ui)

    def setup_skills_section(self) -> None:
        """Configura os widgets para a lista de Perícias."""
        self.skills_scroll_frame = ctk.CTkScrollableFrame(self.skills_frame_container, label_text="Perícias", label_font=ctk.CTkFont(size=16, weight="bold"))
        self.skills_scroll_frame.pack(fill="both", expand=True)

        self.skills_scroll_frame.columnconfigure(0, weight=3)  # Nome da Perícia
        self.skills_scroll_frame.columnconfigure(1, weight=0)  # Treinada (Checkbox)
        self.skills_scroll_frame.columnconfigure(2, weight=0)  # Frame para Valor e botões +/-
        self.skills_scroll_frame.columnconfigure(3, weight=1)  # Atributo Chave
        self.skills_scroll_frame.columnconfigure(4, weight=0)  # Botão de Rolagem

        # Lista de perícias e seus atributos chave de lookup no dicionário self.personagem.atributos
        skill_list_data = [
            ("Acrobacia", "DES", DESTREZA), ("Adestramento", "CAR", CARISMA), ("Atletismo", "FOR", FORCA),
            ("Atuação", "CAR", CARISMA), ("Bloqueio", "CON", CONSTITUICAO), ("Cavalgar", "DES", DESTREZA),
            ("Conhecimento (Arcano)", "INT", INTELIGENCIA), ("Conhecimento (História)", "INT", INTELIGENCIA),
            ("Conhecimento (Natureza)", "INT", INTELIGENCIA), ("Conhecimento (Religião)", "INT", INTELIGENCIA),
            ("Conhecimento (Geografia)", "INT", INTELIGENCIA), ("Conhecimento (Reinos)", "INT", INTELIGENCIA),
            ("Corpo-a-Corpo", "DES/FOR", FORCA), # Usar FORÇA como padrão para lookup, UI pode indicar flexibilidade
            ("Cura", "SAB", SABEDORIA), ("Diplomacia", "CAR", CARISMA),
            ("Elemental", "INT/SAB", INTELIGENCIA), # Usar INT como padrão para lookup
            ("Enganação", "CAR", CARISMA), ("Esquiva", "DES", DESTREZA),
            ("Fortitude", "CON", CONSTITUICAO), ("Furtividade", "DES", DESTREZA),
            ("Guerra", "INT", INTELIGENCIA), ("Iniciativa", "DES", DESTREZA),
            ("Intimidação", "CAR", CARISMA), ("Intuição", "SAB", SABEDORIA),
            ("Investigação", "INT", INTELIGENCIA), ("Jogatina", "CAR", CARISMA),
            ("Ladinagem", "DES", DESTREZA), ("Misticismo", "INT", INTELIGENCIA),
            ("Nobreza", "INT", INTELIGENCIA), ("Percepção", "SAB", SABEDORIA),
            ("Pontaria", "DES", DESTREZA), ("Reflexos", "DES", DESTREZA),
            ("Sobrevivência", "SAB", SABEDORIA), ("Vontade", "SAB", SABEDORIA)
        ]

        for i, (skill_name, key_attr_display, key_attr_lookup_name) in enumerate(skill_list_data):
            name_label = ctk.CTkLabel(master=self.skills_scroll_frame, text=skill_name, anchor="w")
            name_label.grid(row=i, column=0, padx=5, pady=3, sticky="ew")

            trained_var = tkinter.BooleanVar()
            trained_var.trace_add("write", lambda n,idx,m,bv=trained_var,sn=skill_name: self.on_skill_trained_change(sn,bv))
            trained_check = ctk.CTkCheckBox(master=self.skills_scroll_frame, text="", width=20)
            trained_check.configure(variable=trained_var)
            trained_check.grid(row=i, column=1, padx=5, pady=3, sticky="w")
            self.skill_trained_vars[skill_name] = trained_var
            self.skill_widgets[skill_name + "_trained_cb"] = trained_check

            skill_value_frame = ctk.CTkFrame(self.skills_scroll_frame, fg_color="transparent")
            skill_value_frame.grid(row=i, column=2, padx=2, pady=1, sticky="w")

            skill_minus_button = ctk.CTkButton(master=skill_value_frame, text="-", width=25, height=25,
                                               command=lambda name=skill_name: self._adjust_skill_value(name, -1))
            skill_minus_button.pack(side="left", padx=(0,1))

            value_var = ctk.StringVar()
            value_var.trace_add("write", lambda n,idx,m,sv=value_var,sn=skill_name: self.on_skill_value_change(sn,sv))
            value_entry = ctk.CTkEntry(master=skill_value_frame, width=35, placeholder_text="0", textvariable=value_var, justify="center")
            value_entry.pack(side="left", padx=1)
            self.skill_value_stringvars[skill_name] = value_var
            self.skill_widgets[skill_name + "_value_entry"] = value_entry

            skill_plus_button = ctk.CTkButton(master=skill_value_frame, text="+", width=25, height=25,
                                              command=lambda name=skill_name: self._adjust_skill_value(name, 1))
            skill_plus_button.pack(side="left", padx=(1,0))

            attr_label_ui = ctk.CTkLabel(master=self.skills_scroll_frame, text=f"({key_attr_display})", anchor="w")
            attr_label_ui.grid(row=i, column=3, padx=5, pady=3, sticky="w")
            self.skill_key_attribute_map[skill_name] = key_attr_lookup_name # Armazena o nome do atributo para consulta

            roll_button = ctk.CTkButton(
                master=self.skills_scroll_frame, text="🎲", width=30, height=28,
                command=lambda s_name=skill_name, attr_key_n=key_attr_lookup_name: self.roll_specific_skill(s_name, attr_key_n)
            )
            roll_button.grid(row=i, column=4, padx=5, pady=3, sticky="e")
            self.skill_widgets[skill_name + "_roll_button"] = roll_button

    def setup_dice_roll_result_display_section(self) -> None:
        """Configura a seção para exibir os resultados das rolagens de dados."""
        result_display_frame = ctk.CTkFrame(self.main_frame)
        result_display_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=(5,0), sticky="ew")
        result_display_frame.columnconfigure(0, weight=0)
        result_display_frame.columnconfigure(1, weight=1)
        
        self.dice_animation_label = ctk.CTkLabel(master=result_display_frame, text="", width=60, height=30, font=ctk.CTkFont(size=24, weight="bold"))
        self.dice_animation_label.grid(row=0, column=0, padx=(10,5), pady=5, sticky="w")
        
        self.roll_result_label = ctk.CTkLabel(master=result_display_frame, text="Clique em 🎲 para testar uma perícia.", justify="left", height=30, anchor="w", font=ctk.CTkFont(size=14))
        self.roll_result_label.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    def roll_specific_skill(self, skill_name: str, associated_attribute_name_lookup: str) -> None:
        """Realiza um teste para uma perícia específica."""
        skill_val_str = self.skill_value_stringvars.get(skill_name, ctk.StringVar(value="0")).get()
        try:
            skill_value_to_test = int(skill_val_str)
        except ValueError:
            skill_value_to_test = 0 # Padrão se o valor da perícia for inválido na UI

        # Obtém o valor do atributo diretamente do objeto Personagem
        attribute_value_to_test = self.personagem.atributos.get(associated_attribute_name_lookup, 0)

        # Desabilita todos os botões de rolagem durante a animação
        for widget_key in self.skill_widgets:
            if widget_key.endswith("_roll_button"):
                widget = self.skill_widgets[widget_key]
                if isinstance(widget, ctk.CTkButton): # Checagem de tipo para segurança
                    widget.configure(state="disabled")
        
        self.start_dice_roll_animation(attribute_value_to_test, skill_value_to_test, skill_name)

    def start_dice_roll_animation(self, attribute_value: int, skill_value: int, skill_name_for_display: str = "Teste") -> None:
        """Inicia a animação de rolagem de dados na UI."""
        self.dice_animation_label.configure(text="")
        self.roll_result_label.configure(text=f"Rolando {skill_name_for_display}...")
        self.animate_dice(0, attribute_value, skill_value, skill_name_for_display)

    def animate_dice(self, step: int, attribute_value: int, skill_value: int, skill_name_for_display: str) -> None:
        """Executa um passo da animação de rolagem de dados."""
        animation_steps = 8
        animation_interval = 60
        if step < animation_steps:
            num = random.randint(1, 20)
            self.dice_animation_label.configure(text=str(num))
            self.tab_widget.after(animation_interval, self.animate_dice, step + 1, attribute_value, skill_value, skill_name_for_display)
        else:
            final_d20, all_rolls = perform_attribute_test_roll(attribute_value)
            # O natural_roll_for_crit_check é o final_d20, pois perform_attribute_test_roll já considera Vant/Desvant
            success_level = check_success(skill_value, final_d20, final_d20) 
            
            self.dice_animation_label.configure(text=str(final_d20))
            
            roll_details = f" (Rolagens: {all_rolls})" if len(all_rolls) > 1 else ""
            num_dice_attr, roll_type_attr_key = get_dice_for_attribute_test(attribute_value)
            roll_type_attr_text = ""
            if roll_type_attr_key == ROLL_TYPE_ADVANTAGE:
                roll_type_attr_text = " (Maior)"
            elif roll_type_attr_key == ROLL_TYPE_DISADVANTAGE:
                roll_type_attr_text = " (Menor)"
            
            attr_dice_info = f"{num_dice_attr}d20{roll_type_attr_text}"
            
            result_text_lines = [
                f"Perícia: {skill_name_for_display} (Valor {skill_value})",
                f"Atributo base: {attribute_value} -> {attr_dice_info}",
                f"d20 Usado: {final_d20}{roll_details}",
                f"Resultado: {success_level}"
            ]
            self.roll_result_label.configure(text="\n".join(result_text_lines))

            # Reabilita todos os botões de rolagem
            for widget_key in self.skill_widgets:
                if widget_key.endswith("_roll_button"):
                    widget = self.skill_widgets[widget_key]
                    if isinstance(widget, ctk.CTkButton):
                        widget.configure(state="normal")