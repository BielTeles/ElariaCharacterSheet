import customtkinter as ctk
from typing import List, Dict, Any, Union, Optional, Callable

# from core.character import Personagem # Para type hinting, se necessário

class MagicTab:
    """
    Gerencia a aba de Magia, exibindo informações mágicas,
    listando magias/habilidades e permitindo sua adição/remoção.
    """
    personagem: Any  # Idealmente: Personagem
    
    # Lista para guardar os FRAMES e DADOS de cada magia na UI
    spell_ui_elements: List[Dict[str, Any]] 

    # StringVars para os campos de informação geral de magia
    pm_current_var: ctk.StringVar
    pm_max_var: ctk.StringVar
    key_magic_attr_var: ctk.StringVar
    magic_save_dc_var: ctk.StringVar
    magic_attack_bonus_var: ctk.StringVar
    magic_path_var: ctk.StringVar

    spells_scroll_frame: ctk.CTkScrollableFrame

    def __init__(self, tab_widget: ctk.CTkFrame, personagem_atual: Any):
        self.tab_widget = tab_widget
        self.personagem = personagem_atual
        
        self.spell_ui_elements = [] 

        self.pm_current_var = ctk.StringVar()
        self.pm_max_var = ctk.StringVar()
        self.key_magic_attr_var = ctk.StringVar()
        self.magic_save_dc_var = ctk.StringVar()
        self.magic_attack_bonus_var = ctk.StringVar()
        self.magic_path_var = ctk.StringVar()

        self.main_frame = ctk.CTkFrame(self.tab_widget, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True)
        self.main_frame.columnconfigure(0, weight=1) 
        self.main_frame.columnconfigure(1, weight=2) 
        self.main_frame.rowconfigure(1, weight=1) # Para a lista de magias expandir    

        self.setup_magic_info_section()
        self.setup_spells_list_section()
        
        self.load_data_from_personagem()

    def load_data_from_personagem(self) -> None:
        """Carrega/Recarrega dados do self.personagem para os campos da UI desta aba."""
        self.pm_current_var.set(str(self.personagem.pm_atuais))
        self.pm_max_var.set(str(self.personagem.pm_maximo))
        self.key_magic_attr_var.set(str(self.personagem.atributo_chave_magia))
        self.magic_save_dc_var.set(str(self.personagem.cd_teste_resistencia_magia))
        self.magic_attack_bonus_var.set(str(self.personagem.bonus_ataque_magico))
        self.magic_path_var.set(str(self.personagem.caminho_especializacao_magica))

        # Limpar magias existentes na UI
        for spell_element in self.spell_ui_elements:
            frame = spell_element.get('frame')
            if isinstance(frame, ctk.CTkFrame):
                frame.destroy()
        self.spell_ui_elements.clear()

        # Repopular a lista de magias da UI a partir do personagem
        if hasattr(self.personagem, 'magias_habilidades') and isinstance(self.personagem.magias_habilidades, list):
            for spell_data_dict_from_char in self.personagem.magias_habilidades:
                # Passa a referência do dicionário de dados do personagem
                self.add_spell_entry_ui(initial_spell_data=spell_data_dict_from_char, is_loading=True)

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


    def setup_magic_info_section(self) -> None:
        """Configura a seção de informações mágicas gerais na UI."""
        info_frame = ctk.CTkFrame(self.main_frame)
        info_frame.grid(row=0, column=0, padx=10, pady=10, sticky="new")
        info_frame.columnconfigure(1, weight=1)
        title_info_label = ctk.CTkLabel(master=info_frame, text="Recursos Mágicos", font=ctk.CTkFont(size=16, weight="bold"))
        title_info_label.grid(row=0, column=0, columnspan=2, padx=5, pady=(5,10), sticky="n")
        
        # PM
        pm_label = ctk.CTkLabel(master=info_frame, text="Pontos de Mana (PM):")
        pm_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        pm_sub_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        pm_sub_frame.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        pm_current_entry = ctk.CTkEntry(master=pm_sub_frame, placeholder_text="Atual", width=60, textvariable=self.pm_current_var)
        pm_current_entry.pack(side="left", padx=(0,2))
        self.pm_current_var.trace_add("write", lambda n,i,m, attr='pm_atuais', sv=self.pm_current_var : self._update_personagem_magic_attr(attr, sv, is_int=True))
        ctk.CTkLabel(master=pm_sub_frame, text="/").pack(side="left", padx=2)
        pm_max_display_label = ctk.CTkLabel(master=pm_sub_frame, textvariable=self.pm_max_var, width=60) # Apenas display
        pm_max_display_label.pack(side="left", padx=(2,0))

        # Outros campos de informação
        fields_info: List[Tuple[str, ctk.StringVar, str, bool]] = [
            ("Atributo Chave Magia:", self.key_magic_attr_var, 'atributo_chave_magia', False),
            ("CD Teste Resist. Magia:", self.magic_save_dc_var, 'cd_teste_resistencia_magia', True),
            ("Bônus Ataque Mágico:", self.magic_attack_bonus_var, 'bonus_ataque_magico', False), # Pode ser string como "+X"
            ("Caminho/Especialização:", self.magic_path_var, 'caminho_especializacao_magica', False)
        ]
        for i, (text, var, attr_name, is_int_val) in enumerate(fields_info):
            label = ctk.CTkLabel(master=info_frame, text=text)
            label.grid(row=i+2, column=0, padx=5, pady=5, sticky="w")
            entry = ctk.CTkEntry(master=info_frame, textvariable=var)
            entry.grid(row=i+2, column=1, padx=5, pady=5, sticky="ew")
            var.trace_add("write", lambda n,idx,mode, attr=attr_name, sv=var, is_i=is_int_val: self._update_personagem_magic_attr(attr, sv, is_i))

    def setup_spells_list_section(self) -> None:
        """Configura a seção para listar e adicionar magias/habilidades."""
        spells_list_main_frame = ctk.CTkFrame(self.main_frame)
        spells_list_main_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")
        spells_list_main_frame.rowconfigure(1, weight=1) # ScrollFrame expande
        spells_list_main_frame.columnconfigure(0, weight=1)


        title_spells_label = ctk.CTkLabel(master=spells_list_main_frame, text="Magias e Habilidades", font=ctk.CTkFont(size=16, weight="bold"))
        title_spells_label.pack(pady=(5,10)) # Centralizado por padrão com pack

        self.spells_scroll_frame = ctk.CTkScrollableFrame(spells_list_main_frame, label_text="")
        self.spells_scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)

        add_spell_button = ctk.CTkButton(master=spells_list_main_frame, text="Adicionar Magia/Habilidade Manualmente",
                                         command=lambda: self.add_spell_entry_ui())
        add_spell_button.pack(pady=10)
        
    def _on_spell_data_change(self, spell_data_dict_ref: Dict[str, Any], key: str,
                                widget_or_var: Union[ctk.StringVar, ctk.CTkTextbox],
                                is_new_entry: bool = False) -> None:
        """
        Atualiza o dicionário de dados da magia/habilidade no modelo do personagem.
        Se for uma nova entrada e o nome for preenchido, adiciona ao modelo.
        """
        new_value: str
        if isinstance(widget_or_var, ctk.StringVar):
            new_value = widget_or_var.get()
        elif isinstance(widget_or_var, ctk.CTkTextbox):
            new_value = widget_or_var.get("0.0", "end-1c")
        else:
            return # Tipo de widget não esperado

        # Se é uma nova entrada (não carregada) e o nome está sendo preenchido pela primeira vez
        if is_new_entry and key == 'name' and new_value.strip() and \
           spell_data_dict_ref not in self.personagem.magias_habilidades:
            self.personagem.magias_habilidades.append(spell_data_dict_ref)
            # Uma vez adicionado, não é mais 'is_new_entry' para este callback específico
            # (a flag 'is_new_entry' é ligada à criação da linha da UI, não ao estado do objeto)
        
        if spell_data_dict_ref.get(key) != new_value:
            spell_data_dict_ref[key] = new_value
        # print(f"Magia '{spell_data_dict_ref.get('name')}': campo '{key}' -> '{new_value}'") # Debug

    def add_spell_entry_ui(self, initial_spell_data: Optional[Dict[str, Any]] = None, is_loading: bool = False) -> None:
        """
        Adiciona uma entrada de magia/habilidade à UI.
        Se 'initial_spell_data' é fornecido (is_loading=True), usa essa referência do modelo.
        Caso contrário, cria um novo dicionário para uma nova entrada.
        """
        spell_data_dict_ref: Dict[str, Any]
        is_new_ui_entry = False # Flag para o callback _on_spell_data_change

        if is_loading and initial_spell_data is not None:
            spell_data_dict_ref = initial_spell_data # Usa a referência direta do modelo
        else:
            spell_data_dict_ref = {'name': "", 'mp_cost': "", 'cast_time': "", 
                                   'range_dur': "", 'target_effect': ""}
            is_new_ui_entry = True # Esta é uma nova linha criada pelo botão "Adicionar"

        spell_frame = ctk.CTkFrame(self.spells_scroll_frame, border_width=1)
        spell_frame.pack(fill="x", pady=5, padx=5)
        spell_frame.columnconfigure(1, weight=1)
        
        # Armazena o frame e a referência aos dados para facilitar a remoção
        self.spell_ui_elements.append({'frame': spell_frame, 'data_dict_ref': spell_data_dict_ref})

        # Campos para a magia/habilidade
        # (label_text, attr_key, grid_row, is_textbox, height_if_textbox)
        fields_map: List[Tuple[str, str, int, bool, int]] = [
            ("Nome:", 'name', 0, False, 0),
            ("Custo PM:", 'mp_cost', 1, False, 0),
            ("Tempo Uso:", 'cast_time', 2, False, 0),
            ("Alcance/Duração:", 'range_dur', 3, False, 0),
            ("Alvo/Efeito (Resumo):", 'target_effect', 4, True, 60)
        ]
        
        remove_button = ctk.CTkButton(master=spell_frame, text="X", width=25, height=25,
                                      command=lambda sf=spell_frame, sd_ref=spell_data_dict_ref: self.remove_spell_ui(sf, sd_ref))
        remove_button.grid(row=0, column=2, padx=5, pady=(5,0), sticky="ne") # Colocado na primeira linha, coluna 2

        for label_text, attr_key, grid_row, is_textbox, height in fields_map:
            label = ctk.CTkLabel(master=spell_frame, text=label_text)
            label.grid(row=grid_row, column=0, padx=5, pady=2, sticky="nw")

            current_value = str(spell_data_dict_ref.get(attr_key, ""))

            if is_textbox:
                widget = ctk.CTkTextbox(master=spell_frame, height=height if height else 60, wrap="word")
                widget.insert("0.0", current_value)
                # Passa is_new_ui_entry para o callback do nome
                is_name_field = (attr_key == 'name')
                widget.bind("<KeyRelease>", 
                            lambda event, s_data=spell_data_dict_ref, k=attr_key, txt_w=widget, new=is_new_ui_entry and is_name_field:
                            self._on_spell_data_change(s_data, k, txt_w, new))
            else:
                var = ctk.StringVar(value=current_value)
                widget = ctk.CTkEntry(master=spell_frame, placeholder_text=label_text.replace(":", ""), textvariable=var)
                is_name_field = (attr_key == 'name')
                var.trace_add("write", 
                              lambda n,i,m, s_data=spell_data_dict_ref, k=attr_key, v=var, new=is_new_ui_entry and is_name_field:
                              self._on_spell_data_change(s_data, k, v, new))
            
            widget.grid(row=grid_row, column=1, padx=5, pady=2, sticky="ew")


    def remove_spell_ui(self, spell_frame_to_remove: ctk.CTkFrame, spell_data_to_remove: Dict[str, Any]) -> None:
        """Remove uma magia/habilidade da UI e do modelo do personagem."""
        spell_frame_to_remove.destroy()
        
        element_to_remove_from_ui_list: Optional[Dict[str, Any]] = None
        for spell_el in self.spell_ui_elements:
            if spell_el.get('frame') == spell_frame_to_remove:
                element_to_remove_from_ui_list = spell_el
                break
        if element_to_remove_from_ui_list:
            self.spell_ui_elements.remove(element_to_remove_from_ui_list)

        if hasattr(self.personagem, 'magias_habilidades') and spell_data_to_remove in self.personagem.magias_habilidades:
            self.personagem.magias_habilidades.remove(spell_data_to_remove)
        # print(f"Magias no personagem após remover: {len(self.personagem.magias_habilidades)}") # Debug