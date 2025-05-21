import customtkinter as ctk
from ui.tab_attributes_skills import AttributesSkillsTab
from ui.tab_combat import CombatTab
from ui.tab_magic import MagicTab
from ui.tab_inventory import InventoryTab
from ui.tab_notes import NotesTab
from ui.tab_dice_roller_generic import DiceRollerGenericTab # NOVA IMPORTAÇÃO

class AppUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ficha de Personagem Elaria RPG")
        self.root.geometry("850x700")

        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_view = ctk.CTkTabview(self.main_frame)
        self.tab_view.pack(fill="both", expand=True)

        self.tab_principal_widget = self.tab_view.add("Principal")
        self.tab_attrs_skills_widget = self.tab_view.add("Atributos & Perícias")
        self.tab_combat_widget = self.tab_view.add("Combate")
        self.tab_magia_widget = self.tab_view.add("Magia")
        self.tab_inventario_widget = self.tab_view.add("Inventário")
        self.tab_rolador_widget = self.tab_view.add("Rolador de Dados") # NOVA ABA
        self.tab_notas_widget = self.tab_view.add("Notas")

        self.tab_view.set("Principal")

        self.setup_principal_tab(self.tab_principal_widget)
        self.attributes_skills_tab = AttributesSkillsTab(self.tab_attrs_skills_widget)
        self.combat_tab = CombatTab(self.tab_combat_widget)
        self.magic_tab = MagicTab(self.tab_magia_widget)
        self.inventory_tab = InventoryTab(self.tab_inventario_widget)
        self.dice_roller_generic_tab = DiceRollerGenericTab(self.tab_rolador_widget) # NOVA INSTÂNCIA
        self.notes_tab = NotesTab(self.tab_notas_widget)
        

    def setup_principal_tab(self, tab_widget):
        # ... (código da aba principal continua o mesmo) ...
        content_frame = ctk.CTkFrame(tab_widget)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=2)
        content_frame.columnconfigure(2, weight=1)
        content_frame.columnconfigure(3, weight=2)
        fields = {
            "Nome do Personagem:": 1, "Nome do Jogador:": 1,
            "Raça:": 2, "Classe Principal:": 2,
            "Sub-classe:": 3, "Nível:": 3,
            "Origem:": 4, "Divindade/Patrono:": 4,
            "Tendência (Alinhamento):": 5,
        }
        current_row = 1
        current_col = 0
        for label_text, _ in fields.items():
            label = ctk.CTkLabel(master=content_frame, text=label_text, anchor="e")
            label.grid(row=current_row, column=current_col, padx=(10,5), pady=5, sticky="e")
            entry = ctk.CTkEntry(master=content_frame, placeholder_text=label_text.replace(":", ""))
            entry.grid(row=current_row, column=current_col + 1, padx=(0,10), pady=5, sticky="ew")
            current_col += 2
            if current_col >= 4:
                current_col = 0
                current_row += 1