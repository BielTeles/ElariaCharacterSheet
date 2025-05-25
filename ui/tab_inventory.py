import customtkinter as ctk
from typing import List, Dict, Any, Union, Optional

# from core.character import Personagem # Para type hinting, se necessário

class InventoryTab:
    """
    Gerencia a aba de Inventário, incluindo moedas, itens gerais e limite de carga.
    """
    personagem: Any  # Idealmente: Personagem
    item_rows: List[Dict[str, Any]] # Lista para armazenar refs de widgets e dados de cada item
    item_current_row: int # Índice para a próxima linha no scrollframe de itens

    # StringVars para moedas e carga
    ef_var: ctk.StringVar
    efp_var: ctk.StringVar
    load_status_var: ctk.StringVar

    items_scroll_frame: ctk.CTkScrollableFrame
    ef_entry: ctk.CTkEntry
    efp_entry: ctk.CTkEntry
    load_status_entry: ctk.CTkEntry


    def __init__(self, tab_widget: ctk.CTkFrame, personagem_atual: Any):
        self.tab_widget = tab_widget
        self.personagem = personagem_atual
        self.item_rows = []
        self.item_current_row = 1 # Headers estão na linha 0

        self.ef_var = ctk.StringVar()
        self.efp_var = ctk.StringVar()
        self.load_status_var = ctk.StringVar()

        self.main_frame = ctk.CTkFrame(self.tab_widget, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)  # Para a lista de itens expandir

        self.setup_currency_section()
        self.setup_items_list_section()
        self.setup_load_limit_section()

        self.load_data_from_personagem()

    def load_data_from_personagem(self) -> None:
        """Carrega dados do objeto Personagem para a UI da aba de Inventário."""
        self.ef_var.set(str(self.personagem.moedas_ef))
        self.efp_var.set(str(self.personagem.moedas_efp))
        self.load_status_var.set(str(self.personagem.limite_carga_status))

        # Limpa itens existentes na UI antes de carregar
        for row_elements in self.item_rows:
            frame_widget = row_elements.get('frame')
            if isinstance(frame_widget, ctk.CTkFrame): # Verificação de tipo
                frame_widget.destroy()
        self.item_rows.clear()
        self.item_current_row = 1  # Reseta o contador de linha para o scrollframe (após cabeçalhos)

        # Carrega itens do inventário do personagem
        if hasattr(self.personagem, 'itens_gerais') and isinstance(self.personagem.itens_gerais, list):
            for item_data_ref in self.personagem.itens_gerais:
                # Passa a referência direta do dicionário do personagem
                self.add_item_entry_row(item_data_ref=item_data_ref, is_loading=True)
        else: # Adiciona exemplos se não houver nada carregado e a lista não existir
            self.add_item_entry_row(initial_item_data={"name": "Mochila", "quantity": "1", "weight": "", "description": "Equipamento inicial"})
            self.add_item_entry_row(initial_item_data={"name": "Saco de Dormir", "quantity": "1", "weight": "", "description": "Equipamento inicial"})
            # Adiciona uma linha vazia para o usuário começar
            self.add_item_entry_row()


    def _update_personagem_inventory_attr(self, attr_name: str, string_var: ctk.StringVar, is_int: bool = False) -> None:
        """Atualiza um atributo do inventário (moedas, carga) no objeto Personagem."""
        value_str = string_var.get()
        value_to_set: Union[str, int] = value_str
        current_model_value = getattr(self.personagem, attr_name, 0 if is_int else "")

        if is_int:
            try:
                value_to_set = int(value_str) if value_str.strip() else 0
            except ValueError:
                string_var.set(str(current_model_value)) # Reverte na UI
                return # Interrompe se a conversão falhar

        if str(current_model_value) != str(value_to_set):
            setattr(self.personagem, attr_name, value_to_set)
            # print(f"Personagem.{attr_name} atualizado para: {value_to_set}") # Para debug

    def setup_currency_section(self) -> None:
        """Configura a seção de moedas na UI."""
        currency_frame = ctk.CTkFrame(self.main_frame)
        currency_frame.grid(row=0, column=0, padx=5, pady=(0,10), sticky="ew")
        
        title_currency_label = ctk.CTkLabel(master=currency_frame, text="Moedas", font=ctk.CTkFont(size=16, weight="bold"))
        title_currency_label.pack(pady=(5,10))

        money_sub_frame = ctk.CTkFrame(currency_frame, fg_color="transparent")
        money_sub_frame.pack(fill="x", padx=10, pady=5) # Adicionado pady

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

    def setup_items_list_section(self) -> None:
        """Configura a seção da lista de itens gerais na UI."""
        items_list_main_frame = ctk.CTkFrame(self.main_frame)
        items_list_main_frame.grid(row=1, column=0, padx=5, pady=0, sticky="nsew")
        items_list_main_frame.rowconfigure(1, weight=1)
        items_list_main_frame.columnconfigure(0, weight=1)

        title_items_label = ctk.CTkLabel(master=items_list_main_frame, text="Itens Gerais", font=ctk.CTkFont(size=16, weight="bold"))
        title_items_label.pack(pady=(5,10))

        self.items_scroll_frame = ctk.CTkScrollableFrame(items_list_main_frame, label_text="")
        self.items_scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Configuração das colunas
        self.items_scroll_frame.columnconfigure(0, weight=3)  # Item
        self.items_scroll_frame.columnconfigure(1, weight=1)  # Qtd.
        self.items_scroll_frame.columnconfigure(2, weight=1)  # Peso
        self.items_scroll_frame.columnconfigure(3, weight=4)  # Descrição/Notas
        self.items_scroll_frame.columnconfigure(4, weight=0)  # Botão Remover

        # Cabeçalhos
        headers = ["Item", "Qtd.", "Peso", "Descrição/Notas"]
        for col, header_text in enumerate(headers):
            header_label = ctk.CTkLabel(master=self.items_scroll_frame, text=header_text, font=ctk.CTkFont(weight="bold"))
            header_label.grid(row=0, column=col, padx=5, pady=(5,10), sticky="w") # pady ajustado
        
        self.item_current_row = 1 # Inicia na linha 1, após os cabeçalhos

        add_item_button = ctk.CTkButton(master=items_list_main_frame, text="Adicionar Item", command=self.add_item_entry_row)
        add_item_button.pack(pady=10, side="left", padx=10)

    def add_item_entry_row(self, item_data_ref: Optional[Dict[str, Any]] = None, 
                           is_loading: bool = False, 
                           initial_item_data: Optional[Dict[str, str]] = None) -> None:
        """
        Adiciona uma linha de entrada de item à UI.
        Se 'item_data_ref' é fornecido (durante o carregamento), usa essa referência.
        Caso contrário (nova linha pela UI), cria um novo dicionário.
        'initial_item_data' pode ser usado para pré-popular uma nova linha (e.g., exemplos).
        """
        current_item_data: Dict[str, Any]
        is_completely_new_row_by_button_click = False

        if is_loading and item_data_ref is not None:
            current_item_data = item_data_ref # Usa a referência direta do modelo
        else: # Nova linha (ou exemplos iniciais)
            current_item_data = {
                'name': initial_item_data.get('name', "") if initial_item_data else "",
                'quantity': initial_item_data.get('quantity', "1") if initial_item_data else "1",
                'weight': initial_item_data.get('weight', "") if initial_item_data else "",
                'description': initial_item_data.get('description', "") if initial_item_data else ""
            }
            if not initial_item_data: # Se não for um exemplo, é uma linha nova clicada pelo usuário
                 is_completely_new_row_by_button_click = True
            # Este novo dicionário só será adicionado ao self.personagem.itens_gerais
            # em _on_item_data_change se o nome for preenchido.

        item_frame_row = ctk.CTkFrame(self.items_scroll_frame, fg_color="transparent")
        item_frame_row.grid(row=self.item_current_row, column=0, columnspan=5, sticky="ew", pady=(0,2))
        item_frame_row.columnconfigure(0, weight=3); item_frame_row.columnconfigure(1, weight=1)
        item_frame_row.columnconfigure(2, weight=1); item_frame_row.columnconfigure(3, weight=4)
        item_frame_row.columnconfigure(4, weight=0)

        row_ui_elements = {'frame': item_frame_row, 'data_dict_ref': current_item_data}

        # Nome
        name_var = ctk.StringVar(value=str(current_item_data.get('name', "")))
        name_entry = ctk.CTkEntry(master=item_frame_row, placeholder_text="Nome do item", textvariable=name_var)
        name_entry.grid(row=0, column=0, padx=2, pady=2, sticky="ew")
        name_var.trace_add("write", lambda n,i,m, d=current_item_data, k='name', v=name_var, new_row=is_completely_new_row_by_button_click: self._on_item_data_change(d,k,v,new_row))
        
        # Quantidade
        qty_var = ctk.StringVar(value=str(current_item_data.get('quantity', "1")))
        qty_entry = ctk.CTkEntry(master=item_frame_row, placeholder_text="Qtd.", width=60, textvariable=qty_var) # Aumentado width
        qty_entry.grid(row=0, column=1, padx=2, pady=2, sticky="ew")
        qty_var.trace_add("write", lambda n,i,m, d=current_item_data, k='quantity', v=qty_var: self._on_item_data_change(d,k,v))
        
        # Peso
        weight_var = ctk.StringVar(value=str(current_item_data.get('weight', "")))
        weight_entry = ctk.CTkEntry(master=item_frame_row, placeholder_text="Peso", width=70, textvariable=weight_var) # Aumentado width
        weight_entry.grid(row=0, column=2, padx=2, pady=2, sticky="ew")
        weight_var.trace_add("write", lambda n,i,m, d=current_item_data, k='weight', v=weight_var: self._on_item_data_change(d,k,v))
        
        # Descrição
        desc_var = ctk.StringVar(value=str(current_item_data.get('description', "")))
        desc_entry = ctk.CTkEntry(master=item_frame_row, placeholder_text="Descrição ou notas", textvariable=desc_var)
        desc_entry.grid(row=0, column=3, padx=2, pady=2, sticky="ew")
        desc_var.trace_add("write", lambda n,i,m, d=current_item_data, k='description', v=desc_var: self._on_item_data_change(d,k,v))

        remove_button = ctk.CTkButton(master=item_frame_row, text="X", width=25, height=25,
                                      command=lambda r_data=current_item_data, r_frame=item_frame_row: self.remove_item_row(r_data, r_frame))
        remove_button.grid(row=0, column=4, padx=(5,0), pady=2, sticky="e")
        
        self.item_rows.append(row_ui_elements)
        self.item_current_row += 1

    def _on_item_data_change(self, item_data_dict_ref: Dict[str, Any], key: str,
                               string_var: ctk.StringVar, is_new_row_from_button: bool = False) -> None:
        """Atualiza o dicionário de dados do item no objeto Personagem."""
        new_value = string_var.get()
        
        # Se for um item novo (linha vazia adicionada pelo botão) e o nome está sendo preenchido pela 1a vez,
        # e esse item_data_dict_ref ainda não está na lista do personagem.
        if is_new_row_from_button and key == 'name' and new_value.strip() and \
           item_data_dict_ref not in self.personagem.itens_gerais:
            self.personagem.itens_gerais.append(item_data_dict_ref)
            # Uma vez adicionado, não é mais "novo" para este callback
            # A flag is_new_row_from_button só é relevante para a primeira edição do nome.

        if item_data_dict_ref.get(key) != new_value:
             item_data_dict_ref[key] = new_value
        # print(f"Item '{item_data_dict_ref.get('name')}' campo '{key}' atualizado para '{new_value}'.") # Debug

    def remove_item_row(self, item_data_to_remove: Dict[str, Any], item_frame_to_remove: ctk.CTkFrame) -> None:
        """Remove uma linha de item da UI e do inventário do personagem."""
        item_frame_to_remove.destroy()
        
        found_widget_entry = None
        for entry in self.item_rows:
            if entry.get("frame") == item_frame_to_remove:
                found_widget_entry = entry
                break
        if found_widget_entry:
            self.item_rows.remove(found_widget_entry)

        if item_data_to_remove in self.personagem.itens_gerais:
            self.personagem.itens_gerais.remove(item_data_to_remove)
        # print(f"Itens no personagem após remover: {len(self.personagem.itens_gerais)}") # Debug

    def setup_load_limit_section(self) -> None:
        """Configura a seção de limite de carga na UI."""
        load_frame = ctk.CTkFrame(self.main_frame)
        load_frame.grid(row=2, column=0, padx=5, pady=(10,0), sticky="ew")

        load_label = ctk.CTkLabel(master=load_frame, text="Limite de Carga (Narrativo):", font=ctk.CTkFont(weight="bold"))
        load_label.pack(side="left", padx=10, pady=5)
        
        self.load_status_entry = ctk.CTkEntry(master=load_frame, placeholder_text="Ex: Leve, Normal...", textvariable=self.load_status_var)
        self.load_status_entry.pack(side="left", padx=10, pady=5, fill="x", expand=True)
        self.load_status_var.trace_add("write", lambda n,i,m, attr='limite_carga_status', sv=self.load_status_var : self._update_personagem_inventory_attr(attr, sv))