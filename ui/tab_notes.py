import customtkinter as ctk
import tkinter as tk
from typing import Optional, Any, Dict, List
import json
from datetime import datetime

# Cores e Estilos
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

# Categorias predefinidas de notas
NOTE_CATEGORIES = [
    "NPCs",
    "Lugares",
    "Missões",
    "Itens",
    "Segredos",
    "Geral"
]

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
        
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(
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

class NotesTab:
    """
    Gerencia a aba de Anotações na interface do usuário.
    Permite ao usuário organizar e formatar notas em diferentes categorias.
    """
    def __init__(self, tab_widget: ctk.CTkFrame, personagem_atual: Any):
        self.tab_widget = tab_widget
        self.personagem = personagem_atual
        self.current_category = "Geral"
        self.notes_data = {}  # Dicionário para armazenar notas por categoria
        self._save_timer = None  # Timer para auto-save
        self._last_saved_text = ""  # Último texto salvo
        
        # Frame principal com grid layout
        self.main_frame = ctk.CTkFrame(self.tab_widget, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Configuração do grid
        self.main_frame.grid_columnconfigure(0, weight=1)  # Coluna principal
        self.main_frame.grid_columnconfigure(1, weight=3)  # Coluna do editor
        
        # Frame da barra lateral (categorias e pesquisa)
        self.setup_sidebar()
        
        # Frame do editor principal
        self.setup_editor()
        
        # Frame de status
        self.setup_status_bar()
        
        # Carrega as notas do personagem
        self.load_data_from_personagem()

    def setup_sidebar(self):
        """Configura a barra lateral com categorias e pesquisa."""
        sidebar = ctk.CTkFrame(self.main_frame, fg_color=COLORS["surface"])
        sidebar.grid(row=0, column=0, padx=(0,10), pady=(0,10), sticky="nsew")
        
        # Frame de pesquisa
        search_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        search_frame.pack(fill="x", padx=10, pady=10)
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Buscar nas notas...",
            height=35
        )
        self.search_entry.pack(fill="x", padx=5)
        self.search_entry.bind("<KeyRelease>", self.search_notes)
        ToolTip(self.search_entry, "Pesquise em todas as suas notas")
        
        # Lista de categorias
        categories_label = ctk.CTkLabel(
            sidebar,
            text="Categorias",
            font=("Helvetica", 14, "bold"),
            text_color=COLORS["text"]
        )
        categories_label.pack(pady=(10,5), padx=10, anchor="w")
        
        for category in NOTE_CATEGORIES:
            btn = ctk.CTkButton(
                sidebar,
                text=category,
                height=35,
                anchor="w",
                fg_color="transparent",
                text_color=COLORS["text"],
                hover_color=COLORS["primary"],
                command=lambda c=category: self.change_category(c)
            )
            btn.pack(fill="x", padx=5, pady=2)
            ToolTip(btn, f"Notas sobre {category}")

    def setup_editor(self):
        """Configura o editor principal de notas."""
        editor_frame = ctk.CTkFrame(self.main_frame, fg_color=COLORS["surface"])
        editor_frame.grid(row=0, column=1, sticky="nsew")
        
        # Barra de ferramentas
        toolbar = ctk.CTkFrame(editor_frame, fg_color="transparent")
        toolbar.pack(fill="x", padx=10, pady=5)
        
        # Botões de formatação
        bold_btn = ctk.CTkButton(
            toolbar,
            text="B",
            width=35,
            height=35,
            font=("Helvetica", 12, "bold"),
            command=lambda: self.format_text("bold")
        )
        bold_btn.pack(side="left", padx=2)
        ToolTip(bold_btn, "Negrito (Ctrl+B)")
        
        italic_btn = ctk.CTkButton(
            toolbar,
            text="I",
            width=35,
            height=35,
            font=("Helvetica", 12, "italic"),
            command=lambda: self.format_text("italic")
        )
        italic_btn.pack(side="left", padx=2)
        ToolTip(italic_btn, "Itálico (Ctrl+I)")
        
        # Campo de tags
        self.tags_entry = ctk.CTkEntry(
            toolbar,
            placeholder_text="Tags (separadas por vírgula)",
            height=35,
            width=200
        )
        self.tags_entry.pack(side="left", padx=10)
        ToolTip(self.tags_entry, "Adicione tags para organizar suas notas")
        
        # Editor principal
        self.notes_text = ctk.CTkTextbox(
            editor_frame,
            wrap="word",
            font=("Helvetica", 12),
            height=400
        )
        self.notes_text.pack(fill="both", expand=True, padx=10, pady=5)
        self.notes_text.bind("<KeyRelease>", self.auto_save)
        
        # Atalhos de teclado
        self.notes_text.bind("<Control-b>", lambda e: self.format_text("bold"))
        self.notes_text.bind("<Control-i>", lambda e: self.format_text("italic"))

    def setup_status_bar(self):
        """Configura a barra de status."""
        self.status_frame = ctk.CTkFrame(self.main_frame, height=30, fg_color=COLORS["surface"])
        self.status_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(5,0))
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="",
            text_color=COLORS["text_secondary"]
        )
        self.status_label.pack(side="left", padx=10)
        
        self.last_saved_label = ctk.CTkLabel(
            self.status_frame,
            text="",
            text_color=COLORS["text_secondary"]
        )
        self.last_saved_label.pack(side="right", padx=10)

    def change_category(self, category: str):
        """Muda a categoria atual e carrega as notas correspondentes."""
        self.save_current_notes()  # Salva as notas atuais antes de mudar
        self.current_category = category
        
        # Carrega as notas da nova categoria
        self.notes_text.delete("1.0", "end")
        if category in self.notes_data:
            self.notes_text.insert("1.0", self.notes_data[category]["text"])
            self.tags_entry.delete(0, "end")
            self.tags_entry.insert(0, ", ".join(self.notes_data[category].get("tags", [])))
        
        self.status_label.configure(text=f"Categoria atual: {category}")

    def format_text(self, style: str):
        """Aplica formatação ao texto selecionado."""
        try:
            selection = self.notes_text.selection_get()
            start = self.notes_text.index("sel.first")
            end = self.notes_text.index("sel.last")
            
            if style == "bold":
                formatted = f"**{selection}**"
            elif style == "italic":
                formatted = f"*{selection}*"
            
            self.notes_text.delete(start, end)
            self.notes_text.insert(start, formatted)
        except:
            pass  # Nenhuma seleção

    def search_notes(self, event=None):
        """Pesquisa nas notas de todas as categorias."""
        search_term = self.search_entry.get().lower()
        if not search_term:
            return
        
        results = []
        for category, data in self.notes_data.items():
            if search_term in data["text"].lower():
                results.append(f"Em {category}:\n{data['text'][:200]}...")
        
        if results:
            self.notes_text.delete("1.0", "end")
            self.notes_text.insert("1.0", "\n\n".join(results))
            self.status_label.configure(text=f"Resultados da busca para: {search_term}")
        else:
            self.status_label.configure(text="Nenhum resultado encontrado")

    def auto_save(self, event=None):
        """Salva automaticamente as notas após alterações."""
        current_text = self.notes_text.get("1.0", "end-1c")
        
        # Se o texto não mudou, não salva
        if current_text == self._last_saved_text:
            return
            
        # Cancela timer anterior se existir
        if self._save_timer:
            self.tab_widget.after_cancel(self._save_timer)
        
        # Agenda novo salvamento
        self._save_timer = self.tab_widget.after(1000, self._perform_save)
        
    def _perform_save(self):
        """Executa o salvamento efetivo das notas."""
        self._save_timer = None
        current_text = self.notes_text.get("1.0", "end-1c")
        self._last_saved_text = current_text
        
        self.save_current_notes()
        now = datetime.now().strftime("%H:%M:%S")
        self.last_saved_label.configure(text=f"Último salvamento: {now}")

    def save_current_notes(self):
        """Salva as notas da categoria atual."""
        current_text = self.notes_text.get("1.0", "end-1c")
        current_tags = [tag.strip() for tag in self.tags_entry.get().split(",") if tag.strip()]
        
        self.notes_data[self.current_category] = {
            "text": current_text,
            "tags": current_tags,
            "last_modified": datetime.now().isoformat()
        }
        
        # Atualiza o objeto personagem
        if hasattr(self.personagem, 'notas'):
            self.personagem.notas = json.dumps(self.notes_data)

    def load_data_from_personagem(self):
        """Carrega as notas do objeto Personagem."""
        if hasattr(self.personagem, 'notas') and self.personagem.notas:
            try:
                self.notes_data = json.loads(self.personagem.notas)
            except:
                # Se não conseguir carregar como JSON, assume que é o formato antigo
                self.notes_data = {"Geral": {"text": self.personagem.notas, "tags": []}}
        else:
            # Inicializa com notas vazias para cada categoria
            self.notes_data = {category: {"text": "", "tags": []} for category in NOTE_CATEGORIES}
        
        # Carrega a categoria inicial
        self.change_category("Geral")