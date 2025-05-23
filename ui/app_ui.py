import customtkinter as ctk
from tkinter import filedialog
import json
from core.character import Personagem
from ui.tab_attributes_skills import AttributesSkillsTab
from ui.tab_combat import CombatTab
from ui.tab_magic import MagicTab
from ui.tab_inventory import InventoryTab
from ui.tab_notes import NotesTab
from ui.tab_dice_roller_generic import DiceRollerGenericTab
from ui.tab_store_abilities import StoreAbilitiesTab

SUBCLASS_OPTIONS = {
    "Evocador": ["", "Caminho da Terra", "Caminho da Água", "Caminho do Ar", "Caminho do Fogo", "Caminho da Luz", "Caminho da Sombra"],
    "Titã": ["", "Arquétipo do Baluarte", "Arquétipo da Fúria Primal", "Arquétipo do Quebra-Montanhas"],
    "Sentinela": ["", "Arquétipo do Rastreador dos Ermos", "Arquétipo da Lâmina do Crepúsculo", "Arquétipo do Olho Vigilante"],
    "Elo": ["", "Arquétipo da Voz da Harmonia", "Arquétipo do Porta-Voz da Chama", "Arquétipo do Guardião do Coração"],
    "": [""]
}
for class_name_key in SUBCLASS_OPTIONS:
    if SUBCLASS_OPTIONS[class_name_key] and SUBCLASS_OPTIONS[class_name_key][0] != "":
        SUBCLASS_OPTIONS[class_name_key].insert(0, "")


class AppUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ficha de Personagem Elaria RPG")
        self.root.geometry("1280x720")
        self.personagem_atual = Personagem()

        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.file_ops_frame = ctk.CTkFrame(self.main_frame)
        self.file_ops_frame.pack(fill="x", pady=(0, 10))

        self.save_button = ctk.CTkButton(self.file_ops_frame, text="Salvar Ficha", command=self.salvar_ficha)
        self.save_button.pack(side="left", padx=10, pady=5)
        self.load_button = ctk.CTkButton(self.file_ops_frame, text="Carregar Ficha", command=self.carregar_ficha)
        self.load_button.pack(side="left", padx=10, pady=5)
        self.new_char_button = ctk.CTkButton(self.file_ops_frame, text="Nova Ficha", command=self.nova_ficha)
        self.new_char_button.pack(side="left", padx=10, pady=5)
        self.feedback_label = ctk.CTkLabel(self.file_ops_frame, text="")
        self.feedback_label.pack(side="left", padx=10, pady=5)

        self.tab_view = ctk.CTkTabview(self.main_frame)
        self.tab_view.pack(fill="both", expand=True)

        self.tab_principal_widget = self.tab_view.add("Principal")
        self.tab_attrs_skills_widget = self.tab_view.add("Atributos & Perícias")
        self.tab_combat_widget = self.tab_view.add("Combate")
        self.tab_magia_widget = self.tab_view.add("Magia")
        self.tab_inventario_widget = self.tab_view.add("Inventário")
        self.tab_loja_habilidades_widget = self.tab_view.add("Loja & Habilidades")
        self.tab_rolador_widget = self.tab_view.add("Rolador de Dados")
        self.tab_notas_widget = self.tab_view.add("Notas")
        
        self.tab_view.set("Principal")

        self.principal_stringvars = {}
        self.principal_widgets = {}
        self._principal_var_traces_tcl_names = {} # Para guardar os nomes dos callbacks Tcl

        self.setup_principal_tab_widgets(self.tab_principal_widget)
        
        self.attributes_skills_tab = AttributesSkillsTab(self.tab_attrs_skills_widget, self.personagem_atual)
        self.combat_tab = CombatTab(self.tab_combat_widget, self.attributes_skills_tab, self.personagem_atual)
        self.magic_tab = MagicTab(self.tab_magia_widget, self.personagem_atual)
        self.inventory_tab = InventoryTab(self.tab_inventario_widget, self.personagem_atual)
        self.store_abilities_tab = StoreAbilitiesTab(self.tab_loja_habilidades_widget, self.personagem_atual, self)
        self.dice_roller_generic_tab = DiceRollerGenericTab(self.tab_rolador_widget)
        self.notes_tab = NotesTab(self.tab_notas_widget, self.personagem_atual)
        
        self.atualizar_ui_completa() 

    def show_feedback_message(self, message, duration=3000):
        self.feedback_label.configure(text=message)
        self.root.after(duration, lambda: self.feedback_label.configure(text=""))

    def nova_ficha(self):
        self.personagem_atual = Personagem() 
        self.atualizar_ui_completa()       
        self.show_feedback_message("Nova ficha limpa carregada.", 2000)

    def _on_principal_var_change(self, attr_name, string_var_instance, tk_var_name, tk_index, tk_mode):
        self._update_personagem_attr(self.personagem_atual, attr_name, string_var_instance)
        
        if attr_name == "classe_principal":
            self._update_subclass_options(string_var_instance.get()) 
            if hasattr(self, 'store_abilities_tab') and self.store_abilities_tab:
                self.store_abilities_tab.load_data_from_personagem()
        elif attr_name == "sub_classe":
            if hasattr(self, 'store_abilities_tab') and self.store_abilities_tab:
                 self.store_abilities_tab.load_data_from_personagem()
        elif attr_name == "nivel":
            if hasattr(self, 'attributes_skills_tab') and self.attributes_skills_tab:
                 self.attributes_skills_tab.atualizar_display_maximos()
            if hasattr(self, 'store_abilities_tab') and self.store_abilities_tab:
                 self.store_abilities_tab.load_data_from_personagem()


    def _update_personagem_attr(self, personagem_obj, attr_name, string_var_instance):
        new_value_str = string_var_instance.get()
        valor_mudou = False
        
        if attr_name == "nivel":
            try:
                new_value_int = int(new_value_str)
                if new_value_int < 1: new_value_int = 1
                if personagem_obj.nivel != new_value_int:
                    personagem_obj.atualizar_nivel(str(new_value_int)) 
                    valor_mudou = True
            except ValueError: 
                string_var_instance.set(str(personagem_obj.nivel))
                return
        elif attr_name == "classe_principal":
            if personagem_obj.classe_principal != new_value_str:
                personagem_obj.atualizar_classe_principal(new_value_str)
                valor_mudou = True
        elif attr_name == "raca":
            if personagem_obj.raca != new_value_str:
                personagem_obj.atualizar_raca(new_value_str)
                valor_mudou = True
        elif attr_name == "sub_classe":
             if personagem_obj.sub_classe != new_value_str:
                personagem_obj.sub_classe = new_value_str
                valor_mudou = True
        else: 
            # Para atributos gerais que são strings simples ou podem ser convertidos
            if hasattr(personagem_obj, attr_name):
                if str(getattr(personagem_obj, attr_name, "")) != new_value_str:
                    setattr(personagem_obj, attr_name, new_value_str)
                    valor_mudou = True
            # Se for um atributo numérico que não 'nivel' (ex: vindo da aba de atributos)
            elif attr_name in personagem_obj.atributos:
                 try:
                    val_int = int(new_value_str)
                    if personagem_obj.atributos[attr_name] != val_int:
                        personagem_obj.atualizar_atributo(attr_name, val_int) # Usa o método do Personagem
                        valor_mudou = True
                 except ValueError:
                    string_var_instance.set(str(personagem_obj.atributos.get(attr_name,0)))
                    return

        # Recalcula máximos e atualiza display se necessário
        # Verifica se o atributo alterado está na lista de atributos que afetam PV/PM
        atributos_que_afetam_recursos = ["constituicao", "sabedoria", "carisma", "inteligencia"] # Nomes base dos atributos
        atributo_base_alterado = next((key for key in atributos_que_afetam_recursos if attr_name.lower().startswith(key)), None)

        if valor_mudou and (attr_name in ["nivel", "classe_principal", "raca"] or atributo_base_alterado):
            if hasattr(personagem_obj, 'recalcular_maximos'):
                personagem_obj.recalcular_maximos()
            if hasattr(self, 'attributes_skills_tab') and self.attributes_skills_tab:
                self.attributes_skills_tab.atualizar_display_maximos()

    def _update_subclass_options(self, selected_main_class):
        subclass_widget = self.principal_widgets.get("sub_classe")
        subclass_var = self.principal_stringvars.get("sub_classe")

        if isinstance(subclass_widget, ctk.CTkOptionMenu) and subclass_var:
            new_options = SUBCLASS_OPTIONS.get(selected_main_class, [""]) 
            if not new_options : new_options = [""] 
            
            current_subclass_on_object = self.personagem_atual.sub_classe
            
            # Guardar e remover o trace 'write' temporariamente
            # trace_info() retorna uma lista de tuplas (modo_tcl, nome_callback_tcl)
            trace_id_tcl = self._principal_var_traces_tcl_names.get("sub_classe")
            if trace_id_tcl:
                # O modo correto é 'w' para trace de escrita.
                # O trace_id_tcl é o nome do callback Tcl.
                try:
                    subclass_var.trace_vdelete("w", trace_id_tcl)
                except ctk.tkinter.TclError as e:
                    print(f"Aviso: Falha ao remover trace para sub_classe (pode já ter sido removido ou inválido): {e}")


            subclass_widget.configure(values=new_options)
            
            valor_subclasse_final = new_options[0] 
            if current_subclass_on_object in new_options: 
                valor_subclasse_final = current_subclass_on_object
            
            subclass_var.set(valor_subclasse_final)

            if self.personagem_atual.sub_classe != valor_subclasse_final:
                 self.personagem_atual.sub_classe = valor_subclasse_final

            # Recadastrar o trace
            def create_trace_callback(p_atr, sv):
                return lambda n, i, m_op: self._on_principal_var_change(p_atr, sv, n, i, m_op)
            
            # O trace_add retorna o nome do callback Tcl que ele cria
            new_trace_id = subclass_var.trace_add("write", create_trace_callback("sub_classe", subclass_var))
            self._principal_var_traces_tcl_names["sub_classe"] = new_trace_id


    def _adjust_nivel(self, amount):
        try:
            current_level_str = self.principal_stringvars["nivel"].get()
            current_level = int(current_level_str) if current_level_str.lstrip('-').isdigit() else self.personagem_atual.nivel
            new_level = current_level + amount
            if new_level < 1: new_level = 1
            self.principal_stringvars["nivel"].set(str(new_level))
        except ValueError:
            self.principal_stringvars["nivel"].set(str(self.personagem_atual.nivel))
        except KeyError:
            print("Erro: StringVar para 'nivel' não encontrada.")

    def setup_principal_tab_widgets(self, tab_widget):
        content_frame = ctk.CTkFrame(tab_widget)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        content_frame.columnconfigure(0, weight=1); content_frame.columnconfigure(1, weight=2)
        content_frame.columnconfigure(2, weight=1); content_frame.columnconfigure(3, weight=2)
        
        racas_opcoes = ["", "Alari", "Roknar", "Kain", "Faelan", "Celeres", "Aurien", "Vesperi"]
        classes_opcoes = ["", "Evocador", "Titã", "Sentinela", "Elo"]
        origens_opcoes = ["", "Sobrevivente do Círculo de Brasas", "Guarda de Harmonia", "Iniciado das Florestas", "Erudito da Grande Biblioteca", "Artista Itinerante", "Veterano das Guerras"]
        divindades_opcoes = ["", "Ignis", "Ondina", "Terrus", "Zephyrus", "Lumina", "Noctus", "Nenhum"]
        
        initial_subclass_options = SUBCLASS_OPTIONS.get(self.personagem_atual.classe_principal, [""])

        fields_data = [
            ("Nome do Personagem:", "nome_personagem", "entry", []),
            ("Nome do Jogador:", "nome_jogador", "entry", []),
            ("Raça:", "raca", "option", racas_opcoes),
            ("Classe Principal:", "classe_principal", "option", classes_opcoes),
            ("Sub-classe:", "sub_classe", "option", initial_subclass_options),
            ("Nível:", "nivel", "level_adjust", []),
            ("Origem:", "origem", "option", origens_opcoes),
            ("Divindade/Patrono:", "divindade_patrono", "option", divindades_opcoes),
            ("Tendência (Alinhamento):", "tendencia", "entry", []),
        ]
        
        row_count_col1 = 0; row_count_col2 = 0
        for i, (label_text, attr_name, widget_type, options) in enumerate(fields_data):
            target_column_label_idx = 0; target_column_entry_idx = 1; current_row_for_field = 0
            if i % 2 == 0: row_count_col1 += 1; current_row_for_field = row_count_col1
            else: target_column_label_idx = 2; target_column_entry_idx = 3; row_count_col2 += 1; current_row_for_field = row_count_col2
            
            label = ctk.CTkLabel(master=content_frame, text=label_text, anchor="e")
            label.grid(row=current_row_for_field, column=target_column_label_idx, padx=(10,5), pady=5, sticky="e")
            
            current_field_var = ctk.StringVar() 
            self.principal_stringvars[attr_name] = current_field_var
            
            def create_trace_callback(p_atr, sv):
                return lambda tk_var_name, tk_index, tk_mode: self._on_principal_var_change(p_atr, sv, tk_var_name, tk_index, tk_mode)

            trace_id_tcl = current_field_var.trace_add("write", create_trace_callback(attr_name, current_field_var))
            self._principal_var_traces_tcl_names[attr_name] = trace_id_tcl 
            
            widget_container = content_frame 
            target_col_for_widget = target_column_entry_idx

            if widget_type == "entry":
                widget = ctk.CTkEntry(master=widget_container, placeholder_text=label_text.replace(":", ""), textvariable=current_field_var)
            elif widget_type == "option":
                # Para o widget de subclasse, as opções são dinâmicas e serão atualizadas por _update_subclass_options
                current_options = options if attr_name != "sub_classe" else initial_subclass_options
                widget = ctk.CTkOptionMenu(master=widget_container, values=current_options, variable=current_field_var, dynamic_resizing=False)
            elif widget_type == "level_adjust":
                level_frame = ctk.CTkFrame(master=widget_container, fg_color="transparent")
                minus_button = ctk.CTkButton(master=level_frame, text="-", width=28, height=28, command=lambda: self._adjust_nivel(-1))
                minus_button.pack(side="left", padx=(0,2))
                level_display_label = ctk.CTkLabel(master=level_frame, textvariable=current_field_var, width=40, height=28)
                level_display_label.pack(side="left", padx=2)
                self.principal_widgets[attr_name + "_label"] = level_display_label
                plus_button = ctk.CTkButton(master=level_frame, text="+", width=28, height=28, command=lambda: self._adjust_nivel(1))
                plus_button.pack(side="left", padx=(2,0))
                widget = level_frame
            
            if widget:
                widget.grid(row=current_row_for_field, column=target_col_for_widget, padx=(0,10), pady=5, sticky="ew")
                self.principal_widgets[attr_name] = widget

    def salvar_ficha(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json"), ("Todos os Arquivos", "*.*")], title="Salvar Ficha de Personagem Elaria")
        if not filepath: self.show_feedback_message("Salvar cancelado.", 2000); return
        try:
            char_data = self.personagem_atual.to_dict()
            with open(filepath, 'w', encoding='utf-8') as f: json.dump(char_data, f, ensure_ascii=False, indent=4)
            self.show_feedback_message(f"Ficha salva: {filepath.split('/')[-1]}", 3000)
        except Exception as e: self.show_feedback_message(f"Erro ao salvar: {e}", 4000); print(f"Erro ao salvar ficha: {e}")

    def carregar_ficha(self):
        filepath = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json"), ("Todos os Arquivos", "*.*")], title="Carregar Ficha de Personagem Elaria")
        if not filepath: self.show_feedback_message("Carregar cancelado.", 2000); return
        try:
            with open(filepath, 'r', encoding='utf-8') as f: char_data = json.load(f)
            self.personagem_atual = Personagem.from_dict(char_data) 
            self.atualizar_ui_completa()
            self.show_feedback_message(f"Ficha carregada: {filepath.split('/')[-1]}", 3000)
        except Exception as e: self.show_feedback_message(f"Erro ao carregar: {e}", 4000); print(f"Erro ao carregar ficha: {e}")


    def atualizar_ui_completa(self):
        print("Atualizando UI completa com dados do personagem...")

        loaded_main_class = getattr(self.personagem_atual, "classe_principal", "")
        self._update_subclass_options(loaded_main_class) 

        if hasattr(self, 'principal_stringvars'): 
            for attr_name, string_var in self.principal_stringvars.items():
                trace_id_tcl = self._principal_var_traces_tcl_names.get(attr_name)
                if trace_id_tcl:
                    try:
                        string_var.trace_vdelete("w", trace_id_tcl) 
                    except ctk.tkinter.TclError as e:
                         print(f"Aviso: Falha ao remover trace para {attr_name} (pode já ter sido removido ou inválido): {e}")
                
                new_val = str(getattr(self.personagem_atual, attr_name, ""))
                string_var.set(new_val)

                # Recadastrar o trace de escrita específico
                def create_trace_callback(p_atr, sv):
                    return lambda tk_var_name, tk_index, tk_mode: self._on_principal_var_change(p_atr, sv, tk_var_name, tk_index, tk_mode)
                new_trace_id_tcl = string_var.trace_add("write", create_trace_callback(attr_name, string_var))
                self._principal_var_traces_tcl_names[attr_name] = new_trace_id_tcl # Atualiza com o novo ID do trace
        
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
            if hasattr(self.notes_tab, 'notes_textbox') and hasattr(self.personagem_atual, 'notas'):
                self.notes_tab.notes_textbox.delete("0.0", "end") 
                self.notes_tab.notes_textbox.insert("0.0", self.personagem_atual.notas if self.personagem_atual.notas else "")
        print("UI atualizada.")