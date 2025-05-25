import customtkinter as ctk
import random # Mantido para animação de dados
from typing import List, Dict, Any, Optional, Tuple, Literal

from core.dice_roller import (
    roll_generic_dice,
    parse_and_roll_damage_string,
    perform_attribute_test_roll,
    check_success,
    get_dice_for_attribute_test,
    SUCCESS_EXTREME # Para checagem de crítico
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


    def __init__(self, tab_widget: ctk.CTkFrame, attributes_skills_tab_ref: Any, personagem_atual: Any, app_ui_ref: Any): # Adicionado app_ui_ref
        self.tab_widget = tab_widget
        self.attributes_skills_tab_ref = attributes_skills_tab_ref # Usado para acessar personagem.atributos
        self.personagem = personagem_atual
        self.app_ui = app_ui_ref # Para show_feedback_message e potencialmente outras interações

        self.weapon_inventory_ui_rows = []

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

        self.main_frame = ctk.CTkFrame(self.tab_widget, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.main_frame.columnconfigure(0, weight=1); self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=0); self.main_frame.rowconfigure(1, weight=0)
        self.main_frame.rowconfigure(2, weight=0); self.main_frame.rowconfigure(3, weight=1) # Frame das armas ocupa espaço

        self.setup_defense_stats_section()
        self.setup_attack_skills_section()
        self.setup_armor_shield_section()
        self.setup_equipped_weapons_slots_section()
        self.setup_weapons_list_section()

        self.load_data_from_personagem()

    def load_data_from_personagem(self) -> None:
        """Carrega dados do objeto Personagem para a UI da aba de Combate."""
        self.rd_total_var.set(str(self.personagem.rd_total))
        self.esquiva_val_var.set(str(self.personagem.pericias_valores.get("Esquiva", "0")))
        self.bloqueio_val_var.set(str(self.personagem.pericias_valores.get("Bloqueio", "0")))
        self.iniciativa_val_var.set(str(self.personagem.pericias_valores.get("Iniciativa", "0")))
        self.cac_val_var.set(str(self.personagem.pericias_valores.get("Corpo-a-Corpo", "0")))
        self.pontaria_val_var.set(str(self.personagem.pericias_valores.get("Pontaria", "0")))
        self.elemental_val_var.set(str(self.personagem.pericias_valores.get("Elemental", "0")))

        self.armor_name_var.set(self.personagem.armadura_equipada.get("nome", ""))
        self.armor_rd_var.set(str(self.personagem.armadura_equipada.get("rd_fornecida", "0")))
        self.shield_name_var.set(self.personagem.escudo_equipado.get("nome", ""))
        self.shield_notes_var.set(self.personagem.escudo_equipado.get("notas", ""))

        # Limpa e recarrega inventário de armas
        for row_ui_elements in self.weapon_inventory_ui_rows:
            if row_ui_elements.get('frame'):
                row_ui_elements['frame'].destroy()
        self.weapon_inventory_ui_rows.clear()
        self.weapon_current_row_idx = 1 # Resetar o índice da linha para o scrollframe

        if hasattr(self.personagem, 'armas_inventario'):
            for weapon_data_from_inventory in self.personagem.armas_inventario:
                # As chaves em weapon_data_from_inventory devem ser consistentes com WEAPON_KEY_*
                # Se items_data.py usa 'nome', 'dano', etc., então personagem.armas_inventario deve ter essas chaves.
                self.add_weapon_entry_row(**weapon_data_from_inventory, is_loading=True)

        # Garante que as referências de armas equipadas apontem para os dicionários corretos no inventário
        if self.personagem.arma_equipada_principal:
            nome_arma_principal = self.personagem.arma_equipada_principal.get(WEAPON_KEY_NAME)
            found_main = next((w for w in self.personagem.armas_inventario if w.get(WEAPON_KEY_NAME) == nome_arma_principal), None)
            self.personagem.arma_equipada_principal = found_main # Pode ser None se não encontrada (deve ser raro)
        
        if self.personagem.arma_equipada_secundaria:
            nome_arma_secundaria = self.personagem.arma_equipada_secundaria.get(WEAPON_KEY_NAME)
            found_off = next((w for w in self.personagem.armas_inventario if w.get(WEAPON_KEY_NAME) == nome_arma_secundaria), None)
            self.personagem.arma_equipada_secundaria = found_off

        self._update_equipped_weapon_display("main", self.personagem.arma_equipada_principal)
        self._update_equipped_weapon_display("off", self.personagem.arma_equipada_secundaria)
        self.update_all_inventory_equip_button_states()

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
    def setup_defense_stats_section(self) -> None:
        defense_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        defense_frame.grid(row=0, column=0, padx=5, pady=(0, 5), sticky="new")
        defense_frame.columnconfigure(1, weight=1)
        ctk.CTkLabel(master=defense_frame, text="Defesa", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, columnspan=2, padx=5, pady=(0, 5), sticky="n")
        self.create_linked_entry(defense_frame, 1, 0, "RD Total:", self.rd_total_var, attr_keys_in_personagem=('rd_total',), is_int=True)
        self.create_linked_entry(defense_frame, 2, 0, "Esquiva (Valor):", self.esquiva_val_var, skill_name_in_personagem="Esquiva")
        self.create_linked_entry(defense_frame, 3, 0, "Bloqueio (Valor):", self.bloqueio_val_var, skill_name_in_personagem="Bloqueio")

    def setup_attack_skills_section(self) -> None:
        attack_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        attack_frame.grid(row=0, column=1, padx=5, pady=(0, 5), sticky="new")
        attack_frame.columnconfigure(1, weight=1)
        ctk.CTkLabel(master=attack_frame, text="Perícias de Ataque Base", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, columnspan=2, padx=5, pady=(0, 5), sticky="n")
        self.create_linked_entry(attack_frame, 1, 0, "Iniciativa (Valor):", self.iniciativa_val_var, skill_name_in_personagem="Iniciativa")
        self.create_linked_entry(attack_frame, 2, 0, "Corpo-a-Corpo (Valor):", self.cac_val_var, skill_name_in_personagem="Corpo-a-Corpo", placeholder="Valor")
        self.create_linked_entry(attack_frame, 3, 0, "Pontaria (Valor):", self.pontaria_val_var, skill_name_in_personagem="Pontaria", placeholder="Valor")
        self.create_linked_entry(attack_frame, 4, 0, "Elemental (Valor):", self.elemental_val_var, skill_name_in_personagem="Elemental", placeholder="Valor")

    def setup_armor_shield_section(self) -> None:
        armor_shield_frame = ctk.CTkFrame(self.main_frame)
        armor_shield_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="new")
        armor_shield_frame.columnconfigure(1, weight=1); armor_shield_frame.columnconfigure(3, weight=1)
        ctk.CTkLabel(master=armor_shield_frame, text="Equipamento Defensivo", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, columnspan=4, padx=5, pady=(0, 5), sticky="n")
        self.create_linked_entry(armor_shield_frame, 1, 0, "Armadura:", self.armor_name_var, attr_keys_in_personagem=('armadura_equipada', 'nome'), placeholder="Nome")
        self.create_linked_entry(armor_shield_frame, 1, 2, "RD:", self.armor_rd_var, attr_keys_in_personagem=('armadura_equipada', 'rd_fornecida'), is_int=True, placeholder="RD", width=50, entry_sticky="w")
        self.create_linked_entry(armor_shield_frame, 2, 0, "Escudo:", self.shield_name_var, attr_keys_in_personagem=('escudo_equipado', 'nome'), placeholder="Nome")
        self.create_linked_entry(armor_shield_frame, 2, 2, "Notas:", self.shield_notes_var, attr_keys_in_personagem=('escudo_equipado', 'notas'), placeholder="Notas")

    def setup_equipped_weapons_slots_section(self) -> None:
        equipped_frame = ctk.CTkFrame(self.main_frame)
        equipped_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        equipped_frame.columnconfigure(1, weight=2); equipped_frame.columnconfigure(2, weight=1); equipped_frame.columnconfigure(3, weight=0)
        equipped_frame.columnconfigure(4, weight=0); equipped_frame.columnconfigure(5, weight=0); equipped_frame.columnconfigure(6, weight=0)
        ctk.CTkLabel(master=equipped_frame, text="Armas Equipadas", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, columnspan=7, pady=(0, 5), sticky="n")
        
        ctk.CTkLabel(master=equipped_frame, text="Mão Principal:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.mh_name_label = ctk.CTkLabel(master=equipped_frame, text="---", anchor="w")
        self.mh_name_label.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        self.mh_damage_label = ctk.CTkLabel(master=equipped_frame, text="Dano: ---", anchor="w")
        self.mh_damage_label.grid(row=1, column=2, padx=5, pady=2, sticky="w")
        ctk.CTkLabel(master=equipped_frame, text="Mod.D:").grid(row=1, column=3, padx=(10, 0), pady=2, sticky="w")
        self.mh_damage_mod_entry = ctk.CTkEntry(master=equipped_frame, placeholder_text="+0", width=45)
        self.mh_damage_mod_entry.grid(row=1, column=4, padx=(0, 5), pady=2, sticky="w")
        self.mh_roll_damage_button = ctk.CTkButton(master=equipped_frame, text="Dano", width=60, state="disabled", command=lambda: self.roll_equipped_weapon_damage("main"))
        self.mh_roll_damage_button.grid(row=1, column=5, padx=2, pady=2)
        self.mh_roll_attack_button = ctk.CTkButton(master=equipped_frame, text="Ataque", width=70, state="disabled", command=lambda: self.perform_attack_roll("main"))
        self.mh_roll_attack_button.grid(row=1, column=6, padx=2, pady=2)

        ctk.CTkLabel(master=equipped_frame, text="Mão Secundária:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.oh_name_label = ctk.CTkLabel(master=equipped_frame, text="---", anchor="w")
        self.oh_name_label.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        self.oh_damage_label = ctk.CTkLabel(master=equipped_frame, text="Dano: ---", anchor="w")
        self.oh_damage_label.grid(row=2, column=2, padx=5, pady=2, sticky="w")
        ctk.CTkLabel(master=equipped_frame, text="Mod.D:").grid(row=2, column=3, padx=(10, 0), pady=2, sticky="w")
        self.oh_damage_mod_entry = ctk.CTkEntry(master=equipped_frame, placeholder_text="+0", width=45)
        self.oh_damage_mod_entry.grid(row=2, column=4, padx=(0, 5), pady=2, sticky="w")
        self.oh_roll_damage_button = ctk.CTkButton(master=equipped_frame, text="Dano", width=60, state="disabled", command=lambda: self.roll_equipped_weapon_damage("off"))
        self.oh_roll_damage_button.grid(row=2, column=5, padx=2, pady=2)
        self.oh_roll_attack_button = ctk.CTkButton(master=equipped_frame, text="Ataque", width=70, state="disabled", command=lambda: self.perform_attack_roll("off"))
        self.oh_roll_attack_button.grid(row=2, column=6, padx=2, pady=2)
        
        self.action_roll_animation_label = ctk.CTkLabel(master=equipped_frame, text="", width=100, font=ctk.CTkFont(size=20, weight="bold"))
        self.action_roll_animation_label.grid(row=3, column=1, pady=(10, 2), sticky="w")
        self.action_roll_result_label = ctk.CTkLabel(master=equipped_frame, text="", width=450, anchor="w", justify="left", wraplength=440)
        self.action_roll_result_label.grid(row=3, column=2, columnspan=5, pady=(10, 2), sticky="ew")

    def setup_weapons_list_section(self) -> None:
        """Configura a seção do inventário de armas."""
        weapons_main_frame = ctk.CTkFrame(self.main_frame)
        weapons_main_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=(5,0), sticky="nsew")
        weapons_main_frame.rowconfigure(0, weight=0)
        weapons_main_frame.rowconfigure(1, weight=1) # ScrollFrame expande
        weapons_main_frame.rowconfigure(2, weight=0)
        weapons_main_frame.columnconfigure(0, weight=1)

        title_weapons_label = ctk.CTkLabel(master=weapons_main_frame, text="Inventário de Armas", font=ctk.CTkFont(size=16, weight="bold"))
        title_weapons_label.grid(row=0, column=0, pady=(0,5), sticky="n")

        self.weapons_scroll_frame = ctk.CTkScrollableFrame(weapons_main_frame, height=150)
        self.weapons_scroll_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        col_weights = [3, 2, 1, 2, 2, 0, 1, 0, 0] # Nome, Dano, Atr. Vant., Perícia Atq., Tipo, Mãos, Alcance, Equip, Del
        for i, weight in enumerate(col_weights):
            self.weapons_scroll_frame.columnconfigure(i, weight=weight)
        
        headers = ["Nome", "Dano", "Atr. Atq.", "Perícia Atq.", "Tipo Dano", "Mãos", "Alcance", "", ""]
        for col, header_text in enumerate(headers):
            ctk.CTkLabel(master=self.weapons_scroll_frame, text=header_text, font=ctk.CTkFont(weight="bold")).grid(row=0, column=col, padx=2, pady=5, sticky="w")
        
        self.weapon_current_row_idx = 1 # Próxima linha disponível para adicionar armas
        
        add_weapon_button = ctk.CTkButton(master=weapons_main_frame, text="Adicionar Arma ao Inventário", command=lambda: self.add_weapon_entry_row())
        add_weapon_button.grid(row=2, column=0, pady=(5,0), sticky="ew", padx=5)

    # --- Gerenciamento de Armas ---
    def _on_weapon_data_change(self, weapon_data_dict_ref: Dict[str, Any], key: str, string_var_or_value: Union[ctk.StringVar, str]) -> None:
        """Callback para quando dados de uma arma no inventário são alterados na UI."""
        new_value = string_var_or_value.get() if isinstance(string_var_or_value, ctk.StringVar) else string_var_or_value
        
        is_newly_named = False
        if key == WEAPON_KEY_NAME and new_value.strip() and weapon_data_dict_ref.get(WEAPON_KEY_NAME, '').strip() == "":
            is_newly_named = True
            
        if weapon_data_dict_ref.get(key) != new_value:
            weapon_data_dict_ref[key] = new_value
        
        if is_newly_named and weapon_data_dict_ref not in self.personagem.armas_inventario:
            self.personagem.armas_inventario.append(weapon_data_dict_ref)
            
        # Atualiza display de arma equipada se esta arma estiver equipada
        if self.personagem.arma_equipada_principal is weapon_data_dict_ref:
            self._update_equipped_weapon_display("main", self.personagem.arma_equipada_principal)
        if self.personagem.arma_equipada_secundaria is weapon_data_dict_ref:
            self._update_equipped_weapon_display("off", self.personagem.arma_equipada_secundaria)

    def add_weapon_entry_row(self, is_loading: bool = False, **weapon_kwargs: Any) -> None:
        """Adiciona uma linha de entrada de arma ao inventário na UI."""
        weapon_data_for_this_row: Dict[str, Any]
        if is_loading:
            # Ao carregar, weapon_kwargs é o dicionário do personagem. Usá-lo diretamente.
            weapon_data_for_this_row = weapon_kwargs
        else: # Nova arma adicionada pelo usuário
            weapon_data_for_this_row = {
                WEAPON_KEY_NAME: "",
                WEAPON_KEY_DAMAGE: "",
                WEAPON_KEY_ATTR: "FOR", # Padrão
                WEAPON_KEY_SKILL_TYPE: "Corpo-a-Corpo", # Padrão
                WEAPON_KEY_TYPE: "",
                WEAPON_KEY_HANDS: "1 Mão", # Padrão, deve corresponder às opções de items_data.py
                WEAPON_KEY_RANGE: "Corpo"  # Padrão
            }
            # Será adicionado a self.personagem.armas_inventario em _on_weapon_data_change quando o nome for preenchido.

        row_frame = ctk.CTkFrame(self.weapons_scroll_frame, fg_color="transparent")
        row_frame.grid(row=self.weapon_current_row_idx, column=0, columnspan=9, sticky="ew", pady=(0, 1))
        col_weights = [3, 2, 1, 2, 2, 0, 1, 0, 0]
        for i, weight in enumerate(col_weights):
            row_frame.columnconfigure(i, weight=weight)
        
        ui_elements_for_row = {'frame': row_frame, 'data_dict_ref': weapon_data_for_this_row}

        # Nome
        name_var = ctk.StringVar(value=str(weapon_data_for_this_row.get(WEAPON_KEY_NAME, "")))
        name_entry = ctk.CTkEntry(master=row_frame, placeholder_text="Nome", textvariable=name_var)
        name_entry.grid(row=0, column=0, padx=1, pady=1, sticky="ew")
        name_var.trace_add("write", lambda n,i,m, d=weapon_data_for_this_row, k=WEAPON_KEY_NAME, v=name_var: self._on_weapon_data_change(d,k,v))
        ui_elements_for_row[WEAPON_KEY_NAME + "_var"] = name_var
        
        # Dano
        damage_var = ctk.StringVar(value=str(weapon_data_for_this_row.get(WEAPON_KEY_DAMAGE, "")))
        damage_entry = ctk.CTkEntry(master=row_frame, placeholder_text="Ex: 1d8+FOR", textvariable=damage_var)
        damage_entry.grid(row=0, column=1, padx=1, pady=1, sticky="ew")
        damage_var.trace_add("write", lambda n,i,m, d=weapon_data_for_this_row, k=WEAPON_KEY_DAMAGE, v=damage_var: self._on_weapon_data_change(d,k,v))
        ui_elements_for_row[WEAPON_KEY_DAMAGE + "_var"] = damage_var

        # Atributo de Ataque (FOR, DES, etc.)
        atk_attr_var = ctk.StringVar(value=str(weapon_data_for_this_row.get(WEAPON_KEY_ATTR, "FOR")))
        # Idealmente, um OptionMenu se os atributos forem fixos
        atk_attr_entry = ctk.CTkEntry(master=row_frame, placeholder_text="FOR/DES", textvariable=atk_attr_var, width=60)
        atk_attr_entry.grid(row=0, column=2, padx=1, pady=1, sticky="ew")
        atk_attr_var.trace_add("write", lambda n,i,m, d=weapon_data_for_this_row, k=WEAPON_KEY_ATTR, v=atk_attr_var: self._on_weapon_data_change(d,k,v))
        ui_elements_for_row[WEAPON_KEY_ATTR + "_var"] = atk_attr_var

        # Perícia de Ataque (Corpo-a-Corpo, Pontaria, Elemental)
        attack_skill_options = ["Corpo-a-Corpo", "Pontaria", "Elemental"]
        attack_skill_var = ctk.StringVar(value=str(weapon_data_for_this_row.get(WEAPON_KEY_SKILL_TYPE, "Corpo-a-Corpo")))
        attack_skill_menu = ctk.CTkOptionMenu(master=row_frame, values=attack_skill_options, variable=attack_skill_var, width=130, dynamic_resizing=False)
        attack_skill_menu.grid(row=0, column=3, padx=1, pady=1, sticky="ew")
        attack_skill_var.trace_add("write", lambda n,i,m, d=weapon_data_for_this_row, k=WEAPON_KEY_SKILL_TYPE, v=attack_skill_var: self._on_weapon_data_change(d,k,v))
        ui_elements_for_row[WEAPON_KEY_SKILL_TYPE + "_var"] = attack_skill_var

        # Tipo de Dano (Corte, Perf., etc.)
        type_w_var = ctk.StringVar(value=str(weapon_data_for_this_row.get(WEAPON_KEY_TYPE, "")))
        type_entry = ctk.CTkEntry(master=row_frame, placeholder_text="Corte, etc.", textvariable=type_w_var, width=80)
        type_entry.grid(row=0, column=4, padx=1, pady=1, sticky="ew")
        type_w_var.trace_add("write", lambda n,i,m, d=weapon_data_for_this_row, k=WEAPON_KEY_TYPE, v=type_w_var: self._on_weapon_data_change(d,k,v))
        ui_elements_for_row[WEAPON_KEY_TYPE + "_var"] = type_w_var

        # Mãos (Empunhadura)
        hands_options = ["1 Mão", "2 Mãos"] # Consistente com items_data.py
        hands_var = ctk.StringVar(value=str(weapon_data_for_this_row.get(WEAPON_KEY_HANDS, "1 Mão")))
        hands_menu = ctk.CTkOptionMenu(master=row_frame, values=hands_options, variable=hands_var, width=80, dynamic_resizing=False)
        hands_menu.grid(row=0, column=5, padx=1, pady=1, sticky="w")
        hands_var.trace_add("write", lambda n,i,m, d=weapon_data_for_this_row, k=WEAPON_KEY_HANDS, v=hands_var: self._on_weapon_data_change(d,k,v))
        ui_elements_for_row[WEAPON_KEY_HANDS + "_var"] = hands_var
        
        # Alcance
        range_w_var = ctk.StringVar(value=str(weapon_data_for_this_row.get(WEAPON_KEY_RANGE, "Corpo")))
        range_entry = ctk.CTkEntry(master=row_frame, placeholder_text="Corpo, Dist.", textvariable=range_w_var, width=70)
        range_entry.grid(row=0, column=6, padx=1, pady=1, sticky="ew")
        range_w_var.trace_add("write", lambda n,i,m, d=weapon_data_for_this_row, k=WEAPON_KEY_RANGE, v=range_w_var: self._on_weapon_data_change(d,k,v))
        ui_elements_for_row[WEAPON_KEY_RANGE + "_var"] = range_w_var
        
        # Botão Equipar/Desequipar
        equip_button = ctk.CTkButton(master=row_frame, text="Equipar", width=70,
                                     command=lambda w_data=weapon_data_for_this_row: self.equip_weapon(w_data))
        equip_button.grid(row=0, column=7, padx=1, pady=1)
        ui_elements_for_row['equip_button'] = equip_button
        
        # Botão Remover
        remove_button = ctk.CTkButton(master=row_frame, text="X", width=25, height=25,
                                      command=lambda rf=row_frame, rd=weapon_data_for_this_row: self.remove_weapon_row(rf, rd))
        remove_button.grid(row=0, column=8, padx=(2,0), pady=1, sticky="e")
        
        self.weapon_inventory_ui_rows.append(ui_elements_for_row)
        self.weapon_current_row_idx += 1
        self.update_all_inventory_equip_button_states() # Atualiza estado do botão recém-adicionado


    def remove_weapon_row(self, row_frame_to_remove: ctk.CTkFrame, weapon_data_to_remove: Dict[str, Any]) -> None:
        """Remove uma linha de arma da UI e do inventário do personagem."""
        row_frame_to_remove.destroy()
        
        ui_element_to_remove = next((el for el in self.weapon_inventory_ui_rows if el.get('frame') == row_frame_to_remove), None)
        if ui_element_to_remove:
            self.weapon_inventory_ui_rows.remove(ui_element_to_remove)
        
        if weapon_data_to_remove in self.personagem.armas_inventario:
            self.personagem.armas_inventario.remove(weapon_data_to_remove)
        
        # Desequipa se a arma removida estava equipada
        if self.personagem.arma_equipada_principal is weapon_data_to_remove:
            self.unequip_weapon("main", update_buttons=False) # Não precisa atualizar todos os botões ainda
        if self.personagem.arma_equipada_secundaria is weapon_data_to_remove:
            self.unequip_weapon("off", update_buttons=False)
            
        self.update_all_inventory_equip_button_states() # Atualiza todos os botões de equipar agora


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
        self.update_all_inventory_equip_button_states()

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

    def _update_equipped_weapon_display(self, hand_slot: Literal["main", "off"], weapon_data_dict: Optional[Dict[str, Any]]) -> None:
        """Atualiza os labels e botões na UI para uma arma equipada."""
        name_label = self.mh_name_label if hand_slot == "main" else self.oh_name_label
        damage_label = self.mh_damage_label if hand_slot == "main" else self.oh_damage_label
        attack_button = self.mh_roll_attack_button if hand_slot == "main" else self.oh_roll_attack_button
        damage_button = self.mh_roll_damage_button if hand_slot == "main" else self.oh_roll_damage_button
        
        if weapon_data_dict:
            name_label.configure(text=str(weapon_data_dict.get(WEAPON_KEY_NAME, "N/A")))
            damage_label.configure(text=f"Dano: {weapon_data_dict.get(WEAPON_KEY_DAMAGE, 'N/A')}")
            attack_button.configure(state="normal")
            damage_button.configure(state="normal")
            
            # Se a arma principal é de 2 mãos, desabilita slot secundário
            if hand_slot == "main" and str(weapon_data_dict.get(WEAPON_KEY_HANDS, "1 Mão")) == "2 Mãos":
                self.oh_name_label.configure(text="[Mão Sec. Bloqueada]")
                self.oh_damage_label.configure(text="Dano: ---")
                self.oh_roll_attack_button.configure(state="disabled")
                self.oh_roll_damage_button.configure(state="disabled")
            # Se a arma secundária está sendo atualizada, mas a principal é 2-mãos (não deveria acontecer se equipar está certo)
            elif hand_slot == "off" and self.personagem.arma_equipada_principal and \
                 str(self.personagem.arma_equipada_principal.get(WEAPON_KEY_HANDS, "1 Mão")) == "2 Mãos":
                name_label.configure(text="---"); damage_label.configure(text="Dano: ---") # Limpa OH se MH é 2H
                attack_button.configure(state="disabled"); damage_button.configure(state="disabled")
        else:
            name_label.configure(text="---")
            damage_label.configure(text="Dano: ---")
            attack_button.configure(state="disabled")
            damage_button.configure(state="disabled")
            # Se a mão principal foi desequipada e era de 2 mãos, reabilita a secundária (se não houver nada lá)
            if hand_slot == "main" and self.personagem.arma_equipada_secundaria is None:
                # Garante que os botões da OH voltem ao estado "disabled" se vazia, em vez de um estado inconsistente
                if self.oh_roll_attack_button: self.oh_roll_attack_button.configure(state="disabled")
                if self.oh_roll_damage_button: self.oh_roll_damage_button.configure(state="disabled")


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
        
        if not weapon_data:
            self.action_roll_result_label.configure(text="Nenhuma arma equipada nesse slot.")
            return

        self._set_action_buttons_state("disabled") # Desabilita todos os botões de ação

        weapon_name = str(weapon_data.get(WEAPON_KEY_NAME, "N/A"))
        atk_attr_short = str(weapon_data.get(WEAPON_KEY_ATTR, "FOR")).strip().upper()
        attack_skill_name_selected = str(weapon_data.get(WEAPON_KEY_SKILL_TYPE, "Corpo-a-Corpo"))
        
        char_attr_name_full = ATTRIBUTE_NAME_MAP.get(atk_attr_short, "Força") # Default para Força
        
        try:
            # Usa self.personagem diretamente, pois attributes_skills_tab_ref pode não ser necessário aqui
            attribute_value = self.personagem.atributos.get(char_attr_name_full, 0)
            
            skill_val_str = "0" # Padrão
            if attack_skill_name_selected == "Corpo-a-Corpo": skill_val_str = self.cac_val_var.get()
            elif attack_skill_name_selected == "Pontaria": skill_val_str = self.pontaria_val_var.get()
            elif attack_skill_name_selected == "Elemental": skill_val_str = self.elemental_val_var.get()
            
            skill_value_for_attack = int(skill_val_str.strip()) if skill_val_str.strip().lstrip('-').isdigit() else 0
            if skill_value_for_attack == 0 and attack_skill_name_selected: # Valor 0 em perícia geralmente é 1 se treinado, ou 0 se não. Aqui usamos o valor direto.
                # O livro (p.34) diz que perícia não treinada tem valor 0.
                # Se for 0 na ficha, usamos 0 para o teste.
                 pass


        except Exception as e:
            self.action_roll_animation_label.configure(text="Erro")
            self.action_roll_result_label.configure(text=f"Erro ao obter dados para ataque: {e}")
            self.re_enable_action_buttons()
            return
            
        self.action_roll_animation_label.configure(text="")
        self.action_roll_result_label.configure(text=f"Rolando ataque ({attack_skill_name_selected}) com {weapon_name}...")
        self.animate_action_roll(0, "attack", attribute_value, skill_value_for_attack, weapon_name, hand_slot)


    def roll_equipped_weapon_damage(self, hand_slot: Literal["main", "off"]) -> None:
        """Rola o dano para a arma equipada no slot especificado."""
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
        
        modifier = 0
        try:
            mod_str = modifier_entry_widget.get()
            if mod_str: # Tenta converter apenas se não for vazio
                modifier = int(mod_str)
        except ValueError:
            modifier_entry_widget.delete(0, "end")
            modifier_entry_widget.insert(0, "+0") # Reset para +0 se inválido
            modifier = 0
            
        self.action_roll_animation_label.configure(text="")
        self.action_roll_result_label.configure(text=f"Rolando dano para {weapon_name}...")
        self.animate_action_roll(0, "damage", damage_dice_str, modifier, weapon_name, hand_slot)
            

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
                crit_msg = " ACERTO CRÍTICO!" if success_level == SUCCESS_EXTREME and final_d20 == 20 else "" # Específico para 20 natural
                
                num_dice_attr, roll_type_attr_key = get_dice_for_attribute_test(attribute_value)
                roll_type_attr_text = ""
                if roll_type_attr_key == "advantage": roll_type_attr_text = " (Maior)"
                elif roll_type_attr_key == "disadvantage": roll_type_attr_text = " (Menor)"
                
                attr_dice_info = f"{num_dice_attr}d20{roll_type_attr_text}"
                
                weapon_dict_data = self.personagem.arma_equipada_principal if hand_slot_rolled == "main" else self.personagem.arma_equipada_secundaria
                attack_skill_name_used = str(weapon_dict_data.get(WEAPON_KEY_SKILL_TYPE,"N/A")) if weapon_dict_data else "N/A"
                
                result_text_lines = [
                    f"Ataque com {item_name_for_display} ({attack_skill_name_used}): {success_level}{crit_msg}",
                    f"  Atributo Base ({attribute_value}) -> {attr_dice_info}",
                    f"  Valor da Perícia ({attack_skill_name_used}): {skill_value}",
                    f"  d20 Usado: {final_d20}{roll_details}"
                ]
                self.action_roll_result_label.configure(text="\n".join(result_text_lines))

            elif roll_type == "damage":
                damage_dice_str = str(value1) # value1 é damage_dice_str
                static_modifier = value2    # value2 é o modificador do entry
                
                rolls, total_base, final_total = parse_and_roll_damage_string(damage_dice_str, static_modifier)
                
                if rolls is None: # String de dano inválida
                    self.action_roll_animation_label.configure(text="Erro!")
                    self.action_roll_result_label.configure(text=f"String de dano '{damage_dice_str}' inválida.")
                else:
                    self.action_roll_animation_label.configure(text=str(final_total))
                    roll_details_str = f"Rolagens: {rolls}" if rolls else "Dano Fixo/Modificador"
                    
                    # Calcula modificadores separados para exibição
                    # mod_from_dice_string é (total_base - sum_of_rolls)
                    # mod_from_entry é static_modifier (value2)
                    sum_of_actual_dice_rolls = sum(rolls) if rolls else 0
                    mod_from_dice_string = total_base - sum_of_actual_dice_rolls
                    
                    mod_details_list = []
                    if mod_from_dice_string != 0:
                        mod_details_list.append(f"Mod. da Str de Dano: {mod_from_dice_string:+}")
                    if static_modifier != 0:
                        mod_details_list.append(f"Mod. Adicional (UI): {static_modifier:+}")
                    
                    mod_details_str = " (" + ", ".join(mod_details_list) + ")" if mod_details_list else ""
                    
                    self.action_roll_result_label.configure(text=f"Dano ({item_name_for_display}): {final_total}\n  {roll_details_str}{mod_details_str}")
            
            self.re_enable_action_buttons()