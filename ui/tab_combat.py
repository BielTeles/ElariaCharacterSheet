import customtkinter as ctk
import random
from core.dice_roller import (
    roll_generic_dice,
    parse_and_roll_damage_string,
    perform_attribute_test_roll,
    check_success,
    get_dice_for_attribute_test
)

class CombatTab:
    def __init__(self, tab_widget, attributes_skills_tab_ref, personagem_atual):
        self.tab_widget = tab_widget
        self.attributes_skills_tab_ref = attributes_skills_tab_ref
        self.personagem = personagem_atual
        
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

        self.main_frame = ctk.CTkFrame(self.tab_widget)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.main_frame.columnconfigure(0, weight=1); self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=0); self.main_frame.rowconfigure(1, weight=0)
        self.main_frame.rowconfigure(2, weight=0); self.main_frame.rowconfigure(3, weight=1)

        self.setup_defense_stats_section()
        self.setup_attack_skills_section() 
        self.setup_armor_shield_section()
        self.setup_equipped_weapons_slots_section()
        self.setup_weapons_list_section()
        
        self.load_data_from_personagem() 

    def load_data_from_personagem(self):
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

        for row_ui_elements in self.weapon_inventory_ui_rows:
            if row_ui_elements.get('frame'):
                row_ui_elements['frame'].destroy()
        self.weapon_inventory_ui_rows.clear()
        self.weapon_current_row_idx = 1 

        if hasattr(self.personagem, 'armas_inventario'):
            for weapon_data_from_inventory in self.personagem.armas_inventario:
                self.add_weapon_entry_row(existing_data_dict=weapon_data_from_inventory, is_loading=True)
        
        # Garante que as referências de arma_equipada no personagem são as mesmas
        # dos dicionários em armas_inventario após o carregamento, se os nomes coincidirem.
        # Isso é crucial para a comparação de identidade de objeto funcionar.
        if self.personagem.arma_equipada_principal:
            found_main = next((w for w in self.personagem.armas_inventario if w.get('name') == self.personagem.arma_equipada_principal.get('name')), None)
            if found_main: self.personagem.arma_equipada_principal = found_main
            else: self.personagem.arma_equipada_principal = None # Arma equipada não está mais no inventário

        if self.personagem.arma_equipada_secundaria:
            found_off = next((w for w in self.personagem.armas_inventario if w.get('name') == self.personagem.arma_equipada_secundaria.get('name')), None)
            if found_off: self.personagem.arma_equipada_secundaria = found_off
            else: self.personagem.arma_equipada_secundaria = None

        self._update_equipped_weapon_display("main", self.personagem.arma_equipada_principal)
        self._update_equipped_weapon_display("off", self.personagem.arma_equipada_secundaria)
        self.update_all_inventory_equip_button_states()


    def _update_personagem_skill_value_from_combat_tab(self, skill_name, string_var, *args):
        # ... (como antes)
        val_str = string_var.get(); value = 0
        try: value = int(val_str) if val_str.strip() else 0
        except ValueError: string_var.set(str(self.personagem.pericias_valores.get(skill_name,0))); return
        self.personagem.atualizar_pericia_valor(skill_name, value)


    def _update_personagem_combat_attr(self, attr_keys, string_var, is_int=False, *args):
        # ... (como antes)
        value_str = string_var.get(); value_to_set = value_str
        if is_int:
            try: value_to_set = int(value_str) if value_str.strip() else 0
            except ValueError:
                obj_val = self.personagem; revert_val = 0 if is_int else ""
                try:
                    for key in attr_keys[:-1]: obj_val = getattr(obj_val, key) if not isinstance(obj_val, dict) else obj_val[key]
                    revert_val = obj_val[attr_keys[-1]] if isinstance(obj_val, dict) else getattr(obj_val, attr_keys[-1])
                except: pass
                string_var.set(str(revert_val)); return
        obj_ref = self.personagem
        try:
            for key in attr_keys[:-1]: obj_ref = getattr(obj_ref, key) if not isinstance(obj_ref, dict) else obj_ref[key]
            if isinstance(obj_ref, dict): obj_ref[attr_keys[-1]] = value_to_set
            else: setattr(obj_ref, attr_keys[-1], value_to_set)
        except Exception as e: print(f"Erro ao atualizar {'.'.join(attr_keys)}: {e}")


    def create_linked_entry(self, parent, row, col, label_text, string_var, attr_keys_in_personagem=None, skill_name_in_personagem=None, is_int=False, placeholder="0", width=80, label_sticky="w", entry_sticky="ew"):
        # ... (como antes)
        label = ctk.CTkLabel(master=parent, text=label_text); label.grid(row=row, column=col, padx=5, pady=2, sticky=label_sticky)
        entry = ctk.CTkEntry(master=parent, placeholder_text=placeholder, width=width, textvariable=string_var); entry.grid(row=row, column=col + 1, padx=5, pady=2, sticky=entry_sticky)
        if skill_name_in_personagem: string_var.trace_add("write", lambda n,i,m, sk=skill_name_in_personagem, sv=string_var: self._update_personagem_skill_value_from_combat_tab(sk, sv))
        elif attr_keys_in_personagem: string_var.trace_add("write", lambda n,i,m, ap=attr_keys_in_personagem, sv=string_var, is_i=is_int: self._update_personagem_combat_attr(ap, sv, is_i))
        return entry

    def setup_defense_stats_section(self):
        # ... (como antes)
        defense_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent"); defense_frame.grid(row=0, column=0, padx=5, pady=(0, 5), sticky="new"); defense_frame.columnconfigure(1, weight=1)
        ctk.CTkLabel(master=defense_frame, text="Defesa", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, columnspan=2, padx=5, pady=(0, 5), sticky="n")
        self.rd_total_entry = self.create_linked_entry(defense_frame, 1, 0, "RD Total:", self.rd_total_var, attr_keys_in_personagem=('rd_total',), is_int=True)
        self.esquiva_val_entry = self.create_linked_entry(defense_frame, 2, 0, "Esquiva (Valor):", self.esquiva_val_var, skill_name_in_personagem="Esquiva")
        self.bloqueio_val_entry = self.create_linked_entry(defense_frame, 3, 0, "Bloqueio (Valor):", self.bloqueio_val_var, skill_name_in_personagem="Bloqueio")

    def setup_attack_skills_section(self):
        # ... (como antes)
        attack_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent"); attack_frame.grid(row=0, column=1, padx=5, pady=(0, 5), sticky="new"); attack_frame.columnconfigure(1, weight=1)
        ctk.CTkLabel(master=attack_frame, text="Perícias de Ataque Base", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, columnspan=2, padx=5, pady=(0, 5), sticky="n")
        self.iniciativa_entry = self.create_linked_entry(attack_frame, 1, 0, "Iniciativa (Valor):", self.iniciativa_val_var, skill_name_in_personagem="Iniciativa")
        self.cac_val_entry = self.create_linked_entry(attack_frame, 2, 0, "Corpo-a-Corpo (Valor):", self.cac_val_var, skill_name_in_personagem="Corpo-a-Corpo", placeholder="Valor")
        self.pontaria_val_entry = self.create_linked_entry(attack_frame, 3, 0, "Pontaria (Valor):", self.pontaria_val_var, skill_name_in_personagem="Pontaria", placeholder="Valor")
        self.elemental_val_entry = self.create_linked_entry(attack_frame, 4, 0, "Elemental (Valor):", self.elemental_val_var, skill_name_in_personagem="Elemental", placeholder="Valor")

    def setup_armor_shield_section(self):
        # ... (como antes)
        armor_shield_frame = ctk.CTkFrame(self.main_frame); armor_shield_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="new"); armor_shield_frame.columnconfigure(1, weight=1); armor_shield_frame.columnconfigure(3, weight=1)
        ctk.CTkLabel(master=armor_shield_frame, text="Equipamento Defensivo", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, columnspan=4, padx=5, pady=(0, 5), sticky="n")
        self.create_linked_entry(armor_shield_frame, 1, 0, "Armadura:", self.armor_name_var, attr_keys_in_personagem=('armadura_equipada', 'nome'), placeholder="Nome")
        self.create_linked_entry(armor_shield_frame, 1, 2, "RD:", self.armor_rd_var, attr_keys_in_personagem=('armadura_equipada', 'rd_fornecida'), is_int=True, placeholder="RD", width=50, entry_sticky="w")
        self.create_linked_entry(armor_shield_frame, 2, 0, "Escudo:", self.shield_name_var, attr_keys_in_personagem=('escudo_equipado', 'nome'), placeholder="Nome")
        self.create_linked_entry(armor_shield_frame, 2, 2, "Notas:", self.shield_notes_var, attr_keys_in_personagem=('escudo_equipado', 'notas'), placeholder="Notas")

    def setup_equipped_weapons_slots_section(self):
        # ... (como antes)
        equipped_frame = ctk.CTkFrame(self.main_frame); equipped_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew"); 
        equipped_frame.columnconfigure(1, weight=2); equipped_frame.columnconfigure(2, weight=1); equipped_frame.columnconfigure(4, weight=0); equipped_frame.columnconfigure(5, weight=0); equipped_frame.columnconfigure(6, weight=0) 
        ctk.CTkLabel(master=equipped_frame, text="Armas Equipadas", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, columnspan=7, pady=(0, 5), sticky="n")
        ctk.CTkLabel(master=equipped_frame, text="Mão Principal:").grid(row=1, column=0, padx=5, pady=2, sticky="w"); self.mh_name_label = ctk.CTkLabel(master=equipped_frame, text="---", anchor="w"); self.mh_name_label.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        self.mh_damage_label = ctk.CTkLabel(master=equipped_frame, text="Dano: ---", anchor="w"); self.mh_damage_label.grid(row=1, column=2, padx=5, pady=2, sticky="w")
        ctk.CTkLabel(master=equipped_frame, text="Mod.D:").grid(row=1, column=3, padx=(10, 0), pady=2, sticky="w"); self.mh_damage_mod_entry = ctk.CTkEntry(master=equipped_frame, placeholder_text="+0", width=35); self.mh_damage_mod_entry.grid(row=1, column=4, padx=(0, 5), pady=2, sticky="w")
        self.mh_roll_damage_button = ctk.CTkButton(master=equipped_frame, text="Dano", width=60, state="disabled", command=lambda: self.roll_equipped_weapon_damage("main")); self.mh_roll_damage_button.grid(row=1, column=5, padx=2, pady=2)
        self.mh_roll_attack_button = ctk.CTkButton(master=equipped_frame, text="Ataque", width=70, state="disabled", command=lambda: self.perform_attack_roll("main")); self.mh_roll_attack_button.grid(row=1, column=6, padx=2, pady=2)
        ctk.CTkLabel(master=equipped_frame, text="Mão Secundária:").grid(row=2, column=0, padx=5, pady=2, sticky="w"); self.oh_name_label = ctk.CTkLabel(master=equipped_frame, text="---", anchor="w"); self.oh_name_label.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        self.oh_damage_label = ctk.CTkLabel(master=equipped_frame, text="Dano: ---", anchor="w"); self.oh_damage_label.grid(row=2, column=2, padx=5, pady=2, sticky="w")
        ctk.CTkLabel(master=equipped_frame, text="Mod.D:").grid(row=2, column=3, padx=(10, 0), pady=2, sticky="w"); self.oh_damage_mod_entry = ctk.CTkEntry(master=equipped_frame, placeholder_text="+0", width=35); self.oh_damage_mod_entry.grid(row=2, column=4, padx=(0, 5), pady=2, sticky="w")
        self.oh_roll_damage_button = ctk.CTkButton(master=equipped_frame, text="Dano", width=60, state="disabled", command=lambda: self.roll_equipped_weapon_damage("off")); self.oh_roll_damage_button.grid(row=2, column=5, padx=2, pady=2)
        self.oh_roll_attack_button = ctk.CTkButton(master=equipped_frame, text="Ataque", width=70, state="disabled", command=lambda: self.perform_attack_roll("off")); self.oh_roll_attack_button.grid(row=2, column=6, padx=2, pady=2)
        self.action_roll_animation_label = ctk.CTkLabel(master=equipped_frame, text="", width=100, font=ctk.CTkFont(size=20, weight="bold")); self.action_roll_animation_label.grid(row=3, column=1, pady=(10, 2), sticky="w")
        self.action_roll_result_label = ctk.CTkLabel(master=equipped_frame, text="", width=450, anchor="w", justify="left", wraplength=440); self.action_roll_result_label.grid(row=3, column=2, columnspan=5, pady=(10, 2), sticky="ew")

    def setup_weapons_list_section(self):
        # ... (como antes)
        weapons_main_frame = ctk.CTkFrame(self.main_frame); weapons_main_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        weapons_main_frame.rowconfigure(1, weight=1); weapons_main_frame.columnconfigure(0, weight=1)
        ctk.CTkLabel(master=weapons_main_frame, text="Inventário de Armas", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(0, 5))
        self.weapons_scroll_frame = ctk.CTkScrollableFrame(weapons_main_frame, height=150); self.weapons_scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)
        col_weights = [3, 2, 1, 2, 2, 0, 1, 0, 0]; 
        for i, weight in enumerate(col_weights): self.weapons_scroll_frame.columnconfigure(i, weight=weight)
        headers = ["Nome", "Dano", "Atr. Vant.", "Perícia Atq.", "Tipo", "Mãos", "Alcance", "", ""]; 
        for col, header_text in enumerate(headers):
            ctk.CTkLabel(master=self.weapons_scroll_frame, text=header_text, font=ctk.CTkFont(weight="bold")).grid(row=0, column=col, padx=2, pady=5, sticky="w")
        self.weapon_current_row_idx = 1
        ctk.CTkButton(master=weapons_main_frame, text="Adicionar Arma ao Inventário", command=lambda: self.add_weapon_entry_row()).pack(pady=5)

    def _on_weapon_data_change(self, weapon_data_dict_ref, key, string_var, *args):
        new_value = string_var.get()
        is_newly_named = False
        if key == 'name' and new_value.strip() and weapon_data_dict_ref.get('name', '').strip() == "" :
            is_newly_named = True
        
        weapon_data_dict_ref[key] = new_value
        
        if is_newly_named and weapon_data_dict_ref not in self.personagem.armas_inventario:
            self.personagem.armas_inventario.append(weapon_data_dict_ref)
        
        if self.personagem.arma_equipada_principal is weapon_data_dict_ref: # Compara REFERÊNCIAS
            self._update_equipped_weapon_display("main", self.personagem.arma_equipada_principal)
        if self.personagem.arma_equipada_secundaria is weapon_data_dict_ref: # Compara REFERÊNCIAS
            self._update_equipped_weapon_display("off", self.personagem.arma_equipada_secundaria)


    def add_weapon_entry_row(self, existing_data_dict=None, is_loading=False, 
                             name="", damage_dice="", atk_attr="FOR", 
                             attack_skill_type="Corpo-a-Corpo", type_w="", 
                             hands="1", range_w="Corpo"):
        
        weapon_data_for_this_row = None
        if is_loading and existing_data_dict is not None:
            weapon_data_for_this_row = existing_data_dict 
        else: 
            weapon_data_for_this_row = {
                'name': name, 'damage_dice': damage_dice, 'atk_attr': atk_attr, 
                'attack_skill_type': attack_skill_type, 'type_w': type_w,
                'hands': str(hands), 'range_w': range_w
            }
            # Não adiciona a self.personagem.armas_inventario aqui se name for vazio.
            # _on_weapon_data_change adicionará quando o nome for preenchido.
            if name.strip(): # Se um nome já foi fornecido (ex: defaults de um exemplo)
                 if weapon_data_for_this_row not in self.personagem.armas_inventario:
                      self.personagem.armas_inventario.append(weapon_data_for_this_row)


        row_frame = ctk.CTkFrame(self.weapons_scroll_frame, fg_color="transparent")
        row_frame.grid(row=self.weapon_current_row_idx, column=0, columnspan=9, sticky="ew", pady=(0, 1))
        col_weights = [3, 2, 1, 2, 2, 0, 1, 0, 0]
        for i, weight in enumerate(col_weights): row_frame.columnconfigure(i, weight=weight)

        ui_elements_for_row = {'frame': row_frame, 'data_dict_ref': weapon_data_for_this_row}

        # Campos de entrada com StringVars ligadas ao weapon_data_for_this_row
        name_var = ctk.StringVar(value=weapon_data_for_this_row.get('name',""))
        name_entry = ctk.CTkEntry(master=row_frame, placeholder_text="Nome", textvariable=name_var); name_entry.grid(row=0, column=0, padx=1, pady=1, sticky="ew")
        name_var.trace_add("write", lambda n,i,m, d=weapon_data_for_this_row, k='name', v=name_var: self._on_weapon_data_change(d,k,v))
        
        damage_var = ctk.StringVar(value=weapon_data_for_this_row.get('damage_dice',""))
        damage_entry = ctk.CTkEntry(master=row_frame, placeholder_text="Ex: 1d8+2", textvariable=damage_var); damage_entry.grid(row=0, column=1, padx=1, pady=1, sticky="ew")
        damage_var.trace_add("write", lambda n,i,m, d=weapon_data_for_this_row, k='damage_dice', v=damage_var: self._on_weapon_data_change(d,k,v))

        atk_attr_var = ctk.StringVar(value=weapon_data_for_this_row.get('atk_attr',"FOR"))
        atk_attr_entry = ctk.CTkEntry(master=row_frame, placeholder_text="FOR/DES/etc.", textvariable=atk_attr_var); atk_attr_entry.grid(row=0, column=2, padx=1, pady=1, sticky="ew")
        atk_attr_var.trace_add("write", lambda n,i,m, d=weapon_data_for_this_row, k='atk_attr', v=atk_attr_var: self._on_weapon_data_change(d,k,v))

        attack_skill_options = ["Corpo-a-Corpo", "Pontaria", "Elemental"]
        attack_skill_var = ctk.StringVar(value=weapon_data_for_this_row.get('attack_skill_type',"Corpo-a-Corpo"))
        attack_skill_menu = ctk.CTkOptionMenu(master=row_frame, values=attack_skill_options, variable=attack_skill_var, width=140); attack_skill_menu.grid(row=0, column=3, padx=1, pady=1, sticky="ew")
        attack_skill_var.trace_add("write", lambda n,i,m, d=weapon_data_for_this_row, k='attack_skill_type', v=attack_skill_var: self._on_weapon_data_change(d,k,v))
        ui_elements_for_row['attack_skill_type_var'] = attack_skill_var

        type_w_var = ctk.StringVar(value=weapon_data_for_this_row.get('type_w',""))
        type_entry = ctk.CTkEntry(master=row_frame, placeholder_text="Corte, etc.", textvariable=type_w_var); type_entry.grid(row=0, column=4, padx=1, pady=1, sticky="ew")
        type_w_var.trace_add("write", lambda n,i,m, d=weapon_data_for_this_row, k='type_w', v=type_w_var: self._on_weapon_data_change(d,k,v))
        
        hands_var = ctk.StringVar(value=str(weapon_data_for_this_row.get('hands',"1")))
        hands_menu = ctk.CTkOptionMenu(master=row_frame, values=["1", "2"], variable=hands_var, width=60); hands_menu.grid(row=0, column=5, padx=1, pady=1, sticky="w")
        hands_var.trace_add("write", lambda n,i,m, d=weapon_data_for_this_row, k='hands', v=hands_var: self._on_weapon_data_change(d,k,v))
        ui_elements_for_row['hands_var'] = hands_var

        range_w_var = ctk.StringVar(value=weapon_data_for_this_row.get('range_w',"Corpo"))
        range_entry = ctk.CTkEntry(master=row_frame, placeholder_text="Corpo, Dist.", textvariable=range_w_var); range_entry.grid(row=0, column=6, padx=1, pady=1, sticky="ew")
        range_w_var.trace_add("write", lambda n,i,m, d=weapon_data_for_this_row, k='range_w', v=range_w_var: self._on_weapon_data_change(d,k,v))
        
        equip_button = ctk.CTkButton(master=row_frame, text="Equipar", width=70, command=lambda w_data=weapon_data_for_this_row: self.equip_weapon(w_data))
        equip_button.grid(row=0, column=7, padx=1, pady=1)
        ui_elements_for_row['equip_button'] = equip_button

        remove_button = ctk.CTkButton(master=row_frame, text="X", width=25, height=25, command=lambda rf=row_frame, rd=weapon_data_for_this_row: self.remove_weapon_row(rf, rd))
        remove_button.grid(row=0, column=8, padx=1, pady=1, sticky="e")
        
        self.weapon_inventory_ui_rows.append(ui_elements_for_row)
        self.weapon_current_row_idx += 1
    
    def remove_weapon_row(self, row_frame_to_remove, weapon_data_to_remove):
        # ... (código como antes)
        row_frame_to_remove.destroy()
        ui_element_to_remove = next((el for el in self.weapon_inventory_ui_rows if el.get('frame') == row_frame_to_remove), None)
        if ui_element_to_remove: self.weapon_inventory_ui_rows.remove(ui_element_to_remove)
        try: self.personagem.armas_inventario.remove(weapon_data_to_remove)
        except ValueError: pass 
        if self.personagem.arma_equipada_principal == weapon_data_to_remove: self.unequip_weapon("main", update_buttons=False)
        if self.personagem.arma_equipada_secundaria == weapon_data_to_remove: self.unequip_weapon("off", update_buttons=False)
        self.update_all_inventory_equip_button_states()
        
    def equip_weapon(self, weapon_data_dict): # weapon_data_dict é a REFERÊNCIA do dict em self.personagem.armas_inventario
        # ... (código como antes, mas usando weapon_data_dict diretamente para self.personagem.arma_equipada_*)
        weapon_hands = str(weapon_data_dict.get('hands', "1"))
        if weapon_hands == "2":
            self.unequip_weapon("main", update_buttons=False) 
            self.unequip_weapon("off", update_buttons=False)
            self.personagem.arma_equipada_principal = weapon_data_dict # ARMAZENA A REFERÊNCIA
            self.personagem.arma_equipada_secundaria = None
        else: 
            if self.personagem.arma_equipada_principal is None:
                self.personagem.arma_equipada_principal = weapon_data_dict # ARMAZENA A REFERÊNCIA
            elif self.personagem.arma_equipada_secundaria is None and self.personagem.arma_equipada_principal != weapon_data_dict:
                if self.personagem.arma_equipada_principal and str(self.personagem.arma_equipada_principal.get('hands',"1")) == "2": return 
                self.personagem.arma_equipada_secundaria = weapon_data_dict # ARMAZENA A REFERÊNCIA
            else: return 
        self._update_equipped_weapon_display("main", self.personagem.arma_equipada_principal)
        self._update_equipped_weapon_display("off", self.personagem.arma_equipada_secundaria)
        self.update_all_inventory_equip_button_states()

    def unequip_weapon(self, hand_slot, update_buttons=True):
        # ... (como antes)
        is_main_two_handed = False
        if hand_slot == "main" and self.personagem.arma_equipada_principal:
            if str(self.personagem.arma_equipada_principal.get('hands', "1")) == "2": is_main_two_handed = True
            self.personagem.arma_equipada_principal = None
            if is_main_two_handed: self.personagem.arma_equipada_secundaria = None
        elif hand_slot == "off" and self.personagem.arma_equipada_secundaria:
            self.personagem.arma_equipada_secundaria = None
        self._update_equipped_weapon_display(hand_slot, None)
        if is_main_two_handed and hand_slot == "main": self._update_equipped_weapon_display("off", None)
        if update_buttons: self.update_all_inventory_equip_button_states()

    def _update_equipped_weapon_display(self, hand_slot, weapon_data_dict):
        # ... (como antes)
        name_label = self.mh_name_label if hand_slot == "main" else self.oh_name_label
        damage_label = self.mh_damage_label if hand_slot == "main" else self.oh_damage_label
        attack_button = self.mh_roll_attack_button if hand_slot == "main" else self.oh_roll_attack_button
        damage_button = self.mh_roll_damage_button if hand_slot == "main" else self.oh_roll_damage_button
        if weapon_data_dict:
            name_label.configure(text=weapon_data_dict.get('name', "N/A"))
            damage_label.configure(text=f"Dano: {weapon_data_dict.get('damage_dice', 'N/A')}")
            attack_button.configure(state="normal"); damage_button.configure(state="normal")
            if hand_slot == "main" and str(weapon_data_dict.get('hands', "1")) == "2":
                self.oh_name_label.configure(text="[2 Mãos]"); self.oh_damage_label.configure(text="Dano: ---")
                self.oh_roll_attack_button.configure(state="disabled"); self.oh_roll_damage_button.configure(state="disabled")
        else:
            name_label.configure(text="---"); damage_label.configure(text="Dano: ---")
            attack_button.configure(state="disabled"); damage_button.configure(state="disabled")

    def update_all_inventory_equip_button_states(self):
        # ... (como antes, a comparação de referência deve funcionar agora)
        for weapon_ui_el_dict in self.weapon_inventory_ui_rows:
            button = weapon_ui_el_dict.get('equip_button')
            weapon_data_ref = weapon_ui_el_dict.get('data_dict_ref') # Esta é a referência ao dict em personagem.armas_inventario
            if not button or not weapon_data_ref: continue
            is_equipped_main = (self.personagem.arma_equipada_principal == weapon_data_ref) # Compara REFERÊNCIAS
            is_equipped_off = (self.personagem.arma_equipada_secundaria == weapon_data_ref) # Compara REFERÊNCIAS
            if is_equipped_main or is_equipped_off:
                button.configure(text="Desequip.", command=lambda wd_ref=weapon_data_ref: self.perform_unequip_action_from_data(wd_ref))
            else:
                button.configure(text="Equipar", command=lambda w_data=weapon_data_ref: self.equip_weapon(w_data))
            can_equip_this_item = True
            main_is_two_handed = self.personagem.arma_equipada_principal and str(self.personagem.arma_equipada_principal.get('hands',"1")) == "2"
            if main_is_two_handed:
                if not is_equipped_main: can_equip_this_item = False
            elif self.personagem.arma_equipada_principal and self.personagem.arma_equipada_secundaria:
                if not (is_equipped_main or is_equipped_off): can_equip_this_item = False
            if not (is_equipped_main or is_equipped_off) and not can_equip_this_item: button.configure(state="disabled")
            else: button.configure(state="normal")

    def perform_unequip_action_from_data(self, weapon_data_to_unequip):
        # ... (como antes)
        if self.personagem.arma_equipada_principal == weapon_data_to_unequip: self.unequip_weapon("main")
        elif self.personagem.arma_equipada_secundaria == weapon_data_to_unequip: self.unequip_weapon("off")

    def perform_attack_roll(self, hand_slot):
        # ... (como antes)
        weapon_data = None
        if hand_slot == "main": weapon_data = self.personagem.arma_equipada_principal
        elif hand_slot == "off": weapon_data = self.personagem.arma_equipada_secundaria
        active_button_group = []; other_button_group = []
        if hand_slot == "main": active_button_group = [self.mh_roll_attack_button, self.mh_roll_damage_button]; other_button_group = [self.oh_roll_attack_button, self.oh_roll_damage_button]
        else: active_button_group = [self.oh_roll_attack_button, self.oh_roll_damage_button]; other_button_group = [self.mh_roll_attack_button, self.mh_roll_damage_button]
        for btn in active_button_group + other_button_group:
            if btn: btn.configure(state="disabled")
        if weapon_data:
            weapon_name = weapon_data.get('name',"N/A"); atk_attr_short = weapon_data.get('atk_attr',"FOR").strip().upper()
            attack_skill_name_selected = weapon_data.get('attack_skill_type',"Corpo-a-Corpo")
            attribute_name_map = {"FOR": "Força", "DES": "Destreza", "INT": "Inteligência", "SAB": "Sabedoria"}
            char_attr_name_full = attribute_name_map.get(atk_attr_short, "Força")
            try:
                attribute_value = self.attributes_skills_tab_ref.personagem.atributos.get(char_attr_name_full, 0)
                skill_value_for_attack = 1; skill_val_str = ""
                if attack_skill_name_selected == "Corpo-a-Corpo": skill_val_str = self.cac_val_var.get()
                elif attack_skill_name_selected == "Pontaria": skill_val_str = self.pontaria_val_var.get()
                elif attack_skill_name_selected == "Elemental": skill_val_str = self.elemental_val_var.get()
                skill_value_for_attack = int(skill_val_str.strip()) if skill_val_str.strip().isdigit() else 1
            except Exception as e: self.action_roll_animation_label.configure(text="Erro"); self.action_roll_result_label.configure(text=f"Dados p/ ataque: {e}"); self.re_enable_action_buttons(); return
            self.action_roll_animation_label.configure(text="")
            self.action_roll_result_label.configure(text=f"Rolando ataque ({attack_skill_name_selected}) com {weapon_name}...")
            self.animate_action_roll(0, "attack", attribute_value, skill_value_for_attack, weapon_name, hand_slot)
        else: self.action_roll_result_label.configure(text="Nenhuma arma para atacar."); self.re_enable_action_buttons()

    def roll_equipped_weapon_damage(self, hand_slot):
        # ... (como antes)
        weapon_data = None; modifier_entry_widget = None
        if hand_slot == "main": weapon_data = self.personagem.arma_equipada_principal; modifier_entry_widget = self.mh_damage_mod_entry
        elif hand_slot == "off": weapon_data = self.personagem.arma_equipada_secundaria; modifier_entry_widget = self.oh_damage_mod_entry
        active_button_group = []; other_button_group = []
        if hand_slot == "main": active_button_group = [self.mh_roll_attack_button, self.mh_roll_damage_button]; other_button_group = [self.oh_roll_attack_button, self.oh_roll_damage_button]
        else: active_button_group = [self.oh_roll_attack_button, self.oh_roll_damage_button]; other_button_group = [self.mh_roll_attack_button, self.mh_roll_damage_button]
        for btn in active_button_group + other_button_group:
            if btn: btn.configure(state="disabled")
        if weapon_data:
            weapon_name = weapon_data.get('name',"N/A"); damage_dice_str = weapon_data.get('damage_dice',"")
            try:
                mod_str = modifier_entry_widget.get()
                modifier = int(mod_str) if mod_str and (mod_str.startswith(('+', '-')) or mod_str.isdigit()) else 0
            except ValueError: modifier = 0; modifier_entry_widget.delete(0, "end"); modifier_entry_widget.insert(0, "+0")
            self.action_roll_animation_label.configure(text="")
            self.action_roll_result_label.configure(text=f"Rolando dano para {weapon_name}...")
            self.animate_action_roll(0, "damage", damage_dice_str, modifier, weapon_name, hand_slot)
        else: self.action_roll_result_label.configure(text="Nenhuma arma para rolar dano."); self.re_enable_action_buttons()
            
    def re_enable_action_buttons(self):
        # ... (como antes)
        if self.mh_roll_attack_button and self.personagem.arma_equipada_principal: self.mh_roll_attack_button.configure(state="normal")
        if self.mh_roll_damage_button and self.personagem.arma_equipada_principal: self.mh_roll_damage_button.configure(state="normal")
        if self.oh_roll_attack_button and self.personagem.arma_equipada_secundaria: self.oh_roll_attack_button.configure(state="normal")
        if self.oh_roll_damage_button and self.personagem.arma_equipada_secundaria: self.oh_roll_damage_button.configure(state="normal")
        if self.personagem.arma_equipada_principal and str(self.personagem.arma_equipada_principal.get('hands',"1")) == "2":
            if self.oh_roll_attack_button: self.oh_roll_attack_button.configure(state="disabled")
            if self.oh_roll_damage_button: self.oh_roll_damage_button.configure(state="disabled")

    def animate_action_roll(self, step, roll_type, value1, value2, item_name_for_display, hand_slot_rolled):
        # ... (como antes)
        animation_steps = 8; animation_interval = 60
        if step < animation_steps:
            temp_roll_display = random.randint(1, 20 if roll_type == "attack" else 10) 
            self.action_roll_animation_label.configure(text=str(temp_roll_display))
            self.tab_widget.after(animation_interval, self.animate_action_roll, step + 1, roll_type, value1, value2, item_name_for_display, hand_slot_rolled)
        else:
            if roll_type == "attack":
                final_d20, all_rolls = perform_attribute_test_roll(value1) 
                success_level = check_success(value2, final_d20, final_d20)
                self.action_roll_animation_label.configure(text=str(final_d20))
                roll_details = f" (Rolagens: {all_rolls})" if len(all_rolls) > 1 else ""
                crit_msg = " ACERTO CRÍTICO!" if success_level == "Sucesso Extremo" else ""
                num_dice_attr, roll_type_attr_key = get_dice_for_attribute_test(value1)
                roll_type_attr_text = ""; 
                if roll_type_attr_key == "advantage": roll_type_attr_text = " (Maior)"
                elif roll_type_attr_key == "disadvantage": roll_type_attr_text = " (Menor)"
                attr_dice_info = f"{num_dice_attr}d20{roll_type_attr_text}"
                attack_skill_name_used = "N/A"
                weapon_dict_data = self.personagem.arma_equipada_principal if hand_slot_rolled == "main" else self.personagem.arma_equipada_secundaria
                if weapon_dict_data: attack_skill_name_used = weapon_dict_data.get('attack_skill_type',"N/A")
                result_text_lines = [f"Ataque com {item_name_for_display} ({attack_skill_name_used}): {success_level}{crit_msg}",
                                     f"  Atributo Base ({value1}) -> {attr_dice_info}",
                                     f"  Valor da Perícia ({attack_skill_name_used}): {value2}", 
                                     f"  d20 Usado: {final_d20}{roll_details}"]
                self.action_roll_result_label.configure(text="\n".join(result_text_lines))
            elif roll_type == "damage":
                rolls, total_base, final_total = parse_and_roll_damage_string(value1, value2)
                if not rolls and total_base == 0 and final_total == 0 and not (value1.lstrip('-+').isdigit() and not 'd' in value1.lower()):
                    self.action_roll_animation_label.configure(text="Erro!"); self.action_roll_result_label.configure(text=f"String de dano '{value1}' inválida.")
                else:
                    self.action_roll_animation_label.configure(text=str(final_total))
                    roll_details_str = f"Rolagens: {rolls}" if rolls else "Dano Fixo"
                    mod_base_val = total_base - sum(rolls); mod_add_val = value2
                    mod_details_list = []
                    if mod_base_val != 0 : mod_details_list.append(f"Mod. Base Str: {mod_base_val:+}")
                    if mod_add_val != 0: mod_details_list.append(f"Mod. Adicional: {mod_add_val:+}")
                    mod_details_str = " (" + ", ".join(mod_details_list) + ")" if mod_details_list else ""
                    self.action_roll_result_label.configure(text=f"Dano ({item_name_for_display}): {final_total}\n{roll_details_str}{mod_details_str}")
            self.re_enable_action_buttons()

    def is_weapon_equipped_in_other_slot(self, current_hand_slot):
        if current_hand_slot == "main": return self.personagem.arma_equipada_secundaria is not None
        elif current_hand_slot == "off": 
            return self.personagem.arma_equipada_principal is not None and \
                   str(self.personagem.arma_equipada_principal.get('hands',"1")) != "2"
        return False