import customtkinter as ctk
import tkinter
from tkinter import filedialog, messagebox, TclError # Adicionado messagebox para feedback de erro potencial
import json
from typing import Dict, Any, List, Optional, Callable, Tuple
from core.character import Personagem, CLASSE_EVOCADOR, CLASSE_TITA, CLASSE_SENTINELA, CLASSE_ELO
from core.character import Personagem
from ui.tab_attributes_skills import AttributesSkillsTab
from ui.tab_combat import CombatTab
from ui.tab_magic import MagicTab
from ui.tab_inventory import InventoryTab
from ui.tab_notes import NotesTab # Importado para consistência
from ui.tab_dice_roller_generic import DiceRollerGenericTab
from ui.tab_store_abilities import StoreAbilitiesTab
from ui.themes import ThemeManager

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

# Configurações de animação
ANIMATION_SPEED = 300  # milissegundos
HOVER_ANIMATION_SPEED = 150  # milissegundos

# Definindo SUBCLASS_OPTIONS fora da classe se for usado apenas para inicialização
# ou se for uma constante global para a UI.
SUBCLASS_OPTIONS: Dict[str, List[str]] = {
    "Evocador": ["", "Caminho da Terra", "Caminho da Água", "Caminho do Ar", "Caminho do Fogo", "Caminho da Luz", "Caminho da Sombra"],
    "Titã": ["", "Arquétipo do Baluarte", "Arquétipo da Fúria Primal", "Arquétipo do Quebra-Montanhas"],
    "Sentinela": ["", "Arquétipo do Rastreador dos Ermos", "Arquétipo da Lâmina do Crepúsculo", "Arquétipo do Olho Vigilante"],
    "Elo": ["", "Arquétipo da Voz da Harmonia", "Arquétipo do Porta-Voz da Chama", "Arquétipo do Guardião do Coração"],
    "": [""]  # Opção para quando nenhuma classe principal está selecionada
}
# Garantir que a opção vazia (placeholder) seja a primeira, se não estiver presente.
for class_name_key in SUBCLASS_OPTIONS:
    if SUBCLASS_OPTIONS[class_name_key] and SUBCLASS_OPTIONS[class_name_key][0] != "":
        SUBCLASS_OPTIONS[class_name_key].insert(0, "")


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
            font=("Helvetica", 10)
        )
        label.pack()
    
    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


class AppUI:
    """
    Classe principal da Interface do Usuário (UI) para a Ficha de Personagem Elaria RPG.
    Gerencia a janela principal, abas, carregamento/salvamento de dados e
    interações com o objeto Personagem.
    """
    root: ctk.CTk
    personagem_atual: Personagem
    main_frame: ctk.CTkFrame
    file_ops_frame: ctk.CTkFrame
    save_button: ctk.CTkButton
    load_button: ctk.CTkButton
    new_char_button: ctk.CTkButton
    feedback_label: ctk.CTkLabel
    tab_view: ctk.CTkTabview
    theme_manager: ThemeManager

    # Widgets das abas
    tab_principal_widget: ctk.CTkFrame # O tipo real é CTkFrame retornado por tab_view.add()
    tab_attrs_skills_widget: ctk.CTkFrame
    tab_combat_widget: ctk.CTkFrame
    tab_magia_widget: ctk.CTkFrame
    tab_inventario_widget: ctk.CTkFrame
    tab_loja_habilidades_widget: ctk.CTkFrame
    tab_rolador_widget: ctk.CTkFrame
    tab_notas_widget: ctk.CTkFrame

    # StringVars e widgets da aba Principal
    principal_stringvars: Dict[str, ctk.StringVar]
    principal_widgets: Dict[str, Any] # Pode ser CTkEntry, CTkOptionMenu, etc.
    _principal_var_traces_tcl_names: Dict[str, str] # Para gerenciar os nomes dos callbacks Tcl

    # Referências às classes das abas
    attributes_skills_tab: AttributesSkillsTab
    combat_tab: CombatTab
    magic_tab: MagicTab
    inventory_tab: InventoryTab
    store_abilities_tab: StoreAbilitiesTab
    dice_roller_generic_tab: DiceRollerGenericTab
    notes_tab: NotesTab

    def __init__(self, root: ctk.CTk):
        self.root = root
        self.root.title("Ficha de Personagem Elaria RPG")
        
        # Inicializa o gerenciador de temas
        self.theme_manager = ThemeManager()
        
        # Configurações de tema e aparência
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        # Configurar tamanho e posição da janela
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_width = 1280
        window_height = 720
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(1280, 720)
        
        # Configurar ícone da janela
        try:
            self.root.iconbitmap("assets/icon.ico")
        except:
            pass
            
        self.personagem_atual = Personagem()

        # Criar menu de temas
        self._create_theme_menu()

        # Frame principal com animação de fade in
        self.main_frame = ctk.CTkFrame(self.root, fg_color=self.theme_manager.get_theme()["colors"]["background"])
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.main_frame.pack_propagate(False)  # Previne redimensionamento automático
        
        # Animação de fade in
        self.main_frame.configure(fg_color="transparent")
        def fade_in():
            self.main_frame.configure(fg_color=self.theme_manager.get_theme()["colors"]["background"])
        self.root.after(100, fade_in)

        # Frame para operações de arquivo com animação
        self.file_ops_frame = ctk.CTkFrame(self.main_frame, fg_color=self.theme_manager.get_theme()["colors"]["surface"])
        self.file_ops_frame.pack(fill="x", pady=(0, 10))

        # Frame para botões com efeito de elevação
        buttons_frame = ctk.CTkFrame(self.file_ops_frame, fg_color="transparent")
        buttons_frame.pack(side="left", padx=10, pady=5)

        # Botões com ícones, cores e tooltips
        self.new_char_button = ctk.CTkButton(
            buttons_frame,
            text="Nova Ficha",
            command=self.nova_ficha,
            fg_color=self.theme_manager.get_theme()["colors"]["secondary"],
            hover_color="#27ae60",
            width=120,
            height=32,
            corner_radius=8
        )
        self.new_char_button.pack(side="left", padx=(0, 5))
        ToolTip(self.new_char_button, "Criar uma nova ficha de personagem em branco")

        self.load_button = ctk.CTkButton(
            buttons_frame,
            text="Carregar Ficha",
            command=self.carregar_ficha,
            fg_color=self.theme_manager.get_theme()["colors"]["primary"],
            hover_color="#2980b9",
            width=120,
            height=32,
            corner_radius=8
        )
        self.load_button.pack(side="left", padx=5)
        ToolTip(self.load_button, "Carregar uma ficha de personagem existente")

        self.save_button = ctk.CTkButton(
            buttons_frame,
            text="Salvar Ficha",
            command=self.salvar_ficha,
            fg_color=self.theme_manager.get_theme()["colors"]["danger"],
            hover_color="#c0392b",
            width=120,
            height=32,
            corner_radius=8
        )
        self.save_button.pack(side="left", padx=5)
        ToolTip(self.save_button, "Salvar a ficha atual em um arquivo")

        # Frame para feedback com animação
        feedback_frame = ctk.CTkFrame(self.file_ops_frame, fg_color="transparent")
        feedback_frame.pack(side="left", fill="x", expand=True, padx=10, pady=5)

        self.feedback_label = ctk.CTkLabel(
            feedback_frame,
            text="",
            font=("Helvetica", 12),
            text_color=self.theme_manager.get_theme()["colors"]["text_secondary"]
        )
        self.feedback_label.pack(side="left", padx=10)

        # Configuração das Abas com novo visual
        self.tab_view = ctk.CTkTabview(
            self.main_frame,
            anchor="nw",
            segmented_button_fg_color=self.theme_manager.get_theme()["colors"]["surface"],
            segmented_button_selected_color=self.theme_manager.get_theme()["colors"]["primary"],
            segmented_button_selected_hover_color="#2980b9",
            segmented_button_unselected_color=self.theme_manager.get_theme()["colors"]["surface"],
            segmented_button_unselected_hover_color="#34495e"
        )
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=5)

        # Criação das abas com ícones e tooltips
        tabs_info = {
            "Principal": "Informações básicas do personagem",
            "Atributos & Perícias": "Gerenciar atributos e perícias do personagem",
            "Combate": "Configurações e estatísticas de combate",
            "Magia": "Magias e habilidades mágicas",
            "Inventário": "Gerenciar itens e equipamentos",
            "Loja & Habilidades": "Comprar itens e habilidades",
            "Rolador de Dados": "Realizar rolagens de dados",
            "Notas": "Anotações sobre o personagem"
        }

        # Criar as abas e armazenar referências
        self.tab_widgets = {}
        for tab_name in tabs_info.keys():
            tab_widget = self.tab_view.add(tab_name)
            self.tab_widgets[tab_name] = tab_widget
            
            # Adicionar tooltip ao botão da aba usando o widget pai
            tab_button = self.tab_view._segmented_button.winfo_children()[len(self.tab_widgets) - 1]
            if isinstance(tab_button, (ctk.CTkButton, tkinter.Button)):
                ToolTip(tab_button, tabs_info[tab_name])

        # Atribuir as referências das abas aos atributos da classe
        self.tab_principal_widget = self.tab_widgets["Principal"]
        self.tab_attrs_skills_widget = self.tab_widgets["Atributos & Perícias"]
        self.tab_combat_widget = self.tab_widgets["Combate"]
        self.tab_magia_widget = self.tab_widgets["Magia"]
        self.tab_inventario_widget = self.tab_widgets["Inventário"]
        self.tab_loja_habilidades_widget = self.tab_widgets["Loja & Habilidades"]
        self.tab_rolador_widget = self.tab_widgets["Rolador de Dados"]
        self.tab_notas_widget = self.tab_widgets["Notas"]

        # Configurar cores de fundo para cada aba
        for tab in self.tab_widgets.values():
            tab.configure(fg_color=self.theme_manager.get_theme()["colors"]["background"])

        self.tab_view.set("Principal")

        self.principal_stringvars = {}
        self.principal_widgets = {}
        self._principal_var_traces_tcl_names = {}

        # Configurar widgets da aba principal com animação de fade in
        def setup_principal_delayed():
            self.setup_principal_tab_widgets(self.tab_principal_widget)
            self.atualizar_ui_completa(primeira_carga=True)
        
        self.root.after(ANIMATION_SPEED, setup_principal_delayed)
        
        # Instanciação das classes das abas
        self.attributes_skills_tab = AttributesSkillsTab(self.tab_attrs_skills_widget, self.personagem_atual)
        self.combat_tab = CombatTab(self.tab_combat_widget, self.attributes_skills_tab, self.personagem_atual, self) # Adicionado 'self' no final
        self.magic_tab = MagicTab(self.tab_magia_widget, self.personagem_atual)
        self.inventory_tab = InventoryTab(self.tab_inventario_widget, self.personagem_atual)
        self.store_abilities_tab = StoreAbilitiesTab(self.tab_loja_habilidades_widget, self.personagem_atual, self)
        self.dice_roller_generic_tab = DiceRollerGenericTab(self.tab_rolador_widget)
        self.notes_tab = NotesTab(self.tab_notas_widget, self.personagem_atual)

    def _create_theme_menu(self) -> None:
        """Cria o menu de temas na barra de menu."""
        menubar = tkinter.Menu(self.root)
        self.root.config(menu=menubar)
        
        theme_menu = tkinter.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Temas", menu=theme_menu)
        
        available_themes = self.theme_manager.get_available_themes()
        for theme_id, theme_name in available_themes.items():
            theme_menu.add_command(
                label=theme_name,
                command=lambda t=theme_id: self._change_theme(t)
            )

    def _change_theme(self, theme_name: str) -> None:
        """Muda o tema do aplicativo."""
        if self.theme_manager.set_theme(theme_name):
            theme = self.theme_manager.get_theme()
            colors = theme["colors"]
            
            # Atualiza cores dos frames principais
            self.main_frame.configure(fg_color=colors["background"])
            self.file_ops_frame.configure(fg_color=colors["surface"])
            
            # Atualiza cores dos botões
            self.new_char_button.configure(
                fg_color=colors["secondary"],
                hover_color="#27ae60"
            )
            self.load_button.configure(
                fg_color=colors["primary"],
                hover_color="#2980b9"
            )
            self.save_button.configure(
                fg_color=colors["danger"],
                hover_color="#c0392b"
            )
            
            # Atualiza cores do feedback
            self.feedback_label.configure(text_color=colors["text_secondary"])
            
            # Atualiza cores das abas
            self.tab_view.configure(
                segmented_button_fg_color=colors["surface"],
                segmented_button_selected_color=colors["primary"],
                segmented_button_unselected_color=colors["surface"]
            )
            
            # Atualiza cores de fundo das abas
            for tab in self.tab_widgets.values():
                tab.configure(fg_color=colors["background"])
            
            # Mostra feedback da mudança de tema
            self.show_feedback_message(f"Tema alterado para {theme['name']}", "info", 2000)

    def show_feedback_message(self, message: str, message_type: str = "info", duration: int = 3000) -> None:
        """
        Exibe uma mensagem de feedback temporária na UI com animação e cores baseadas no tipo.
        
        Args:
            message: A mensagem a ser exibida
            message_type: O tipo de mensagem ('success', 'error', 'warning', 'info')
            duration: Duração em milissegundos para exibir a mensagem
        """
        # Definir cores baseadas no tipo de mensagem
        colors = {
            "success": COLORS["success"],
            "error": COLORS["danger"],
            "warning": COLORS["warning"],
            "info": COLORS["info"]
        }
        
        # Configurar a cor do texto baseado no tipo de mensagem
        text_color = colors.get(message_type, colors["info"])
        
        # Animação de fade in
        self.feedback_label.configure(text="")
        
        def fade_in():
            self.feedback_label.configure(
                text=message,
                text_color=text_color,
                font=("Helvetica", 12, "bold")
            )
        
        # Função para fade out
        def fade_out():
            self.feedback_label.configure(
                text_color=COLORS["text_secondary"],
                font=("Helvetica", 12)
            )
            
            def clear_message():
                self.feedback_label.configure(text="")
            
            self.root.after(HOVER_ANIMATION_SPEED, clear_message)
        
        # Agendar as animações
        self.root.after(50, fade_in)  # Pequeno delay antes do fade in
        self.root.after(duration - HOVER_ANIMATION_SPEED, fade_out)  # Inicia fade out antes do fim

    def nova_ficha(self) -> None:
        """Cria uma nova ficha de personagem em branco e atualiza a UI."""
        self.personagem_atual = Personagem()
        self.atualizar_ui_completa(primeira_carga=True) # Sinaliza que é como uma primeira carga
        self.show_feedback_message("Nova ficha limpa carregada.", "success", 2000)

    def _on_principal_var_change(self, attr_name: str, string_var_instance: ctk.StringVar,
                                 tk_var_name: str, tk_index: str, tk_mode: str) -> None:
        """Callback para mudanças nas StringVars da aba Principal."""
        if not hasattr(self, 'personagem_atual') or self.personagem_atual is None:
            return

        new_value_str = string_var_instance.get()
        valor_atual_modelo: Any

        if attr_name == "nivel":
            try:
                valor_atual_modelo = self.personagem_atual.nivel
                new_value_int = int(new_value_str)
                if new_value_int < 1: new_value_int = 1
                if valor_atual_modelo != new_value_int:
                    self.personagem_atual.atualizar_nivel(str(new_value_int))
                    # A atualização de nível já chama recalcular_maximos, que por sua vez
                    # deveria levar à atualização do display de PV/PM pela AttributesSkillsTab.
                    # Chamadas adicionais aqui podem ser redundantes se o fluxo estiver correto.
                    if hasattr(self, 'attributes_skills_tab'):
                         self.attributes_skills_tab.atualizar_display_maximos()
                    if hasattr(self, 'store_abilities_tab'):
                        self.store_abilities_tab.load_data_from_personagem()

            except ValueError:
                string_var_instance.set(str(valor_atual_modelo)) # Reverte na UI
                return
        else:
            valor_atual_modelo = getattr(self.personagem_atual, attr_name, "")
            if str(valor_atual_modelo) != new_value_str: # Compara como string para evitar problemas com tipos diferentes
                if attr_name == "classe_principal":
                    self.personagem_atual.atualizar_classe_principal(new_value_str)
                    self._update_subclass_options(new_value_str)
                    if hasattr(self, 'store_abilities_tab'):
                        self.store_abilities_tab.load_data_from_personagem()
                elif attr_name == "sub_classe":
                    self.personagem_atual.sub_classe = new_value_str
                    if hasattr(self, 'store_abilities_tab'):
                        self.store_abilities_tab.load_data_from_personagem()
                elif attr_name == "raca":
                    self.personagem_atual.atualizar_raca(new_value_str)
                else: # Para outros atributos string
                    setattr(self.personagem_atual, attr_name, new_value_str)
                
                # Se a classe, raça ou nível mudarem, os máximos podem precisar ser recalculados
                if attr_name in ["classe_principal", "raca"] and hasattr(self, 'attributes_skills_tab'):
                    self.attributes_skills_tab.atualizar_display_maximos()


    def _update_subclass_options(self, selected_main_class: str) -> None:
        """Atualiza as opções do widget de Sub-classe baseado na Classe Principal selecionada."""
        subclass_widget = self.principal_widgets.get("sub_classe")
        subclass_var = self.principal_stringvars.get("sub_classe")

        if isinstance(subclass_widget, ctk.CTkOptionMenu) and subclass_var:
            new_options = SUBCLASS_OPTIONS.get(selected_main_class, [""])
            if not new_options: new_options = [""]

            current_subclass_on_object = self.personagem_atual.sub_classe
            
            trace_id_tcl = self._principal_var_traces_tcl_names.get("sub_classe")
            if trace_id_tcl:
                try:
                    subclass_var.trace_vdelete("w", trace_id_tcl)
                except TclError:
                    pass # Pode já ter sido removido

            subclass_widget.configure(values=new_options)
            
            valor_subclasse_final = new_options[0]
            if current_subclass_on_object in new_options:
                valor_subclasse_final = current_subclass_on_object
            
            subclass_var.set(valor_subclasse_final)

            if self.personagem_atual.sub_classe != valor_subclasse_final:
                self.personagem_atual.sub_classe = valor_subclasse_final
                # Se a subclasse mudar, algumas abas podem precisar de atualização
                if hasattr(self, 'store_abilities_tab'):
                    self.store_abilities_tab.load_data_from_personagem()


            # Recadastrar o trace
            def create_trace_callback(p_atr: str, sv: ctk.StringVar) -> Callable[[str, str, str], None]:
                return lambda tk_var_name, tk_index, tk_mode: self._on_principal_var_change(p_atr, sv, tk_var_name, tk_index, tk_mode)
            
            new_trace_id = subclass_var.trace_add("write", create_trace_callback("sub_classe", subclass_var))
            self._principal_var_traces_tcl_names["sub_classe"] = new_trace_id

    def _adjust_nivel(self, amount: int) -> None:
        """Ajusta o nível do personagem e atualiza a StringVar correspondente."""
        nivel_var = self.principal_stringvars.get("nivel")
        if nivel_var:
            try:
                current_level = int(nivel_var.get())
                new_level = max(1, current_level + amount) # Nível mínimo 1
                nivel_var.set(str(new_level))
                # O trace na StringVar chamará _on_principal_var_change
            except ValueError:
                nivel_var.set(str(self.personagem_atual.nivel)) # Reverte em caso de erro

    def setup_principal_tab_widgets(self, tab_widget: ctk.CTkFrame) -> None:
        """Configura os widgets para a aba 'Principal' com animações e efeitos visuais."""
        content_frame = ctk.CTkFrame(tab_widget, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=2)
        content_frame.columnconfigure(2, weight=1)
        content_frame.columnconfigure(3, weight=2)
        
        racas_opcoes = ["", "Alari", "Roknar", "Kain", "Faelan", "Celeres", "Aurien", "Vesperi"]
        classes_opcoes = ["", CLASSE_EVOCADOR, CLASSE_TITA, CLASSE_SENTINELA, CLASSE_ELO]
        origens_opcoes = ["", "Sobrevivente do Círculo de Brasas", "Guarda de Harmonia", "Iniciado das Florestas", 
                         "Erudito da Grande Biblioteca", "Artista Itinerante", "Veterano das Guerras"]
        divindades_opcoes = ["", "Ignis", "Ondina", "Terrus", "Zephyrus", "Lumina", "Noctus", "Nenhum"]
        
        initial_subclass_options = SUBCLASS_OPTIONS.get(self.personagem_atual.classe_principal, [""])

        fields_data = [
            ("Nome do Personagem:", "nome_personagem", "entry", [], "Nome completo do seu personagem"),
            ("Nome do Jogador:", "nome_jogador", "entry", [], "Seu nome como jogador"),
            ("Raça:", "raca", "option", racas_opcoes, "Escolha a raça do seu personagem"),
            ("Classe Principal:", "classe_principal", "option", classes_opcoes, "Escolha a classe principal do personagem"),
            ("Sub-classe:", "sub_classe", "option", initial_subclass_options, "Especialização da classe principal"),
            ("Nível:", "nivel", "level_adjust", [], "Nível atual do personagem"),
            ("Origem:", "origem", "option", origens_opcoes, "Background do personagem"),
            ("Divindade/Patrono:", "divindade_patrono", "option", divindades_opcoes, "Divindade ou patrono do personagem"),
            ("Tendência (Alinhamento):", "tendencia", "entry", [], "Alinhamento moral do personagem"),
        ]
        
        # Função para criar widget com animação de fade in
        def create_widget_with_animation(row: int, col: int, widget: ctk.CTkBaseClass, delay: int):
            widget.grid(row=row, column=col, padx=(0,10), pady=5, sticky="ew")
            widget.grid_remove()  # Esconde inicialmente
            
            def show_widget():
                widget.grid()
            
            content_frame.after(delay, show_widget)
        
        row_count_col1 = 0
        row_count_col2 = 0
        
        for i, (label_text, attr_name, widget_type, options, tooltip_text) in enumerate(fields_data):
            delay = i * 100  # Atraso progressivo para cada widget
            
            target_column_label_idx = 0
            target_column_entry_idx = 1
            current_row_for_field = 0
            
            if i % 2 == 0:
                row_count_col1 += 1
                current_row_for_field = row_count_col1
            else:
                target_column_label_idx = 2
                target_column_entry_idx = 3
                row_count_col2 += 1
                current_row_for_field = row_count_col2
            
            # Label com estilo melhorado
            label = ctk.CTkLabel(
                master=content_frame,
                text=label_text,
                anchor="e",
                font=("Helvetica", 12),
                text_color=COLORS["text"]
            )
            create_widget_with_animation(current_row_for_field, target_column_label_idx, label, delay)
            
            current_field_var = ctk.StringVar()
            self.principal_stringvars[attr_name] = current_field_var
            
            def create_trace_callback(p_atr: str, sv: ctk.StringVar) -> Callable[[str, str, str], None]:
                return lambda tk_var_name, tk_index, tk_mode: self._on_principal_var_change(p_atr, sv, tk_var_name, tk_index, tk_mode)
            
            trace_id_tcl = current_field_var.trace_add("write", create_trace_callback(attr_name, current_field_var))
            self._principal_var_traces_tcl_names[attr_name] = trace_id_tcl
            
            widget: Optional[ctk.CTkBaseClass] = None
            
            if widget_type == "entry":
                widget = ctk.CTkEntry(
                    master=content_frame,
                    placeholder_text=label_text.replace(":", ""),
                    textvariable=current_field_var,
                    height=32,
                    font=("Helvetica", 12),
                    corner_radius=8,
                    border_color=COLORS["primary"]
                )
            
            elif widget_type == "option":
                current_options_for_menu = options
                if attr_name == "sub_classe":
                    current_options_for_menu = initial_subclass_options
                widget = ctk.CTkOptionMenu(
                    master=content_frame,
                    values=current_options_for_menu,
                    variable=current_field_var,
                    dynamic_resizing=False,
                    height=32,
                    font=("Helvetica", 12),
                    corner_radius=8,
                    button_color=COLORS["primary"],
                    button_hover_color="#2980b9",
                    fg_color=COLORS["surface"]
                )
            
            elif widget_type == "level_adjust":
                level_frame = ctk.CTkFrame(master=content_frame, fg_color="transparent")
                
                minus_button = ctk.CTkButton(
                    master=level_frame,
                    text="-",
                    width=32,
                    height=32,
                    command=lambda: self._adjust_nivel(-1),
                    corner_radius=8,
                    fg_color=COLORS["danger"],
                    hover_color="#c0392b"
                )
                minus_button.pack(side="left", padx=(0,2))
                
                level_entry = ctk.CTkEntry(
                    master=level_frame,
                    textvariable=current_field_var,
                    width=50,
                    height=32,
                    justify="center",
                    font=("Helvetica", 12, "bold"),
                    corner_radius=8,
                    border_color=COLORS["primary"]
                )
                level_entry.pack(side="left", padx=2)
                self.principal_widgets[attr_name + "_entry"] = level_entry
                
                plus_button = ctk.CTkButton(
                    master=level_frame,
                    text="+",
                    width=32,
                    height=32,
                    command=lambda: self._adjust_nivel(1),
                    corner_radius=8,
                    fg_color=COLORS["success"],
                    hover_color="#27ae60"
                )
                plus_button.pack(side="left", padx=(2,0))
                
                widget = level_frame
            
            if widget:
                create_widget_with_animation(current_row_for_field, target_column_entry_idx, widget, delay + 50)
                self.principal_widgets[attr_name] = widget
                ToolTip(widget, tooltip_text)

    def salvar_ficha(self) -> None:
        """Salva os dados do personagem atual em um arquivo JSON."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("Todos os Arquivos", "*.*")],
            title="Salvar Ficha de Personagem Elaria"
        )
        if not filepath:
            self.show_feedback_message("Salvar cancelado.", "warning", 2000)
            return
        try:
            char_data = self.personagem_atual.to_dict()
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(char_data, f, ensure_ascii=False, indent=4)
            self.show_feedback_message(f"Ficha salva: {filepath.split('/')[-1]}", "success", 3000)
        except Exception as e:
            self.show_feedback_message(f"Erro ao salvar: {e}", "error", 4000)
            print(f"Erro ao salvar ficha: {e}") # Log para debug
            messagebox.showerror("Erro ao Salvar", f"Ocorreu um erro ao salvar a ficha:\n{e}")


    def carregar_ficha(self) -> None:
        """Carrega os dados de um personagem de um arquivo JSON e atualiza a UI."""
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json"), ("Todos os Arquivos", "*.*")],
            title="Carregar Ficha de Personagem Elaria"
        )
        if not filepath:
            self.show_feedback_message("Carregar cancelado.", "warning", 2000)
            return
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                char_data = json.load(f)
            self.personagem_atual = Personagem.from_dict(char_data)
            self.atualizar_ui_completa(primeira_carga=False) # Não é a primeira carga do app, mas é de uma ficha
            self.show_feedback_message(f"Ficha carregada: {filepath.split('/')[-1]}", "success", 3000)
        except Exception as e:
            self.show_feedback_message(f"Erro ao carregar: {e}", "error", 4000)
            print(f"Erro ao carregar ficha: {e}") # Log para debug
            messagebox.showerror("Erro ao Carregar", f"Ocorreu um erro ao carregar a ficha:\n{e}")


    def atualizar_ui_completa(self, primeira_carga: bool = False) -> None:
        """
        Atualiza toda a interface do usuário para refletir o estado do
        `personagem_atual`. Chamado ao carregar uma ficha ou criar uma nova.
        """
        # print("Atualizando UI completa com dados do personagem...") # Para debug

        # Atualiza a aba Principal
        # Primeiro, remove os traces existentes para evitar disparos durante o set
        if hasattr(self, 'principal_stringvars'):
            for attr_name, string_var in self.principal_stringvars.items():
                trace_id_tcl = self._principal_var_traces_tcl_names.get(attr_name)
                if trace_id_tcl:
                    try:
                        string_var.trace_vdelete("w", trace_id_tcl)
                    except TclError:
                        pass # O trace pode já não existir ou ser inválido

        # Atualiza as opções de subclasse antes de definir o valor da StringVar de subclasse
        loaded_main_class = getattr(self.personagem_atual, "classe_principal", "")
        self._update_subclass_options(loaded_main_class) # Isso já reconfigura o trace da subclasse

        # Define os novos valores nas StringVars da aba Principal
        if hasattr(self, 'principal_stringvars'):
            for attr_name, string_var in self.principal_stringvars.items():
                new_val = str(getattr(self.personagem_atual, attr_name, ""))
                string_var.set(new_val) # Define o valor sem disparar o callback antigo

                # Recadastra o trace de escrita específico, exceto para subclasse que já foi tratada
                if attr_name != "sub_classe":
                    def create_trace_callback(p_atr: str, sv: ctk.StringVar) -> Callable[[str, str, str], None]:
                        return lambda tk_var_name, tk_index, tk_mode: self._on_principal_var_change(p_atr, sv, tk_var_name, tk_index, tk_mode)
                    new_trace_id_tcl = string_var.trace_add("write", create_trace_callback(attr_name, string_var))
                    self._principal_var_traces_tcl_names[attr_name] = new_trace_id_tcl
        
        # Atualiza as outras abas, passando a nova (ou mesma) instância de personagem
        if hasattr(self, 'attributes_skills_tab') and self.attributes_skills_tab:
            self.attributes_skills_tab.personagem = self.personagem_atual
            self.attributes_skills_tab.load_data_from_personagem()
        
        if hasattr(self, 'combat_tab') and self.combat_tab:
            self.combat_tab.personagem = self.personagem_atual
            self.combat_tab.load_data_from_personagem()
            
        if hasattr(self, 'magic_tab') and self.magic_tab:
            self.magic_tab.personagem = self.personagem_atual
            self.magic_tab.load_data_from_personagem()
            
        if hasattr(self, 'inventory_tab') and self.inventory_tab:
            self.inventory_tab.personagem = self.personagem_atual
            self.inventory_tab.load_data_from_personagem()
        
        if hasattr(self, 'store_abilities_tab') and self.store_abilities_tab:
            self.store_abilities_tab.personagem = self.personagem_atual
            self.store_abilities_tab.load_data_from_personagem()

        if hasattr(self, 'notes_tab') and self.notes_tab:
            self.notes_tab.personagem = self.personagem_atual
            self.notes_tab.load_data_from_personagem() # Chama o novo método

        # print("UI atualizada.") # Para debug