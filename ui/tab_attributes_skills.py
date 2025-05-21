import customtkinter as ctk
import random
from core.dice_roller import perform_attribute_test_roll, check_success, get_dice_for_attribute_test

class AttributesSkillsTab:
    def __init__(self, tab_widget):
        self.tab_widget = tab_widget

        # --- Frame Principal para a Aba ---
        self.main_frame = ctk.CTkFrame(self.tab_widget)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.main_frame.columnconfigure(0, weight=1) # Coluna para Atributos/PV/PM
        self.main_frame.columnconfigure(1, weight=2) # Coluna para Perícias (será mais larga)
        self.main_frame.rowconfigure(0, weight=1) # Linha para Atributos e Perícias (para expandir)
        self.main_frame.rowconfigure(1, weight=0) # Linha para a seção de resultados da rolagem (tamanho fixo)

        # --- Seção de Atributos e Pontos ---
        self.attr_points_frame = ctk.CTkFrame(self.main_frame)
        self.attr_points_frame.grid(row=0, column=0, padx=(0, 5), pady=(0,10), sticky="nsew")
        self.attr_points_frame.columnconfigure(1, weight=1) # Para os campos de entrada dos atributos

        # Dicionários para guardar referências
        self.attribute_entries = {}
        self.attribute_dice_labels = {}
        self.attribute_stringvars = {} # Para StringVars dos atributos

        self.skill_value_entries = {}
        self.skill_associated_attr_labels = {} # Guarda o NOME do atributo para lookup
        self.skill_widgets = {} # Guarda outros widgets de perícia (botões, checkboxes)


        self.setup_attributes_points_section()

        # --- Seção de Perícias ---
        self.skills_frame_container = ctk.CTkFrame(self.main_frame, fg_color="transparent") # Container para o scrollable
        self.skills_frame_container.grid(row=0, column=1, padx=(5, 0), pady=0, sticky="nsew")
        self.skills_frame_container.rowconfigure(0, weight=1) # Para o scrollable frame expandir
        self.setup_skills_section()

        # --- Seção de Exibição de Resultados da Rolagem ---
        self.setup_dice_roll_result_display_section()

    def on_attribute_change(self, attr_name_key, string_var_instance, *args):
        """Callback quando o valor de um atributo (StringVar) muda."""
        attr_val_str = string_var_instance.get().strip()
        
        attr_value = 0 # Valor padrão
        if not attr_val_str: 
            attr_value = 0
        elif attr_val_str == "-": 
            attr_value = 0 
        elif attr_val_str.lstrip('-').isdigit(): 
            try:
                attr_value = int(attr_val_str)
            except ValueError:
                attr_value = 0
        
        num_dice, roll_type_key = get_dice_for_attribute_test(attr_value)
        
        roll_type_text = ""
        if roll_type_key == "advantage":
            roll_type_text = " (Maior)"
        elif roll_type_key == "disadvantage":
            roll_type_text = " (Menor)"

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

            attr_var = ctk.StringVar(value="0")
            self.attribute_stringvars[attr_name] = attr_var
            attr_var.trace_add("write", lambda name_arg, index_arg, mode_arg, sv=attr_var, an=attr_name: self.on_attribute_change(an, sv))

            entry_val = ctk.CTkEntry(master=self.attr_points_frame, width=50, textvariable=attr_var)
            entry_val.grid(row=i + 1, column=1, padx=5, pady=5, sticky="w")
            self.attribute_entries[attr_name + "_val"] = entry_val

            dice_label = ctk.CTkLabel(master=self.attr_points_frame, text=" (1d20)", width=120, anchor="w")
            dice_label.grid(row=i + 1, column=2, padx=5, pady=5, sticky="w")
            self.attribute_dice_labels[attr_name + "_dice_label"] = dice_label
            
            self.on_attribute_change(attr_name, attr_var)

        points_frame = ctk.CTkFrame(self.attr_points_frame)
        points_frame.grid(row=len(attributes) + 1, column=0, columnspan=3, padx=5, pady=(15,5), sticky="ew")
        points_frame.columnconfigure(0, weight=1); points_frame.columnconfigure(1, weight=1)
        points_frame.columnconfigure(2, weight=0); points_frame.columnconfigure(3, weight=1) # Ajuste para / ficar centrado

        pv_label = ctk.CTkLabel(master=points_frame, text="PV:")
        pv_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.pv_current_entry = ctk.CTkEntry(master=points_frame, placeholder_text="Atual", width=60)
        self.pv_current_entry.grid(row=0, column=1, padx=2, pady=5, sticky="ew")
        ctk.CTkLabel(master=points_frame, text="/").grid(row=0, column=2, padx=0, pady=5)
        self.pv_max_entry = ctk.CTkEntry(master=points_frame, placeholder_text="Máx", width=60)
        self.pv_max_entry.grid(row=0, column=3, padx=2, pady=5, sticky="ew")

        pm_label = ctk.CTkLabel(master=points_frame, text="PM:")
        pm_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.pm_current_entry = ctk.CTkEntry(master=points_frame, placeholder_text="Atual", width=60)
        self.pm_current_entry.grid(row=1, column=1, padx=2, pady=5, sticky="ew")
        ctk.CTkLabel(master=points_frame, text="/").grid(row=1, column=2, padx=0, pady=5)
        self.pm_max_entry = ctk.CTkEntry(master=points_frame, placeholder_text="Máx", width=60)
        self.pm_max_entry.grid(row=1, column=3, padx=2, pady=5, sticky="ew")

        vigor_label = ctk.CTkLabel(master=points_frame, text="Vigor (V):")
        vigor_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.vigor_current_entry = ctk.CTkEntry(master=points_frame, placeholder_text="Atual", width=60)
        self.vigor_current_entry.grid(row=2, column=1, padx=2, pady=5, sticky="ew")
        ctk.CTkLabel(master=points_frame, text="/").grid(row=2, column=2, padx=0, pady=5)
        self.vigor_max_entry = ctk.CTkEntry(master=points_frame, placeholder_text="Máx", width=60)
        self.vigor_max_entry.grid(row=2, column=3, padx=2, pady=5, sticky="ew")

    def setup_skills_section(self):
        self.skills_scroll_frame = ctk.CTkScrollableFrame(self.skills_frame_container, label_text="Perícias", label_font=ctk.CTkFont(size=16, weight="bold"))
        self.skills_scroll_frame.pack(fill="both", expand=True)
        
        self.skills_scroll_frame.columnconfigure(0, weight=3)
        self.skills_scroll_frame.columnconfigure(1, weight=0)
        self.skills_scroll_frame.columnconfigure(2, weight=0)
        self.skills_scroll_frame.columnconfigure(3, weight=1)
        self.skills_scroll_frame.columnconfigure(4, weight=0)

        skill_list_data = [ 
            ("Acrobacia", "DES", "Destreza"), ("Adestramento", "CAR", "Carisma"), ("Atletismo", "FOR", "Força"),
            ("Atuação", "CAR", "Carisma"), ("Bloqueio", "CON", "Constituição"), ("Cavalgar", "DES", "Destreza"),
            ("Conhecimento (Arcano)", "INT", "Inteligência"), ("Conhecimento (História)", "INT", "Inteligência"),
            ("Conhecimento (Natureza)", "INT", "Inteligência"), ("Conhecimento (Religião)", "INT", "Inteligência"),
            ("Conhecimento (Geografia)", "INT", "Inteligência"), ("Conhecimento (Reinos)", "INT", "Inteligência"),
            ("Corpo-a-Corpo", "DES/FOR", "Força"), 
            ("Cura", "SAB", "Sabedoria"), ("Diplomacia", "CAR", "Carisma"),
            ("Elemental", "INT/SAB", "Inteligência"), 
            ("Enganação", "CAR", "Carisma"), ("Esquiva", "DES", "Destreza"),
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

            trained_check = ctk.CTkCheckBox(master=self.skills_scroll_frame, text="", width=20)
            trained_check.grid(row=i, column=1, padx=5, pady=3, sticky="w")
            self.skill_widgets[skill_name + "_trained"] = trained_check

            value_entry = ctk.CTkEntry(master=self.skills_scroll_frame, width=40, placeholder_text="0")
            value_entry.grid(row=i, column=2, padx=5, pady=3, sticky="w")
            self.skill_value_entries[skill_name] = value_entry

            attr_label = ctk.CTkLabel(master=self.skills_scroll_frame, text=f"({key_attr_display})", anchor="w")
            attr_label.grid(row=i, column=3, padx=5, pady=3, sticky="w")
            self.skill_associated_attr_labels[skill_name] = key_attr_lookup

            roll_button = ctk.CTkButton(
                master=self.skills_scroll_frame,
                text="🎲", 
                width=30,
                height=28,
                command=lambda s_name=skill_name, attr_key=key_attr_lookup: self.roll_specific_skill(s_name, attr_key)
            )
            roll_button.grid(row=i, column=4, padx=5, pady=3, sticky="e")
            self.skill_widgets[skill_name + "_roll_button"] = roll_button

    def setup_dice_roll_result_display_section(self):
        result_display_frame = ctk.CTkFrame(self.main_frame)
        result_display_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=(5,0), sticky="ew")
        result_display_frame.columnconfigure(0, weight=0) # Label do dado
        result_display_frame.columnconfigure(1, weight=1) # Label do resultado (para expandir)


        self.dice_animation_label = ctk.CTkLabel(master=result_display_frame, text="", width=60, height=30, font=ctk.CTkFont(size=24, weight="bold"))
        self.dice_animation_label.grid(row=0, column=0, padx=(10,5), pady=5, sticky="w")

        self.roll_result_label = ctk.CTkLabel(master=result_display_frame, text="Clique em 🎲 para testar uma perícia.", justify="left", height=30, anchor="w", font=ctk.CTkFont(size=14))
        self.roll_result_label.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    def roll_specific_skill(self, skill_name, associated_attribute_name):
        try:
            skill_val_str = self.skill_value_entries.get(skill_name).get()
            skill_value_to_test = int(skill_val_str) if skill_val_str.strip() else 1
        except (AttributeError, ValueError, TypeError):
            skill_value_to_test = 1 

        try:
            # Acessa a StringVar do atributo e depois pega seu valor
            attr_var = self.attribute_stringvars.get(associated_attribute_name)
            attr_val_str = attr_var.get().strip() if attr_var else "0"
            
            attribute_value_to_test = 0 # Padrão
            if not attr_val_str:
                attribute_value_to_test = 0
            elif attr_val_str == "-":
                attribute_value_to_test = 0
            elif attr_val_str.lstrip('-').isdigit():
                attribute_value_to_test = int(attr_val_str)
                
        except (AttributeError, ValueError, TypeError):
            attribute_value_to_test = 0

        for widget_key in self.skill_widgets:
            if widget_key.endswith("_roll_button"):
                self.skill_widgets[widget_key].configure(state="disabled")
        
        self.start_dice_roll_animation(attribute_value_to_test, skill_value_to_test, skill_name)

    def start_dice_roll_animation(self, attribute_value, skill_value, skill_name_for_display="Teste"):
        self.dice_animation_label.configure(text="")
        self.roll_result_label.configure(text=f"Rolando {skill_name_for_display}...")
        self.animate_dice(0, attribute_value, skill_value, skill_name_for_display)

    def animate_dice(self, step, attribute_value, skill_value, skill_name_for_display):
        animation_duration_steps = 8 
        animation_interval_ms = 60  
        if step < animation_duration_steps:
            num = random.randint(1, 20)
            self.dice_animation_label.configure(text=str(num))
            self.tab_widget.after(animation_interval_ms, self.animate_dice, step + 1, attribute_value, skill_value, skill_name_for_display)
        else:
            final_d20, all_rolls = perform_attribute_test_roll(attribute_value)
            success_level = check_success(skill_value, final_d20, final_d20)

            self.dice_animation_label.configure(text=str(final_d20))
            roll_details = f" (Rolagens: {all_rolls})" if len(all_rolls) > 1 else ""
            
            result_text_lines = [f"Perícia: {skill_name_for_display} (Valor {skill_value})",
                                 f"Atributo base: {attribute_value} -> {get_dice_for_attribute_test(attribute_value)[0]}d20 {get_dice_for_attribute_test(attribute_value)[1].replace('advantage','Maior').replace('disadvantage','Menor').replace('normal','Normal')}",
                                 f"d20 Usado: {final_d20}{roll_details}",
                                 f"Resultado: {success_level}"]
            self.roll_result_label.configure(text="\n".join(result_text_lines))

            for widget_key in self.skill_widgets:
                if widget_key.endswith("_roll_button"):
                    self.skill_widgets[widget_key].configure(state="normal")