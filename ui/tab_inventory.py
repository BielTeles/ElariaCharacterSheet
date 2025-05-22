import customtkinter as ctk
# from core.dice_roller import roll_generic_dice # Não é usado diretamente aqui

class InventoryTab:
    def __init__(self, tab_widget, personagem_atual): # Adicionado personagem_atual
        self.tab_widget = tab_widget
        self.personagem = personagem_atual # Guarda a referência
        self.item_rows = [] 

        # StringVars para moedas e status de carga
        self.ef_var = ctk.StringVar()
        self.efp_var = ctk.StringVar()
        self.load_status_var = ctk.StringVar()

        self.main_frame = ctk.CTkFrame(self.tab_widget, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        self.main_frame.columnconfigure(0, weight=1) 
        self.main_frame.rowconfigure(1, weight=1) 

        self.setup_currency_section()
        self.setup_items_list_section()
        self.setup_load_limit_section()

        self.load_data_from_personagem() # Carrega dados ao iniciar

    def load_data_from_personagem(self):
        """Carrega dados do objeto Personagem para a UI da aba de Inventário."""
        self.ef_var.set(str(self.personagem.moedas_ef))
        self.efp_var.set(str(self.personagem.moedas_efp))
        self.load_status_var.set(self.personagem.limite_carga_status)

        # Limpa itens existentes na UI antes de carregar (para evitar duplicatas se chamado de novo)
        for row_frame_dict in self.item_rows:
            if row_frame_dict and row_frame_dict.get('frame'): # Adicionado 'frame'
                 row_frame_dict['frame'].destroy()
        self.item_rows.clear()
        self.item_current_row = 1 # Reseta o contador de linha para o scrollframe

        # Carrega itens do inventário do personagem
        if hasattr(self.personagem, 'itens_gerais'):
            for item_data in self.personagem.itens_gerais:
                self.add_item_entry_row(
                    name=item_data.get('name', ""),
                    quantity=str(item_data.get('quantity', "")), # Garante que é string
                    weight=str(item_data.get('weight', "")),   # Garante que é string
                    description=item_data.get('description', "")
                )
        else: # Adiciona exemplos se não houver nada carregado e a lista não existir
            self.add_item_entry_row(name="Mochila", quantity="1", weight="", description="Equipamento inicial")
            self.add_item_entry_row(name="Saco de Dormir", quantity="1", weight="", description="Equipamento inicial")
            self.add_item_entry_row(name="Traje de Viajante", quantity="1", weight="", description="Equipamento inicial")
            self.add_item_entry_row()


    def _update_personagem_inventory_attr(self, attr_name, string_var, is_int=False, *args):
        """Atualiza um atributo do inventário no objeto Personagem."""
        value_str = string_var.get()
        value_to_set = value_str
        
        if is_int:
            try:
                value_to_set = int(value_str) if value_str else 0 # Default 0 se vazio
            except ValueError:
                revert_val = getattr(self.personagem, attr_name, 0)
                string_var.set(str(revert_val))
                print(f"Valor inválido '{value_str}' para {attr_name}.")
                return
        
        setattr(self.personagem, attr_name, value_to_set)
        # print(f"Personagem.{attr_name} atualizado para: {value_to_set}") # Para debug

    def setup_currency_section(self):
        currency_frame = ctk.CTkFrame(self.main_frame)
        currency_frame.grid(row=0, column=0, padx=5, pady=(0,10), sticky="ew")
        
        title_currency_label = ctk.CTkLabel(master=currency_frame, text="Moedas", font=ctk.CTkFont(size=16, weight="bold"))
        title_currency_label.pack(pady=(5,10))

        money_sub_frame = ctk.CTkFrame(currency_frame, fg_color="transparent")
        money_sub_frame.pack(fill="x", padx=10)

        ef_label = ctk.CTkLabel(master=money_sub_frame, text="Elfen (Ef):")
        ef_label.pack(side="left", padx=(0,5))
        self.ef_entry = ctk.CTkEntry(master=money_sub_frame, placeholder_text="0", width=100, textvariable=self.ef_var)
        self.ef_entry.pack(side="left", padx=(0,20))
        self.ef_var.trace_add("write", lambda n,i,m, attr='moedas_ef', sv=self.ef_var : self._update_personagem_inventory_attr(attr, sv, is_int=True))


        efp_label = ctk.CTkLabel(master=money_sub_frame, text="Elfen Prata (EfP):")
        efp_label.pack(side="left", padx=(0,5))
        self.efp_entry = ctk.CTkEntry(master=money_sub_frame, placeholder_text="0", width=100, textvariable=self.efp_var)
        self.efp_entry.pack(side="left", padx=(0,5))
        self.efp_var.trace_add("write", lambda n,i,m, attr='moedas_efp', sv=self.efp_var : self._update_personagem_inventory_attr(attr, sv, is_int=True))


    def setup_items_list_section(self):
        items_list_main_frame = ctk.CTkFrame(self.main_frame)
        items_list_main_frame.grid(row=1, column=0, padx=5, pady=0, sticky="nsew")
        items_list_main_frame.rowconfigure(1, weight=1) 
        items_list_main_frame.columnconfigure(0, weight=1) 

        title_items_label = ctk.CTkLabel(master=items_list_main_frame, text="Itens Gerais", font=ctk.CTkFont(size=16, weight="bold"))
        title_items_label.pack(pady=(5,10))

        self.items_scroll_frame = ctk.CTkScrollableFrame(items_list_main_frame, label_text="")
        self.items_scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.items_scroll_frame.columnconfigure(0, weight=3); self.items_scroll_frame.columnconfigure(1, weight=1)
        self.items_scroll_frame.columnconfigure(2, weight=1); self.items_scroll_frame.columnconfigure(3, weight=4)
        self.items_scroll_frame.columnconfigure(4, weight=0)

        headers = ["Item", "Qtd.", "Peso", "Descrição/Notas"]
        for col, header_text in enumerate(headers):
            header_label = ctk.CTkLabel(master=self.items_scroll_frame, text=header_text, font=ctk.CTkFont(weight="bold"))
            header_label.grid(row=0, column=col, padx=5, pady=5, sticky="w")
        
        self.item_current_row = 1 

        add_item_button = ctk.CTkButton(master=items_list_main_frame, text="Adicionar Item", command=lambda: self.add_item_entry_row()) # Lambda para chamar sem args padrão
        add_item_button.pack(pady=10, side="left", padx=10)
        
        # O botão de remover selecionados ainda é WIP
        # remove_selected_button = ctk.CTkButton(master=items_list_main_frame, text="Remover Selecionados (WIP)", command=self.remove_selected_items, fg_color="gray")
        # remove_selected_button.pack(pady=10, side="left", padx=10)

    def add_item_entry_row(self, name="", quantity="1", weight="", description=""):
        item_data = { # Dicionário para guardar os dados do item
            'name': name, 'quantity': quantity, 
            'weight': weight, 'description': description
        }
        
        # Adiciona ao objeto personagem se for uma nova linha adicionada pela UI e tiver nome
        # A lógica de carregamento já popula self.personagem.itens_gerais
        # Esta lógica é para quando o *usuário* clica em "Adicionar Item"
        is_new_from_ui_button = not (name or description or weight) # Heurística para saber se é um clique no botão "Adicionar"
        if is_new_from_ui_button:
            # Se for um clique no botão, os valores iniciais já estão nos placeholders
            # Atualizamos o item_data com os placeholders, mas só adicionamos ao personagem quando houver nome.
             pass # Adicionaremos ao self.personagem quando o nome for preenchido no _on_item_data_change
        elif not any(item['name'] == name for item in self.personagem.itens_gerais if name): # Evita duplicar ao carregar
             self.personagem.itens_gerais.append(item_data)


        item_frame_row = ctk.CTkFrame(self.items_scroll_frame, fg_color="transparent")
        item_frame_row.grid(row=self.item_current_row, column=0, columnspan=5, sticky="ew", pady=(0,2))
        item_frame_row.columnconfigure(0, weight=3); item_frame_row.columnconfigure(1, weight=1)
        item_frame_row.columnconfigure(2, weight=1); item_frame_row.columnconfigure(3, weight=4)
        item_frame_row.columnconfigure(4, weight=0) 

        row_ui_elements = {'frame': item_frame_row, 'data_dict_ref': item_data} # Guarda referência ao dict

        name_var = ctk.StringVar(value=name)
        name_entry = ctk.CTkEntry(master=item_frame_row, placeholder_text="Nome do item", textvariable=name_var)
        name_entry.grid(row=0, column=0, padx=2, pady=2, sticky="ew")
        name_var.trace_add("write", lambda n,i,m, d=item_data, k='name', v=name_var: self._on_item_data_change(d,k,v, is_new_from_ui_button))
        row_ui_elements['name_entry'] = name_entry # Guardar o widget em si

        qty_var = ctk.StringVar(value=str(quantity))
        qty_entry = ctk.CTkEntry(master=item_frame_row, placeholder_text="Qtd.", width=50, textvariable=qty_var)
        qty_entry.grid(row=0, column=1, padx=2, pady=2, sticky="ew")
        qty_var.trace_add("write", lambda n,i,m, d=item_data, k='quantity', v=qty_var: self._on_item_data_change(d,k,v))
        row_ui_elements['qty_entry'] = qty_entry

        weight_var = ctk.StringVar(value=str(weight))
        weight_entry = ctk.CTkEntry(master=item_frame_row, placeholder_text="Peso", textvariable=weight_var)
        weight_entry.grid(row=0, column=2, padx=2, pady=2, sticky="ew")
        weight_var.trace_add("write", lambda n,i,m, d=item_data, k='weight', v=weight_var: self._on_item_data_change(d,k,v))
        row_ui_elements['weight_entry'] = weight_entry
        
        desc_var = ctk.StringVar(value=description)
        desc_entry = ctk.CTkEntry(master=item_frame_row, placeholder_text="Descrição ou notas", textvariable=desc_var)
        desc_entry.grid(row=0, column=3, padx=2, pady=2, sticky="ew")
        desc_var.trace_add("write", lambda n,i,m, d=item_data, k='description', v=desc_var: self._on_item_data_change(d,k,v))
        row_ui_elements['desc_entry'] = desc_entry

        remove_button = ctk.CTkButton(master=item_frame_row, text="X", width=25, height=25,
                                      command=lambda r_data=item_data, r_frame=item_frame_row: self.remove_item_row(r_data, r_frame))
        remove_button.grid(row=0, column=4, padx=(5,0), pady=2, sticky="e")
        row_ui_elements['remove_button'] = remove_button
        
        self.item_rows.append(row_ui_elements) 
        self.item_current_row += 1

    def _on_item_data_change(self, item_data_dict_ref, key, string_var, is_new_row_from_button=False, *args):
        """Atualiza o dicionário de dados do item no objeto Personagem."""
        new_value = string_var.get()
        
        # Se for um item novo (linha vazia adicionada pelo botão) e o nome está sendo preenchido pela 1a vez,
        # e esse item_data_dict_ref ainda não está na lista do personagem.
        if is_new_row_from_button and key == 'name' and new_value.strip() and \
           item_data_dict_ref not in self.personagem.itens_gerais:
            self.personagem.itens_gerais.append(item_data_dict_ref)
            # Marcar que não é mais "novo" para evitar readicionar
            # Isso requer uma forma de passar o estado 'is_new_from_ui_button' para False após a primeira edição de nome.
            # Uma solução mais simples é checar se 'name' está em item_data_dict_ref antes de adicionar.
            # A lógica de adicionar em add_item_entry_row foi ajustada para ser mais simples.
            # Aqui, apenas atualizamos o dicionário que *já deve estar* na lista do personagem.
            
        item_data_dict_ref[key] = new_value
        # print(f"Item '{item_data_dict_ref.get('name')}' campo '{key}' atualizado para '{new_value}'. Personagem itens: {self.personagem.itens_gerais}") # Debug
        
    def remove_item_row(self, item_data_to_remove, item_frame_to_remove):
        item_frame_to_remove.destroy()
        
        # Remove da lista de widgets da UI
        found_widget_entry = None
        for entry in self.item_rows:
            if entry.get("frame") == item_frame_to_remove:
                found_widget_entry = entry
                break
        if found_widget_entry:
            self.item_rows.remove(found_widget_entry)

        # Remove do objeto Personagem
        if item_data_to_remove in self.personagem.itens_gerais:
            self.personagem.itens_gerais.remove(item_data_to_remove)
        # print(f"Itens no personagem após remover: {self.personagem.itens_gerais}") # Debug

    def setup_load_limit_section(self):
        load_frame = ctk.CTkFrame(self.main_frame)
        load_frame.grid(row=2, column=0, padx=5, pady=(10,0), sticky="ew")

        load_label = ctk.CTkLabel(master=load_frame, text="Limite de Carga (Narrativo):", font=ctk.CTkFont(weight="bold"))
        load_label.pack(side="left", padx=10, pady=5)
        
        self.load_status_entry = ctk.CTkEntry(master=load_frame, placeholder_text="Ex: Leve, Normal...", textvariable=self.load_status_var)
        self.load_status_entry.pack(side="left", padx=10, pady=5, fill="x", expand=True)
        self.load_status_var.trace_add("write", lambda n,i,m, attr='limite_carga_status', sv=self.load_status_var : self._update_personagem_inventory_attr(attr, sv))