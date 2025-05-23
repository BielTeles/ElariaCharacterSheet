import customtkinter as ctk
from data.items_data import TODOS_ITENS_LOJA
from data.abilities_data import ABILITIES_DATA

class StoreAbilitiesTab:
    def __init__(self, tab_widget, personagem_atual, app_ui_ref):
        self.tab_widget = tab_widget
        self.personagem = personagem_atual
        self.app_ui = app_ui_ref  # Referência à AppUI para atualizar outras abas

        self.main_frame = ctk.CTkFrame(self.tab_widget, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True)

        self.store_tab_view = ctk.CTkTabview(self.main_frame, anchor="nw")
        self.store_tab_view.pack(fill="both", expand=True, padx=5, pady=5)

        self.items_store_tab_widget = self.store_tab_view.add("Loja de Itens")
        self.abilities_tab_widget = self.store_tab_view.add("Habilidades")

        # --- UI da Loja de Itens ---
        self.items_top_info_frame = ctk.CTkFrame(self.items_store_tab_widget, fg_color="transparent")
        self.items_top_info_frame.pack(fill="x", pady=(5,0), padx=5)
        
        ctk.CTkLabel(master=self.items_top_info_frame, text="Moedas:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(0,5))
        self.char_ef_label = ctk.CTkLabel(master=self.items_top_info_frame, text="Ef: 0")
        self.char_ef_label.pack(side="left", padx=(0,10))
        self.char_efp_label = ctk.CTkLabel(master=self.items_top_info_frame, text="EfP: 0")
        self.char_efp_label.pack(side="left", padx=(0,10))

        self.items_scroll_frame = ctk.CTkScrollableFrame(self.items_store_tab_widget)
        self.items_scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Configuração das colunas do ScrollFrame de Itens
        self.items_scroll_frame.columnconfigure(0, weight=3)  # Nome
        self.items_scroll_frame.columnconfigure(1, weight=2)  # Custo
        self.items_scroll_frame.columnconfigure(2, weight=2)  # Categoria Loja
        self.items_scroll_frame.columnconfigure(3, weight=0)  # Botão Comprar
        
        # Cabeçalhos da Loja de Itens
        headers_items = ["Item", "Custo", "Categoria"]
        for col, header_text in enumerate(headers_items):
            ctk.CTkLabel(master=self.items_scroll_frame, text=header_text, font=ctk.CTkFont(weight="bold")).grid(row=0, column=col, padx=5, pady=(5,10), sticky="w")

        # --- UI da Aba de Habilidades ---
        self.abilities_info_frame = ctk.CTkFrame(self.abilities_tab_widget, fg_color="transparent")
        self.abilities_info_frame.pack(fill="x", pady=(5,0), padx=5)
        ctk.CTkLabel(master=self.abilities_info_frame, text="Nível:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(0,5))
        self.char_level_label_abilities = ctk.CTkLabel(master=self.abilities_info_frame, text="N/A")
        self.char_level_label_abilities.pack(side="left", padx=(0,10))
        ctk.CTkLabel(master=self.abilities_info_frame, text="Classe:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(0,5))
        self.char_class_label_abilities = ctk.CTkLabel(master=self.abilities_info_frame, text="N/A")
        self.char_class_label_abilities.pack(side="left", padx=(0,10))
        ctk.CTkLabel(master=self.abilities_info_frame, text="Subclasse:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(0,5))
        self.char_subclass_label_abilities = ctk.CTkLabel(master=self.abilities_info_frame, text="N/A")
        self.char_subclass_label_abilities.pack(side="left", padx=(0,10))


        self.abilities_scroll_frame = ctk.CTkScrollableFrame(self.abilities_tab_widget)
        self.abilities_scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)
        self.abilities_scroll_frame.columnconfigure(0, weight=2) # Nível Req. / Nome
        self.abilities_scroll_frame.columnconfigure(1, weight=4) # Descrição
        self.abilities_scroll_frame.columnconfigure(2, weight=1) # Custo/Ação
        self.abilities_scroll_frame.columnconfigure(3, weight=0) # Botão

        self.load_data_from_personagem()

    def update_character_currency_display(self):
        """Atualiza a exibição das moedas do personagem na aba da loja."""
        if hasattr(self, 'personagem') and self.personagem:
            self.char_ef_label.configure(text=f"Ef: {self.personagem.moedas_ef}")
            self.char_efp_label.configure(text=f"EfP: {self.personagem.moedas_efp}")

    def update_character_info_for_abilities(self):
        """Atualiza a exibição de nível, classe e subclasse na aba de habilidades."""
        if hasattr(self, 'personagem') and self.personagem:
            self.char_level_label_abilities.configure(text=str(self.personagem.nivel))
            self.char_class_label_abilities.configure(text=self.personagem.classe_principal if self.personagem.classe_principal else "Nenhuma")
            self.char_subclass_label_abilities.configure(text=self.personagem.sub_classe if self.personagem.sub_classe else "Nenhuma")

    def load_data_from_personagem(self):
        """Chamado para carregar/recarregar opções da loja e habilidades."""
        self.personagem = self.app_ui.personagem_atual 
        self.update_character_currency_display()
        self.update_character_info_for_abilities()
        self.populate_items_store()
        self.populate_abilities_list()

    def populate_items_store(self):
        for widget in self.items_scroll_frame.winfo_children():
            if widget.grid_info().get("row", 0) > 0: # Não remover os cabeçalhos
                widget.destroy()

        current_row = 1
        for item_data in TODOS_ITENS_LOJA:
            nome_item = item_data.get("nome", "N/A")
            nome_label = ctk.CTkLabel(master=self.items_scroll_frame, text=nome_item, anchor="w", wraplength=250)
            nome_label.grid(row=current_row, column=0, padx=5, pady=3, sticky="ew")

            custo_ef = item_data.get("custo_ef", 0)
            custo_efp = item_data.get("custo_efp", 0)
            custo_str = ""
            if custo_ef > 0: custo_str += f"{custo_ef} Ef"
            if custo_efp > 0:
                if custo_str: custo_str += " "
                custo_str += f"{custo_efp} EfP"
            if not custo_str: custo_str = "Grátis"
            custo_label = ctk.CTkLabel(master=self.items_scroll_frame, text=custo_str, anchor="w")
            custo_label.grid(row=current_row, column=1, padx=5, pady=3, sticky="w")

            categoria_loja = item_data.get("categoria_loja", "N/A")
            categoria_label = ctk.CTkLabel(master=self.items_scroll_frame, text=categoria_loja, anchor="w")
            categoria_label.grid(row=current_row, column=2, padx=5, pady=3, sticky="w")

            buy_button = ctk.CTkButton(master=self.items_scroll_frame, text="Comprar", width=80,
                                       command=lambda i=item_data: self.buy_item(i))
            buy_button.grid(row=current_row, column=3, padx=5, pady=3, sticky="e")
            current_row += 1
    
    def buy_item(self, item_data):
        custo_ef_item = item_data.get("custo_ef", 0)
        custo_efp_item = item_data.get("custo_efp", 0)
        custo_total_em_efp_item = (custo_ef_item * 10) + custo_efp_item
        saldo_total_em_efp_personagem = (self.personagem.moedas_ef * 10) + self.personagem.moedas_efp

        if saldo_total_em_efp_personagem >= custo_total_em_efp_item:
            saldo_restante_efp = saldo_total_em_efp_personagem - custo_total_em_efp_item
            self.personagem.moedas_ef = saldo_restante_efp // 10
            self.personagem.moedas_efp = saldo_restante_efp % 10

            tipo_inv = item_data.get("tipo_item_para_inventario", "item_geral")
            item_adicionado_copia = item_data.copy() # Trabalhar com uma cópia

            if tipo_inv == "arma":
                self.personagem.armas_inventario.append(item_adicionado_copia)
            elif tipo_inv == "armadura":
                # A lógica para "equipar" uma armadura pode ser mais complexa.
                # Por agora, adicionamos ao inventário geral e atualizamos RD do personagem se aplicável.
                self.personagem.itens_gerais.append({"nome": item_adicionado_copia.get("nome"), "quantity": 1, "weight": "", "description": f"Tipo: {item_adicionado_copia.get('tipo_armadura')}, RD: {item_adicionado_copia.get('rd')}"})
                # Se quiser que a armadura comprada seja automaticamente equipada:
                # self.personagem.armadura_equipada = {"nome": item_adicionado_copia.get("nome"), "rd_fornecida": item_adicionado_copia.get("rd",0)}
                # self.personagem.rd_total = item_adicionado_copia.get("rd",0) # Ou lógica mais complexa de RD
            elif tipo_inv == "escudo":
                self.personagem.itens_gerais.append({"nome": item_adicionado_copia.get("nome"), "quantity": 1, "weight": "", "description": item_adicionado_copia.get("observacoes","")})
                # Se quiser que o escudo comprado seja automaticamente equipado:
                # self.personagem.escudo_equipado = {"nome": item_adicionado_copia.get("nome"), "notas": item_adicionado_copia.get("observacoes","")}
            else: # item_geral
                found_item = None
                for inv_item in self.personagem.itens_gerais:
                    if inv_item.get("nome") == item_adicionado_copia.get("nome"):
                        found_item = inv_item
                        break
                if found_item:
                    try: found_item["quantity"] = int(found_item.get("quantity", 0)) + 1
                    except: found_item["quantity"] = 1 
                else:
                    self.personagem.itens_gerais.append({"nome": item_adicionado_copia.get("nome"), "quantity": 1, "weight": item_adicionado_copia.get("peso_estimado",""), "description": ""})

            self.app_ui.show_feedback_message(f"'{item_data.get('nome')}' comprado!", 2000)
            self.update_character_currency_display()
            self.app_ui.inventory_tab.load_data_from_personagem()
            self.app_ui.combat_tab.load_data_from_personagem() # Atualiza armas e RD
        else:
            self.app_ui.show_feedback_message("Moedas insuficientes!", 2000)


    def populate_abilities_list(self):
        for widget in self.abilities_scroll_frame.winfo_children():
            widget.destroy()

        classe = self.personagem.classe_principal
        subclasse = self.personagem.sub_classe
        nivel_personagem = self.personagem.nivel

        if not classe or not ABILITIES_DATA.get(classe):
            ctk.CTkLabel(master=self.abilities_scroll_frame, text="Selecione uma Classe Principal na aba 'Principal'.").pack(pady=10)
            return

        habilidades_para_renderizar = []

        # Habilidades Base da Classe
        for ability in ABILITIES_DATA[classe].get("base", []):
            if ability.get("nivel_req", 1) <= nivel_personagem:
                habilidades_para_renderizar.append(ability)
        
        # Habilidades da Subclasse
        if subclasse and "subclasses" in ABILITIES_DATA[classe] and subclasse in ABILITIES_DATA[classe]["subclasses"]:
            for ability in ABILITIES_DATA[classe]["subclasses"][subclasse].get("habilidades", []):
                if ability.get("nivel_req", 1) <= nivel_personagem:
                    habilidades_para_renderizar.append(ability)
        
        current_row = 0
        grupos_renderizados = {} # Para controlar os frames dos grupos

        for ability in habilidades_para_renderizar:
            grupo_escolha = ability.get("grupo_escolha")

            if grupo_escolha:
                if grupo_escolha not in grupos_renderizados:
                    limite = ability.get("limite_escolha", 1)
                    frame_grupo = ctk.CTkFrame(self.abilities_scroll_frame, border_width=1)
                    frame_grupo.pack(fill="x", pady=(10,2), padx=2)
                    ctk.CTkLabel(master=frame_grupo, text=f"Escolha {limite} de: {grupo_escolha.replace('_lvl1', ' (Nível 1)')}", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=5, pady=(2,5))
                    grupos_renderizados[grupo_escolha] = {"frame": frame_grupo, "vars": [], "limite": limite, "opcoes_data": []}
                
                # Adiciona esta opção ao grupo
                var_escolha = ctk.BooleanVar()
                habilidade_ja_escolhida = any(h.get('nome') == ability.get('nome') and h.get('grupo_escolha_origem') == grupo_escolha for h in self.personagem.magias_habilidades)
                var_escolha.set(habilidade_ja_escolhida)
                
                chk = ctk.CTkCheckBox(
                    master=grupos_renderizados[grupo_escolha]["frame"], 
                    text=f"{ability.get('nome')} - {ability.get('descricao', '')[:60]}... (Custo: {ability.get('custo','N/A')})", 
                    variable=var_escolha,
                    wraplength=400, justify="left",
                    command=lambda v=var_escolha, ab_data=ability, g_nome=grupo_escolha: self.handle_ability_choice(v, ab_data, g_nome)
                )
                chk.pack(anchor="w", padx=15, pady=1)
                grupos_renderizados[grupo_escolha]["vars"].append(var_escolha)
                grupos_renderizados[grupo_escolha]["opcoes_data"].append({"checkbox": chk, "var": var_escolha, "ability_data": ability})
            
            else: # Habilidades não agrupadas (geralmente passivas ou aprendidas automaticamente)
                frame_habilidade = ctk.CTkFrame(self.abilities_scroll_frame) # Um frame por habilidade para melhor layout
                frame_habilidade.pack(fill="x", pady=2, padx=2)
                frame_habilidade.columnconfigure(0, weight=3) # Nome
                frame_habilidade.columnconfigure(1, weight=5) # Descrição
                frame_habilidade.columnconfigure(2, weight=0) # Botão/Status

                nome_display = f"{ability.get('nome')}"
                if ability.get('nivel_req', 1) > 1 : nome_display += f" (Nível {ability.get('nivel_req')})"

                ctk.CTkLabel(master=frame_habilidade, text=nome_display, anchor="w", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(master=frame_habilidade, text=f"{ability.get('descricao', '')[:80]}...", anchor="w", wraplength=300, justify="left").grid(row=0, column=1, padx=5, pady=2, sticky="ew")
                
                habilidade_ja_adquirida = any(h.get('nome') == ability.get('nome') for h in self.personagem.magias_habilidades)
                
                if habilidade_ja_adquirida or ability.get("tipo") == "Passiva de Classe" or ability.get("tipo") == "Passiva de Arquétipo" or ability.get("tipo") == "Passiva de Caminho" or ability.get("tipo") == "Escolha de Subclasse":
                    status_text = "Adquirida" if habilidade_ja_adquirida else "Automática"
                    if ability.get("tipo") == "Escolha de Subclasse" and not self.personagem.sub_classe : status_text = "Escolha Subclasse"
                    
                    ctk.CTkLabel(master=frame_habilidade, text=status_text, text_color="gray", width=80).grid(row=0, column=2, padx=5, pady=2, sticky="e")
                    if not habilidade_ja_adquirida and "Automática" in status_text and ability.get("tipo") != "Escolha de Subclasse": # Adiciona automaticamente se não for escolha
                        self.learn_ability(ability.copy(), is_auto_learn=True) # Adiciona uma cópia

                else:
                    btn_learn = ctk.CTkButton(master=frame_habilidade, text="Aprender", width=80, command=lambda ab=ability: self.learn_ability(ab))
                    btn_learn.grid(row=0, column=2, padx=5, pady=2, sticky="e")
            current_row +=1

        # Atualizar estados dos checkboxes para cada grupo
        for nome_grupo, dados_grupo_dict in grupos_renderizados.items():
            self.update_checkbox_states_for_group(nome_grupo, dados_grupo_dict)


    def handle_ability_choice(self, bool_var, ability_data, group_name):
        # Encontra os dados do grupo correto
        group_info = None
        # Precisamos iterar pelos grupos renderizados para encontrar o correto, pois group_vars_list não é passado diretamente
        # Isso é um pouco ineficiente, idealmente a referência ao grupo_renderizado seria passada.
        # Para simplificar agora, vamos buscar a info do grupo pelo nome.
        # (Em uma refatoração, a estrutura de 'grupos_renderizados' ou a forma como é acessada poderia ser melhorada)
        
        # Busca o grupo de dados correto
        dados_grupo_dict_atual = None
        # Esta busca é um placeholder. A estrutura de `grupos_renderizados` precisa ser acessível
        # de uma forma que `update_checkbox_states_for_group` possa usar.
        # Vamos assumir que a estrutura de `self.grupos_renderizados_para_validacao` (ou similar) é mantida.
        
        # Lógica simplificada (precisa ser robustecida com a referência correta ao grupo_data)
        habilidades_atuais_personagem = self.personagem.magias_habilidades
        
        if bool_var.get(): # Se está marcando
            # Contar quantas já foram escolhidas DESTE GRUPO ESPECÍFICO no personagem
            escolhidas_neste_grupo_no_personagem = sum(1 for h_pers in habilidades_atuais_personagem if h_pers.get("grupo_escolha_origem") == group_name)
            
            # Encontra o limite do grupo (precisaria buscar em ABILITIES_DATA ou ter armazenado)
            # Esta é uma simplificação, você precisará buscar o limite correto.
            limite_do_grupo_atual = 1 
            for classe, data_classe in ABILITIES_DATA.items():
                for sub_nome, data_sub in data_classe.get("subclasses", {}).items():
                    for hab_sub in data_sub.get("habilidades", []):
                        if hab_sub.get("grupo_escolha") == group_name:
                            limite_do_grupo_atual = hab_sub.get("limite_escolha", 1)
                            break
                    if limite_do_grupo_atual != 1: break # Encontrou
                if limite_do_grupo_atual != 1: break # Encontrou

            if escolhidas_neste_grupo_no_personagem < limite_do_grupo_atual:
                if not any(h.get('nome') == ability_data.get('nome') and h.get('grupo_escolha_origem') == group_name for h in habilidades_atuais_personagem):
                    ability_copy = ability_data.copy()
                    ability_copy["grupo_escolha_origem"] = group_name
                    self.personagem.magias_habilidades.append(ability_copy)
                    self.app_ui.show_feedback_message(f"'{ability_data.get('nome')}' selecionada.", 1500)
            else:
                bool_var.set(False) # Desmarca
                self.app_ui.show_feedback_message(f"Limite de {limite_do_grupo_atual} para '{group_name.replace('_lvl1',' Nível 1')}' atingido.", 2000)
        else: # Se está desmarcando
            self.personagem.magias_habilidades = [
                h for h in habilidades_atuais_personagem 
                if not (h.get('nome') == ability_data.get('nome') and h.get('grupo_escolha_origem') == group_name)
            ]
            self.app_ui.show_feedback_message(f"'{ability_data.get('nome')}' desmarcada.", 1500)

        # Re-popular a lista para atualizar estados dos checkboxes (isso redesenhará tudo)
        self.populate_abilities_list() 
        self.app_ui.magic_tab.load_data_from_personagem()


    def update_checkbox_states_for_group(self, group_name, group_data_dict):
        """Atualiza o estado (habilitado/desabilitado) dos checkboxes em um grupo."""
        if not group_data_dict or not isinstance(group_data_dict.get("vars"), list):
            return

        escolhidas_count = sum(1 for var_chk in group_data_dict["vars"] if var_chk.get())
        limite = group_data_dict.get("limite", 1)

        for item_info in group_data_dict.get("opcoes_data", []):
            checkbox_widget = item_info.get("checkbox")
            var_atual = item_info.get("var")
            if checkbox_widget and var_atual:
                if escolhidas_count >= limite and not var_atual.get():
                    checkbox_widget.configure(state="disabled")
                else:
                    checkbox_widget.configure(state="normal")


    def learn_ability(self, ability_data, is_auto_learn=False):
        # Verifica se a habilidade já foi adicionada para evitar duplicatas
        if not any(h.get('nome') == ability_data.get('nome') for h in self.personagem.magias_habilidades):
            self.personagem.magias_habilidades.append(ability_data.copy()) # Adiciona uma cópia
            if not is_auto_learn:
                self.app_ui.show_feedback_message(f"Habilidade '{ability_data.get('nome')}' aprendida!", 2000)
                # Atualiza a lista de habilidades na UI da loja para refletir o status "Adquirida"
                self.populate_abilities_list() 
            # Atualiza a aba de Magia para mostrar a nova habilidade
            self.app_ui.magic_tab.load_data_from_personagem()
        elif not is_auto_learn:
            self.app_ui.show_feedback_message("Habilidade já conhecida.", 2000)