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
        self.attr_points_frame.columnconfigure(1, weight=1) 
        
        # Dicionários para guardar referências
        self.attribute_entries = {} # Para os widgets CTkEntry dos atributos
        self.attribute_dice_labels = {} # Para os CTkLabels dos dados de vantagem/desvantagem
        self.attribute_stringvars = {} # Para as StringVars dos atributos

        self.skill_value_stringvars = {} 
        self.skill_trained_vars = {} 
        self.skill_widgets = {} # Para outros widgets de perícia (botões, etc.)
        self.skill_associated_attr_labels = {} # Mapeia nome da perícia para nome do atributo de lookup

        # StringVars para PV/PM/Vigor (serão ligadas aos widgets)
        self.pv_atuais_var = ctk.StringVar()
        self.pv_max_var = ctk.StringVar() # Será um Label, apenas para display do valor do personagem
        self.pm_atuais_var = ctk.StringVar()
        self.pm_max_var = ctk.StringVar() # Será um Label
        self.vigor_atuais_var = ctk.StringVar()
        self.vigor_max_var = ctk.StringVar() # Será um Label

        self.setup_attributes_points_section()

        self.skills_frame_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.skills_frame_container.grid(row=0, column=1, padx=(5, 0), pady=0, sticky="nsew")
        self.skills_frame_container.rowconfigure(0, weight=1)
        self.setup_skills_section() # Cria os widgets das perícias

        self.setup_dice_roll_result_display_section()
        
        self.load_data_from_personagem() # Carrega os dados iniciais do personagem para a UI

    def load_data_from_personagem(self):
        """Carrega/Recarrega dados do self.personagem para os campos da UI desta aba."""
        # Atributos
        if hasattr(self, 'attribute_stringvars'): 
            for attr_name_key, string_var in self.attribute_stringvars.items():
                current_val_in_obj_str = str(self.personagem.atributos.get(attr_name_key, 0))
                # Atualiza a StringVar sem disparar o trace de escrita no objeto Personagem desnecessariamente
                # A chamada subsequente a on_attribute_change com o sinalizador cuidará da atualização do label de dados.
                string_var.set(current_val_in_obj_str)
                self.on_attribute_change(attr_name_key, string_var, "ui_reload_skip_personagem_update")

        # PV, PM, Vigor
        if hasattr(self, 'pv_atuais_var'): 
            self.pv_atuais_var.set(str(self.personagem.pv_atuais))
            self.pv_max_var.set(str(self.personagem.pv_maximo)) 
            self.pm_atuais_var.set(str(self.personagem.pm_atuais))
            self.pm_max_var.set(str(self.personagem.pm_maximo))
            self.vigor_atuais_var.set(str(self.personagem.vigor_atuais))
            self.vigor_max_var.set(str(self.personagem.vigor_maximo))

        # Perícias
        if hasattr(self, 'skill_trained_vars') and hasattr(self, 'skill_value_stringvars'):
            for skill_name, trained_var in self.skill_trained_vars.items():
                is_trained = skill_name in self.personagem.pericias_treinadas
                trained_var.set(is_trained) 
                # A trace de trained_var chamará on_skill_trained_change.
                # Vamos chamar explicitamente para garantir a lógica de valor base ao carregar.
                self.on_skill_trained_change(skill_name, trained_var, "ui_reload_skip_personagem_update")


            for skill_name, value_var in self.skill_value_stringvars.items():
                is_trained = skill_name in self.personagem.pericias_treinadas
                default_val_if_not_found = 1 if is_trained and self.personagem.pericias_valores.get(skill_name) is None else 0
                current_val_in_obj_str = str(self.personagem.pericias_valores.get(skill_name, default_val_if_not_found))
                value_var.set(current_val_in_obj_str)
                # A trace de value_var chamará on_skill_value_change.

    def on_attribute_change(self, attr_name_key, string_var_instance, *args):
        attr_val_str = string_var_instance.get().strip()
        attr_value = 0 
        if not attr_val_str: attr_value = 0
        elif attr_val_str == "-": attr_value = 0 
        elif attr_val_str.lstrip('-').isdigit():
            try: attr_value = int(attr_val_str)
            except ValueError: attr_value = 0
        
        if "ui_reload_skip_personagem_update" not in args:
            # Só atualiza o objeto Personagem se a mudança veio da UI diretamente,
            # não de um recarregamento programático da UI.
            self.personagem.atualizar_atributo(attr_name_key, attr_value)

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
            label.grid(row=i + 1, column=0, padx=5, pady=5, sticky="e")

            attr_var = ctk.StringVar() # Valor será setado por load_data_from_personagem
            self.attribute_stringvars[attr_name] = attr_var
            # A lambda agora passa os argumentos de trace para on_attribute_change
            attr_var.trace_add("write", lambda n_trace, i_trace, m_trace, sv=attr_var, an=attr_name: self.on_attribute_change(an, sv))

            entry_val = ctk.CTkEntry(master=self.attr_points_frame, width=50, textvariable=attr_var, placeholder_text="0")
            entry_val.grid(row=i + 1, column=1, padx=5, pady=5, sticky="w")
            self.attribute_entries[attr_name + "_val"] = entry_val

            dice_label = ctk.CTkLabel(master=self.attr_points_frame, text="", width=120, anchor="w")
            dice_label.grid(row=i + 1, column=2, padx=5, pady=5, sticky="w")
            self.attribute_dice_labels[attr_name + "_dice_label"] = dice_label
            
        # --- PV, PM, Vigor ---
        points_frame = ctk.CTkFrame(self.attr_points_frame)
        points_frame.grid(row=len(attributes) + 1, column=0, columnspan=3, padx=5, pady=(15,5), sticky="ew")
        points_frame.columnconfigure(0, weight=1); points_frame.columnconfigure(1, weight=1)
        points_frame.columnconfigure(2, weight=0); points_frame.columnconfigure(3, weight=1)

        pv_label = ctk.CTkLabel(master=points_frame, text="PV:")
        pv_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.pv_current_entry = ctk.CTkEntry(master=points_frame, placeholder_text="Atual", width=60, textvariable=self.pv_atuais_var)
        self.pv_current_entry.grid(row=0, column=1, padx=2, pady=5, sticky="ew")
        self.pv_atuais_var.trace_add("write", lambda n,i,m,p=self.personagem,v=self.pv_atuais_var: setattr(p, 'pv_atuais', int(v.get()) if v.get().strip().isdigit() else p.pv_atuais ))
        ctk.CTkLabel(master=points_frame, text="/").grid(row=0, column=2, padx=0, pady=5)
        self.pv_max_label = ctk.CTkLabel(master=points_frame, textvariable=self.pv_max_var, width=60)
        self.pv_max_label.grid(row=0, column=3, padx=2, pady=5, sticky="ew")

        pm_label = ctk.CTkLabel(master=points_frame, text="PM:")
        pm_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.pm_current_entry = ctk.CTkEntry(master=points_frame, placeholder_text="Atual", width=60, textvariable=self.pm_atuais_var)
        self.pm_current_entry.grid(row=1, column=1, padx=2, pady=5, sticky="ew")
        self.pm_atuais_var.trace_add("write", lambda n,i,m,p=self.personagem,v=self.pm_atuais_var: setattr(p, 'pm_atuais', int(v.get()) if v.get().strip().isdigit() else p.pm_atuais))
        ctk.CTkLabel(master=points_frame, text="/").grid(row=1, column=2, padx=0, pady=5)
        self.pm_max_label = ctk.CTkLabel(master=points_frame, textvariable=self.pm_max_var, width=60)
        self.pm_max_label.grid(row=1, column=3, padx=2, pady=5, sticky="ew")

        vigor_label = ctk.CTkLabel(master=points_frame, text="Vigor (V):")
        vigor_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.vigor_current_entry = ctk.CTkEntry(master=points_frame, placeholder_text="Atual", width=60, textvariable=self.vigor_atuais_var)
        self.vigor_current_entry.grid(row=2, column=1, padx=2, pady=5, sticky="ew")
        self.vigor_atuais_var.trace_add("write", lambda n,i,m,p=self.personagem,v=self.vigor_atuais_var: setattr(p, 'vigor_atuais', int(v.get()) if v.get().strip().isdigit() else p.vigor_atuais))
        ctk.CTkLabel(master=points_frame, text="/").grid(row=2, column=2, padx=0, pady=5)
        self.vigor_max_label = ctk.CTkLabel(master=points_frame, textvariable=self.vigor_max_var, width=60)
        self.vigor_max_label.grid(row=2, column=3, padx=2, pady=5, sticky="ew")

    def on_skill_value_change(self, skill_name, string_var_instance, *args):
        if "ui_reload_skip_personagem_update" in args: return 
        
        skill_val_str = string_var_instance.get().strip()
        new_value = 0 # Padrão se não for número ou vazio
        is_trained = self.skill_trained_vars.get(skill_name, ctk.BooleanVar(value=False)).get() # Pega o estado de treinamento

        if skill_val_str.isdigit():
            new_value = int(skill_val_str)
        elif skill_val_str == "": # Se apagar o campo
            new_value = 1 if is_trained else 0 # Volta para 1 se treinado, senão 0
            string_var_instance.set(str(new_value)) # Atualiza a UI para refletir
        else: 
            current_val_in_obj = self.personagem.pericias_valores.get(skill_name, 1 if is_trained else 0)
            string_var_instance.set(str(current_val_in_obj)) # Reverte na UI para o valor do objeto
            print(f"Valor de perícia inválido '{skill_val_str}' para {skill_name}. Revertido.")
            return # Não atualiza o objeto com valor inválido

        self.personagem.atualizar_pericia_valor(skill_name, new_value)

    def on_skill_trained_change(self, skill_name, boolean_var_instance, *args):
        is_trained = boolean_var_instance.get()
        
        if "ui_reload_skip_personagem_update" not in args:
            self.personagem.marcar_pericia_treinada(skill_name, is_trained)
        
        # Se marcou como treinado e o valor atual é 0 (ou menor que 1), define para 1.
        # Se desmarcou, o valor da perícia agora é 0 se era 1 (de treinamento).
        value_var = self.skill_value_stringvars.get(skill_name)
        if value_var: # Garante que a string_var do valor existe
            current_val_str = value_var.get()
            current_val = int(current_val_str) if current_val_str.isdigit() else 0

            if is_trained and current_val < 1:
                value_var.set("1") # Isso vai disparar on_skill_value_change que atualizará o objeto Personagem
            elif not is_trained: # Se desmarcou como treinado
                 # Se o valor era 1 (presumivelmente por ser treinado), zera.
                 # Se o jogador investiu pontos além de 1, não zeramos, ele perde o "treinamento" mas mantém os pontos.
                 # O livro (p34) diz "Valor 0 (não treinado)". "Treinado = Valor 1 (custo 0)".
                 # Então, se não é treinado, o valor mínimo deveria ser 0.
                 # Se ele tinha pontos, esses pontos permanecem, mas sem o benefício de ser "treinado"
                 # (que no nosso sistema é o valor base 1 e a permissão para aumentar).
                 # Para simplificar: se desmarcar, e o valor era 1, pode-se setar para 0.
                 # Se era >1, mantém, mas o sistema de gasto de pontos pode impedir aumentos futuros sem ser treinado.
                if current_val == 1: # Se era 1 apenas por ser treinado
                     value_var.set("0")


    def setup_skills_section(self):
        self.skills_scroll_frame = ctk.CTkScrollableFrame(self.skills_frame_container, label_text="Perícias", label_font=ctk.CTkFont(size=16, weight="bold"))
        self.skills_scroll_frame.pack(fill="both", expand=True)
        
        self.skills_scroll_frame.columnconfigure(0, weight=3); self.skills_scroll_frame.columnconfigure(1, weight=0)
        self.skills_scroll_frame.columnconfigure(2, weight=0); self.skills_scroll_frame.columnconfigure(3, weight=1)
        self.skills_scroll_frame.columnconfigure(4, weight=0)

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

            value_var = ctk.StringVar() 
            value_var.trace_add("write", lambda n,idx,m,sv=value_var,sn=skill_name: self.on_skill_value_change(sn,sv))
            value_entry = ctk.CTkEntry(master=self.skills_scroll_frame, width=40, placeholder_text="0", textvariable=value_var)
            value_entry.grid(row=i, column=2, padx=5, pady=3, sticky="w")
            self.skill_value_stringvars[skill_name] = value_var
            self.skill_widgets[skill_name + "_value_entry"] = value_entry

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
        result_display_frame = ctk.CTkFrame(self.main_frame)
        result_display_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=(5,0), sticky="ew")
        result_display_frame.columnconfigure(0, weight=0); result_display_frame.columnconfigure(1, weight=1)
        self.dice_animation_label = ctk.CTkLabel(master=result_display_frame, text="", width=60, height=30, font=ctk.CTkFont(size=24, weight="bold")); self.dice_animation_label.grid(row=0, column=0, padx=(10,5), pady=5, sticky="w")
        self.roll_result_label = ctk.CTkLabel(master=result_display_frame, text="Clique em 🎲 para testar uma perícia.", justify="left", height=30, anchor="w", font=ctk.CTkFont(size=14)); self.roll_result_label.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    def roll_specific_skill(self, skill_name, associated_attribute_name_lookup):
        skill_val_str = self.skill_value_stringvars.get(skill_name).get()
        skill_value_to_test = int(skill_val_str) if skill_val_str.strip().isdigit() else 1
        
        attr_var = self.attribute_stringvars.get(associated_attribute_name_lookup)
        attr_val_str = attr_var.get().strip() if attr_var else "0"
        attribute_value_to_test = int(attr_val_str) if attr_val_str and attr_val_str.lstrip('-').isdigit() else 0
        
        for widget_key in self.skill_widgets:
            if widget_key.endswith("_roll_button"): self.skill_widgets[widget_key].configure(state="disabled")
        self.start_dice_roll_animation(attribute_value_to_test, skill_value_to_test, skill_name)

    def start_dice_roll_animation(self, attribute_value, skill_value, skill_name_for_display="Teste"):
        self.dice_animation_label.configure(text="")
        self.roll_result_label.configure(text=f"Rolando {skill_name_for_display}...")
        self.animate_dice(0, attribute_value, skill_value, skill_name_for_display)

    def animate_dice(self, step, attribute_value, skill_value, skill_name_for_display):
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