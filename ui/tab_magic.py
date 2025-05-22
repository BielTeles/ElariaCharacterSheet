import customtkinter as ctk
# Não precisamos de random ou core.dice_roller aqui diretamente

class MagicTab:
    def __init__(self, tab_widget, personagem_atual):
        self.tab_widget = tab_widget
        self.personagem = personagem_atual
        
        # Lista para guardar os FRAMES de cada magia na UI, para poderem ser destruídos ao recarregar
        self.spell_ui_frames = [] 

        # StringVars para os campos de informação geral de magia
        self.pm_current_var = ctk.StringVar()
        self.pm_max_var = ctk.StringVar()
        self.key_magic_attr_var = ctk.StringVar()
        self.magic_save_dc_var = ctk.StringVar()
        self.magic_attack_bonus_var = ctk.StringVar()
        self.magic_path_var = ctk.StringVar()

        # --- Frame Principal para a Aba de Magia ---
        self.main_frame = ctk.CTkFrame(self.tab_widget, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True)
        self.main_frame.columnconfigure(0, weight=1) 
        self.main_frame.columnconfigure(1, weight=2) 
        self.main_frame.rowconfigure(1, weight=1)    

        self.setup_magic_info_section()
        self.setup_spells_list_section()
        
        self.load_data_from_personagem() # Carrega dados ao iniciar

    def load_data_from_personagem(self):
        """Carrega/Recarrega dados do self.personagem para os campos da UI desta aba."""
        self.pm_current_var.set(str(self.personagem.pm_atuais))
        self.pm_max_var.set(str(self.personagem.pm_maximo))
        self.key_magic_attr_var.set(self.personagem.atributo_chave_magia)
        self.magic_save_dc_var.set(str(self.personagem.cd_teste_resistencia_magia))
        self.magic_attack_bonus_var.set(str(self.personagem.bonus_ataque_magico))
        self.magic_path_var.set(self.personagem.caminho_especializacao_magica)

        # Limpar magias existentes na UI
        for spell_frame in self.spell_ui_frames:
            spell_frame.destroy()
        self.spell_ui_frames.clear()

        # Repopular a lista de magias da UI a partir do personagem
        if hasattr(self.personagem, 'magias_habilidades'):
            for spell_data_dict in self.personagem.magias_habilidades:
                # Passa o dicionário de dados para que a UI seja construída com ele
                # e as StringVars/binds atualizem este mesmo dicionário.
                self.add_spell_entry_ui(**spell_data_dict, is_loading=True)

    def _update_personagem_magic_attr(self, attr_name_in_personagem, string_var, is_int=False, *args):
        value_str = string_var.get()
        value_to_set = value_str
        if is_int:
            try: value_to_set = int(value_str) if value_str.strip() else 0
            except ValueError:
                revert_val = getattr(self.personagem, attr_name_in_personagem, 0)
                string_var.set(str(revert_val))
                return
        setattr(self.personagem, attr_name_in_personagem, value_to_set)

    def setup_magic_info_section(self):
        # ... (Implementação como na última versão, mas usando _update_personagem_magic_attr para os traces)
        info_frame = ctk.CTkFrame(self.main_frame)
        info_frame.grid(row=0, column=0, padx=10, pady=10, sticky="new")
        info_frame.columnconfigure(1, weight=1)
        title_info_label = ctk.CTkLabel(master=info_frame, text="Recursos Mágicos", font=ctk.CTkFont(size=16, weight="bold")); title_info_label.grid(row=0, column=0, columnspan=2, padx=5, pady=(5,10), sticky="n")
        
        pm_label = ctk.CTkLabel(master=info_frame, text="Pontos de Mana (PM):"); pm_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        pm_sub_frame = ctk.CTkFrame(info_frame, fg_color="transparent"); pm_sub_frame.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        pm_current_entry = ctk.CTkEntry(master=pm_sub_frame, placeholder_text="Atual", width=60, textvariable=self.pm_current_var); pm_current_entry.pack(side="left", padx=(0,2))
        self.pm_current_var.trace_add("write", lambda n,i,m, attr='pm_atuais', sv=self.pm_current_var : self._update_personagem_magic_attr(attr, sv, is_int=True))
        ctk.CTkLabel(master=pm_sub_frame, text="/").pack(side="left", padx=2)
        pm_max_display_label = ctk.CTkLabel(master=pm_sub_frame, textvariable=self.pm_max_var, width=60); pm_max_display_label.pack(side="left", padx=(2,0))

        fields_info = [
            ("Atributo Chave Magia:", self.key_magic_attr_var, 'atributo_chave_magia', False),
            ("CD Teste Resist. Magia:", self.magic_save_dc_var, 'cd_teste_resistencia_magia', True),
            ("Bônus Ataque Mágico:", self.magic_attack_bonus_var, 'bonus_ataque_magico', False), # Pode ser string como "+X" ou int
            ("Caminho/Especialização:", self.magic_path_var, 'caminho_especializacao_magica', False)
        ]
        for i, (text, var, attr_name, is_int_val) in enumerate(fields_info):
            label = ctk.CTkLabel(master=info_frame, text=text); label.grid(row=i+2, column=0, padx=5, pady=5, sticky="w")
            entry = ctk.CTkEntry(master=info_frame, textvariable=var); entry.grid(row=i+2, column=1, padx=5, pady=5, sticky="ew")
            var.trace_add("write", lambda n,idx,mode, attr=attr_name, sv=var, is_i=is_int_val: self._update_personagem_magic_attr(attr, sv, is_i))


    def setup_spells_list_section(self):
        spells_list_main_frame = ctk.CTkFrame(self.main_frame)
        spells_list_main_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")
        spells_list_main_frame.rowconfigure(1, weight=1) 

        title_spells_label = ctk.CTkLabel(master=spells_list_main_frame, text="Magias e Habilidades", font=ctk.CTkFont(size=16, weight="bold"))
        title_spells_label.pack(pady=(5,10))

        self.spells_scroll_frame = ctk.CTkScrollableFrame(spells_list_main_frame, label_text="")
        self.spells_scroll_frame.pack(fill="both", expand=True)

        add_spell_button = ctk.CTkButton(master=spells_list_main_frame, text="Adicionar Magia/Habilidade", command=lambda: self.add_spell_entry_ui()) # Chama sem args para nova magia
        add_spell_button.pack(pady=10)
        
    def _on_spell_data_change(self, spell_data_dict_ref, key, string_var_or_textbox_val, *args):
        """Atualiza o dicionário de dados da magia em self.personagem.magias_habilidades."""
        new_value = ""
        if isinstance(string_var_or_textbox_val, ctk.StringVar):
            new_value = string_var_or_textbox_val.get()
        elif isinstance(string_var_or_textbox_val, ctk.CTkTextbox): # Se for o textbox
            new_value = string_var_or_textbox_val.get("0.0", "end-1c")
        
        # Se a magia é nova (ainda não tem nome) e o nome está sendo definido,
        # adiciona o dicionário à lista do personagem.
        if key == 'name' and new_value.strip() and spell_data_dict_ref.get('name', '').strip() == "":
            if spell_data_dict_ref not in self.personagem.magias_habilidades:
                self.personagem.magias_habilidades.append(spell_data_dict_ref)
        
        spell_data_dict_ref[key] = new_value
        # print(f"Magia '{spell_data_dict_ref.get('name')}': campo '{key}' -> '{new_value}'") # Debug

    def add_spell_entry_ui(self, name="", mp_cost="", cast_time="", range_dur="", target_effect="", is_loading=False):
        spell_data_dict = None
        if is_loading:
            # Ao carregar, o spell_data_dict é o próprio dicionário da lista do personagem.
            # A chamada de load_data_from_personagem itera sobre self.personagem.magias_habilidades
            # e passa cada dicionário para esta função.
            spell_data_dict = {'name': name, 'mp_cost': mp_cost, 'cast_time': cast_time, 
                               'range_dur': range_dur, 'target_effect': target_effect}
            # Não precisa adicionar a self.personagem.magias_habilidades aqui, pois já está lá.
        else: # Adicionando uma nova magia pela UI (botão "Adicionar")
            spell_data_dict = {'name': "", 'mp_cost': "", 'cast_time': "", 
                               'range_dur': "", 'target_effect': ""}
            # O dicionário será adicionado a self.personagem.magias_habilidades em _on_spell_data_change
            # quando o nome da magia for preenchido.

        spell_frame = ctk.CTkFrame(self.spells_scroll_frame, border_width=1)
        spell_frame.pack(fill="x", pady=5, padx=5)
        spell_frame.columnconfigure(1, weight=1)
        self.spell_ui_frames.append(spell_frame) # Adiciona o frame à lista para poder destruí-lo depois

        fields_map = { 
            "Nome:": ('name', spell_data_dict['name'], 0, False, 0),
            "Custo PM:": ('mp_cost', spell_data_dict['mp_cost'], 1, False, 0),
            "Tempo Uso:": ('cast_time', spell_data_dict['cast_time'], 2, False, 0),
            "Alcance/Duração:": ('range_dur', spell_data_dict['range_dur'], 3, False, 0),
            "Alvo/Efeito (Resumo):": ('target_effect', spell_data_dict['target_effect'], 4, True, 60)
        }
        
        remove_button = ctk.CTkButton(master=spell_frame, text="X", width=25, height=25, 
                                      command=lambda sf=spell_frame, sd_ref=spell_data_dict: self.remove_spell_ui(sf, sd_ref))
        remove_button.grid(row=0, column=2, padx=5, pady=(5,0), sticky="ne")

        for label_text, (attr_key, initial_val, grid_row, is_textbox, height) in fields_map.items():
            label = ctk.CTkLabel(master=spell_frame, text=label_text)
            label.grid(row=grid_row, column=0, padx=5, pady=2, sticky="nw")

            if is_textbox:
                widget = ctk.CTkTextbox(master=spell_frame, height=height if height else 60)
                widget.insert("0.0", str(initial_val))
                widget.bind("<KeyRelease>", lambda event, s_data=spell_data_dict, k=attr_key, txt_w=widget: self._on_spell_data_change(s_data, k, txt_w))
            else:
                var = ctk.StringVar(value=str(initial_val))
                widget = ctk.CTkEntry(master=spell_frame, placeholder_text=label_text.replace(":", ""), textvariable=var)
                var.trace_add("write", lambda n,i,m, s_data=spell_data_dict, k=attr_key, v=var: self._on_spell_data_change(s_data,k,v))
            
            widget.grid(row=grid_row, column=1, padx=5, pady=2, sticky="ew")
            # Guardar referência aos widgets se necessário para acesso direto,
            # mas a atualização via _on_spell_data_change no dicionário é o principal.

    def remove_spell_ui(self, spell_frame_to_remove, spell_data_to_remove):
        spell_frame_to_remove.destroy()
        if spell_frame_to_remove in self.spell_ui_frames:
            self.spell_ui_frames.remove(spell_frame_to_remove)

        if spell_data_to_remove in self.personagem.magias_habilidades:
            self.personagem.magias_habilidades.remove(spell_data_to_remove)
        # print(f"Magias no personagem após remover: {len(self.personagem.magias_habilidades)}") # Debug