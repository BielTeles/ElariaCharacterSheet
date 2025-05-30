import customtkinter as ctk
from typing import List, Dict, Any, Optional, TYPE_CHECKING
import tkinter
from collections import defaultdict

# Supondo que Personagem e dados da loja/habilidades estão acessíveis
# from core.character import Personagem # Para type hint
from data.items_data import TODOS_ITENS_LOJA

if TYPE_CHECKING: # Evita import circular em tempo de execução, mas permite type hinting
    from ui.app_ui import AppUI
    from core.character import Personagem

# Constantes de cores e temas
COLORS = {
    "primary": "#3498db",
    "secondary": "#2ecc71",
    "danger": "#e74c3c",
    "warning": "#f1c40f",
    "info": "#3498db",
    "success": "#2ecc71",
    "background": "#2c3e50",
    "surface": "#34495e",
    "text": "#ecf0f1",
    "text_secondary": "#95a5a6"
}

class ToolTip:
    """Classe para criar tooltips personalizados."""
    
    def __init__(self, widget: ctk.CTkBaseClass, text: str):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind('<Enter>', self.show_tooltip)
        self.widget.bind('<Leave>', self.hide_tooltip)
    
    def show_tooltip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        self.tooltip_window = tkinter.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        label = tkinter.Label(
            self.tooltip_window,
            text=self.text,
            justify='left',
            background="#34495e",
            foreground="#ecf0f1",
            relief='solid',
            borderwidth=1,
            font=("Helvetica", 10),
            wraplength=300
        )
        label.pack()
    
    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

class StoreTab:
    """
    Gerencia a aba da Loja de Itens, permitindo ao jogador
    comprar itens para o personagem.
    """
    personagem: 'Personagem' # Usando string para type hint para evitar import circular
    app_ui: 'AppUI'

    # --- Atributos da UI ---
    char_ef_label: ctk.CTkLabel
    char_efp_label: ctk.CTkLabel
    items_scroll_frame: ctk.CTkScrollableFrame
    category_buttons: Dict[str, ctk.CTkButton]
    search_entry: ctk.CTkEntry
    current_category: str

    def __init__(self, tab_widget: ctk.CTkFrame, personagem_atual: 'Personagem', app_ui_ref: 'AppUI'):
        self.tab_widget = tab_widget
        self.personagem = personagem_atual
        self.app_ui = app_ui_ref
        self.current_category = "Todos"
        self.category_buttons = {}

        self.main_frame = ctk.CTkFrame(self.tab_widget, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True)

        self._setup_items_store_ui()
        self.load_data_from_personagem()

    def _setup_items_store_ui(self) -> None:
        """Configura os widgets da loja de itens."""
        # --- Frame Superior com Moedas e Pesquisa ---
        top_frame = ctk.CTkFrame(self.main_frame, fg_color=COLORS["surface"], corner_radius=10)
        top_frame.pack(fill="x", padx=10, pady=5)

        # Frame para moedas com ícones
        currency_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        currency_frame.pack(side="left", padx=10, pady=5)
        
        ctk.CTkLabel(
            master=currency_frame,
            text="💰 Moedas:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text"]
        ).pack(side="left", padx=(0,5))
        
        self.char_ef_label = ctk.CTkLabel(
            master=currency_frame,
            text="0 Ef",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text"]
        )
        self.char_ef_label.pack(side="left", padx=(0,10))
        
        self.char_efp_label = ctk.CTkLabel(
            master=currency_frame,
            text="0 EfP",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text"]
        )
        self.char_efp_label.pack(side="left", padx=(0,10))

        # Frame para pesquisa
        search_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        search_frame.pack(side="right", padx=10, pady=5)
        
        self.search_entry = ctk.CTkEntry(
            master=search_frame,
            placeholder_text="🔍 Buscar item...",
            width=200,
            height=32,
            font=ctk.CTkFont(size=12)
        )
        self.search_entry.pack(side="right", padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.filter_items())

        # --- Frame para Categorias ---
        categories_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        categories_frame.pack(fill="x", padx=10, pady=5)

        # Obtém categorias únicas dos itens
        categories = ["Todos"] + sorted(list(set(item.get("categoria_loja", "") for item in TODOS_ITENS_LOJA)))
        
        for category in categories:
            btn = ctk.CTkButton(
                master=categories_frame,
                text=category,
                width=120,
                height=32,
                fg_color=COLORS["primary"] if category == "Todos" else "transparent",
                hover_color="#2980b9",
                command=lambda c=category: self.filter_by_category(c)
            )
            btn.pack(side="left", padx=5, pady=5)
            self.category_buttons[category] = btn

        # --- Frame Principal para Itens ---
        self.items_scroll_frame = ctk.CTkScrollableFrame(
            self.main_frame,
            fg_color="transparent",
            corner_radius=10
        )
        self.items_scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)

    def filter_by_category(self, category: str) -> None:
        """Filtra os itens por categoria."""
        self.current_category = category
        
        # Atualiza aparência dos botões
        for cat, btn in self.category_buttons.items():
            btn.configure(
                fg_color=COLORS["primary"] if cat == category else "transparent"
            )
        
        self.filter_items()

    def filter_items(self) -> None:
        """Filtra os itens baseado na categoria selecionada e texto de busca."""
        search_text = self.search_entry.get().lower()
        
        # Limpa itens existentes
        for widget in self.items_scroll_frame.winfo_children():
            widget.destroy()

        # Filtra itens
        filtered_items = TODOS_ITENS_LOJA
        if self.current_category != "Todos":
            filtered_items = [item for item in TODOS_ITENS_LOJA if item.get("categoria_loja") == self.current_category]
        if search_text:
            filtered_items = [item for item in filtered_items if search_text in item.get("nome", "").lower()]

        # Agrupa itens por categoria para melhor organização
        items_by_category = defaultdict(list)
        for item in filtered_items:
            items_by_category[item.get("categoria_loja", "Outros")].append(item)

        current_row = 0
        for categoria in sorted(items_by_category.keys()):
            if self.current_category == "Todos":
                # Adiciona cabeçalho da categoria
                header_frame = ctk.CTkFrame(self.items_scroll_frame, fg_color=COLORS["surface"])
                header_frame.pack(fill="x", padx=5, pady=(10,5))
                ctk.CTkLabel(
                    master=header_frame,
                    text=categoria,
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=COLORS["text"]
                ).pack(pady=5)

            # Adiciona itens da categoria
            items_frame = ctk.CTkFrame(self.items_scroll_frame, fg_color="transparent")
            items_frame.pack(fill="x", padx=5, pady=5)
            items_frame.grid_columnconfigure((0,1,2), weight=1)

            for col, item_data in enumerate(items_by_category[categoria]):
                if col % 3 == 0 and col > 0:
                    current_row += 1

                self.create_item_card(items_frame, item_data, current_row, col % 3)

    def create_item_card(self, parent: ctk.CTkFrame, item_data: Dict[str, Any], row: int, col: int) -> None:
        """Cria um card para um item."""
        card = ctk.CTkFrame(parent, fg_color=COLORS["surface"], corner_radius=10)
        card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        # Nome do item
        nome_label = ctk.CTkLabel(
            master=card,
            text=item_data.get("nome", "N/A"),
            font=ctk.CTkFont(size=12, weight="bold"),
            wraplength=150
        )
        nome_label.pack(padx=10, pady=(10,5))

        # Preço
        custo_ef = item_data.get("custo_ef", 0)
        custo_efp = item_data.get("custo_efp", 0)
        custo_str = ""
        if custo_ef > 0: custo_str += f"{custo_ef} Ef"
        if custo_efp > 0:
            if custo_str: custo_str += " + "
            custo_str += f"{custo_efp} EfP"
        if not custo_str: custo_str = "Grátis"
        
        preco_label = ctk.CTkLabel(
            master=card,
            text=custo_str,
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        )
        preco_label.pack(pady=5)

        # Botão de compra
        buy_button = ctk.CTkButton(
            master=card,
            text="Comprar",
            width=100,
            height=32,
            command=lambda: self.buy_item(item_data.copy()),
            fg_color=COLORS["primary"],
            hover_color="#2980b9"
        )
        buy_button.pack(pady=10)

        # Adiciona tooltip com descrição do item
        tooltip_text = f"{item_data.get('nome')}\n\nPreço: {custo_str}"
        if "observacoes" in item_data:
            tooltip_text += f"\n\nDescrição: {item_data['observacoes']}"
        ToolTip(card, tooltip_text)

    def update_character_currency_display(self) -> None:
        """Atualiza a exibição das moedas do personagem na aba da loja."""
        if hasattr(self, 'personagem') and self.personagem:
            self.char_ef_label.configure(text=f"{self.personagem.moedas_ef} Ef")
            self.char_efp_label.configure(text=f"{self.personagem.moedas_efp} EfP")

    def load_data_from_personagem(self) -> None:
        """Chamado para carregar/recarregar opções da loja."""
        self.personagem = self.app_ui.personagem_atual # Garante que está usando a instância mais recente
        self.update_character_currency_display()
        self.filter_items()

    def buy_item(self, item_data_compra: Dict[str, Any]) -> None:
        """Processa a compra de um item da loja."""
        custo_ef_item = item_data_compra.get("custo_ef", 0)
        custo_efp_item = item_data_compra.get("custo_efp", 0)
        
        # Conversão de custo para EfP (1 Ef = 10 EfP)
        custo_total_em_efp_item = (custo_ef_item * 10) + custo_efp_item
        saldo_total_em_efp_personagem = (self.personagem.moedas_ef * 10) + self.personagem.moedas_efp

        if saldo_total_em_efp_personagem >= custo_total_em_efp_item:
            saldo_restante_efp = saldo_total_em_efp_personagem - custo_total_em_efp_item
            self.personagem.moedas_ef = saldo_restante_efp // 10
            self.personagem.moedas_efp = saldo_restante_efp % 10

            # Adiciona item ao inventário do personagem
            tipo_inv = item_data_compra.get("tipo_inventario", "item_geral")

            if tipo_inv == "arma":
                item_data_compra["origem"] = "loja"
                self.personagem.armas_inventario.append(item_data_compra)
            elif tipo_inv == "armadura":
                self.personagem.itens_gerais.append({
                    "nome": item_data_compra.get("nome"), 
                    "quantity": 1, 
                    "weight": "", 
                    "description": f"Tipo: {item_data_compra.get('tipo_armadura')}, RD: {item_data_compra.get('rd')}"
                })
            elif tipo_inv == "escudo":
                self.personagem.itens_gerais.append({
                    "nome": item_data_compra.get("nome"), 
                    "quantity": 1, 
                    "weight": "", 
                    "description": item_data_compra.get("observacoes","")
                })
            else: # item_geral
                found_item_in_inventory = None
                for inv_item in self.personagem.itens_gerais:
                    if inv_item.get("nome") == item_data_compra.get("nome"):
                        found_item_in_inventory = inv_item
                        break
                if found_item_in_inventory:
                    try:
                        found_item_in_inventory["quantity"] = int(found_item_in_inventory.get("quantity", 0)) + 1
                    except ValueError:
                        found_item_in_inventory["quantity"] = 1 
                else:
                    self.personagem.itens_gerais.append({
                        "nome": item_data_compra.get("nome"), 
                        "quantity": 1, 
                        "weight": item_data_compra.get("peso_estimado",""), 
                        "description": item_data_compra.get("observacoes", "")
                    })

            self.app_ui.show_feedback_message(f"'{item_data_compra.get('nome')}' comprado!", "success", 2000)
            self.update_character_currency_display()
            # Notifica outras abas para recarregar dados
            self.app_ui.inventory_tab.load_data_from_personagem()
            self.app_ui.combat_tab.load_data_from_personagem()
        else:
            self.app_ui.show_feedback_message("Moedas insuficientes!", "error", 2000)