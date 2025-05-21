import customtkinter as ctk

class MagicTab:
    def __init__(self, tab_widget):
        self.tab_widget = tab_widget
        self.spell_widgets_list = [] # Para guardar referências aos frames das magias

        # --- Frame Principal para a Aba de Magia ---
        self.main_frame = ctk.CTkFrame(self.tab_widget, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True)
        self.main_frame.columnconfigure(0, weight=1) # Coluna para informações gerais de magia
        self.main_frame.columnconfigure(1, weight=2) # Coluna para a lista de magias (mais larga)
        self.main_frame.rowconfigure(1, weight=1)    # Para a lista de magias expandir verticalmente


        # --- Seção de Informações Gerais de Magia ---
        self.setup_magic_info_section()

        # --- Seção da Lista de Magias/Habilidades ---
        self.setup_spells_list_section()


    def setup_magic_info_section(self):
        info_frame = ctk.CTkFrame(self.main_frame)
        info_frame.grid(row=0, column=0, padx=10, pady=10, sticky="new")
        info_frame.columnconfigure(1, weight=1) # Para os campos de entrada

        title_info_label = ctk.CTkLabel(master=info_frame, text="Recursos Mágicos", font=ctk.CTkFont(size=16, weight="bold"))
        title_info_label.grid(row=0, column=0, columnspan=2, padx=5, pady=(5,10), sticky="n")

        # Pontos de Mana (PM)
        pm_label = ctk.CTkLabel(master=info_frame, text="Pontos de Mana (PM):")
        pm_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        
        pm_sub_frame = ctk.CTkFrame(info_frame, fg_color="transparent") # Frame para Atual/Max
        pm_sub_frame.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        self.pm_current_entry = ctk.CTkEntry(master=pm_sub_frame, placeholder_text="Atual", width=60)
        self.pm_current_entry.pack(side="left", padx=(0,2))
        separator_pm = ctk.CTkLabel(master=pm_sub_frame, text="/")
        separator_pm.pack(side="left", padx=2)
        self.pm_max_entry = ctk.CTkEntry(master=pm_sub_frame, placeholder_text="Máx", width=60)
        self.pm_max_entry.pack(side="left", padx=(2,0))

        # Atributo Chave de Magia
        key_attr_label = ctk.CTkLabel(master=info_frame, text="Atributo Chave Magia:")
        key_attr_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.key_magic_attr_entry = ctk.CTkEntry(master=info_frame, placeholder_text="Ex: SAB, INT")
        self.key_magic_attr_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        # CD de Resistência de Magia
        save_dc_label = ctk.CTkLabel(master=info_frame, text="CD Teste Resist. Magia:")
        save_dc_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.magic_save_dc_entry = ctk.CTkEntry(master=info_frame, placeholder_text="Ex: Normal")
        self.magic_save_dc_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        # Bônus de Ataque Mágico
        attack_bonus_label = ctk.CTkLabel(master=info_frame, text="Bônus Ataque Mágico:")
        attack_bonus_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.magic_attack_bonus_entry = ctk.CTkEntry(master=info_frame, placeholder_text="Ex: +5")
        self.magic_attack_bonus_entry.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

        # Caminho Elemental / Especialização (Ex: Evocador)
        path_label = ctk.CTkLabel(master=info_frame, text="Caminho/Especialização:")
        path_label.grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.magic_path_entry = ctk.CTkEntry(master=info_frame, placeholder_text="Ex: Caminho da Terra")
        self.magic_path_entry.grid(row=5, column=1, padx=5, pady=5, sticky="ew")


    def setup_spells_list_section(self):
        spells_list_main_frame = ctk.CTkFrame(self.main_frame)
        spells_list_main_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")
        spells_list_main_frame.rowconfigure(1, weight=1) # Para o scrollable frame expandir

        title_spells_label = ctk.CTkLabel(master=spells_list_main_frame, text="Magias e Habilidades", font=ctk.CTkFont(size=16, weight="bold"))
        title_spells_label.pack(pady=(5,10))

        self.spells_scroll_frame = ctk.CTkScrollableFrame(spells_list_main_frame, label_text="")
        self.spells_scroll_frame.pack(fill="both", expand=True)

        # Botão para adicionar nova magia/habilidade
        add_spell_button = ctk.CTkButton(master=spells_list_main_frame, text="Adicionar Magia/Habilidade", command=self.add_spell_entry_ui)
        add_spell_button.pack(pady=10)
        
        # Adicionar algumas magias de exemplo
        self.add_spell_entry_ui(name="Canalizar Elemento (Básico)", mp_cost="1 PM", cast_time="Ação", range_dur="Curto / Variável", target_effect="Efeito menor do elemento.")
        self.add_spell_entry_ui(name="Postura Inabalável (Terra)", mp_cost="1 PM", cast_time="Reação", range_dur="Pessoal", target_effect="Vantagem vs. mov. forçado.")


    def add_spell_entry_ui(self, name="", mp_cost="", cast_time="", range_dur="", target_effect=""):
        spell_frame = ctk.CTkFrame(self.spells_scroll_frame, border_width=1)
        spell_frame.pack(fill="x", pady=5, padx=5)
        spell_frame.columnconfigure(1, weight=1) # Coluna dos campos de entrada

        fields = {
            "Nome:": (name, 0),
            "Custo PM:": (mp_cost, 1),
            "Tempo Uso:": (cast_time, 2),
            "Alcance/Duração:": (range_dur, 3),
            "Alvo/Efeito (Resumo):": (target_effect, 4, 80) # (valor, linha, altura_textbox)
        }
        
        # Botão para remover a magia (placeholder de funcionalidade)
        remove_button = ctk.CTkButton(master=spell_frame, text="X", width=25, height=25, command=lambda sf=spell_frame: self.remove_spell_ui(sf))
        remove_button.grid(row=0, column=2, padx=5, pady=(5,0), sticky="ne")


        for i, (label_text, (initial_value, grid_row, *textbox_height)) in enumerate(fields.items()):
            label = ctk.CTkLabel(master=spell_frame, text=label_text)
            label.grid(row=grid_row, column=0, padx=5, pady=2, sticky="nw")

            if label_text == "Alvo/Efeito (Resumo):":
                entry = ctk.CTkTextbox(master=spell_frame, height=textbox_height[0] if textbox_height else 60)
                entry.insert("1.0", initial_value)
                entry.grid(row=grid_row, column=1, padx=5, pady=2, sticky="ew")
            else:
                entry = ctk.CTkEntry(master=spell_frame, placeholder_text=label_text.replace(":", ""))
                entry.insert(0, initial_value)
                entry.grid(row=grid_row, column=1, padx=5, pady=2, sticky="ew")
            
            # Guardar referência se necessário (não implementado aqui para simplificar)
            # setattr(spell_frame, f"entry_{label_text.lower().replace(':', '').replace('/', '_').replace(' ', '_')}", entry)
        
        self.spell_widgets_list.append(spell_frame)

    def remove_spell_ui(self, spell_frame_to_remove):
        spell_frame_to_remove.destroy()
        if spell_frame_to_remove in self.spell_widgets_list:
            self.spell_widgets_list.remove(spell_frame_to_remove)