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

        # Limpa os itens existentes na UI
        for scroll_frame in [self.weapons_scroll, self.armor_scroll, self.misc_scroll]:
            for widget in scroll_frame.winfo_children():
                widget.destroy()

        # Carrega armas
        if hasattr(self.personagem, 'armas') and isinstance(self.personagem.armas, list):
            for weapon_data in self.personagem.armas:
                self._add_weapon_to_list(weapon_data)
        
        # Carrega armaduras
        if hasattr(self.personagem, 'armaduras') and isinstance(self.personagem.armaduras, list):
            for armor_data in self.personagem.armaduras:
                self._add_armor_to_list(armor_data)
        
        # Carrega itens diversos
        if hasattr(self.personagem, 'itens_diversos') and isinstance(self.personagem.itens_diversos, list):
            for misc_data in self.personagem.itens_diversos:
                self._add_misc_to_list(misc_data)

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
        
        # Título da seção
        title_frame = ctk.CTkFrame(currency_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=5, pady=(5,0))
        ctk.CTkLabel(title_frame, text="💰 Moedas", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
        
        # Container para os valores de moedas
        money_frame = ctk.CTkFrame(currency_frame, fg_color="transparent")
        money_frame.pack(fill="x", padx=10, pady=5)
        
        # Elfen com ícone
        ef_frame = ctk.CTkFrame(money_frame, fg_color="#2B2B2B")
        ef_frame.pack(side="left", padx=5, fill="both", expand=True)
        ctk.CTkLabel(ef_frame, text="💎", font=ctk.CTkFont(size=20)).pack(side="left", padx=5)
        ctk.CTkLabel(ef_frame, text="Elfen (Ef)", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=2)
        self.ef_entry = ctk.CTkEntry(ef_frame, textvariable=self.ef_var, width=80, justify="center")
        self.ef_entry.pack(side="right", padx=5, pady=5)
        self.ef_var.trace_add("write", lambda n,i,m, attr='moedas_ef', sv=self.ef_var : self._update_personagem_inventory_attr(attr, sv, is_int=True))
        
        # Elfen Prata com ícone
        efp_frame = ctk.CTkFrame(money_frame, fg_color="#2B2B2B")
        efp_frame.pack(side="left", padx=5, fill="both", expand=True)
        ctk.CTkLabel(efp_frame, text="🔘", font=ctk.CTkFont(size=20)).pack(side="left", padx=5)
        ctk.CTkLabel(efp_frame, text="Elfen Prata (EfP)", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=2)
        self.efp_entry = ctk.CTkEntry(efp_frame, textvariable=self.efp_var, width=80, justify="center")
        self.efp_entry.pack(side="right", padx=5, pady=5)
        self.efp_var.trace_add("write", lambda n,i,m, attr='moedas_efp', sv=self.efp_var : self._update_personagem_inventory_attr(attr, sv, is_int=True))

    def setup_items_list_section(self) -> None:
        """Configura a seção da lista de itens gerais na UI."""
        items_list_main_frame = ctk.CTkFrame(self.main_frame)
        items_list_main_frame.grid(row=1, column=0, padx=5, pady=0, sticky="nsew")
        items_list_main_frame.rowconfigure(1, weight=1)
        items_list_main_frame.columnconfigure(0, weight=1)

        # Título da seção
        title_frame = ctk.CTkFrame(items_list_main_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=5, pady=(5,0))
        ctk.CTkLabel(title_frame, text="📦 Inventário", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
        
        # Botões de adicionar por categoria
        buttons_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
        buttons_frame.pack(side="right", padx=5)
        
        add_weapon_button = ctk.CTkButton(buttons_frame, 
                                        text="⚔️ Nova Arma", 
                                        command=lambda: self.show_add_item_dialog("weapon"),
                                        fg_color="#2B2B2B",
                                        hover_color="#1a1a1a",
                                        width=100)
        add_weapon_button.pack(side="left", padx=2)
        
        add_armor_button = ctk.CTkButton(buttons_frame, 
                                       text="🛡️ Nova Armadura", 
                                       command=lambda: self.show_add_item_dialog("armor"),
                                       fg_color="#2B2B2B",
                                       hover_color="#1a1a1a",
                                       width=120)
        add_armor_button.pack(side="left", padx=2)
        
        add_misc_button = ctk.CTkButton(buttons_frame, 
                                      text="📦 Novo Item", 
                                      command=lambda: self.show_add_item_dialog("misc"),
                                      fg_color="#2B2B2B",
                                      hover_color="#1a1a1a",
                                      width=100)
        add_misc_button.pack(side="left", padx=2)

        # TabView para as diferentes categorias
        self.inventory_tabview = ctk.CTkTabview(items_list_main_frame)
        self.inventory_tabview.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Criação das abas
        self.weapons_tab = self.inventory_tabview.add("⚔️ Armas")
        self.armor_tab = self.inventory_tabview.add("🛡️ Armaduras")
        self.misc_tab = self.inventory_tabview.add("📦 Itens Diversos")
        
        # Configuração dos frames scrolláveis para cada categoria
        self.setup_weapons_list()
        self.setup_armor_list()
        self.setup_misc_items_list()

    def setup_weapons_list(self) -> None:
        """Configura a lista de armas."""
        self.weapons_scroll = ctk.CTkScrollableFrame(self.weapons_tab)
        self.weapons_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Cabeçalhos para armas
        headers = [
            ("⚔️ Nome", 0),
            ("🎯 Atributo", 1),
            ("💥 Dano", 2),
            ("🎲 Perícia", 3),
            ("✋ Empunhadura", 4),
            ("📏 Alcance", 5),
            ("📝 Notas", 6)
        ]
        
        header_frame = ctk.CTkFrame(self.weapons_scroll, fg_color="#2B2B2B")
        header_frame.pack(fill="x", pady=(0,5))
        
        for header_text, col in headers:
            header_label = ctk.CTkLabel(master=header_frame, 
                                      text=header_text, 
                                      font=ctk.CTkFont(weight="bold"),
                                      anchor="w")
            header_label.grid(row=0, column=col, padx=5, pady=5, sticky="ew")
            header_frame.columnconfigure(col, weight=1 if col == 6 else 0)

    def setup_armor_list(self) -> None:
        """Configura a lista de armaduras."""
        self.armor_scroll = ctk.CTkScrollableFrame(self.armor_tab)
        self.armor_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Cabeçalhos para armaduras
        headers = [
            ("🛡️ Nome", 0),
            ("💪 RD", 1),
            ("👕 Tipo", 2),
            ("⚖️ Peso", 3),
            ("📝 Notas", 4)
        ]
        
        header_frame = ctk.CTkFrame(self.armor_scroll, fg_color="#2B2B2B")
        header_frame.pack(fill="x", pady=(0,5))
        
        for header_text, col in headers:
            header_label = ctk.CTkLabel(master=header_frame, 
                                      text=header_text, 
                                      font=ctk.CTkFont(weight="bold"),
                                      anchor="w")
            header_label.grid(row=0, column=col, padx=5, pady=5, sticky="ew")
            header_frame.columnconfigure(col, weight=1 if col == 4 else 0)

    def setup_misc_items_list(self) -> None:
        """Configura a lista de itens diversos."""
        self.misc_scroll = ctk.CTkScrollableFrame(self.misc_tab)
        self.misc_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Cabeçalhos para itens diversos
        headers = [
            ("📦 Nome", 0),
            ("# Qtd.", 1),
            ("⚖️ Peso", 2),
            ("📝 Descrição", 3)
        ]
        
        header_frame = ctk.CTkFrame(self.misc_scroll, fg_color="#2B2B2B")
        header_frame.pack(fill="x", pady=(0,5))
        
        for header_text, col in headers:
            header_label = ctk.CTkLabel(master=header_frame, 
                                      text=header_text, 
                                      font=ctk.CTkFont(weight="bold"),
                                      anchor="w")
            header_label.grid(row=0, column=col, padx=5, pady=5, sticky="ew")
            header_frame.columnconfigure(col, weight=1 if col == 3 else 0)

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

        # Frame principal da linha com fundo escuro
        item_frame_row = ctk.CTkFrame(self.items_scroll_frame, fg_color="#2B2B2B")
        item_frame_row.grid(row=self.item_current_row, column=0, columnspan=5, sticky="ew", pady=(0,2))
        
        # Configuração do grid
        item_frame_row.columnconfigure(0, weight=3)  # Nome
        item_frame_row.columnconfigure(1, weight=1)  # Quantidade
        item_frame_row.columnconfigure(2, weight=1)  # Peso
        item_frame_row.columnconfigure(3, weight=4)  # Descrição
        item_frame_row.columnconfigure(4, weight=0)  # Botão remover

        row_ui_elements = {'frame': item_frame_row, 'data_dict_ref': current_item_data}

        # Container para nome do item
        name_container = ctk.CTkFrame(item_frame_row, fg_color="transparent")
        name_container.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        name_container.columnconfigure(1, weight=1)
        
        ctk.CTkLabel(name_container, text="📦", font=ctk.CTkFont(size=14)).grid(row=0, column=0, padx=(0,5))
        name_var = ctk.StringVar(value=str(current_item_data.get('name', "")))
        name_entry = ctk.CTkEntry(master=name_container, 
                                placeholder_text="Nome do item",
                                textvariable=name_var)
        name_entry.grid(row=0, column=1, sticky="ew")
        name_var.trace_add("write", lambda n,i,m, d=current_item_data, k='name', v=name_var, new_row=is_completely_new_row_by_button_click: self._on_item_data_change(d,k,v,new_row))
        
        # Container para quantidade
        qty_container = ctk.CTkFrame(item_frame_row, fg_color="transparent")
        qty_container.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        qty_container.columnconfigure(1, weight=1)
        
        ctk.CTkLabel(qty_container, text="#", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=(0,5))
        qty_var = ctk.StringVar(value=str(current_item_data.get('quantity', "1")))
        qty_entry = ctk.CTkEntry(master=qty_container, 
                               placeholder_text="Qtd.",
                               width=60,
                               textvariable=qty_var,
                               justify="center")
        qty_entry.grid(row=0, column=1, sticky="ew")
        qty_var.trace_add("write", lambda n,i,m, d=current_item_data, k='quantity', v=qty_var: self._on_item_data_change(d,k,v))
        
        # Container para peso
        weight_container = ctk.CTkFrame(item_frame_row, fg_color="transparent")
        weight_container.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        weight_container.columnconfigure(1, weight=1)
        
        ctk.CTkLabel(weight_container, text="⚖️", font=ctk.CTkFont(size=14)).grid(row=0, column=0, padx=(0,5))
        weight_var = ctk.StringVar(value=str(current_item_data.get('weight', "")))
        weight_entry = ctk.CTkEntry(master=weight_container, 
                                  placeholder_text="Peso",
                                  width=70,
                                  textvariable=weight_var,
                                  justify="center")
        weight_entry.grid(row=0, column=1, sticky="ew")
        weight_var.trace_add("write", lambda n,i,m, d=current_item_data, k='weight', v=weight_var: self._on_item_data_change(d,k,v))
        
        # Container para descrição
        desc_container = ctk.CTkFrame(item_frame_row, fg_color="transparent")
        desc_container.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        desc_container.columnconfigure(1, weight=1)
        
        ctk.CTkLabel(desc_container, text="📝", font=ctk.CTkFont(size=14)).grid(row=0, column=0, padx=(0,5))
        desc_var = ctk.StringVar(value=str(current_item_data.get('description', "")))
        desc_entry = ctk.CTkEntry(master=desc_container, 
                                placeholder_text="Descrição ou notas",
                                textvariable=desc_var)
        desc_entry.grid(row=0, column=1, sticky="ew")
        desc_var.trace_add("write", lambda n,i,m, d=current_item_data, k='description', v=desc_var: self._on_item_data_change(d,k,v))

        # Botão Remover
        remove_button = ctk.CTkButton(master=item_frame_row, 
                                    text="❌",
                                    width=30,
                                    height=30,
                                    fg_color="transparent",
                                    hover_color="#1a1a1a",
                                    command=lambda r_data=current_item_data, r_frame=item_frame_row: self.remove_item_row(r_data, r_frame))
        remove_button.grid(row=0, column=4, padx=5, pady=5, sticky="e")
        
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

        # Título da seção
        title_frame = ctk.CTkFrame(load_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=5, pady=(5,0))
        ctk.CTkLabel(title_frame, text="⚖️ Limite de Carga", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
        
        # Container para o status de carga
        status_frame = ctk.CTkFrame(load_frame, fg_color="#2B2B2B")
        status_frame.pack(fill="x", padx=10, pady=5)
        
        # Label e Entry para o status
        ctk.CTkLabel(status_frame, text="Status:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10, pady=5)
        self.load_status_entry = ctk.CTkEntry(status_frame, 
                                            placeholder_text="Ex: Leve, Normal...", 
                                            textvariable=self.load_status_var)
        self.load_status_entry.pack(side="left", padx=10, pady=5, fill="x", expand=True)
        self.load_status_var.trace_add("write", lambda n,i,m, attr='limite_carga_status', sv=self.load_status_var : self._update_personagem_inventory_attr(attr, sv))

    def show_add_item_dialog(self, item_type: str) -> None:
        """Mostra o diálogo apropriado para adicionar um novo item baseado no tipo."""
        dialog = ctk.CTkToplevel(self.tab_widget)
        dialog.title(f"Adicionar {item_type.capitalize()}")
        dialog.geometry("600x400")
        dialog.grab_set()  # Torna o diálogo modal
        
        # Frame principal do diálogo
        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Dicionário para armazenar as variáveis dos campos
        field_vars = {}
        
        if item_type == "weapon":
            self._setup_weapon_dialog(main_frame, field_vars)
        elif item_type == "armor":
            self._setup_armor_dialog(main_frame, field_vars)
        else:  # misc
            self._setup_misc_dialog(main_frame, field_vars)
        
        # Frame para botões
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10,0))
        
        # Botão Cancelar
        cancel_btn = ctk.CTkButton(button_frame, 
                                 text="Cancelar",
                                 command=dialog.destroy,
                                 fg_color="#2B2B2B",
                                 hover_color="#1a1a1a")
        cancel_btn.pack(side="right", padx=5)
        
        # Botão Adicionar
        add_btn = ctk.CTkButton(button_frame,
                               text="Adicionar",
                               command=lambda: self._add_item_from_dialog(item_type, field_vars, dialog),
                               fg_color="#2B2B2B",
                               hover_color="#1a1a1a")
        add_btn.pack(side="right", padx=5)

    def _setup_weapon_dialog(self, parent: ctk.CTkFrame, field_vars: Dict[str, ctk.StringVar]) -> None:
        """Configura os campos do diálogo para adicionar arma."""
        # Nome
        name_frame = ctk.CTkFrame(parent, fg_color="transparent")
        name_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(name_frame, text="⚔️ Nome:").pack(side="left", padx=5)
        field_vars['name'] = ctk.StringVar()
        ctk.CTkEntry(name_frame, textvariable=field_vars['name']).pack(side="left", fill="x", expand=True, padx=5)
        
        # Custo
        cost_frame = ctk.CTkFrame(parent, fg_color="transparent")
        cost_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(cost_frame, text="💰 Custo:").pack(side="left", padx=5)
        
        cost_ef_frame = ctk.CTkFrame(cost_frame, fg_color="transparent")
        cost_ef_frame.pack(side="left", padx=5)
        field_vars['custo_ef'] = ctk.StringVar(value="0")
        ctk.CTkEntry(cost_ef_frame, textvariable=field_vars['custo_ef'], width=60, justify="right").pack(side="left")
        ctk.CTkLabel(cost_ef_frame, text="Ef").pack(side="left", padx=2)
        
        cost_efp_frame = ctk.CTkFrame(cost_frame, fg_color="transparent")
        cost_efp_frame.pack(side="left", padx=5)
        field_vars['custo_efp'] = ctk.StringVar(value="0")
        ctk.CTkEntry(cost_efp_frame, textvariable=field_vars['custo_efp'], width=60, justify="right").pack(side="left")
        ctk.CTkLabel(cost_efp_frame, text="EfP").pack(side="left", padx=2)
        
        # Dano
        damage_frame = ctk.CTkFrame(parent, fg_color="transparent")
        damage_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(damage_frame, text="💥 Dano:").pack(side="left", padx=5)
        field_vars['dano'] = ctk.StringVar()
        ctk.CTkEntry(damage_frame, textvariable=field_vars['dano'], placeholder_text="Ex: 1d6").pack(side="left", padx=5)
        
        # Atributo
        attr_frame = ctk.CTkFrame(parent, fg_color="transparent")
        attr_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(attr_frame, text="🎯 Atributo:").pack(side="left", padx=5)
        field_vars['atributo_chave'] = ctk.StringVar()
        attr_combo = ctk.CTkComboBox(attr_frame, 
                                   values=["FOR", "DES"],
                                   variable=field_vars['atributo_chave'])
        attr_combo.pack(side="left", padx=5)
        
        # Tipo de Dano
        type_frame = ctk.CTkFrame(parent, fg_color="transparent")
        type_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(type_frame, text="🗡️ Tipo:").pack(side="left", padx=5)
        field_vars['tipo_dano'] = ctk.StringVar()
        type_combo = ctk.CTkComboBox(type_frame, 
                                   values=["Corte", "Perfuração", "Impacto", "Corte/Perf."],
                                   variable=field_vars['tipo_dano'])
        type_combo.pack(side="left", padx=5)
        
        # Empunhadura
        grip_frame = ctk.CTkFrame(parent, fg_color="transparent")
        grip_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(grip_frame, text="✋ Empunhadura:").pack(side="left", padx=5)
        field_vars['empunhadura'] = ctk.StringVar()
        grip_combo = ctk.CTkComboBox(grip_frame, 
                                   values=["1 Mão", "2 Mãos", "Versátil"],
                                   variable=field_vars['empunhadura'])
        grip_combo.pack(side="left", padx=5)
        
        # Alcance
        range_frame = ctk.CTkFrame(parent, fg_color="transparent")
        range_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(range_frame, text="📏 Alcance:").pack(side="left", padx=5)
        field_vars['alcance'] = ctk.StringVar()
        range_combo = ctk.CTkComboBox(range_frame,
                                    values=["Corpo a Corpo", "Distância (24/96m)", "Distância (45/180m)"],
                                    variable=field_vars['alcance'])
        range_combo.pack(side="left", padx=5)
        
        # Categoria
        category_frame = ctk.CTkFrame(parent, fg_color="transparent")
        category_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(category_frame, text="📋 Categoria:").pack(side="left", padx=5)
        field_vars['categoria'] = ctk.StringVar()
        category_combo = ctk.CTkComboBox(category_frame,
                                       values=["Arma Simples", "Arma Marcial"],
                                       variable=field_vars['categoria'])
        category_combo.pack(side="left", padx=5)
        
        # Perícia de Ataque
        skill_frame = ctk.CTkFrame(parent, fg_color="transparent")
        skill_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(skill_frame, text="🎲 Perícia:").pack(side="left", padx=5)
        field_vars['pericia_ataque'] = ctk.StringVar()
        skill_combo = ctk.CTkComboBox(skill_frame,
                                    values=["Corpo-a-Corpo", "Pontaria"],
                                    variable=field_vars['pericia_ataque'])
        skill_combo.pack(side="left", padx=5)
        
        # Observações
        notes_frame = ctk.CTkFrame(parent, fg_color="transparent")
        notes_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(notes_frame, text="📝 Observações:").pack(side="left", padx=5)
        field_vars['observacoes'] = ctk.StringVar()
        ctk.CTkEntry(notes_frame, textvariable=field_vars['observacoes']).pack(side="left", fill="x", expand=True, padx=5)

    def _setup_armor_dialog(self, parent: ctk.CTkFrame, field_vars: Dict[str, ctk.StringVar]) -> None:
        """Configura os campos do diálogo para adicionar armadura."""
        # Nome
        name_frame = ctk.CTkFrame(parent, fg_color="transparent")
        name_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(name_frame, text="🛡️ Nome:").pack(side="left", padx=5)
        field_vars['name'] = ctk.StringVar()
        ctk.CTkEntry(name_frame, textvariable=field_vars['name']).pack(side="left", fill="x", expand=True, padx=5)
        
        # Custo
        cost_frame = ctk.CTkFrame(parent, fg_color="transparent")
        cost_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(cost_frame, text="💰 Custo:").pack(side="left", padx=5)
        
        cost_ef_frame = ctk.CTkFrame(cost_frame, fg_color="transparent")
        cost_ef_frame.pack(side="left", padx=5)
        field_vars['custo_ef'] = ctk.StringVar(value="0")
        ctk.CTkEntry(cost_ef_frame, textvariable=field_vars['custo_ef'], width=60, justify="right").pack(side="left")
        ctk.CTkLabel(cost_ef_frame, text="Ef").pack(side="left", padx=2)
        
        cost_efp_frame = ctk.CTkFrame(cost_frame, fg_color="transparent")
        cost_efp_frame.pack(side="left", padx=5)
        field_vars['custo_efp'] = ctk.StringVar(value="0")
        ctk.CTkEntry(cost_efp_frame, textvariable=field_vars['custo_efp'], width=60, justify="right").pack(side="left")
        ctk.CTkLabel(cost_efp_frame, text="EfP").pack(side="left", padx=2)
        
        # RD (Redução de Dano)
        rd_frame = ctk.CTkFrame(parent, fg_color="transparent")
        rd_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(rd_frame, text="💪 RD:").pack(side="left", padx=5)
        field_vars['rd'] = ctk.StringVar()
        rd_combo = ctk.CTkComboBox(rd_frame,
                                 values=["1", "2", "3", "4"],
                                 variable=field_vars['rd'])
        rd_combo.pack(side="left", padx=5)
        
        # Tipo
        type_frame = ctk.CTkFrame(parent, fg_color="transparent")
        type_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(type_frame, text="👕 Tipo:").pack(side="left", padx=5)
        field_vars['tipo_armadura'] = ctk.StringVar()
        type_combo = ctk.CTkComboBox(type_frame, 
                                   values=["Leve", "Média", "Pesada"],
                                   variable=field_vars['tipo_armadura'])
        type_combo.pack(side="left", padx=5)
        
        # Penalidade de Atributo
        penalty_frame = ctk.CTkFrame(parent, fg_color="transparent")
        penalty_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(penalty_frame, text="⚠️ Penalidade:").pack(side="left", padx=5)
        field_vars['penalidade_atributo'] = ctk.StringVar()
        penalty_combo = ctk.CTkComboBox(penalty_frame,
                                      values=["0", "-1 DES (Esquiva Max +2)", "-1 DES (Esquiva Max +0)"],
                                      variable=field_vars['penalidade_atributo'])
        penalty_combo.pack(side="left", padx=5)
        
        # Observações
        notes_frame = ctk.CTkFrame(parent, fg_color="transparent")
        notes_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(notes_frame, text="📝 Observações:").pack(side="left", padx=5)
        field_vars['observacoes'] = ctk.StringVar()
        ctk.CTkEntry(notes_frame, textvariable=field_vars['observacoes']).pack(side="left", fill="x", expand=True, padx=5)

    def _setup_misc_dialog(self, parent: ctk.CTkFrame, field_vars: Dict[str, ctk.StringVar]) -> None:
        """Configura os campos do diálogo para adicionar item diverso."""
        # Nome
        name_frame = ctk.CTkFrame(parent, fg_color="transparent")
        name_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(name_frame, text="📦 Nome:").pack(side="left", padx=5)
        field_vars['name'] = ctk.StringVar()
        ctk.CTkEntry(name_frame, textvariable=field_vars['name']).pack(side="left", fill="x", expand=True, padx=5)
        
        # Custo
        cost_frame = ctk.CTkFrame(parent, fg_color="transparent")
        cost_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(cost_frame, text="💰 Custo:").pack(side="left", padx=5)
        
        cost_ef_frame = ctk.CTkFrame(cost_frame, fg_color="transparent")
        cost_ef_frame.pack(side="left", padx=5)
        field_vars['custo_ef'] = ctk.StringVar(value="0")
        ctk.CTkEntry(cost_ef_frame, textvariable=field_vars['custo_ef'], width=60, justify="right").pack(side="left")
        ctk.CTkLabel(cost_ef_frame, text="Ef").pack(side="left", padx=2)
        
        cost_efp_frame = ctk.CTkFrame(cost_frame, fg_color="transparent")
        cost_efp_frame.pack(side="left", padx=5)
        field_vars['custo_efp'] = ctk.StringVar(value="0")
        ctk.CTkEntry(cost_efp_frame, textvariable=field_vars['custo_efp'], width=60, justify="right").pack(side="left")
        ctk.CTkLabel(cost_efp_frame, text="EfP").pack(side="left", padx=2)
        
        # Quantidade
        qty_frame = ctk.CTkFrame(parent, fg_color="transparent")
        qty_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(qty_frame, text="# Quantidade:").pack(side="left", padx=5)
        field_vars['quantity'] = ctk.StringVar(value="1")
        ctk.CTkEntry(qty_frame, textvariable=field_vars['quantity']).pack(side="left", padx=5)
        
        # Peso Estimado
        weight_frame = ctk.CTkFrame(parent, fg_color="transparent")
        weight_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(weight_frame, text="⚖️ Peso:").pack(side="left", padx=5)
        field_vars['peso_estimado'] = ctk.StringVar()
        weight_combo = ctk.CTkComboBox(weight_frame,
                                     values=["Mínimo", "Leve", "Médio", "Pesado"],
                                     variable=field_vars['peso_estimado'])
        weight_combo.pack(side="left", padx=5)
        
        # Categoria da Loja
        category_frame = ctk.CTkFrame(parent, fg_color="transparent")
        category_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(category_frame, text="🏪 Categoria:").pack(side="left", padx=5)
        field_vars['categoria_loja'] = ctk.StringVar()
        category_combo = ctk.CTkComboBox(category_frame,
                                       values=["Equipamentos", "Livro/Documento"],
                                       variable=field_vars['categoria_loja'])
        category_combo.pack(side="left", padx=5)
        
        # Descrição
        desc_frame = ctk.CTkFrame(parent, fg_color="transparent")
        desc_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(desc_frame, text="📝 Descrição:").pack(side="left", padx=5)
        field_vars['description'] = ctk.StringVar()
        ctk.CTkEntry(desc_frame, textvariable=field_vars['description']).pack(side="left", fill="x", expand=True, padx=5)

    def _add_item_from_dialog(self, item_type: str, field_vars: Dict[str, ctk.StringVar], dialog: ctk.CTkToplevel) -> None:
        """Adiciona o item baseado no tipo e nos valores dos campos do diálogo."""
        # Coleta os valores dos campos
        values = {k: v.get().strip() for k, v in field_vars.items()}
        
        # Verifica se o nome está preenchido
        if not values.get('name'):
            return  # Não adiciona item sem nome
        
        # Cria o item baseado no tipo e adiciona ao personagem
        if item_type == "weapon":
            if not hasattr(self.personagem, 'armas'):
                self.personagem.armas = []
            self.personagem.armas.append(values)
            self._add_weapon_to_list(values)
        
        elif item_type == "armor":
            if not hasattr(self.personagem, 'armaduras'):
                self.personagem.armaduras = []
            self.personagem.armaduras.append(values)
            self._add_armor_to_list(values)
        
        else:  # misc
            if not hasattr(self.personagem, 'itens_diversos'):
                self.personagem.itens_diversos = []
            self.personagem.itens_diversos.append(values)
            self._add_misc_to_list(values)
        
        dialog.destroy()

    def _add_weapon_to_list(self, values: Dict[str, str]) -> None:
        """Adiciona uma nova arma à lista de armas."""
        frame = ctk.CTkFrame(self.weapons_scroll, fg_color="#2B2B2B")
        frame.pack(fill="x", pady=(0,2))
        
        # Adiciona os campos na ordem dos cabeçalhos
        ctk.CTkLabel(frame, text=values.get('name', '')).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(frame, text=values.get('atributo_chave', '')).grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkLabel(frame, text=values.get('dano', '')).grid(row=0, column=2, padx=5, pady=5)
        ctk.CTkLabel(frame, text=values.get('pericia_ataque', '')).grid(row=0, column=3, padx=5, pady=5)
        ctk.CTkLabel(frame, text=values.get('empunhadura', '')).grid(row=0, column=4, padx=5, pady=5)
        ctk.CTkLabel(frame, text=values.get('alcance', '')).grid(row=0, column=5, padx=5, pady=5)
        
        # Informações adicionais em tooltip
        info_text = f"Tipo: {values.get('tipo_dano', '')}\n"
        info_text += f"Categoria: {values.get('categoria', '')}\n"
        info_text += f"Custo: {values.get('custo_ef', '0')} Ef, {values.get('custo_efp', '0')} EfP\n"
        if values.get('observacoes'):
            info_text += f"Obs: {values.get('observacoes')}"
        
        info_label = ctk.CTkLabel(frame, text="ℹ️", cursor="hand2")
        info_label.grid(row=0, column=6, padx=5, pady=5)
        
        # Botão remover
        remove_btn = ctk.CTkButton(frame, text="❌", width=30, height=30,
                                 fg_color="transparent", hover_color="#1a1a1a",
                                 command=lambda: self._remove_weapon(frame, values))
        remove_btn.grid(row=0, column=7, padx=5, pady=5)

    def _add_armor_to_list(self, values: Dict[str, str]) -> None:
        """Adiciona uma nova armadura à lista de armaduras."""
        frame = ctk.CTkFrame(self.armor_scroll, fg_color="#2B2B2B")
        frame.pack(fill="x", pady=(0,2))
        
        # Adiciona os campos na ordem dos cabeçalhos
        ctk.CTkLabel(frame, text=values.get('name', '')).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(frame, text=values.get('rd', '')).grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkLabel(frame, text=values.get('tipo_armadura', '')).grid(row=0, column=2, padx=5, pady=5)
        
        # Informações adicionais em tooltip
        info_text = f"Penalidade: {values.get('penalidade_atributo', '0')}\n"
        info_text += f"Custo: {values.get('custo_ef', '0')} Ef, {values.get('custo_efp', '0')} EfP\n"
        if values.get('observacoes'):
            info_text += f"Obs: {values.get('observacoes')}"
        
        info_label = ctk.CTkLabel(frame, text="ℹ️", cursor="hand2")
        info_label.grid(row=0, column=3, padx=5, pady=5)
        
        # Botão remover
        remove_btn = ctk.CTkButton(frame, text="❌", width=30, height=30,
                                 fg_color="transparent", hover_color="#1a1a1a",
                                 command=lambda: self._remove_armor(frame, values))
        remove_btn.grid(row=0, column=4, padx=5, pady=5)

    def _add_misc_to_list(self, values: Dict[str, str]) -> None:
        """Adiciona um novo item diverso à lista de itens."""
        frame = ctk.CTkFrame(self.misc_scroll, fg_color="#2B2B2B")
        frame.pack(fill="x", pady=(0,2))
        
        # Adiciona os campos na ordem dos cabeçalhos
        ctk.CTkLabel(frame, text=values.get('name', '')).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(frame, text=values.get('quantity', '1')).grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkLabel(frame, text=values.get('peso_estimado', '')).grid(row=0, column=2, padx=5, pady=5)
        
        # Informações adicionais em tooltip
        info_text = f"Categoria: {values.get('categoria_loja', '')}\n"
        info_text += f"Custo: {values.get('custo_ef', '0')} Ef, {values.get('custo_efp', '0')} EfP\n"
        if values.get('description'):
            info_text += f"Desc: {values.get('description')}"
        
        info_label = ctk.CTkLabel(frame, text="ℹ️", cursor="hand2")
        info_label.grid(row=0, column=3, padx=5, pady=5)
        
        # Botão remover
        remove_btn = ctk.CTkButton(frame, text="❌", width=30, height=30,
                                 fg_color="transparent", hover_color="#1a1a1a",
                                 command=lambda: self._remove_misc(frame, values))
        remove_btn.grid(row=0, column=4, padx=5, pady=5)

    def _remove_weapon(self, frame: ctk.CTkFrame, weapon_data: Dict[str, str]) -> None:
        """Remove uma arma da UI e do personagem."""
        frame.destroy()
        if hasattr(self.personagem, 'armas') and weapon_data in self.personagem.armas:
            self.personagem.armas.remove(weapon_data)

    def _remove_armor(self, frame: ctk.CTkFrame, armor_data: Dict[str, str]) -> None:
        """Remove uma armadura da UI e do personagem."""
        frame.destroy()
        if hasattr(self.personagem, 'armaduras') and armor_data in self.personagem.armaduras:
            self.personagem.armaduras.remove(armor_data)

    def _remove_misc(self, frame: ctk.CTkFrame, misc_data: Dict[str, str]) -> None:
        """Remove um item diverso da UI e do personagem."""
        frame.destroy()
        if hasattr(self.personagem, 'itens_diversos') and misc_data in self.personagem.itens_diversos:
            self.personagem.itens_diversos.remove(misc_data)