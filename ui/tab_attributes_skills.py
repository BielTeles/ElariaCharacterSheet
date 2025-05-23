import customtkinter as ctk
import random
from core.dice_roller import (
    perform_attribute_test_roll,
    check_success,
    get_dice_for_attribute_test
)

class AttributesSkillsTab:
    def __init__(self, tab_widget, personagem):
        self.tab_widget = tab_widget
        self.personagem = personagem 

        self.main_frame = ctk.CTkFrame(self.tab_widget)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.main_frame.columnconfigure(0, weight=1) 
        self.main_frame.columnconfigure(1, weight=2) 
        self.main_frame.rowconfigure(0, weight=1) 
        self.main_frame.rowconfigure(1, weight=0) 

        self.attr_points_frame = ctk.CTkFrame(self.main_frame)
        self.attr_points_frame.grid(row=0, column=0, padx=(0, 5), pady=(0,10), sticky="nsew")
        self.attr_points_frame.columnconfigure(0, weight=0) 
        self.attr_points_frame.columnconfigure(1, weight=0) 
        self.attr_points_frame.columnconfigure(2, weight=1) 
        
        self.attribute_entries = {}
        self.attribute_dice_labels = {}
        self.attribute_stringvars = {}

        self.skill_value_stringvars = {} 
        self.skill_trained_vars = {} 
        self.skill_widgets = {} 
        self.skill_associated_attr_labels = {}

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

    def load_data_from_personagem(self):
        if hasattr(self, 'attribute_stringvars'): 
            for attr_name_key, string_var in self.attribute_stringvars.items():
                current_val_in_obj_str = str(self.personagem.atributos.get(attr_name_key, 0))
                if string_var.get() != current_val_in_obj_str:
                    string_var.set(current_val_in_obj_str)
                else: 
                    self.on_attribute_change(attr_name_key, string_var, "ui_reload_skip_personagem_update")
        
        self.personagem.recalcular_maximos()
        if hasattr(self, 'pv_atuais_var'): 
            self.pv_atuais_var.set(str(self.personagem.pv_atuais))
            self.atualizar_display_maximos()
            self.pm_atuais_var.set(str(self.personagem.pm_atuais))
            self.vigor_atuais_var.set(str(self.personagem.vigor_atuais))

        if hasattr(self, 'skill_trained_vars') and hasattr(self, 'skill_value_stringvars'):
            for skill_name, trained_var in self.skill_trained_vars.items():
                is_trained = skill_name in self.personagem.pericias_treinadas
                if trained_var.get() != is_trained:
                    trained_var.set(is_trained)
                else:
                    self.on_skill_trained_change(skill_name, trained_var, "ui_reload_skip_personagem_update")
            for skill_name, value_var in self.skill_value_stringvars.items():
                is_trained = skill_name in self.personagem.pericias_treinadas
                default_val_if_not_found = 1 if is_trained and self.personagem.pericias_valores.get(skill_name) is None else 0
                current_val_in_obj_str = str(self.personagem.pericias_valores.get(skill_name, default_val_if_not_found))
                if value_var.get() != current_val_in_obj_str:
                    value_var.set(current_val_in_obj_str)

    def atualizar_display_maximos(self):
        if hasattr(self, 'personagem'):
            self.pv_max_var.set(str(self.personagem.pv_maximo))
            self.pm_max_var.set(str(self.personagem.pm_maximo))
            self.vigor_max_var.set(str(self.personagem.vigor_maximo))

    def _adjust_attribute_value(self, attr_name, amount):
        try:
            current_val_str = self.attribute_stringvars[attr_name].get()
            current_val = int(current_val_str) if current_val_str.lstrip('-').isdigit() else 0
            new_val = current_val + amount
            if new_val < -1: new_val = -1 
            self.attribute_stringvars[attr_name].set(str(new_val)) 
        except ValueError: self.attribute_stringvars[attr_name].set(str(self.personagem.atributos.get(attr_name,0)))
        except KeyError: print(f"Erro: Stringvar para atributo {attr_name} não encontrada.")

    def on_attribute_change(self, attr_name_key, string_var_instance, *args):
        attr_val_str = string_var_instance.get().strip()
        attr_value = 0 
        if not attr_val_str: attr_value = 0
        elif attr_val_str == "-": attr_value = 0 
        elif attr_val_str.lstrip('-').isdigit():
            try: attr_value = int(attr_val_str)
            except ValueError: attr_value = 0
        
        if "ui_reload_skip_personagem_update" not in args:
            self.personagem.atualizar_atributo(attr_name_key, attr_value) 
            self.atualizar_display_maximos()

        num_dice, roll_type_key = get_dice_for_attribute_test(attr_value)
        roll_type_text = ""
        if roll_type_key == "advantage": roll_type_text = " (Maior)"
        elif roll_type_key == "disadvantage": roll_type_text = " (Menor)"
        dice_text = f" ({num_dice}d20{roll_type_text})" 
        if attr_name_key + "_dice_label" in self.attribute_dice_labels:
            self.attribute_dice_labels[attr_name_key + "_dice_label"].configure(text=dice_text)

    def setup_attributes_points_section(self):
        title_attr_label = ctk.CTkLabel(master=self.attr_points_frame, text="Atributos", font=ctk.CTkFont(size=16, weight="bold"))
        title_attr_label.grid(row=0, column=0, columnspan=3, padx=5, pady=(5,10), sticky="n")
        attributes = ["Força", "Destreza", "Constituição", "Inteligência", "Sabedoria", "Carisma"]
        for i, attr_name in enumerate(attributes):
            label = ctk.CTkLabel(master=self.attr_points_frame, text=f"{attr_name}:")
            label.grid(row=i + 1, column=0, padx=(10,2), pady=5, sticky="e")
            attr_input_frame = ctk.CTkFrame(self.attr_points_frame, fg_color="transparent")
            attr_input_frame.grid(row=i + 1, column=1, padx=0, pady=2, sticky="w")
            attr_var = ctk.StringVar() 
            self.attribute_stringvars[attr_name] = attr_var
            attr_var.trace_add("write", lambda n_trace, i_trace, m_trace, sv=attr_var, an=attr_name: self.on_attribute_change(an, sv))
            minus_button = ctk.CTkButton(master=attr_input_frame, text="-", width=28, height=28, command=lambda name=attr_name: self._adjust_attribute_value(name, -1))
            minus_button.pack(side="left", padx=(0,1))
            entry_val = ctk.CTkEntry(master=attr_input_frame, width=40, textvariable=attr_var, justify="center", placeholder_text="0")
            entry_val.pack(side="left", padx=1)
            self.attribute_entries[attr_name + "_val"] = entry_val
            plus_button = ctk.CTkButton(master=attr_input_frame, text="+", width=28, height=28, command=lambda name=attr_name: self._adjust_attribute_value(name, 1))
            plus_button.pack(side="left", padx=(1,0))
            dice_label = ctk.CTkLabel(master=self.attr_points_frame, text="", width=120, anchor="w")
            dice_label.grid(row=i + 1, column=2, padx=(5,0), pady=5, sticky="w")
            self.attribute_dice_labels[attr_name + "_dice_label"] = dice_label
            
        points_frame = ctk.CTkFrame(self.attr_points_frame)
        points_frame.grid(row=len(attributes) + 1, column=0, columnspan=3, padx=5, pady=(15,5), sticky="ew")
        points_frame.columnconfigure(0, weight=1); points_frame.columnconfigure(1, weight=1); points_frame.columnconfigure(2, weight=0); points_frame.columnconfigure(3, weight=1)
        pv_label = ctk.CTkLabel(master=points_frame, text="PV:"); pv_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.pv_current_entry = ctk.CTkEntry(master=points_frame, placeholder_text="Atual", width=60, textvariable=self.pv_atuais_var); self.pv_current_entry.grid(row=0, column=1, padx=2, pady=5, sticky="ew")
        self.pv_atuais_var.trace_add("write", lambda n,i,m,p=self.personagem,v=self.pv_atuais_var, max_v_strvar=self.pv_max_var: self._update_current_stat(p, 'pv_atuais', v, max_v_strvar))
        ctk.CTkLabel(master=points_frame, text="/").grid(row=0, column=2, padx=0, pady=5)
        self.pv_max_label = ctk.CTkLabel(master=points_frame, textvariable=self.pv_max_var, width=60); self.pv_max_label.grid(row=0, column=3, padx=2, pady=5, sticky="ew")
        pm_label = ctk.CTkLabel(master=points_frame, text="PM:"); pm_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.pm_current_entry = ctk.CTkEntry(master=points_frame, placeholder_text="Atual", width=60, textvariable=self.pm_atuais_var); self.pm_current_entry.grid(row=1, column=1, padx=2, pady=5, sticky="ew")
        self.pm_atuais_var.trace_add("write", lambda n,i,m,p=self.personagem,v=self.pm_atuais_var, max_v_strvar=self.pm_max_var: self._update_current_stat(p, 'pm_atuais', v, max_v_strvar))
        ctk.CTkLabel(master=points_frame, text="/").grid(row=1, column=2, padx=0, pady=5)
        self.pm_max_label = ctk.CTkLabel(master=points_frame, textvariable=self.pm_max_var, width=60); self.pm_max_label.grid(row=1, column=3, padx=2, pady=5, sticky="ew")
        vigor_label = ctk.CTkLabel(master=points_frame, text="Vigor (V):"); vigor_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.vigor_current_entry = ctk.CTkEntry(master=points_frame, placeholder_text="Atual", width=60, textvariable=self.vigor_atuais_var); self.vigor_current_entry.grid(row=2, column=1, padx=2, pady=5, sticky="ew")
        self.vigor_atuais_var.trace_add("write", lambda n,i,m,p=self.personagem,v=self.vigor_atuais_var, max_v_strvar=self.vigor_max_var: self._update_current_stat(p, 'vigor_atuais', v, max_v_strvar))
        ctk.CTkLabel(master=points_frame, text="/").grid(row=2, column=2, padx=0, pady=5)
        self.vigor_max_label = ctk.CTkLabel(master=points_frame, textvariable=self.vigor_max_var, width=60); self.vigor_max_label.grid(row=2, column=3, padx=2, pady=5, sticky="ew")

    def _update_current_stat(self, personagem_obj, stat_attr_name, current_val_var, max_val_strvar, *args):
        if "ui_reload_skip_personagem_update" in args: return
        try:
            current_val = int(current_val_var.get())
            max_val = int(max_val_strvar.get()) 
            if current_val > max_val: current_val = max_val; current_val_var.set(str(max_val)) 
            elif current_val < 0: current_val = 0; current_val_var.set("0")
            setattr(personagem_obj, stat_attr_name, current_val)
        except ValueError:
            current_val_in_obj = getattr(personagem_obj, stat_attr_name, 0)
            current_val_var.set(str(current_val_in_obj))

    def _adjust_skill_value(self, skill_name, amount):
        """Ajusta o valor de uma perícia e atualiza a StringVar."""
        try:
            current_val_str = self.skill_value_stringvars[skill_name].get()
            current_val = int(current_val_str) if current_val_str.isdigit() else 0
            
            new_val = current_val + amount
            
            # Limites para valores de perícia (0 a 20+ conforme o livro)
            # O livro menciona "Valor 0 (não treinado) a 20 ou mais (maestria lendária)" pág 34.
            # E "Ser treinado significa que sua perícia começa com Valor 1"
            is_trained = self.skill_trained_vars.get(skill_name, ctk.BooleanVar(value=False)).get()
            min_val = 1 if is_trained and new_val < 1 else 0 # Se treinado, mínimo 1, senão mínimo 0.
            if new_val < min_val: new_val = min_val
            # Não vamos impor um máximo rígido aqui, pois o livro diz "20 ou mais".
            
            self.skill_value_stringvars[skill_name].set(str(new_val))
            # O trace na StringVar chamará on_skill_value_change
        except ValueError:
            is_trained = self.skill_trained_vars.get(skill_name, ctk.BooleanVar(value=False)).get()
            default_revert_val = 1 if is_trained else 0
            self.skill_value_stringvars[skill_name].set(str(self.personagem.pericias_valores.get(skill_name, default_revert_val)))
        except KeyError:
            print(f"Erro: Stringvar para perícia {skill_name} não encontrada.")

    def on_skill_value_change(self, skill_name, string_var_instance, *args):
        if "ui_reload_skip_personagem_update" in args: return 
        skill_val_str = string_var_instance.get().strip()
        new_value = 0 
        is_trained = self.skill_trained_vars.get(skill_name, ctk.BooleanVar(value=False)).get()
        
        if skill_val_str.isdigit(): 
            new_value = int(skill_val_str)
            if is_trained and new_value < 1: # Se treinado, valor não pode ser < 1
                new_value = 1
                string_var_instance.set(str(new_value)) # Corrige na UI
            elif not is_trained and new_value < 0: # Se não treinado, não pode ser < 0
                 new_value = 0
                 string_var_instance.set(str(new_value)) # Corrige na UI
        elif skill_val_str == "": 
            new_value = 1 if is_trained else 0
            string_var_instance.set(str(new_value))
        else: 
            current_val_in_obj = self.personagem.pericias_valores.get(skill_name, 1 if is_trained else 0)
            string_var_instance.set(str(current_val_in_obj)); return
        self.personagem.atualizar_pericia_valor(skill_name, new_value)

    def on_skill_trained_change(self, skill_name, boolean_var_instance, *args):
        is_trained_ui = boolean_var_instance.get()
        if "ui_reload_skip_personagem_update" not in args:
            self.personagem.marcar_pericia_treinada(skill_name, is_trained_ui)
        
        value_var = self.skill_value_stringvars.get(skill_name)
        if value_var:
            current_val_str = value_var.get()
            current_val = int(current_val_str) if current_val_str.isdigit() else 0
            if is_trained_ui and current_val < 1:
                value_var.set("1") 
            elif not is_trained_ui: # Se desmarcou
                 value_var.set("0") # Perícia não treinada tem valor 0.

    def setup_skills_section(self):
        self.skills_scroll_frame = ctk.CTkScrollableFrame(self.skills_frame_container, label_text="Perícias", label_font=ctk.CTkFont(size=16, weight="bold"))
        self.skills_scroll_frame.pack(fill="both", expand=True)
        
        # Colunas: Nome, Treinada, [+/- Valor +/-], Atributo, Botão Rolar
        self.skills_scroll_frame.columnconfigure(0, weight=3)  # Nome da Perícia
        self.skills_scroll_frame.columnconfigure(1, weight=0)  # Treinada (Checkbox)
        self.skills_scroll_frame.columnconfigure(2, weight=0)  # Frame para Valor e botões +/-
        self.skills_scroll_frame.columnconfigure(3, weight=1)  # Atributo Chave
        self.skills_scroll_frame.columnconfigure(4, weight=0)  # Botão de Rolagem

        skill_list_data = [ 
            ("Acrobacia", "DES", "Destreza"), ("Adestramento", "CAR", "Carisma"), ("Atletismo", "FOR", "Força"),
            ("Atuação", "CAR", "Carisma"), ("Bloqueio", "CON", "Constituição"), ("Cavalgar", "DES", "Destreza"),
            ("Conhecimento (Arcano)", "INT", "Inteligência"), ("Conhecimento (História)", "INT", "Inteligência"),
            ("Conhecimento (Natureza)", "INT", "Inteligência"), ("Conhecimento (Religião)", "INT", "Inteligência"),
            ("Conhecimento (Geografia)", "INT", "Inteligência"), ("Conhecimento (Reinos)", "INT", "Inteligência"),
            ("Corpo-a-Corpo", "DES/FOR", "Força"), ("Cura", "SAB", "Sabedoria"), ("Diplomacia", "CAR", "Carisma"),
            ("Elemental", "INT/SAB", "Inteligência"), ("Enganação", "CAR", "Carisma"), ("Esquiva", "DES", "Destreza"),
            ("Fortitude", "CON", "Constituição"), ("Furtividade", "DES", "Destreza"), ("Guerra", "INT", "Inteligência"),
            ("Iniciativa", "DES", "Destreza"), ("Intimidação", "CAR", "Carisma"), ("Intuição", "SAB", "Sabedoria"),
            ("Investigação", "INT", "Inteligência"), ("Jogatina", "CAR", "Carisma"), ("Ladinagem", "DES", "Destreza"),
            ("Misticismo", "INT", "Inteligência"), ("Nobreza", "INT", "Inteligência"), ("Percepção", "SAB", "Sabedoria"),
            ("Pontaria", "DES", "Destreza"), ("Reflexos", "DES", "Destreza"), ("Sobrevivência", "SAB", "Sabedoria"),
            ("Vontade", "SAB", "Sabedoria")
        ]

        for i, (skill_name, key_attr_display, key_attr_lookup) in enumerate(skill_list_data):
            name_label = ctk.CTkLabel(master=self.skills_scroll_frame, text=skill_name, anchor="w")
            name_label.grid(row=i, column=0, padx=5, pady=3, sticky="ew")

            trained_var = ctk.BooleanVar()
            trained_var.trace_add("write", lambda n,idx,m,bv=trained_var,sn=skill_name: self.on_skill_trained_change(sn,bv))
            trained_check = ctk.CTkCheckBox(master=self.skills_scroll_frame, text="", width=20, variable=trained_var)
            trained_check.grid(row=i, column=1, padx=5, pady=3, sticky="w")
            self.skill_trained_vars[skill_name] = trained_var
            self.skill_widgets[skill_name + "_trained_cb"] = trained_check

            # --- Frame para valor da perícia e botões +/- ---
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
            # --- Fim do Frame de valor da perícia ---

            attr_label = ctk.CTkLabel(master=self.skills_scroll_frame, text=f"({key_attr_display})", anchor="w")
            attr_label.grid(row=i, column=3, padx=5, pady=3, sticky="w")
            self.skill_associated_attr_labels[skill_name] = key_attr_lookup

            roll_button = ctk.CTkButton(
                master=self.skills_scroll_frame, text="🎲", width=30, height=28,
                command=lambda s_name=skill_name, attr_key=key_attr_lookup: self.roll_specific_skill(s_name, attr_key)
            )
            roll_button.grid(row=i, column=4, padx=5, pady=3, sticky="e")
            self.skill_widgets[skill_name + "_roll_button"] = roll_button


    def setup_dice_roll_result_display_section(self):
        # ... (como antes)
        result_display_frame = ctk.CTkFrame(self.main_frame); result_display_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=(5,0), sticky="ew")
        result_display_frame.columnconfigure(0, weight=0); result_display_frame.columnconfigure(1, weight=1)
        self.dice_animation_label = ctk.CTkLabel(master=result_display_frame, text="", width=60, height=30, font=ctk.CTkFont(size=24, weight="bold")); self.dice_animation_label.grid(row=0, column=0, padx=(10,5), pady=5, sticky="w")
        self.roll_result_label = ctk.CTkLabel(master=result_display_frame, text="Clique em 🎲 para testar uma perícia.", justify="left", height=30, anchor="w", font=ctk.CTkFont(size=14)); self.roll_result_label.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    def roll_specific_skill(self, skill_name, associated_attribute_name_lookup):
        # ... (como antes)
        skill_val_str = self.skill_value_stringvars.get(skill_name).get()
        skill_value_to_test = int(skill_val_str) if skill_val_str.strip().isdigit() else 1
        attr_var = self.attribute_stringvars.get(associated_attribute_name_lookup)
        attr_val_str = attr_var.get().strip() if attr_var else "0"
        attribute_value_to_test = int(attr_val_str) if attr_val_str and attr_val_str.lstrip('-').isdigit() else 0
        for widget_key in self.skill_widgets:
            if widget_key.endswith("_roll_button"): self.skill_widgets[widget_key].configure(state="disabled")
        self.start_dice_roll_animation(attribute_value_to_test, skill_value_to_test, skill_name)

    def start_dice_roll_animation(self, attribute_value, skill_value, skill_name_for_display="Teste"):
        # ... (como antes)
        self.dice_animation_label.configure(text="")
        self.roll_result_label.configure(text=f"Rolando {skill_name_for_display}...")
        self.animate_dice(0, attribute_value, skill_value, skill_name_for_display)

    def animate_dice(self, step, attribute_value, skill_value, skill_name_for_display):
        # ... (como antes)
        animation_steps = 8; animation_interval = 60
        if step < animation_steps:
            num = random.randint(1, 20); self.dice_animation_label.configure(text=str(num))
            self.tab_widget.after(animation_interval, self.animate_dice, step + 1, attribute_value, skill_value, skill_name_for_display)
        else:
            final_d20, all_rolls = perform_attribute_test_roll(attribute_value)
            success_level = check_success(skill_value, final_d20, final_d20)
            self.dice_animation_label.configure(text=str(final_d20))
            roll_details = f" (Rolagens: {all_rolls})" if len(all_rolls) > 1 else ""
            num_dice_attr, roll_type_attr_key = get_dice_for_attribute_test(attribute_value)
            roll_type_attr_text = ""; 
            if roll_type_attr_key == "advantage": roll_type_attr_text = " (Maior)"
            elif roll_type_attr_key == "disadvantage": roll_type_attr_text = " (Menor)"
            attr_dice_info = f"{num_dice_attr}d20{roll_type_attr_text}"
            result_text_lines = [f"Perícia: {skill_name_for_display} (Valor {skill_value})",
                                 f"Atributo base: {attribute_value} -> {attr_dice_info}",
                                 f"d20 Usado: {final_d20}{roll_details}",
                                 f"Resultado: {success_level}"]
            self.roll_result_label.configure(text="\n".join(result_text_lines))
            for widget_key in self.skill_widgets:
                if widget_key.endswith("_roll_button"): self.skill_widgets[widget_key].configure(state="normal")