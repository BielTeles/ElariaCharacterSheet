import customtkinter as ctk
from typing import List, Dict, Any, Union, Optional, Callable, Tuple

# from core.character import Personagem # Para type hinting, se necessário

class MagicTab:
    """
    Gerencia a aba de Magia, exibindo e controlando as habilidades mágicas do personagem.
    """
    personagem: Any  # Deveria ser Personagem
    app_ui: Any  # Deveria ser AppUI
    
    # Lista para guardar os FRAMES e DADOS de cada magia na UI
    spell_ui_elements: List[Dict[str, Any]] 

    # StringVars para os campos de informação geral de magia
    pm_current_var: ctk.StringVar
    pm_max_var: ctk.StringVar
    key_magic_attr_var: ctk.StringVar
    magic_save_dc_var: ctk.StringVar
    magic_attack_bonus_var: ctk.StringVar
    magic_path_var: ctk.StringVar

    # Labels e botões para habilidades equipadas
    equipped_spells_labels: List[ctk.CTkLabel]
    equipped_spells_buttons: List[ctk.CTkButton]
    action_roll_animation_label: ctk.CTkLabel
    action_roll_result_label: ctk.CTkLabel

    def __init__(self, tab_widget: ctk.CTkFrame, personagem_atual: Any, app_ui_ref: Any):
        self.tab_widget = tab_widget
        self.personagem = personagem_atual
        self.app_ui = app_ui_ref
        
        self.spell_ui_elements = [] 

        self.pm_current_var = ctk.StringVar()
        self.pm_max_var = ctk.StringVar()
        self.key_magic_attr_var = ctk.StringVar()
        self.magic_save_dc_var = ctk.StringVar()
        self.magic_attack_bonus_var = ctk.StringVar()
        self.magic_path_var = ctk.StringVar()

        self.main_scroll = ctk.CTkScrollableFrame(self.tab_widget, fg_color="transparent")
        self.main_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Grid configuration para o frame principal
        self.main_scroll.columnconfigure(0, weight=1)
        self.main_scroll.columnconfigure(1, weight=1)

        # Seções da UI
        self.setup_magic_overview_section()  # Visão geral das magias
        self.setup_equipped_spells_section()  # Magias equipadas
        self.setup_spell_result_section()  # Área de resultado das rolagens
        
        self.load_data_from_personagem()

    def load_data_from_personagem(self) -> None:
        """Carrega dados do objeto Personagem para a UI da aba de Magia."""
        # Atualizar valor da perícia Elemental
        self.elemental_val_var.set(str(self.personagem.pericias_valores.get("Elemental", 0)))
        
        # Atualizar magias equipadas
        self._update_equipped_spells_display()

    def _update_personagem_magic_attr(self, attr_name_in_personagem: str,
                                      string_var: ctk.StringVar, is_int: bool = False) -> None:
        """Atualiza um atributo de magia no objeto Personagem."""
        value_str = string_var.get()
        value_to_set: Union[str, int] = value_str
        current_model_value = getattr(self.personagem, attr_name_in_personagem, 0 if is_int else "")

        if is_int:
            try:
                value_to_set = int(value_str) if value_str.strip() else 0
            except ValueError:
                string_var.set(str(current_model_value)) # Reverte na UI
                return
        
        if str(current_model_value) != str(value_to_set):
            setattr(self.personagem, attr_name_in_personagem, value_to_set)
            # Se a mudança aqui (ex: atributo_chave_magia) afetar pm_maximo,
            # self.personagem.recalcular_maximos() deve ser chamado,
            # e a AppUI deve coordenar a atualização de pm_max_var aqui.
            if attr_name_in_personagem == 'atributo_chave_magia':
                self.personagem.recalcular_maximos()
                self.pm_max_var.set(str(self.personagem.pm_maximo))

    def setup_magic_overview_section(self) -> None:
        """Configura a seção de visão geral das magias."""
        overview_frame = ctk.CTkFrame(self.main_scroll)
        overview_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        
        # Título da seção
        title_frame = ctk.CTkFrame(overview_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=5, pady=(5,0))
        ctk.CTkLabel(title_frame, text="Visão Geral das Magias", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
        
        # Container para os valores principais
        values_frame = ctk.CTkFrame(overview_frame, fg_color="transparent")
        values_frame.pack(fill="x", padx=10, pady=5)
        
        # Primeira linha - Valores principais
        main_values_frame = ctk.CTkFrame(values_frame, fg_color="transparent")
        main_values_frame.pack(fill="x", pady=(0,5))
        
        # Perícia Elemental com ícone
        magic_frame = ctk.CTkFrame(main_values_frame, fg_color="#2B2B2B")
        magic_frame.pack(side="left", padx=5, fill="both")
        ctk.CTkLabel(magic_frame, text="✨", font=ctk.CTkFont(size=20)).pack(side="left", padx=5)
        ctk.CTkLabel(magic_frame, text="Elemental", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=2)
        
        # Criar StringVar para o valor da perícia Elemental
        self.elemental_val_var = ctk.StringVar()
        
        self.elemental_val_entry = ctk.CTkEntry(magic_frame, width=50, justify="center", 
                                               textvariable=self.elemental_val_var,
                                               state="readonly",  # Torna o entry somente leitura
                                               fg_color="#1a1a1a")  # Cor de fundo mais escura para indicar read-only
        self.elemental_val_entry.pack(side="left", padx=5, pady=5)

    def _on_elemental_value_change(self) -> None:
        """Manipula mudanças no valor da perícia Elemental."""
        try:
            new_val = int(self.elemental_val_var.get())
            if new_val < 0:
                new_val = 0
                self.elemental_val_var.set("0")
            
            # Atualiza o personagem
            if self.personagem.pericias_valores.get("Elemental") != new_val:
                self.personagem.atualizar_pericia_valor("Elemental", new_val)
                
                # Atualiza a aba de Atributos & Perícias
                if hasattr(self.app_ui, 'attributes_skills_tab'):
                    self.app_ui.attributes_skills_tab.load_data_from_personagem()
                
        except ValueError:
            # Reverte para o valor anterior em caso de entrada inválida
            self.elemental_val_var.set(str(self.personagem.pericias_valores.get("Elemental", 0)))

    def setup_equipped_spells_section(self) -> None:
        """Configura a seção de magias equipadas."""
        equipped_frame = ctk.CTkFrame(self.main_scroll)
        equipped_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        
        # Título da seção
        title_frame = ctk.CTkFrame(equipped_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=5, pady=(5,0))
        ctk.CTkLabel(title_frame, text="✨ Magias Equipadas", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
        
        # Container para as magias
        spells_frame = ctk.CTkFrame(equipped_frame, fg_color="transparent")
        spells_frame.pack(fill="x", padx=10, pady=5)
        
        # Lista para armazenar referências dos widgets de magias equipadas
        self.equipped_spells_labels = []
        self.equipped_spells_buttons = []
        
        # Criar slots para magias equipadas (exemplo com 4 slots)
        for i in range(4):
            spell_frame = ctk.CTkFrame(spells_frame, fg_color="#2B2B2B")
            spell_frame.pack(fill="x", pady=(0,5))
            
            # Cabeçalho do slot
            header = ctk.CTkFrame(spell_frame, fg_color="transparent")
            header.pack(fill="x", padx=5, pady=2)
            ctk.CTkLabel(header, text="✨", font=ctk.CTkFont(size=20)).pack(side="left", padx=2)
            ctk.CTkLabel(header, text=f"Slot {i+1}", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
            
            # Informações da magia
            info = ctk.CTkFrame(spell_frame, fg_color="transparent")
            info.pack(fill="x", padx=5, pady=2)
            
            name_label = ctk.CTkLabel(info, text="---", anchor="w")
            name_label.pack(side="left", padx=5, fill="x", expand=True)
            self.equipped_spells_labels.append(name_label)
            
            # Botões de ação
            actions = ctk.CTkFrame(spell_frame, fg_color="transparent")
            actions.pack(fill="x", padx=5, pady=2)
            
            unequip_btn = ctk.CTkButton(actions, text="❌ Desequipar", width=80, state="disabled",
                                      command=lambda idx=i: self.unequip_spell(idx))
            unequip_btn.pack(side="right", padx=2)
            
            cast_btn = ctk.CTkButton(actions, text="✨ Lançar", width=80, state="disabled",
                                   command=lambda idx=i: self.cast_spell(idx))
            cast_btn.pack(side="right", padx=2)
            
            self.equipped_spells_buttons.extend([cast_btn, unequip_btn])

    def setup_spell_result_section(self) -> None:
        """Configura a área de resultado das rolagens de magia."""
        result_frame = ctk.CTkFrame(self.main_scroll)
        result_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        
        # Título da seção
        ctk.CTkLabel(result_frame, text="🎲", font=ctk.CTkFont(size=20)).pack(side="left", padx=5)
        ctk.CTkLabel(result_frame, text="Resultado", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        
        # Labels para animação e resultado
        self.action_roll_animation_label = ctk.CTkLabel(result_frame, text="", width=100,
                                                       font=ctk.CTkFont(size=20, weight="bold"))
        self.action_roll_animation_label.pack(side="left", padx=5)
        
        self.action_roll_result_label = ctk.CTkLabel(result_frame, text="", anchor="w", wraplength=440)
        self.action_roll_result_label.pack(side="left", fill="x", expand=True, padx=5)

    def cast_spell(self, slot_index: int) -> None:
        """Lança a magia equipada no slot especificado."""
        if hasattr(self.personagem, 'magias_habilidades') and isinstance(self.personagem.magias_habilidades, list):
            if 0 <= slot_index < len(self.personagem.magias_habilidades):
                magia = self.personagem.magias_habilidades[slot_index]
                # TODO: Implementar a lógica de lançamento de magia
                self.action_roll_animation_label.configure(text="🎲")
                self.action_roll_result_label.configure(text=f"Lançando {magia.get('nome', '---')}...")

    def _update_equipped_spells_display(self) -> None:
        """Atualiza os labels e botões na UI para as magias equipadas."""
        # Limpar todos os labels
        for label in self.equipped_spells_labels:
            label.configure(text="---")
        
        # Desabilitar todos os botões
        for button in self.equipped_spells_buttons:
            button.configure(state="disabled")
        
        # Atualizar com as magias equipadas do personagem
        if hasattr(self.personagem, 'magias_habilidades') and isinstance(self.personagem.magias_habilidades, list):
            for i, magia in enumerate(self.personagem.magias_habilidades[:4]):  # Limita a 4 magias
                if i < len(self.equipped_spells_labels):
                    # Atualiza o nome da magia
                    self.equipped_spells_labels[i].configure(text=magia.get('nome', '---'))
                    
                    # Habilita os botões correspondentes
                    cast_btn_idx = i * 2  # Cada slot tem 2 botões
                    unequip_btn_idx = cast_btn_idx + 1
                    
                    if cast_btn_idx < len(self.equipped_spells_buttons):
                        self.equipped_spells_buttons[cast_btn_idx].configure(state="normal")
                    if unequip_btn_idx < len(self.equipped_spells_buttons):
                        self.equipped_spells_buttons[unequip_btn_idx].configure(state="normal")

    def unequip_spell(self, slot_index: int) -> None:
        """Remove uma magia equipada do slot especificado."""
        if hasattr(self.personagem, 'magias_habilidades') and isinstance(self.personagem.magias_habilidades, list):
            if 0 <= slot_index < len(self.personagem.magias_habilidades):
                self.personagem.magias_habilidades.pop(slot_index)
                self._update_equipped_spells_display()
                self.app_ui.show_feedback_message("Magia desequipada com sucesso!", 1500)

    def _update_equipped_spells_display(self) -> None:
        """Atualiza os labels e botões na UI para as magias equipadas."""
        # TODO: Implementar quando tivermos o sistema de magias
        pass