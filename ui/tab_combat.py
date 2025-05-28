import customtkinter as ctk
import random # Mantido para animação de dados
from typing import List, Dict, Any, Optional, Tuple, Literal, Union

from core.dice_roller import (
    roll_generic_dice,
    parse_and_roll_damage_string,
    perform_attribute_test_roll,
    check_success,
    get_dice_for_attribute_test,
    SUCCESS_EXTREME, # Para checagem de crítico
    SUCCESS_GOOD,
    SUCCESS_NORMAL,
    FAILURE_NORMAL,
    FAILURE_EXTREME
)
# from core.character import Personagem # Para type hinting, se não causar problemas de import circular com AppUI

# Constantes para chaves de dicionário de armas (para consistência)
WEAPON_KEY_NAME = "nome"
WEAPON_KEY_DAMAGE = "dano" # Era 'damage_dice' na UI, mas 'dano' em items_data
WEAPON_KEY_ATTR = "atributo_chave" # Era 'atk_attr' na UI, mas 'atributo_chave' em items_data
WEAPON_KEY_SKILL_TYPE = "pericia_ataque" # Nova chave para substituir 'attack_skill_type'
WEAPON_KEY_TYPE = "tipo_dano" # Era 'type_w' na UI, mas 'tipo_dano' em items_data
WEAPON_KEY_HANDS = "empunhadura" # Era 'hands' na UI, mas 'empunhadura' em items_data
WEAPON_KEY_RANGE = "alcance" # Era 'range_w' na UI, mas 'alcance' em items_data
WEAPON_KEY_SOURCE = "origem"  # Nova chave para rastrear origem da arma
WEAPON_KEY_PRICE = "preco"    # Nova chave para guardar preço original

# Constantes para origem das armas
WEAPON_SOURCE_STORE = "loja"
WEAPON_SOURCE_CUSTOM = "personalizada"

# Mapeamento de atributos para nomes completos (usado em perform_attack_roll)
ATTRIBUTE_NAME_MAP: Dict[str, str] = {
    "FOR": "Força", "DES": "Destreza", "CON": "Constituição",
    "INT": "Inteligência", "SAB": "Sabedoria", "CAR": "Carisma"
}


class CombatTab:
    """
    Gerencia a aba de Combate, incluindo estatísticas defensivas, perícias de ataque,
    equipamento (armadura, escudo, armas) e rolagens de combate.
    """
    personagem: Any # Deveria ser Personagem
    attributes_skills_tab_ref: Any # Deveria ser AttributesSkillsTab
    app_ui: Any # Deveria ser AppUI, para show_feedback_message

    weapon_inventory_ui_rows: List[Dict[str, Any]] # Guarda refs para widgets e dados de armas

    # StringVars para estatísticas de defesa e equipamento
    rd_total_var: ctk.StringVar
    esquiva_val_var: ctk.StringVar
    bloqueio_val_var: ctk.StringVar
    iniciativa_val_var: ctk.StringVar
    cac_val_var: ctk.StringVar
    pontaria_val_var: ctk.StringVar
    elemental_val_var: ctk.StringVar
    armor_name_var: ctk.StringVar
    armor_rd_var: ctk.StringVar
    shield_name_var: ctk.StringVar
    shield_notes_var: ctk.StringVar

    # Labels e botões para armas equipadas
    mh_name_label: ctk.CTkLabel
    mh_damage_label: ctk.CTkLabel
    mh_damage_mod_entry: ctk.CTkEntry
    mh_roll_damage_button: ctk.CTkButton
    mh_roll_attack_button: ctk.CTkButton
    oh_name_label: ctk.CTkLabel
    oh_damage_label: ctk.CTkLabel
    oh_damage_mod_entry: ctk.CTkEntry
    oh_roll_damage_button: ctk.CTkButton
    oh_roll_attack_button: ctk.CTkButton
    action_roll_animation_label: ctk.CTkLabel
    action_roll_result_label: ctk.CTkLabel
    
    weapons_scroll_frame: ctk.CTkScrollableFrame
    weapon_current_row_idx: int


    def __init__(self, tab_widget: ctk.CTkFrame, attributes_skills_tab_ref: Any, personagem_atual: Any, app_ui_ref: Any):
        print("DEBUG: CombatTab __init__ FOI CHAMADO com 4+self args")
        self.tab_widget = tab_widget
        self.attributes_skills_tab_ref = attributes_skills_tab_ref
        self.personagem = personagem_atual
        self.app_ui = app_ui_ref 

        self.weapon_inventory_ui_rows = []

        # Variáveis de UI
        self.rd_total_var = ctk.StringVar()
        self.esquiva_val_var = ctk.StringVar()
        self.bloqueio_val_var = ctk.StringVar()
        self.iniciativa_val_var = ctk.StringVar()
        self.cac_val_var = ctk.StringVar()
        self.pontaria_val_var = ctk.StringVar()
        self.elemental_val_var = ctk.StringVar()
        self.armor_name_var = ctk.StringVar()
        self.armor_rd_var = ctk.StringVar()
        self.shield_name_var = ctk.StringVar()
        self.shield_notes_var = ctk.StringVar()

        # Frame principal com scroll
        self.main_scroll = ctk.CTkScrollableFrame(self.tab_widget, fg_color="transparent")
        self.main_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Grid configuration para o frame principal
        self.main_scroll.columnconfigure(0, weight=1)
        self.main_scroll.columnconfigure(1, weight=1)

        # Seções da UI
        self.setup_combat_overview_section()  # Nova seção com visão geral do combate
        self.setup_equipped_weapons_slots_section()  # Movido para cima por ser mais importante
        self.setup_armor_shield_section()  # Mantido como estava

        self.load_data_from_personagem()

    def load_data_from_personagem(self) -> None:
        """Carrega dados do objeto Personagem para a UI da aba de Combate."""
        self.rd_total_var.set(str(self.personagem.rd_total))
        self.esquiva_val_var.set(str(self.personagem.pericias_valores.get("Esquiva", 0)))
        self.bloqueio_val_var.set(str(self.personagem.pericias_valores.get("Bloqueio", 0)))
        self.iniciativa_val_var.set(str(self.personagem.pericias_valores.get("Iniciativa", 0)))
        self.cac_val_var.set(str(self.personagem.pericias_valores.get("Corpo-a-Corpo", 0)))
        self.pontaria_val_var.set(str(self.personagem.pericias_valores.get("Pontaria", 0)))
        self.elemental_val_var.set(str(self.personagem.pericias_valores.get("Elemental", 0)))

        self.armor_name_var.set(self.personagem.armadura_equipada.get("nome", ""))
        self.armor_rd_var.set(str(self.personagem.armadura_equipada.get("rd_fornecida", "0")))
        self.shield_name_var.set(self.personagem.escudo_equipado.get("nome", ""))
        self.shield_notes_var.set(self.personagem.escudo_equipado.get("notas", ""))

        # Atualiza display das armas equipadas
        self._update_equipped_weapon_display("main", self.personagem.arma_equipada_principal)
        self._update_equipped_weapon_display("off", self.personagem.arma_equipada_secundaria)

    def _update_personagem_skill_value_from_combat_tab(self, skill_name: str, string_var: ctk.StringVar) -> None:
        """Atualiza o valor de uma perícia no objeto Personagem a partir desta aba."""
        val_str = string_var.get()
        new_value: int
        try:
            new_value = int(val_str) if val_str.strip() else 0
        except ValueError:
            # Reverte para o valor atual no modelo se a entrada for inválida
            string_var.set(str(self.personagem.pericias_valores.get(skill_name, 0)))
            return
        
        if self.personagem.pericias_valores.get(skill_name) != new_value:
            self.personagem.atualizar_pericia_valor(skill_name, new_value)
            # Se esta atualização afetar outras partes da UI (e.g., CombatTab), AppUI.atualizar_ui_completa
            # ou um sistema de notificação mais granular seria necessário.

    def _update_personagem_combat_attr(self, attr_keys: Tuple[str, ...], string_var: ctk.StringVar, is_int: bool = False) -> None:
        """Atualiza um atributo de combate no objeto Personagem."""
        value_str = string_var.get()
        value_to_set: Union[str, int] = value_str
        
        obj_ref = self.personagem
        current_model_value: Any = None
        try:
            temp_obj = obj_ref
            for key in attr_keys[:-1]:
                temp_obj = getattr(temp_obj, key) if not isinstance(temp_obj, dict) else temp_obj[key]
            current_model_value = temp_obj[attr_keys[-1]] if isinstance(temp_obj, dict) else getattr(temp_obj, attr_keys[-1])
        except (AttributeError, KeyError):
             pass # Valor antigo não encontrado, prossegue com a atualização

        if is_int:
            try:
                value_to_set = int(value_str) if value_str.strip() else 0
            except ValueError:
                string_var.set(str(current_model_value if current_model_value is not None else (0 if is_int else "")))
                return
        
        if str(current_model_value) != str(value_to_set): # Compara como string para lidar com tipos mistos na UI
            try:
                for key in attr_keys[:-1]:
                    obj_ref = getattr(obj_ref, key) if not isinstance(obj_ref, dict) else obj_ref[key] # Correção obj_val -> obj_ref
                
                if isinstance(obj_ref, dict):
                    obj_ref[attr_keys[-1]] = value_to_set
                else:
                    setattr(obj_ref, attr_keys[-1], value_to_set)
            except Exception as e:
                print(f"Erro ao atualizar {'.'.join(attr_keys)}: {e}") # Log para debug
                # Reverter na UI
                string_var.set(str(current_model_value if current_model_value is not None else (0 if is_int else "")))


    def create_linked_entry(self, parent: ctk.CTkFrame, row: int, col: int, label_text: str,
                              string_var: ctk.StringVar,
                              attr_keys_in_personagem: Optional[Tuple[str, ...]] = None,
                              skill_name_in_personagem: Optional[str] = None,
                              is_int: bool = False, placeholder: str = "0", width: int = 80,
                              label_sticky: str = "w", entry_sticky: str = "ew") -> ctk.CTkEntry:
        """Cria um Label e um Entry vinculados a uma StringVar e a um atributo/perícia do personagem."""
        label = ctk.CTkLabel(master=parent, text=label_text)
        label.grid(row=row, column=col, padx=5, pady=2, sticky=label_sticky)
        entry = ctk.CTkEntry(master=parent, placeholder_text=placeholder, width=width, textvariable=string_var)
        entry.grid(row=row, column=col + 1, padx=5, pady=2, sticky=entry_sticky)
        
        if skill_name_in_personagem:
            string_var.trace_add("write", lambda n,i,m, sk=skill_name_in_personagem, sv=string_var: self._update_personagem_skill_value_from_combat_tab(sk, sv))
        elif attr_keys_in_personagem:
            string_var.trace_add("write", lambda n,i,m, ap=attr_keys_in_personagem, sv=string_var, is_i=is_int: self._update_personagem_combat_attr(ap, sv, is_i))
        return entry

    # --- Setup das Seções da UI ---
    def setup_combat_overview_section(self) -> None:
        """Configura a seção de visão geral do combate com informações principais."""
        overview_frame = ctk.CTkFrame(self.main_scroll)
        overview_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        
        # Título da seção
        title_frame = ctk.CTkFrame(overview_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=5, pady=(5,0))
        ctk.CTkLabel(title_frame, text="Visão Geral do Combate", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
        
        # Container para os valores principais
        values_frame = ctk.CTkFrame(overview_frame, fg_color="transparent")
        values_frame.pack(fill="x", padx=10, pady=5)
        
        # Primeira linha - Valores principais
        main_values_frame = ctk.CTkFrame(values_frame, fg_color="transparent")
        main_values_frame.pack(fill="x", pady=(0,5))
        
        # RD Total com ícone/símbolo
        rd_frame = ctk.CTkFrame(main_values_frame, fg_color="#2B2B2B")
        rd_frame.pack(side="left", padx=5, fill="both")
        ctk.CTkLabel(rd_frame, text="🛡️", font=ctk.CTkFont(size=20)).pack(side="left", padx=5)
        ctk.CTkLabel(rd_frame, text="RD Total", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=2)
        rd_entry = ctk.CTkEntry(rd_frame, textvariable=self.rd_total_var, width=50, justify="center")
        rd_entry.pack(side="left", padx=5, pady=5)
        
        # Esquiva com ícone
        dodge_frame = ctk.CTkFrame(main_values_frame, fg_color="#2B2B2B")
        dodge_frame.pack(side="left", padx=5, fill="both")
        ctk.CTkLabel(dodge_frame, text="💨", font=ctk.CTkFont(size=20)).pack(side="left", padx=5)
        ctk.CTkLabel(dodge_frame, text="Esquiva", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=2)
        dodge_entry = ctk.CTkEntry(dodge_frame, textvariable=self.esquiva_val_var, width=50, justify="center",
                                 state="readonly", fg_color="#1a1a1a")
        dodge_entry.pack(side="left", padx=5, pady=5)
        
        # Bloqueio com ícone
        block_frame = ctk.CTkFrame(main_values_frame, fg_color="#2B2B2B")
        block_frame.pack(side="left", padx=5, fill="both")
        ctk.CTkLabel(block_frame, text="🛡️", font=ctk.CTkFont(size=20)).pack(side="left", padx=5)
        ctk.CTkLabel(block_frame, text="Bloqueio", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=2)
        block_entry = ctk.CTkEntry(block_frame, textvariable=self.bloqueio_val_var, width=50, justify="center",
                                 state="readonly", fg_color="#1a1a1a")
        block_entry.pack(side="left", padx=5, pady=5)
        
        # Iniciativa com ícone
        init_frame = ctk.CTkFrame(main_values_frame, fg_color="#2B2B2B")
        init_frame.pack(side="left", padx=5, fill="both")
        ctk.CTkLabel(init_frame, text="⚡", font=ctk.CTkFont(size=20)).pack(side="left", padx=5)
        ctk.CTkLabel(init_frame, text="Iniciativa", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=2)
        init_entry = ctk.CTkEntry(init_frame, textvariable=self.iniciativa_val_var, width=50, justify="center",
                                state="readonly", fg_color="#1a1a1a")
        init_entry.pack(side="left", padx=5, pady=5)

        # Segunda linha - Perícias de Ataque
        attack_skills_frame = ctk.CTkFrame(values_frame, fg_color="transparent")
        attack_skills_frame.pack(fill="x", pady=5)
        
        # Corpo a Corpo com ícone
        melee_frame = ctk.CTkFrame(attack_skills_frame, fg_color="#2B2B2B")
        melee_frame.pack(side="left", padx=5, fill="both", expand=True)
        ctk.CTkLabel(melee_frame, text="⚔️", font=ctk.CTkFont(size=20)).pack(side="left", padx=5)
        ctk.CTkLabel(melee_frame, text="Corpo-a-Corpo", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=2)
        melee_entry = ctk.CTkEntry(melee_frame, textvariable=self.cac_val_var, width=50, justify="center",
                                 state="readonly", fg_color="#1a1a1a")
        melee_entry.pack(side="right", padx=5, pady=5)
        
        # Pontaria com ícone
        ranged_frame = ctk.CTkFrame(attack_skills_frame, fg_color="#2B2B2B")
        ranged_frame.pack(side="left", padx=5, fill="both", expand=True)
        ctk.CTkLabel(ranged_frame, text="🎯", font=ctk.CTkFont(size=20)).pack(side="left", padx=5)
        ctk.CTkLabel(ranged_frame, text="Pontaria", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=2)
        ranged_entry = ctk.CTkEntry(ranged_frame, textvariable=self.pontaria_val_var, width=50, justify="center",
                                  state="readonly", fg_color="#1a1a1a")
        ranged_entry.pack(side="right", padx=5, pady=5)
        
        # Elemental com ícone
        magic_frame = ctk.CTkFrame(attack_skills_frame, fg_color="#2B2B2B")
        magic_frame.pack(side="left", padx=5, fill="both", expand=True)
        ctk.CTkLabel(magic_frame, text="✨", font=ctk.CTkFont(size=20)).pack(side="left", padx=5)
        ctk.CTkLabel(magic_frame, text="Elemental", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=2)
        magic_entry = ctk.CTkEntry(magic_frame, textvariable=self.elemental_val_var, width=50, justify="center",
                                 state="readonly", fg_color="#1a1a1a")
        magic_entry.pack(side="right", padx=5, pady=5)

    def setup_equipped_weapons_slots_section(self) -> None:
        """Configura a seção de armas equipadas."""
        equipped_frame = ctk.CTkFrame(self.main_scroll)
        equipped_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        
        # Título da seção
        title_frame = ctk.CTkFrame(equipped_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=5, pady=(5,0))
        ctk.CTkLabel(title_frame, text="⚔️ Armas Equipadas", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
        
        # Container para as armas
        weapons_frame = ctk.CTkFrame(equipped_frame, fg_color="transparent")
        weapons_frame.pack(fill="x", padx=10, pady=5)
        
        # Mão Principal
        main_hand_frame = ctk.CTkFrame(weapons_frame, fg_color="#2B2B2B")
        main_hand_frame.pack(fill="x", pady=(0,5))
        
        # Cabeçalho da mão principal
        mh_header = ctk.CTkFrame(main_hand_frame, fg_color="transparent")
        mh_header.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(mh_header, text="🗡️", font=ctk.CTkFont(size=20)).pack(side="left", padx=2)
        ctk.CTkLabel(mh_header, text="Mão Principal", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        
        # Informações da arma principal
        mh_info = ctk.CTkFrame(main_hand_frame, fg_color="transparent")
        mh_info.pack(fill="x", padx=5, pady=2)
        self.mh_name_label = ctk.CTkLabel(mh_info, text="---", anchor="w")
        self.mh_name_label.pack(side="left", padx=5, fill="x", expand=True)
        self.mh_damage_label = ctk.CTkLabel(mh_info, text="Dano: ---", anchor="w", width=120)
        self.mh_damage_label.pack(side="left", padx=5)
        
        # Botões e modificadores da mão principal
        mh_buttons = ctk.CTkFrame(main_hand_frame, fg_color="transparent")
        mh_buttons.pack(fill="x", padx=5, pady=2)
        
        # Frame para modificadores
        mh_mods = ctk.CTkFrame(mh_buttons, fg_color="transparent")
        mh_mods.pack(side="left", fill="x", expand=True)
        
        # Modificador de Ataque
        ctk.CTkLabel(mh_mods, text="Mod. Ataque:").pack(side="left", padx=2)
        self.mh_attack_mod_entry = ctk.CTkEntry(mh_mods, placeholder_text="+0", width=45)
        self.mh_attack_mod_entry.pack(side="left", padx=2)
        
        # Modificador de Dano
        ctk.CTkLabel(mh_mods, text="Mod. Dano:").pack(side="left", padx=2)
        self.mh_damage_mod_entry = ctk.CTkEntry(mh_mods, placeholder_text="+0", width=45)
        self.mh_damage_mod_entry.pack(side="left", padx=2)
        
        # Frame para botões de ação
        mh_actions = ctk.CTkFrame(mh_buttons, fg_color="transparent")
        mh_actions.pack(side="right")
        
        self.mh_roll_damage_button = ctk.CTkButton(mh_actions, text="🎲 Dano", width=80, state="disabled",
                                                  command=lambda: self.roll_equipped_weapon_damage("main"))
        self.mh_roll_damage_button.pack(side="right", padx=2)
        self.mh_roll_attack_button = ctk.CTkButton(mh_actions, text="🎯 Ataque", width=80, state="disabled",
                                                  command=lambda: self.perform_attack_roll("main"))
        self.mh_roll_attack_button.pack(side="right", padx=2)
        self.mh_unequip_button = ctk.CTkButton(mh_actions, text="❌ Desequipar", width=80, state="disabled",
                                              command=lambda: self.unequip_weapon("main"))
        self.mh_unequip_button.pack(side="right", padx=2)

        # Mão Secundária
        off_hand_frame = ctk.CTkFrame(weapons_frame, fg_color="#2B2B2B")
        off_hand_frame.pack(fill="x", pady=5)
        
        # Cabeçalho da mão secundária
        oh_header = ctk.CTkFrame(off_hand_frame, fg_color="transparent")
        oh_header.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(oh_header, text="🗡️", font=ctk.CTkFont(size=20)).pack(side="left", padx=2)
        ctk.CTkLabel(oh_header, text="Mão Secundária", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        
        # Informações da arma secundária
        oh_info = ctk.CTkFrame(off_hand_frame, fg_color="transparent")
        oh_info.pack(fill="x", padx=5, pady=2)
        self.oh_name_label = ctk.CTkLabel(oh_info, text="---", anchor="w")
        self.oh_name_label.pack(side="left", padx=5, fill="x", expand=True)
        self.oh_damage_label = ctk.CTkLabel(oh_info, text="Dano: ---", anchor="w", width=120)
        self.oh_damage_label.pack(side="left", padx=5)
        
        # Botões e modificadores da mão secundária
        oh_buttons = ctk.CTkFrame(off_hand_frame, fg_color="transparent")
        oh_buttons.pack(fill="x", padx=5, pady=2)
        
        # Frame para modificadores
        oh_mods = ctk.CTkFrame(oh_buttons, fg_color="transparent")
        oh_mods.pack(side="left", fill="x", expand=True)
        
        # Modificador de Ataque
        ctk.CTkLabel(oh_mods, text="Mod. Ataque:").pack(side="left", padx=2)
        self.oh_attack_mod_entry = ctk.CTkEntry(oh_mods, placeholder_text="+0", width=45)
        self.oh_attack_mod_entry.pack(side="left", padx=2)
        
        # Modificador de Dano
        ctk.CTkLabel(oh_mods, text="Mod. Dano:").pack(side="left", padx=2)
        self.oh_damage_mod_entry = ctk.CTkEntry(oh_mods, placeholder_text="+0", width=45)
        self.oh_damage_mod_entry.pack(side="left", padx=2)
        
        # Frame para botões de ação
        oh_actions = ctk.CTkFrame(oh_buttons, fg_color="transparent")
        oh_actions.pack(side="right")
        
        self.oh_roll_damage_button = ctk.CTkButton(oh_actions, text="🎲 Dano", width=80, state="disabled",
                                                  command=lambda: self.roll_equipped_weapon_damage("off"))
        self.oh_roll_damage_button.pack(side="right", padx=2)
        self.oh_roll_attack_button = ctk.CTkButton(oh_actions, text="🎯 Ataque", width=80, state="disabled",
                                                  command=lambda: self.perform_attack_roll("off"))
        self.oh_roll_attack_button.pack(side="right", padx=2)
        self.oh_unequip_button = ctk.CTkButton(oh_actions, text="❌ Desequipar", width=80, state="disabled",
                                              command=lambda: self.unequip_weapon("off"))
        self.oh_unequip_button.pack(side="right", padx=2)

        # Área de resultado de rolagem
        roll_result_frame = ctk.CTkFrame(weapons_frame, fg_color="#2B2B2B")
        roll_result_frame.pack(fill="x", pady=(10,0))
        ctk.CTkLabel(roll_result_frame, text="🎲", font=ctk.CTkFont(size=20)).pack(side="left", padx=5)
        ctk.CTkLabel(roll_result_frame, text="Resultado", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        self.action_roll_animation_label = ctk.CTkLabel(roll_result_frame, text="", width=100,
                                                       font=ctk.CTkFont(size=20, weight="bold"))
        self.action_roll_animation_label.pack(side="left", padx=5)
        self.action_roll_result_label = ctk.CTkLabel(roll_result_frame, text="", anchor="w", wraplength=440)
        self.action_roll_result_label.pack(side="left", fill="x", expand=True, padx=5)

    def setup_armor_shield_section(self) -> None:
        """Configura a seção de equipamento defensivo."""
        armor_shield_frame = ctk.CTkFrame(self.main_scroll)
        armor_shield_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        
        # Título da seção
        title_frame = ctk.CTkFrame(armor_shield_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=5, pady=(5,0))
        ctk.CTkLabel(title_frame, text="🛡️ Equipamento Defensivo", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
        
        # Container para os equipamentos
        equip_frame = ctk.CTkFrame(armor_shield_frame, fg_color="transparent")
        equip_frame.pack(fill="x", padx=10, pady=5)
        
        # Armadura
        armor_frame = ctk.CTkFrame(equip_frame, fg_color="#2B2B2B")
        armor_frame.pack(fill="x", pady=(0,5))
        ctk.CTkLabel(armor_frame, text="🛡️", font=ctk.CTkFont(size=20)).pack(side="left", padx=5)
        ctk.CTkLabel(armor_frame, text="Armadura:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=2)
        armor_entry = ctk.CTkEntry(armor_frame, textvariable=self.armor_name_var, placeholder_text="Nome da Armadura")
        armor_entry.pack(side="left", padx=5, pady=5, fill="x", expand=True)
        ctk.CTkLabel(armor_frame, text="RD:").pack(side="left", padx=2)
        rd_entry = ctk.CTkEntry(armor_frame, textvariable=self.armor_rd_var, width=50, justify="center")
        rd_entry.pack(side="left", padx=5, pady=5)
        
        # Escudo
        shield_frame = ctk.CTkFrame(equip_frame, fg_color="#2B2B2B")
        shield_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(shield_frame, text="🛡️", font=ctk.CTkFont(size=20)).pack(side="left", padx=5)
        ctk.CTkLabel(shield_frame, text="Escudo:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=2)
        shield_entry = ctk.CTkEntry(shield_frame, textvariable=self.shield_name_var, placeholder_text="Nome do Escudo")
        shield_entry.pack(side="left", padx=5, pady=5, fill="x", expand=True)
        ctk.CTkLabel(shield_frame, text="Notas:").pack(side="left", padx=2)
        notes_entry = ctk.CTkEntry(shield_frame, textvariable=self.shield_notes_var, placeholder_text="Notas do Escudo")
        notes_entry.pack(side="left", padx=5, pady=5, fill="x", expand=True)

    def _update_equipped_weapon_display(self, hand_slot: Literal["main", "off"], weapon_data_dict: Optional[Dict[str, Any]]) -> None:
        """Atualiza os labels e botões na UI para uma arma equipada."""
        name_label = self.mh_name_label if hand_slot == "main" else self.oh_name_label
        damage_label = self.mh_damage_label if hand_slot == "main" else self.oh_damage_label
        attack_button = self.mh_roll_attack_button if hand_slot == "main" else self.oh_roll_attack_button
        damage_button = self.mh_roll_damage_button if hand_slot == "main" else self.oh_roll_damage_button
        unequip_button = self.mh_unequip_button if hand_slot == "main" else self.oh_unequip_button
        
        if weapon_data_dict:
            name_label.configure(text=str(weapon_data_dict.get(WEAPON_KEY_NAME, "N/A")))
            damage_label.configure(text=f"Dano: {weapon_data_dict.get(WEAPON_KEY_DAMAGE, 'N/A')}")
            attack_button.configure(state="normal")
            damage_button.configure(state="normal")
            unequip_button.configure(state="normal")
            
            # Se a arma principal é de 2 mãos, desabilita slot secundário
            if hand_slot == "main" and str(weapon_data_dict.get(WEAPON_KEY_HANDS, "1 Mão")) == "2 Mãos":
                self.oh_name_label.configure(text="[Mão Sec. Bloqueada]")
                self.oh_damage_label.configure(text="Dano: ---")
                self.oh_roll_attack_button.configure(state="disabled")
                self.oh_roll_damage_button.configure(state="disabled")
                self.oh_unequip_button.configure(state="disabled")
            # Se a arma secundária está sendo atualizada, mas a principal é 2-mãos (não deveria acontecer se equipar está certo)
            elif hand_slot == "off" and self.personagem.arma_equipada_principal and \
                 str(self.personagem.arma_equipada_principal.get(WEAPON_KEY_HANDS, "1 Mão")) == "2 Mãos":
                name_label.configure(text="---")
                damage_label.configure(text="Dano: ---")
                attack_button.configure(state="disabled")
                damage_button.configure(state="disabled")
                unequip_button.configure(state="disabled")
        else:
            name_label.configure(text="---")
            damage_label.configure(text="Dano: ---")
            attack_button.configure(state="disabled")
            damage_button.configure(state="disabled")
            unequip_button.configure(state="disabled")
            # Se a mão principal foi desequipada e era de 2 mãos, reabilita a secundária (se não houver nada lá)
            if hand_slot == "main" and self.personagem.arma_equipada_secundaria is None:
                # Garante que os botões da OH voltem ao estado "disabled" se vazia
                if self.oh_roll_attack_button: self.oh_roll_attack_button.configure(state="disabled")
                if self.oh_roll_damage_button: self.oh_roll_damage_button.configure(state="disabled")
                if self.oh_unequip_button: self.oh_unequip_button.configure(state="disabled")

    def equip_weapon(self, weapon_data_dict: Dict[str, Any]) -> None:
        """Equipa uma arma do inventário."""
        weapon_hands = str(weapon_data_dict.get(WEAPON_KEY_HANDS, "1 Mão")) # Usar chave padronizada

        if weapon_hands == "2 Mãos": #
            # Se a arma principal atual for a que estamos tentando equipar (já é de 2 mãos), não faz nada
            if self.personagem.arma_equipada_principal is weapon_data_dict:
                self.app_ui.show_feedback_message(f"'{weapon_data_dict.get(WEAPON_KEY_NAME)}' já está equipada.", 2000)
                return

            self.unequip_weapon("main", update_buttons=False)
            self.unequip_weapon("off", update_buttons=False)
            self.personagem.arma_equipada_principal = weapon_data_dict
            self.personagem.arma_equipada_secundaria = None # Arma de 2 mãos ocupa ambos os slots implicitamente
        else: # Arma de 1 Mão
            if self.personagem.arma_equipada_principal is None:
                self.personagem.arma_equipada_principal = weapon_data_dict
            elif self.personagem.arma_equipada_secundaria is None and self.personagem.arma_equipada_principal is not weapon_data_dict:
                 # Verifica se a principal é de 2 mãos, não deveria permitir equipar na secundária
                if self.personagem.arma_equipada_principal and str(self.personagem.arma_equipada_principal.get(WEAPON_KEY_HANDS,"1 Mão")) == "2 Mãos":
                    self.app_ui.show_feedback_message("Mão principal ocupada por arma de 2 mãos.", 2500)
                    return
                self.personagem.arma_equipada_secundaria = weapon_data_dict
            elif self.personagem.arma_equipada_principal is weapon_data_dict or self.personagem.arma_equipada_secundaria is weapon_data_dict:
                self.app_ui.show_feedback_message(f"'{weapon_data_dict.get(WEAPON_KEY_NAME)}' já está equipada.", 2000)
                return # Já está equipada em um dos slots
            else:
                self.app_ui.show_feedback_message("Ambos os slots de arma estão ocupados.", 2500)
                return

        self._update_equipped_weapon_display("main", self.personagem.arma_equipada_principal)
        self._update_equipped_weapon_display("off", self.personagem.arma_equipada_secundaria)

    def unequip_weapon(self, hand_slot: Literal["main", "off"], update_buttons: bool = True) -> None:
        """Desequipa uma arma do slot especificado."""
        unequipped_weapon_name: Optional[str] = None
        
        if hand_slot == "main" and self.personagem.arma_equipada_principal:
            unequipped_weapon_name = self.personagem.arma_equipada_principal.get(WEAPON_KEY_NAME)
            # Se a arma principal era de 2 mãos, também limpa a secundária (que já deveria ser None)
            if str(self.personagem.arma_equipada_principal.get(WEAPON_KEY_HANDS, "1 Mão")) == "2 Mãos":
                self.personagem.arma_equipada_secundaria = None
            self.personagem.arma_equipada_principal = None
        elif hand_slot == "off" and self.personagem.arma_equipada_secundaria:
            unequipped_weapon_name = self.personagem.arma_equipada_secundaria.get(WEAPON_KEY_NAME)
            self.personagem.arma_equipada_secundaria = None
        
        if unequipped_weapon_name:
             self.app_ui.show_feedback_message(f"'{unequipped_weapon_name}' desequipada.", 1500)

        self._update_equipped_weapon_display("main", self.personagem.arma_equipada_principal)
        self._update_equipped_weapon_display("off", self.personagem.arma_equipada_secundaria)
        
        if update_buttons:
            self.update_all_inventory_equip_button_states()

    def update_all_inventory_equip_button_states(self) -> None:
        """Atualiza o texto e estado dos botões 'Equipar/Desequipar' no inventário de armas."""
        for weapon_ui_el_dict in self.weapon_inventory_ui_rows:
            button = weapon_ui_el_dict.get('equip_button')
            weapon_data_ref = weapon_ui_el_dict.get('data_dict_ref')
            if not isinstance(button, ctk.CTkButton) or not weapon_data_ref:
                continue

            is_equipped_main = (self.personagem.arma_equipada_principal is weapon_data_ref)
            is_equipped_off = (self.personagem.arma_equipada_secundaria is weapon_data_ref)
            
            can_equip_this_item = True
            # Arma principal é de 2 mãos e este item (weapon_data_ref) não é ela?
            main_is_two_handed = (self.personagem.arma_equipada_principal and
                                  str(self.personagem.arma_equipada_principal.get(WEAPON_KEY_HANDS, "1 Mão")) == "2 Mãos" and
                                  self.personagem.arma_equipada_principal is not weapon_data_ref)

            if is_equipped_main or is_equipped_off:
                button.configure(text="Desequip.", command=lambda wd_ref=weapon_data_ref: self.perform_unequip_action_from_data(wd_ref))
                button.configure(state="normal") # Sempre pode desequipar
            else: # Se não está equipada
                button.configure(text="Equipar", command=lambda w_data=weapon_data_ref: self.equip_weapon(w_data))
                if main_is_two_handed: # Não pode equipar nada se a principal já é 2 mãos
                    can_equip_this_item = False
                elif str(weapon_data_ref.get(WEAPON_KEY_HANDS, "1 Mão")) == "2 Mãos":
                    # Tentando equipar item de 2 mãos: ambos os slots devem estar livres
                    if self.personagem.arma_equipada_principal is not None or self.personagem.arma_equipada_secundaria is not None:
                        can_equip_this_item = False
                elif self.personagem.arma_equipada_principal is not None and self.personagem.arma_equipada_secundaria is not None:
                    # Ambos os slots de 1 mão ocupados, não pode equipar outra de 1 mão
                    can_equip_this_item = False
                button.configure(state="normal" if can_equip_this_item else "disabled")

    def perform_unequip_action_from_data(self, weapon_data_to_unequip: Dict[str, Any]) -> None:
        """Chamado pelo botão 'Desequipar' para desequipar a arma correspondente."""
        if self.personagem.arma_equipada_principal is weapon_data_to_unequip:
            self.unequip_weapon("main")
        elif self.personagem.arma_equipada_secundaria is weapon_data_to_unequip:
            self.unequip_weapon("off")
        # update_all_inventory_equip_button_states() é chamado dentro de unequip_weapon


    # --- Rolagem de Ações ---
    def _set_action_buttons_state(self, state: Literal["normal", "disabled"]) -> None:
        """Habilita ou desabilita todos os botões de ação (ataque/dano)."""
        buttons = [
            self.mh_roll_attack_button, self.mh_roll_damage_button,
            self.oh_roll_attack_button, self.oh_roll_damage_button
        ]
        for btn in buttons:
            if btn: # Verifica se o widget existe
                btn.configure(state=state)
    
    def re_enable_action_buttons(self) -> None:
        """Reabilita os botões de ação com base nas armas equipadas."""
        # Mão Principal
        if self.mh_roll_attack_button and self.mh_roll_damage_button:
            state_mh = "normal" if self.personagem.arma_equipada_principal else "disabled"
            self.mh_roll_attack_button.configure(state=state_mh)
            self.mh_roll_damage_button.configure(state=state_mh)

        # Mão Secundária
        state_oh = "disabled" # Padrão para OH
        if self.personagem.arma_equipada_secundaria:
            # Só habilita OH se MH não for 2-mãos
            if not (self.personagem.arma_equipada_principal and \
                    str(self.personagem.arma_equipada_principal.get(WEAPON_KEY_HANDS,"1 Mão")) == "2 Mãos"):
                state_oh = "normal"
        
        if self.oh_roll_attack_button and self.oh_roll_damage_button:
            self.oh_roll_attack_button.configure(state=state_oh)
            self.oh_roll_damage_button.configure(state=state_oh)


    def perform_attack_roll(self, hand_slot: Literal["main", "off"]) -> None:
        """Realiza uma rolagem de ataque para a arma equipada no slot especificado."""
        weapon_data = self.personagem.arma_equipada_principal if hand_slot == "main" else self.personagem.arma_equipada_secundaria
        attack_mod_entry = self.mh_attack_mod_entry if hand_slot == "main" else self.oh_attack_mod_entry
        
        if not weapon_data:
            self.action_roll_result_label.configure(text="Nenhuma arma equipada nesse slot.")
            return

        self._set_action_buttons_state("disabled") # Desabilita todos os botões de ação

        weapon_name = str(weapon_data.get(WEAPON_KEY_NAME, "N/A"))
        atk_attr_short = str(weapon_data.get(WEAPON_KEY_ATTR, "FOR")).strip().upper()
        attack_skill_name_selected = str(weapon_data.get(WEAPON_KEY_SKILL_TYPE, "Corpo-a-Corpo"))
        
        char_attr_name_full = ATTRIBUTE_NAME_MAP.get(atk_attr_short, "Força") # Default para Força
        
        try:
            # Obtém o valor do atributo
            attribute_value = self.personagem.atributos.get(char_attr_name_full, 0)
            
            # Obtém o valor da perícia
            skill_val_str = "0" # Padrão
            if attack_skill_name_selected == "Corpo-a-Corpo": skill_val_str = self.cac_val_var.get()
            elif attack_skill_name_selected == "Pontaria": skill_val_str = self.pontaria_val_var.get()
            elif attack_skill_name_selected == "Elemental": skill_val_str = self.elemental_val_var.get()
            
            skill_value_for_attack = int(skill_val_str.strip()) if skill_val_str.strip().lstrip('-').isdigit() else 0
            
            # Obtém o modificador de ataque
            attack_modifier = 0
            mod_str = attack_mod_entry.get().strip()
            if mod_str:
                try:
                    attack_modifier = int(mod_str)
                except ValueError:
                    attack_mod_entry.delete(0, "end")
                    attack_mod_entry.insert(0, "+0")
            
            # Aplica o modificador ao valor da perícia
            skill_value_for_attack += attack_modifier

        except Exception as e:
            self.action_roll_animation_label.configure(text="Erro")
            self.action_roll_result_label.configure(text=f"Erro ao obter dados para ataque: {e}")
            self.re_enable_action_buttons()
            return
            
        self.action_roll_animation_label.configure(text="")
        self.action_roll_result_label.configure(text=f"Rolando ataque ({attack_skill_name_selected}) com {weapon_name}...")
        self.animate_action_roll(0, "attack", attribute_value, skill_value_for_attack, weapon_name, hand_slot)


    def roll_equipped_weapon_damage(self, hand_slot: Literal["main", "off"], is_critical: bool = False) -> None:
        """
        Rola o dano para a arma equipada no slot especificado.
        
        Args:
            hand_slot: Qual mão está usando a arma ("main" ou "off")
            is_critical: Se True, aplica as regras de dano crítico
        """
        weapon_data: Optional[Dict[str, Any]] = None
        modifier_entry_widget: Optional[ctk.CTkEntry] = None

        if hand_slot == "main":
            weapon_data = self.personagem.arma_equipada_principal
            modifier_entry_widget = self.mh_damage_mod_entry
        elif hand_slot == "off":
            weapon_data = self.personagem.arma_equipada_secundaria
            modifier_entry_widget = self.oh_damage_mod_entry
        
        if not weapon_data or not modifier_entry_widget:
            self.action_roll_result_label.configure(text="Nenhuma arma para rolar dano ou widget de modificador ausente.")
            return

        self._set_action_buttons_state("disabled")

        weapon_name = str(weapon_data.get(WEAPON_KEY_NAME, "N/A"))
        damage_dice_str = str(weapon_data.get(WEAPON_KEY_DAMAGE, ""))
        weapon_attr = str(weapon_data.get(WEAPON_KEY_ATTR, "FOR")).strip().upper()
        
        # Calcula o modificador total
        total_modifier = 0
        
        # Modificador do atributo
        attr_name_full = ATTRIBUTE_NAME_MAP.get(weapon_attr, "Força")
        attr_value = self.personagem.atributos.get(attr_name_full, 0)
        if attr_value > 0:  # Só adiciona bônus se o atributo for positivo
            total_modifier += attr_value
        
        # Modificador da UI
        try:
            mod_str = modifier_entry_widget.get().strip()
            if mod_str:
                ui_modifier = int(mod_str)
                total_modifier += ui_modifier
        except ValueError:
            modifier_entry_widget.delete(0, "end")
            modifier_entry_widget.insert(0, "+0")
        
        # Se for crítico, dobra os dados de dano mas não os modificadores
        if is_critical:
            # Duplica os dados mantendo os modificadores
            # Exemplo: "2d6+2" vira "4d6+2"
            match = DAMAGE_STRING_PATTERN.match(damage_dice_str.strip())
            if match:
                num_dice_str, dice_type_str, base_mod_str, fixed_damage_str = match.groups()
                if fixed_damage_str is not None:  # É um número fixo
                    damage_dice_str = str(int(fixed_damage_str) * 2)  # Dobra o dano fixo
                elif dice_type_str is not None:  # Tem dados para rolar
                    num_dice = int(num_dice_str) if num_dice_str else 1
                    damage_dice_str = f"{num_dice * 2}d{dice_type_str}"
                    if base_mod_str:  # Mantém o modificador original
                        damage_dice_str += base_mod_str
            
        self.action_roll_animation_label.configure(text="")
        crit_text = " [CRÍTICO]" if is_critical else ""
        self.action_roll_result_label.configure(text=f"Rolando dano para {weapon_name}{crit_text}...")
        self.animate_action_roll(0, "damage", damage_dice_str, total_modifier, weapon_name, hand_slot)
            

    def animate_action_roll(self, step: int, roll_type: Literal["attack", "damage"],
                              value1: Union[int, str], value2: int, # value1 é attr_val para ataque, damage_str para dano
                              item_name_for_display: str, hand_slot_rolled: Literal["main", "off"]) -> None:
        """Anima e executa a rolagem de ataque ou dano."""
        animation_steps = 8
        animation_interval = 60
        if step < animation_steps:
            temp_roll_display = random.randint(1, 20 if roll_type == "attack" else 10)
            self.action_roll_animation_label.configure(text=str(temp_roll_display))
            # Passando todos os argumentos corretamente para a próxima chamada recursiva
            self.tab_widget.after(animation_interval, 
                                  lambda s=step + 1, rt=roll_type, v1=value1, v2=value2, item=item_name_for_display, hs=hand_slot_rolled:
                                  self.animate_action_roll(s, rt, v1, v2, item, hs))
        else:
            if roll_type == "attack":
                attribute_value = int(value1) # value1 é attribute_value para ataque
                skill_value = value2      # value2 é skill_value_for_attack
                
                final_d20, all_rolls = perform_attribute_test_roll(attribute_value)
                success_level = check_success(skill_value, final_d20, final_d20) # Usa final_d20 para check de crítico
                
                self.action_roll_animation_label.configure(text=str(final_d20))
                roll_details = f" (Rolagens: {all_rolls})" if len(all_rolls) > 1 else ""
                
                # Verifica se é um crítico (20 natural ou Sucesso Extremo)
                is_critical = (success_level == SUCCESS_EXTREME and final_d20 == 20)
                crit_msg = " 🎯 ACERTO CRÍTICO!" if is_critical else ""
                
                num_dice_attr, roll_type_attr_key = get_dice_for_attribute_test(attribute_value)
                roll_type_attr_text = ""
                if roll_type_attr_key == "advantage": roll_type_attr_text = " (Maior)"
                elif roll_type_attr_key == "disadvantage": roll_type_attr_text = " (Menor)"
                
                attr_dice_info = f"{num_dice_attr}d20{roll_type_attr_text}"
                
                weapon_dict_data = self.personagem.arma_equipada_principal if hand_slot_rolled == "main" else self.personagem.arma_equipada_secundaria
                attack_skill_name_used = str(weapon_dict_data.get(WEAPON_KEY_SKILL_TYPE,"N/A")) if weapon_dict_data else "N/A"
                
                # Formata o resultado com cores e ícones
                success_icons = {
                    SUCCESS_EXTREME: "⭐⭐",
                    SUCCESS_GOOD: "⭐",
                    SUCCESS_NORMAL: "✓",
                    FAILURE_NORMAL: "✗",
                    FAILURE_EXTREME: "✗✗"
                }
                
                result_icon = success_icons.get(success_level, "")
                
                result_text_lines = [
                    f"Ataque com {item_name_for_display} ({attack_skill_name_used}): {result_icon} {success_level}{crit_msg}",
                    f"  Atributo Base ({attribute_value}) -> {attr_dice_info}",
                    f"  Valor da Perícia ({attack_skill_name_used}): {skill_value}",
                    f"  d20 Usado: {final_d20}{roll_details}"
                ]
                self.action_roll_result_label.configure(text="\n".join(result_text_lines))
                
                # Se for crítico, rola o dano crítico automaticamente
                if is_critical:
                    self.tab_widget.after(1000, lambda: self.roll_equipped_weapon_damage(hand_slot_rolled, True))

            elif roll_type == "damage":
                damage_dice_str = str(value1) # value1 é damage_dice_str
                static_modifier = value2    # value2 é o modificador total
                
                rolls, total_base, final_total = parse_and_roll_damage_string(damage_dice_str, static_modifier)
                
                if rolls is None: # String de dano inválida
                    self.action_roll_animation_label.configure(text="Erro!")
                    self.action_roll_result_label.configure(text=f"String de dano '{damage_dice_str}' inválida.")
                else:
                    self.action_roll_animation_label.configure(text=str(final_total))
                    roll_details_str = f"Rolagens: {rolls}" if rolls else "Dano Fixo"
                    
                    # Calcula modificadores separados para exibição
                    # mod_from_dice_string é (total_base - sum_of_rolls)
                    # mod_from_entry é static_modifier (value2)
                    sum_of_actual_dice_rolls = sum(rolls) if rolls else 0
                    mod_from_dice_string = total_base - sum_of_actual_dice_rolls
                    
                    mod_details_list = []
                    if mod_from_dice_string != 0:
                        mod_details_list.append(f"Mod. da Arma: {mod_from_dice_string:+}")
                    if static_modifier != 0:
                        mod_details_list.append(f"Mod. Total: {static_modifier:+}")
                    
                    mod_details_str = " (" + ", ".join(mod_details_list) + ")" if mod_details_list else ""
                    
                    # Adiciona ícone de dano
                    damage_icon = "💥" if "CRÍTICO" in self.action_roll_result_label.cget("text") else "⚔️"
                    
                    self.action_roll_result_label.configure(
                        text=f"{damage_icon} Dano ({item_name_for_display}): {final_total}\n  {roll_details_str}{mod_details_str}"
                    )
            
            self.re_enable_action_buttons()