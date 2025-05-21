import customtkinter as ctk

class InventoryTab:
    def __init__(self, tab_widget):
        self.tab_widget = tab_widget
        self.item_rows = [] # Para guardar referências às linhas de itens

        # --- Frame Principal para a Aba de Inventário ---
        self.main_frame = ctk.CTkFrame(self.tab_widget, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        self.main_frame.columnconfigure(0, weight=1) # Coluna única para expandir a lista de itens
        self.main_frame.rowconfigure(1, weight=1) # Para a lista de itens expandir verticalmente

        # --- Seção de Moedas ---
        self.setup_currency_section()

        # --- Seção da Lista de Itens ---
        self.setup_items_list_section()
        
        # --- Seção de Carga (Opcional, mais narrativo no Elaria RPG) ---
        self.setup_load_limit_section()

    def setup_currency_section(self):
        currency_frame = ctk.CTkFrame(self.main_frame)
        currency_frame.grid(row=0, column=0, padx=5, pady=(0,10), sticky="ew")
        
        title_currency_label = ctk.CTkLabel(master=currency_frame, text="Moedas", font=ctk.CTkFont(size=16, weight="bold"))
        title_currency_label.pack(pady=(5,10))

        money_sub_frame = ctk.CTkFrame(currency_frame, fg_color="transparent")
        money_sub_frame.pack(fill="x", padx=10)

        # Elfen (Ef)
        ef_label = ctk.CTkLabel(master=money_sub_frame, text="Elfen (Ef):")
        ef_label.pack(side="left", padx=(0,5))
        self.ef_entry = ctk.CTkEntry(master=money_sub_frame, placeholder_text="0", width=100)
        self.ef_entry.pack(side="left", padx=(0,20))

        # Elfen Prata (EfP)
        efp_label = ctk.CTkLabel(master=money_sub_frame, text="Elfen Prata (EfP):")
        efp_label.pack(side="left", padx=(0,5))
        self.efp_entry = ctk.CTkEntry(master=money_sub_frame, placeholder_text="0", width=100)
        self.efp_entry.pack(side="left", padx=(0,5))
        # [cite: 695, 696]

    def setup_items_list_section(self):
        items_list_main_frame = ctk.CTkFrame(self.main_frame)
        items_list_main_frame.grid(row=1, column=0, padx=5, pady=0, sticky="nsew")
        items_list_main_frame.rowconfigure(1, weight=1) # Para o scrollable frame expandir
        items_list_main_frame.columnconfigure(0, weight=1) # Para o scrollable frame expandir


        title_items_label = ctk.CTkLabel(master=items_list_main_frame, text="Itens Gerais", font=ctk.CTkFont(size=16, weight="bold"))
        title_items_label.pack(pady=(5,10))

        self.items_scroll_frame = ctk.CTkScrollableFrame(items_list_main_frame, label_text="")
        self.items_scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Configurar colunas para a lista de itens
        self.items_scroll_frame.columnconfigure(0, weight=3)  # Nome do Item (mais largo)
        self.items_scroll_frame.columnconfigure(1, weight=1)  # Quantidade
        self.items_scroll_frame.columnconfigure(2, weight=1)  # Peso (opcional)
        self.items_scroll_frame.columnconfigure(3, weight=4)  # Descrição/Notas (mais largo)
        self.items_scroll_frame.columnconfigure(4, weight=0)  # Botão Remover (compacto)


        # Cabeçalhos da lista de itens
        headers = ["Item", "Qtd.", "Peso", "Descrição/Notas"]
        for col, header_text in enumerate(headers):
            header_label = ctk.CTkLabel(master=self.items_scroll_frame, text=header_text, font=ctk.CTkFont(weight="bold"))
            header_label.grid(row=0, column=col, padx=5, pady=5, sticky="w")
        
        # Inicializar contador de linha de item
        self.item_current_row = 1 # Começa após os cabeçalhos

        # Adicionar alguns itens de exemplo do equipamento inicial gratuito [cite: 698, 699]
        self.add_item_entry_row(name="Mochila", quantity="1", weight="", description="Equipamento inicial")
        self.add_item_entry_row(name="Saco de Dormir", quantity="1", weight="", description="Equipamento inicial")
        self.add_item_entry_row(name="Traje de Viajante", quantity="1", weight="", description="Equipamento inicial")
        self.add_item_entry_row() # Linha vazia para novo item

        add_item_button = ctk.CTkButton(master=items_list_main_frame, text="Adicionar Item", command=self.add_item_entry_row)
        add_item_button.pack(pady=10, side="left", padx=10)
        
        remove_selected_button = ctk.CTkButton(master=items_list_main_frame, text="Remover Selecionados (WIP)", command=self.remove_selected_items, fg_color="gray")
        remove_selected_button.pack(pady=10, side="left", padx=10)


    def add_item_entry_row(self, name="", quantity="", weight="", description=""):
        item_frame_row = ctk.CTkFrame(self.items_scroll_frame, fg_color="transparent") # Frame para a linha
        item_frame_row.grid(row=self.item_current_row, column=0, columnspan=5, sticky="ew", pady=(0,2))
        # Configurar colunas dentro do frame da linha para corresponder aos cabeçalhos
        item_frame_row.columnconfigure(0, weight=3)
        item_frame_row.columnconfigure(1, weight=1)
        item_frame_row.columnconfigure(2, weight=1)
        item_frame_row.columnconfigure(3, weight=4)
        item_frame_row.columnconfigure(4, weight=0) # Para o botão de remover individual

        row_widgets = {}

        name_entry = ctk.CTkEntry(master=item_frame_row, placeholder_text="Nome do item")
        name_entry.insert(0, name)
        name_entry.grid(row=0, column=0, padx=2, pady=2, sticky="ew")
        row_widgets['name'] = name_entry

        qty_entry = ctk.CTkEntry(master=item_frame_row, placeholder_text="Qtd.", width=50)
        qty_entry.insert(0, quantity)
        qty_entry.grid(row=0, column=1, padx=2, pady=2, sticky="ew")
        row_widgets['quantity'] = qty_entry

        weight_entry = ctk.CTkEntry(master=item_frame_row, placeholder_text="Peso")
        weight_entry.insert(0, weight)
        weight_entry.grid(row=0, column=2, padx=2, pady=2, sticky="ew")
        row_widgets['weight'] = weight_entry
        
        desc_entry = ctk.CTkEntry(master=item_frame_row, placeholder_text="Descrição ou notas")
        desc_entry.insert(0, description)
        desc_entry.grid(row=0, column=3, padx=2, pady=2, sticky="ew")
        row_widgets['description'] = desc_entry

        remove_button = ctk.CTkButton(master=item_frame_row, text="X", width=25, height=25,
                                      command=lambda r_frame=item_frame_row: self.remove_item_row(r_frame))
        remove_button.grid(row=0, column=4, padx=(5,0), pady=2, sticky="e")
        row_widgets['remove_button'] = remove_button
        
        self.item_rows.append(item_frame_row) # Adiciona o frame da linha para rastreamento
        self.item_current_row += 1
        
    def remove_item_row(self, item_frame_to_remove):
        item_frame_to_remove.destroy()
        if item_frame_to_remove in self.item_rows:
            self.item_rows.remove(item_frame_to_remove)
        # Nota: A renumeração das linhas do grid não acontece automaticamente.
        # Para uma remoção mais robusta com reorganização visual, seria preciso reconstruir
        # as posições no grid ou usar um gerenciador de layout diferente para os itens.
        # Por enquanto, a linha some, o que é funcional.

    def remove_selected_items(self):
        # Esta função é um placeholder (WIP - Work In Progress)
        # Implementação futura: adicionar checkboxes a cada item e remover os selecionados.
        print("Funcionalidade 'Remover Selecionados' ainda não implementada.")

    def setup_load_limit_section(self):
        load_frame = ctk.CTkFrame(self.main_frame)
        load_frame.grid(row=2, column=0, padx=5, pady=(10,0), sticky="ew")

        load_label = ctk.CTkLabel(master=load_frame, text="Limite de Carga (Narrativo):", font=ctk.CTkFont(weight="bold"))
        load_label.pack(side="left", padx=10, pady=5)
        
        self.load_status_entry = ctk.CTkEntry(master=load_frame, placeholder_text="Ex: Leve, Normal, Pesado...")
        self.load_status_entry.pack(side="left", padx=10, pady=5, fill="x", expand=True)
        # [cite: 710, 711, 712]