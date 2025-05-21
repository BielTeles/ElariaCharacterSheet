import customtkinter as ctk

class CombatTab:
    def __init__(self, tab_widget):
        self.tab_widget = tab_widget

        # --- Frame Principal para a Aba ---
        self.main_frame = ctk.CTkFrame(self.tab_widget)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        # Configurar colunas do frame principal da aba de combate
        self.main_frame.columnconfigure(0, weight=1) # Coluna para Defesa/Ataque
        self.main_frame.columnconfigure(1, weight=1) # (Espaço para futura coluna, ex: manobras)
        self.main_frame.rowconfigure(2, weight=1) # Linha para a lista de armas (para expandir)


        # --- Seção de Estatísticas de Defesa ---
        self.setup_defense_stats_section()

        # --- Seção de Estatísticas de Ataque ---
        self.setup_attack_stats_section()
        
        # --- Seção de Armas ---
        self.setup_weapons_section()
        
        # --- Seção de Armadura e Escudo ---
        self.setup_armor_shield_section()

    def create_stat_entry(self, parent, row, label_text, placeholder="0"):
        """Helper para criar um label e um entry para estatísticas."""
        label = ctk.CTkLabel(master=parent, text=label_text)
        label.grid(row=row, column=0, padx=5, pady=5, sticky="w")
        entry = ctk.CTkEntry(master=parent, placeholder_text=placeholder, width=80)
        entry.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
        return entry

    def setup_defense_stats_section(self):
        defense_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        defense_frame.grid(row=0, column=0, padx=5, pady=(0,10), sticky="new")
        defense_frame.columnconfigure(1, weight=1) # Para expandir o entry

        title_defense_label = ctk.CTkLabel(master=defense_frame, text="Defesa", font=ctk.CTkFont(size=16, weight="bold"))
        title_defense_label.grid(row=0, column=0, columnspan=2, padx=5, pady=(0,5), sticky="n")

        self.rd_total_entry = self.create_stat_entry(defense_frame, 1, "RD Total:")
        self.esquiva_val_entry = self.create_stat_entry(defense_frame, 2, "Esquiva (Valor):")
        self.bloqueio_val_entry = self.create_stat_entry(defense_frame, 3, "Bloqueio (Valor):")
        # Adicionar CA (Classe de Armadura) se seu sistema usar, ou outros status defensivos

    def setup_attack_stats_section(self):
        attack_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        attack_frame.grid(row=0, column=1, padx=5, pady=(0,10), sticky="new") # Colocado na segunda coluna
        attack_frame.columnconfigure(1, weight=1) # Para expandir o entry

        title_attack_label = ctk.CTkLabel(master=attack_frame, text="Ataque", font=ctk.CTkFont(size=16, weight="bold"))
        title_attack_label.grid(row=0, column=0, columnspan=2, padx=5, pady=(0,5), sticky="n")

        self.iniciativa_entry = self.create_stat_entry(attack_frame, 1, "Iniciativa (Valor):")
        self.cac_val_entry = self.create_stat_entry(attack_frame, 2, "Corpo-a-Corpo (Valor):") # Valor da Perícia de Ataque
        self.pontaria_val_entry = self.create_stat_entry(attack_frame, 3, "Pontaria (Valor):") # Valor da Perícia de Ataque
        self.elemental_val_entry = self.create_stat_entry(attack_frame, 4, "Elemental (Valor):") # Valor da Perícia de Ataque


    def setup_armor_shield_section(self):
        armor_shield_frame = ctk.CTkFrame(self.main_frame)
        armor_shield_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=10, sticky="new")
        armor_shield_frame.columnconfigure(1, weight=1)
        armor_shield_frame.columnconfigure(3, weight=1)

        title_armor_label = ctk.CTkLabel(master=armor_shield_frame, text="Equipamento Defensivo", font=ctk.CTkFont(size=16, weight="bold"))
        title_armor_label.grid(row=0, column=0, columnspan=4, padx=5, pady=(0,10), sticky="n")

        # Armadura
        armor_name_label = ctk.CTkLabel(master=armor_shield_frame, text="Armadura:")
        armor_name_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.armor_name_entry = ctk.CTkEntry(master=armor_shield_frame, placeholder_text="Nome da Armadura")
        self.armor_name_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        armor_rd_label = ctk.CTkLabel(master=armor_shield_frame, text="RD Fornecida:")
        armor_rd_label.grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.armor_rd_entry = ctk.CTkEntry(master=armor_shield_frame, placeholder_text="RD", width=50)
        self.armor_rd_entry.grid(row=1, column=3, padx=5, pady=5, sticky="w") # sticky w para não expandir muito

        # Escudo
        shield_name_label = ctk.CTkLabel(master=armor_shield_frame, text="Escudo:")
        shield_name_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.shield_name_entry = ctk.CTkEntry(master=armor_shield_frame, placeholder_text="Nome do Escudo")
        self.shield_name_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        # O livro não especifica RD de escudo, mas foca na perícia Bloqueio.
        # Pode-se adicionar um campo para "RD Adicional do Escudo" ou "Notas do Escudo" se desejado.
        shield_notes_label = ctk.CTkLabel(master=armor_shield_frame, text="Notas Escudo:")
        shield_notes_label.grid(row=2, column=2, padx=5, pady=5, sticky="w")
        self.shield_notes_entry = ctk.CTkEntry(master=armor_shield_frame, placeholder_text="Ex: +1 Bloqueio")
        self.shield_notes_entry.grid(row=2, column=3, padx=5, pady=5, sticky="ew")


    def setup_weapons_section(self):
        weapons_main_frame = ctk.CTkFrame(self.main_frame)
        weapons_main_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=10, sticky="nsew")
        weapons_main_frame.rowconfigure(1, weight=1) # Para o scrollable frame expandir

        title_weapons_label = ctk.CTkLabel(master=weapons_main_frame, text="Armas", font=ctk.CTkFont(size=16, weight="bold"))
        title_weapons_label.pack(pady=(0,5))

        # Frame rolável para a lista de armas
        self.weapons_scroll_frame = ctk.CTkScrollableFrame(weapons_main_frame, height=150) # Altura inicial
        self.weapons_scroll_frame.pack(fill="x", expand=True)

        # Configurar colunas para a lista de armas
        self.weapons_scroll_frame.columnconfigure(0, weight=2) # Nome
        self.weapons_scroll_frame.columnconfigure(1, weight=1) # Dano
        self.weapons_scroll_frame.columnconfigure(2, weight=1) # Atributo Vant.
        self.weapons_scroll_frame.columnconfigure(3, weight=1) # Tipo
        self.weapons_scroll_frame.columnconfigure(4, weight=1) # Empunhadura
        self.weapons_scroll_frame.columnconfigure(5, weight=1) # Alcance
        self.weapons_scroll_frame.columnconfigure(6, weight=1) # Valor Ataque Arma

        # Cabeçalhos da lista de armas
        headers = ["Nome", "Dano", "Atrib. Vant.", "Tipo", "Empunh.", "Alcance", "Val. Ataque"]
        for col, header_text in enumerate(headers):
            header_label = ctk.CTkLabel(master=self.weapons_scroll_frame, text=header_text, font=ctk.CTkFont(weight="bold"))
            header_label.grid(row=0, column=col, padx=5, pady=5, sticky="w")

        # Exemplo de como adicionar uma arma (futuramente isso será dinâmico)
        self.add_weapon_entry_row(
            name="Adaga Exemplo", damage="1d4", key_attr="DES", type_w="Perf./Corte",
            hands="1 Mão", range_w="Corpo", attack_val="Perícia"
        )
        self.add_weapon_entry_row() # Linha vazia para nova arma

        # Botão para adicionar mais armas
        add_weapon_button = ctk.CTkButton(master=weapons_main_frame, text="Adicionar Arma", command=self.add_weapon_entry_row)
        add_weapon_button.pack(pady=5)

    def add_weapon_entry_row(self, name="", damage="", key_attr="", type_w="", hands="", range_w="", attack_val=""):
        # Determina a próxima linha disponível no grid do weapons_scroll_frame
        # Simplesmente contando os widgets filhos pode ser uma abordagem,
        # mas é melhor ter um contador de linhas se as remoções forem complexas.
        # Por agora, vamos pegar o número atual de linhas configuradas pelos cabeçalhos.
        # Cada arma ocupa uma linha.
        # len(self.weapons_scroll_frame.winfo_children()) // num_cols_per_weapon_row ... é complexo.
        # Vamos usar um atributo de instância para rastrear a próxima linha de arma.
        if not hasattr(self, 'weapon_current_row'):
            self.weapon_current_row = 1 # Começa após os cabeçalhos

        row_widgets = []
        placeholders = ["Nome Arma", "Dano", "Atrib.", "Tipo", "Empunh.", "Alcance", "Valor"]
        initial_values = [name, damage, key_attr, type_w, hands, range_w, attack_val]

        for col in range(7): # 7 colunas para armas
            entry = ctk.CTkEntry(master=self.weapons_scroll_frame, placeholder_text=placeholders[col])
            entry.insert(0, initial_values[col])
            entry.grid(row=self.weapon_current_row, column=col, padx=2, pady=2, sticky="ew")
            row_widgets.append(entry)
        
        # Você pode querer guardar 'row_widgets' em uma lista para poder deletar linhas depois
        self.weapon_current_row += 1