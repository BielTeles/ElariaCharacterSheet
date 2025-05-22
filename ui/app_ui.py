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

class AppUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ficha de Personagem Elaria RPG")
        self.root.geometry("850x700")

        self.personagem_atual = Personagem()

        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.file_ops_frame = ctk.CTkFrame(self.main_frame)
        self.file_ops_frame.pack(fill="x", pady=(0, 10))

        self.save_button = ctk.CTkButton(self.file_ops_frame, text="Salvar Ficha", command=self.salvar_ficha)
        self.save_button.pack(side="left", padx=10, pady=5)

        self.load_button = ctk.CTkButton(self.file_ops_frame, text="Carregar Ficha", command=self.carregar_ficha)
        self.load_button.pack(side="left", padx=10, pady=5)

        self.tab_view = ctk.CTkTabview(self.main_frame)
        self.tab_view.pack(fill="both", expand=True)

        self.tab_principal_widget = self.tab_view.add("Principal")
        self.tab_attrs_skills_widget = self.tab_view.add("Atributos & Perícias")
        self.tab_combat_widget = self.tab_view.add("Combate")
        self.tab_magia_widget = self.tab_view.add("Magia")
        self.tab_inventario_widget = self.tab_view.add("Inventário")
        self.tab_rolador_widget = self.tab_view.add("Rolador de Dados")
        self.tab_notas_widget = self.tab_view.add("Notas")

        self.tab_view.set("Principal")

        self.principal_stringvars = {}
        self.principal_entries = {}
        # O setup_principal_tab agora é chamado dentro de atualizar_ui_completa pela primeira vez
        # ou podemos chamá-lo aqui para configurar os widgets inicialmente, e atualizar_ui_completa
        # apenas setaria os valores das StringVars. Vamos configurar aqui.
        self.setup_principal_tab_widgets(self.tab_principal_widget) # Apenas configura widgets
        
        self.attributes_skills_tab = AttributesSkillsTab(self.tab_attrs_skills_widget, self.personagem_atual)
        self.combat_tab = CombatTab(self.tab_combat_widget, self.attributes_skills_tab, self.personagem_atual)
        self.magic_tab = MagicTab(self.tab_magia_widget, self.personagem_atual)
        self.inventory_tab = InventoryTab(self.tab_inventario_widget, self.personagem_atual)
        self.dice_roller_generic_tab = DiceRollerGenericTab(self.tab_rolador_widget)
        self.notes_tab = NotesTab(self.tab_notas_widget, self.personagem_atual)

        self.atualizar_ui_completa() # Carrega dados iniciais do personagem padrão na UI

    def _update_personagem_attr(self, personagem_obj, attr_name, string_var, *args): # Adicionado *args
        # Se o último argumento for 'ui_reload_skip_personagem_update', não atualiza o objeto personagem.
        if args and args[-1] == "ui_reload_skip_personagem_update":
            return

        new_value_str = string_var.get()
        current_value_in_obj = getattr(personagem_obj, attr_name, "")

        if attr_name == "nivel":
            try:
                new_value_int = int(new_value_str)
                if personagem_obj.nivel != new_value_int:
                    setattr(personagem_obj, attr_name, new_value_int)
                    # print(f"Personagem.{attr_name} atualizado para: {new_value_int}")
            except ValueError:
                string_var.set(str(current_value_in_obj)) # Reverte na UI
                # print(f"Aviso: Nível '{new_value_str}' não é um inteiro válido. Mantido: {current_value_in_obj}")
        else:
            if str(current_value_in_obj) != new_value_str:
                setattr(personagem_obj, attr_name, new_value_str)
                # print(f"Personagem.{attr_name} atualizado para: {new_value_str}")

    def setup_principal_tab_widgets(self, tab_widget): # Renomeado, apenas configura os widgets
        content_frame = ctk.CTkFrame(tab_widget)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        content_frame.columnconfigure(0, weight=1); content_frame.columnconfigure(1, weight=2)
        content_frame.columnconfigure(2, weight=1); content_frame.columnconfigure(3, weight=2)
        
        fields_data = [
            ("Nome do Personagem:", "nome_personagem"), ("Nome do Jogador:", "nome_jogador"),
            ("Raça:", "raca"), ("Classe Principal:", "classe_principal"),
            ("Sub-classe:", "sub_classe"), ("Nível:", "nivel"),
            ("Origem:", "origem"), ("Divindade/Patrono:", "divindade_patrono"),
            ("Tendência (Alinhamento):", "tendencia"),]
        
        row_count_col1 = 0; row_count_col2 = 0
        for i, (label_text, attr_name) in enumerate(fields_data):
            target_column_label_idx = 0; target_column_entry_idx = 1; current_row_for_field = 0
            if i % 2 == 0: row_count_col1 += 1; current_row_for_field = row_count_col1
            else: target_column_label_idx = 2; target_column_entry_idx = 3; row_count_col2 += 1; current_row_for_field = row_count_col2
            
            label = ctk.CTkLabel(master=content_frame, text=label_text, anchor="e")
            label.grid(row=current_row_for_field, column=target_column_label_idx, padx=(10,5), pady=5, sticky="e")
            
            var = ctk.StringVar() # O valor será setado por atualizar_ui_completa
            var.trace_add("write", lambda n, idx, m, p=self.personagem_atual, atr=attr_name, v=var: self._update_personagem_attr(p, atr, v))
            self.principal_stringvars[attr_name] = var
            
            entry = ctk.CTkEntry(master=content_frame, placeholder_text=label_text.replace(":", ""), textvariable=var)
            entry.grid(row=current_row_for_field, column=target_column_entry_idx, padx=(0,10), pady=5, sticky="ew")
            self.principal_entries[attr_name] = entry
            
    def salvar_ficha(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("Todos os Arquivos", "*.*")],
            title="Salvar Ficha de Personagem Elaria"
        )
        if not filepath:
            print("Salvar cancelado.")
            return
        try:
            # Garante que os dados das StringVars que não usam _update_personagem_attr (se houver)
            # são coletados antes de salvar. No nosso caso, _update_personagem_attr é chamado pelos traces.
            char_data = self.personagem_atual.to_dict()
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(char_data, f, ensure_ascii=False, indent=4)
            print(f"Ficha salva com sucesso em: {filepath}")
        except Exception as e:
            print(f"Erro ao salvar ficha: {e}")

    def carregar_ficha(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json"), ("Todos os Arquivos", "*.*")],
            title="Carregar Ficha de Personagem Elaria"
        )
        if not filepath:
            print("Carregar cancelado.")
            return
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                char_data = json.load(f)
            
            # Cria uma NOVA instância de Personagem a partir dos dados carregados
            self.personagem_atual = Personagem.from_dict(char_data) 
            print(f"Ficha carregada de: {filepath}. Personagem: {self.personagem_atual.nome_personagem}")
            
            # Atualizar toda a UI para refletir o novo self.personagem_atual
            self.atualizar_ui_completa()

        except Exception as e:
            print(f"Erro ao carregar ficha: {e}")

    def atualizar_ui_completa(self):
        """Atualiza todos os campos da UI com os dados do self.personagem_atual."""
        print("Atualizando UI completa com dados do personagem...")
        
        # Aba Principal - Atualiza as StringVars, que atualizam os Entries
        if hasattr(self, 'principal_stringvars'): # Verifica se já foi inicializado
            for attr_name, string_var in self.principal_stringvars.items():
                new_val = str(getattr(self.personagem_atual, attr_name, ""))
                # Para evitar loop de trace desnecessário, podemos desabilitar e reabilitar o trace
                # ou, mais simples, a lógica em _update_personagem_attr deve impedir a reescrita se o valor for o mesmo.
                # A forma mais segura é setar o valor da stringvar sem que ela dispare o callback de escrita no objeto.
                # No entanto, o trace "write" é para quando a UI muda o valor. Aqui, estamos mudando o valor da UI.
                # Se _update_personagem_attr for idempotente ou verificar se o valor realmente mudou, está OK.
                string_var.set(new_val)


        # Aba Atributos & Perícias
        if hasattr(self, 'attributes_skills_tab') and self.attributes_skills_tab:
            self.attributes_skills_tab.personagem = self.personagem_atual # Garante que a aba usa o personagem carregado
            self.attributes_skills_tab.load_data_from_personagem() 

        # Aba Combate
        if hasattr(self, 'combat_tab') and self.combat_tab:
            self.combat_tab.personagem = self.personagem_atual
            self.combat_tab.load_data_from_personagem()

        # Aba Magia
        if hasattr(self, 'magic_tab') and self.magic_tab:
            self.magic_tab.personagem = self.personagem_atual
            self.magic_tab.load_data_from_personagem()
        
        # Aba Inventário
        if hasattr(self, 'inventory_tab') and self.inventory_tab:
            self.inventory_tab.personagem = self.personagem_atual
            self.inventory_tab.load_data_from_personagem()

        # Aba Notas
        if hasattr(self, 'notes_tab') and self.notes_tab:
            self.notes_tab.personagem = self.personagem_atual
            # NotesTab agora deve ter seu próprio load_data_from_personagem ou um método para setar o texto
            if hasattr(self.notes_tab, 'load_data_from_personagem'):
                 self.notes_tab.load_data_from_personagem()
            elif hasattr(self.notes_tab, 'notes_textbox') and hasattr(self.personagem_atual, 'notas'): # Fallback
                self.notes_tab.notes_textbox.delete("0.0", "end")
                self.notes_tab.notes_textbox.insert("0.0", self.personagem_atual.notas if self.personagem_atual.notas else "")
        
        print("UI atualizada.")