import customtkinter as ctk

class MagicTab:
    def __init__(self, tab_widget, personagem_atual): # Adicionado personagem_atual aqui
        self.tab_widget = tab_widget
        self.personagem = personagem_atual # Guarda a referência
        self.spell_widgets_list = [] 

        # --- Frame Principal para a Aba de Magia ---
        self.main_frame = ctk.CTkFrame(self.tab_widget, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True)
        self.main_frame.columnconfigure(0, weight=1) 
        self.main_frame.columnconfigure(1, weight=2) 
        self.main_frame.rowconfigure(1, weight=1)    

        # StringVars para os campos de informação de magia
        self.pm_current_var = ctk.StringVar()
        self.pm_max_var = ctk.StringVar() # Provavelmente será um label, preenchido por cálculo
        self.key_magic_attr_var = ctk.StringVar()
        self.magic_save_dc_var = ctk.StringVar()
        self.magic_attack_bonus_var = ctk.StringVar()
        self.magic_path_var = ctk.StringVar()

        self.setup_magic_info_section()
        self.setup_spells_list_section()

        self.load_data_from_personagem() # Carrega dados ao iniciar

    def load_data_from_personagem(self):
        """Carrega dados do objeto Personagem para a UI da aba de Magia."""
        self.pm_current_var.set(str(self.personagem.pm_atuais))
        self.pm_max_var.set(str(self.personagem.pm_maximo)) # Será atualizado quando PM Máx for calculado
        self.key_magic_attr_var.set(self.personagem.atributo_chave_magia)
        self.magic_save_dc_var.set(str(self.personagem.cd_teste_resistencia_magia))
        self.magic_attack_bonus_var.set(str(self.personagem.bonus_ataque_magico)) # Ou formatar como "+X"
        self.magic_path_var.set(self.personagem.caminho_especializacao_magica)

    def _update_personagem_magic_attr(self, attr_name, string_var, is_int=False, *args):
        """Atualiza um atributo de magia no objeto Personagem."""
        value_str = string_var.get()
        value_to_set = value_str
        
        if is_int:
            try:
                value_to_set = int(value_str)
            except ValueError:
                # Reverte para o valor atual no objeto se a conversão falhar
                revert_val = getattr(self.personagem, attr_name, 0 if is_int else "")
                string_var.set(str(revert_val))
                print(f"Valor inválido '{value_str}' para {attr_name}.")
                return
        
        setattr(self.personagem, attr_name, value_to_set)
        # print(f"Personagem.{attr_name} atualizado para: {value_to_set}") # Para debug


    def setup_magic_info_section(self):
        info_frame = ctk.CTkFrame(self.main_frame)
        info_frame.grid(row=0, column=0, padx=10, pady=10, sticky="new")
        info_frame.columnconfigure(1, weight=1)

        title_info_label = ctk.CTkLabel(master=info_frame, text="Recursos Mágicos", font=ctk.CTkFont(size=16, weight="bold"))
        title_info_label.grid(row=0, column=0, columnspan=2, padx=5, pady=(5,10), sticky="n")

        # Pontos de Mana (PM)
        pm_label = ctk.CTkLabel(master=info_frame, text="Pontos de Mana (PM):")
        pm_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        pm_sub_frame = ctk.CTkFrame(info_frame, fg_color="transparent") 
        pm_sub_frame.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        
        # PM Atuais - Linkado
        pm_current_entry = ctk.CTkEntry(master=pm_sub_frame, placeholder_text="Atual", width=60, textvariable=self.pm_current_var)
        pm_current_entry.pack(side="left", padx=(0,2))
        self.pm_current_var.trace_add("write", lambda n,i,m, attr='pm_atuais', sv=self.pm_current_var : self._update_personagem_magic_attr(attr, sv, is_int=True))
        
        separator_pm = ctk.CTkLabel(master=pm_sub_frame, text="/")
        separator_pm.pack(side="left", padx=2)
        
        # PM Máximos - Apenas display, será calculado/carregado
        pm_max_display_label = ctk.CTkLabel(master=pm_sub_frame, textvariable=self.pm_max_var, width=60) # Usar Label
        pm_max_display_label.pack(side="left", padx=(2,0))

        # Atributo Chave de Magia - Linkado
        key_attr_label = ctk.CTkLabel(master=info_frame, text="Atributo Chave Magia:")
        key_attr_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        key_magic_attr_entry = ctk.CTkEntry(master=info_frame, placeholder_text="Ex: SAB, INT", textvariable=self.key_magic_attr_var)
        key_magic_attr_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.key_magic_attr_var.trace_add("write", lambda n,i,m, attr='atributo_chave_magia', sv=self.key_magic_attr_var : self._update_personagem_magic_attr(attr, sv))
        
        # CD de Resistência de Magia - Linkado (será calculado futuramente)
        save_dc_label = ctk.CTkLabel(master=info_frame, text="CD Teste Resist. Magia:")
        save_dc_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        magic_save_dc_entry = ctk.CTkEntry(master=info_frame, placeholder_text="Ex: 13", textvariable=self.magic_save_dc_var)
        magic_save_dc_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        self.magic_save_dc_var.trace_add("write", lambda n,i,m, attr='cd_teste_resistencia_magia', sv=self.magic_save_dc_var : self._update_personagem_magic_attr(attr, sv, is_int=True))

        # Bônus de Ataque Mágico - Linkado (será calculado futuramente)
        attack_bonus_label = ctk.CTkLabel(master=info_frame, text="Bônus Ataque Mágico:")
        attack_bonus_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")
        magic_attack_bonus_entry = ctk.CTkEntry(master=info_frame, placeholder_text="Ex: +5", textvariable=self.magic_attack_bonus_var)
        magic_attack_bonus_entry.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        self.magic_attack_bonus_var.trace_add("write", lambda n,i,m, attr='bonus_ataque_magico', sv=self.magic_attack_bonus_var : self._update_personagem_magic_attr(attr, sv, is_int=True)) # Assumindo que pode ser int

        # Caminho Elemental / Especialização - Linkado
        path_label = ctk.CTkLabel(master=info_frame, text="Caminho/Especialização:")
        path_label.grid(row=5, column=0, padx=5, pady=5, sticky="w")
        magic_path_entry = ctk.CTkEntry(master=info_frame, placeholder_text="Ex: Caminho da Terra", textvariable=self.magic_path_var)
        magic_path_entry.grid(row=5, column=1, padx=5, pady=5, sticky="ew")
        self.magic_path_var.trace_add("write", lambda n,i,m, attr='caminho_especializacao_magica', sv=self.magic_path_var : self._update_personagem_magic_attr(attr, sv))

    # ... (o restante dos métodos de MagicTab: setup_spells_list_section, add_spell_entry_ui, remove_spell_ui)
    # Eles permanecem os mesmos por enquanto, pois a lista de magias ainda não está
    # diretamente ligada ao self.personagem.magias_habilidades.
    # Para ser completo, vou adicioná-los:
    def setup_spells_list_section(self):
        spells_list_main_frame = ctk.CTkFrame(self.main_frame)
        spells_list_main_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")
        spells_list_main_frame.rowconfigure(1, weight=1) 

        title_spells_label = ctk.CTkLabel(master=spells_list_main_frame, text="Magias e Habilidades", font=ctk.CTkFont(size=16, weight="bold"))
        title_spells_label.pack(pady=(5,10))

        self.spells_scroll_frame = ctk.CTkScrollableFrame(spells_list_main_frame, label_text="")
        self.spells_scroll_frame.pack(fill="both", expand=True)

        add_spell_button = ctk.CTkButton(master=spells_list_main_frame, text="Adicionar Magia/Habilidade", command=self.add_spell_entry_ui)
        add_spell_button.pack(pady=10)
        
        # Carregar magias do self.personagem.magias_habilidades se já existirem
        if hasattr(self.personagem, 'magias_habilidades') and self.personagem.magias_habilidades:
            for spell_data in self.personagem.magias_habilidades:
                self.add_spell_entry_ui(**spell_data) # Passa o dicionário como kwargs
        else: # Adiciona exemplos se não houver nada carregado
            self.add_spell_entry_ui(name="Canalizar Elemento (Básico)", mp_cost="1 PM", cast_time="Ação", range_dur="Curto / Variável", target_effect="Efeito menor do elemento.")
            self.add_spell_entry_ui(name="Postura Inabalável (Terra)", mp_cost="1 PM", cast_time="Reação", range_dur="Pessoal", target_effect="Vantagem vs. mov. forçado.")


    def add_spell_entry_ui(self, name="", mp_cost="", cast_time="", range_dur="", target_effect=""):
        spell_data = {
            'name': name, 'mp_cost': mp_cost, 'cast_time': cast_time,
            'range_dur': range_dur, 'target_effect': target_effect
        }
        # Adiciona ao objeto personagem se ainda não estiver lá (para novos itens via UI)
        # A verificação de duplicidade pode ser mais robusta
        # if spell_data not in self.personagem.magias_habilidades and name: # Evita adicionar entradas vazias por padrão
        # self.personagem.magias_habilidades.append(spell_data)


        spell_frame = ctk.CTkFrame(self.spells_scroll_frame, border_width=1)
        spell_frame.pack(fill="x", pady=5, padx=5)
        spell_frame.columnconfigure(1, weight=1)
        
        # Guardar os StringVars da magia para atualizar o objeto Personagem
        current_spell_vars = {}

        fields_map = { # label: (attribute_name_in_spell_data, initial_value, grid_row, is_textbox, textbox_height)
            "Nome:": ('name', name, 0, False, 0),
            "Custo PM:": ('mp_cost', mp_cost, 1, False, 0),
            "Tempo Uso:": ('cast_time', cast_time, 2, False, 0),
            "Alcance/Duração:": ('range_dur', range_dur, 3, False, 0),
            "Alvo/Efeito (Resumo):": ('target_effect', target_effect, 4, True, 80)
        }
        
        remove_button = ctk.CTkButton(master=spell_frame, text="X", width=25, height=25, 
                                      command=lambda sf=spell_frame, sd=spell_data: self.remove_spell_ui(sf, sd))
        remove_button.grid(row=0, column=2, padx=5, pady=(5,0), sticky="ne")

        for label_text, (attr_key, initial_val, grid_row, is_textbox, height) in fields_map.items():
            label = ctk.CTkLabel(master=spell_frame, text=label_text)
            label.grid(row=grid_row, column=0, padx=5, pady=2, sticky="nw")

            var = ctk.StringVar(value=str(initial_val))
            current_spell_vars[attr_key] = var
            # Atualizar o dicionário spell_data no objeto Personagem quando o var mudar
            var.trace_add("write", lambda n,i,m, s_data=spell_data, k=attr_key, v=var: s_data.update({k: v.get()}))


            if is_textbox:
                entry = ctk.CTkTextbox(master=spell_frame, height=height if height else 60)
                entry.insert("1.0", str(initial_val))
                # Para CTkTextbox, a atualização via StringVar é mais complexa,
                # pode-se usar binding em <KeyRelease> para atualizar spell_data[attr_key]
                entry.bind("<KeyRelease>", lambda event, s_data=spell_data, k=attr_key, txt_widget=entry: s_data.update({k: txt_widget.get("1.0", "end-1c")}))

            else:
                entry = ctk.CTkEntry(master=spell_frame, placeholder_text=label_text.replace(":", ""), textvariable=var)
            
            entry.grid(row=grid_row, column=1, padx=5, pady=2, sticky="ew")
            setattr(spell_frame, f"widget_{attr_key}", entry) # Para possível referência futura ao widget
        
        # Adiciona a referência do dicionário de dados da magia à lista do personagem se ainda não estiver lá
        # Esta lógica de adição/sincronização pode ser melhorada
        # A ideia é que add_spell_entry_ui é chamada para exibir magias existentes ou adicionar novas
        is_new_spell = True
        if name: # Se um nome foi fornecido, verifica se já existe (baseado no nome)
            for existing_spell in self.personagem.magias_habilidades:
                if existing_spell.get('name') == name:
                    is_new_spell = False
                    # Atualizar o dicionário existente com os novos vars (se necessário, mas vars devem refletir)
                    # Isso é complicado porque spell_data aqui é um novo dict.
                    # O ideal é que a UI reflita uma lista de objetos/dicionários do personagem.
                    # Por agora, vamos focar em adicionar novas magias via UI ao objeto personagem
                    # e carregar as existentes.
                    break
        
        if is_new_spell and name: # Só adiciona se tiver um nome e for considerada nova
             self.personagem.magias_habilidades.append(spell_data)


        self.spell_widgets_list.append({"frame": spell_frame, "data_dict": spell_data})


    def remove_spell_ui(self, spell_frame_to_remove, spell_data_to_remove):
        spell_frame_to_remove.destroy()
        
        # Remove da lista de widgets da UI
        found_widget_entry = None
        for entry in self.spell_widgets_list:
            if entry["frame"] == spell_frame_to_remove:
                found_widget_entry = entry
                break
        if found_widget_entry:
            self.spell_widgets_list.remove(found_widget_entry)

        # Remove do objeto Personagem
        if spell_data_to_remove in self.personagem.magias_habilidades:
            self.personagem.magias_habilidades.remove(spell_data_to_remove)
        # print(f"Magias no personagem após remover: {self.personagem.magias_habilidades}") # Debug