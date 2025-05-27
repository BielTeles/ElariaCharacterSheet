import customtkinter as ctk
from typing import List, Dict, Any, Optional, TYPE_CHECKING
import tkinter

# Supondo que Personagem e dados da loja/habilidades estão acessíveis
# from core.character import Personagem # Para type hint
from data.items_data import TODOS_ITENS_LOJA
from data.abilities_data import ABILITIES_DATA

if TYPE_CHECKING: # Evita import circular em tempo de execução, mas permite type hinting
    from ui.app_ui import AppUI
    from core.character import Personagem


class StoreAbilitiesTab:
    """
    Gerencia a aba da Loja de Itens e Habilidades, permitindo ao jogador
    comprar itens e aprender/escolher habilidades para o personagem.
    """
    personagem: 'Personagem' # Usando string para type hint para evitar import circular
    app_ui: 'AppUI'

    # --- Atributos da UI ---
    char_ef_label: ctk.CTkLabel
    char_efp_label: ctk.CTkLabel
    items_scroll_frame: ctk.CTkScrollableFrame

    char_level_label_abilities: ctk.CTkLabel
    char_class_label_abilities: ctk.CTkLabel
    char_subclass_label_abilities: ctk.CTkLabel
    abilities_scroll_frame: ctk.CTkScrollableFrame
    
    # Dicionário para gerenciar grupos de habilidades na UI
    # Estrutura: { "nome_grupo": {"frame": CTkFrame, "vars": List[CTkCheckBox], "limite": int, "opcoes_data": List[Dict]} }
    grupos_renderizados: Dict[str, Dict[str, Any]]


    def __init__(self, tab_widget: ctk.CTkTabview, personagem_atual: 'Personagem', app_ui_ref: 'AppUI'):
        self.tab_widget = tab_widget
        self.personagem = personagem_atual
        self.app_ui = app_ui_ref

        self.main_frame = ctk.CTkFrame(self.tab_widget, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True)

        self.store_tab_view = ctk.CTkTabview(self.main_frame, anchor="nw")
        self.store_tab_view.pack(fill="both", expand=True, padx=5, pady=5)

        self.items_store_tab_widget = self.store_tab_view.add("Loja de Itens")
        self.abilities_tab_widget = self.store_tab_view.add("Habilidades")
        
        self.grupos_renderizados = {} # Inicializa aqui

        self._setup_items_store_ui()
        self._setup_abilities_tab_ui()

        self.load_data_from_personagem()

    def _setup_items_store_ui(self) -> None:
        """Configura os widgets da sub-aba Loja de Itens."""
        # --- UI da Loja de Itens ---
        items_top_info_frame = ctk.CTkFrame(self.items_store_tab_widget, fg_color="transparent")
        items_top_info_frame.pack(fill="x", pady=(5,0), padx=5)
        
        ctk.CTkLabel(master=items_top_info_frame, text="Moedas:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(0,5))
        self.char_ef_label = ctk.CTkLabel(master=items_top_info_frame, text="Ef: 0")
        self.char_ef_label.pack(side="left", padx=(0,10))
        self.char_efp_label = ctk.CTkLabel(master=items_top_info_frame, text="EfP: 0")
        self.char_efp_label.pack(side="left", padx=(0,10))

        self.items_scroll_frame = ctk.CTkScrollableFrame(self.items_store_tab_widget)
        self.items_scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.items_scroll_frame.columnconfigure(0, weight=3)  # Nome
        self.items_scroll_frame.columnconfigure(1, weight=2)  # Custo
        self.items_scroll_frame.columnconfigure(2, weight=2)  # Categoria Loja
        self.items_scroll_frame.columnconfigure(3, weight=0)  # Botão Comprar
        
        headers_items = ["Item", "Custo", "Categoria"]
        for col, header_text in enumerate(headers_items):
            ctk.CTkLabel(master=self.items_scroll_frame, text=header_text, font=ctk.CTkFont(weight="bold")).grid(row=0, column=col, padx=5, pady=(5,10), sticky="w")

    def _setup_abilities_tab_ui(self) -> None:
        """Configura os widgets da sub-aba Habilidades."""
        abilities_info_frame = ctk.CTkFrame(self.abilities_tab_widget, fg_color="transparent")
        abilities_info_frame.pack(fill="x", pady=(5,0), padx=5)
        ctk.CTkLabel(master=abilities_info_frame, text="Nível:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(0,5))
        self.char_level_label_abilities = ctk.CTkLabel(master=abilities_info_frame, text="N/A")
        self.char_level_label_abilities.pack(side="left", padx=(0,10))
        ctk.CTkLabel(master=abilities_info_frame, text="Classe:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(0,5))
        self.char_class_label_abilities = ctk.CTkLabel(master=abilities_info_frame, text="N/A")
        self.char_class_label_abilities.pack(side="left", padx=(0,10))
        ctk.CTkLabel(master=abilities_info_frame, text="Subclasse:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(0,5))
        self.char_subclass_label_abilities = ctk.CTkLabel(master=abilities_info_frame, text="N/A")
        self.char_subclass_label_abilities.pack(side="left", padx=(0,10))

        self.abilities_scroll_frame = ctk.CTkScrollableFrame(self.abilities_tab_widget)
        self.abilities_scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)
        # Configuração de colunas para habilidades não agrupadas (se houver)
        # self.abilities_scroll_frame.columnconfigure(0, weight=2) 
        # self.abilities_scroll_frame.columnconfigure(1, weight=4) 
        # self.abilities_scroll_frame.columnconfigure(2, weight=1) 
        # self.abilities_scroll_frame.columnconfigure(3, weight=0)

    def update_character_currency_display(self) -> None:
        """Atualiza a exibição das moedas do personagem na aba da loja."""
        if hasattr(self, 'personagem') and self.personagem:
            self.char_ef_label.configure(text=f"Ef: {self.personagem.moedas_ef}")
            self.char_efp_label.configure(text=f"EfP: {self.personagem.moedas_efp}")

    def update_character_info_for_abilities(self) -> None:
        """Atualiza a exibição de nível, classe e subclasse na aba de habilidades."""
        if hasattr(self, 'personagem') and self.personagem:
            self.char_level_label_abilities.configure(text=str(self.personagem.nivel))
            self.char_class_label_abilities.configure(text=self.personagem.classe_principal if self.personagem.classe_principal else "Nenhuma")
            self.char_subclass_label_abilities.configure(text=self.personagem.sub_classe if self.personagem.sub_classe else "Nenhuma")

    def load_data_from_personagem(self) -> None:
        """Chamado para carregar/recarregar opções da loja e habilidades."""
        self.personagem = self.app_ui.personagem_atual # Garante que está usando a instância mais recente
        self.update_character_currency_display()
        self.update_character_info_for_abilities()
        self.populate_items_store()
        self.populate_abilities_list()

    def populate_items_store(self) -> None:
        """Popula a lista de itens na loja de itens."""
        # Limpa itens antigos, exceto cabeçalhos
        for widget in self.items_scroll_frame.winfo_children():
            if widget.grid_info().get("row", 0) > 0: 
                widget.destroy()

        current_row = 1
        for item_data in TODOS_ITENS_LOJA:
            nome_item = item_data.get("nome", "N/A")
            nome_label = ctk.CTkLabel(master=self.items_scroll_frame, text=nome_item, anchor="w", wraplength=250)
            nome_label.grid(row=current_row, column=0, padx=5, pady=3, sticky="ew")

            custo_ef = item_data.get("custo_ef", 0)
            custo_efp = item_data.get("custo_efp", 0)
            custo_str = ""
            if custo_ef > 0: custo_str += f"{custo_ef} Ef"
            if custo_efp > 0:
                if custo_str: custo_str += " "
                custo_str += f"{custo_efp} EfP"
            if not custo_str: custo_str = "Grátis"
            custo_label = ctk.CTkLabel(master=self.items_scroll_frame, text=custo_str, anchor="w")
            custo_label.grid(row=current_row, column=1, padx=5, pady=3, sticky="w")

            categoria_loja = item_data.get("categoria_loja", "N/A")
            categoria_label = ctk.CTkLabel(master=self.items_scroll_frame, text=categoria_loja, anchor="w")
            categoria_label.grid(row=current_row, column=2, padx=5, pady=3, sticky="w")

            # Usando partial para command se preferir, mas lambda funciona bem aqui
            buy_button = ctk.CTkButton(master=self.items_scroll_frame, text="Comprar", width=80,
                                       command=lambda i=item_data.copy(): self.buy_item(i)) # Passa uma cópia para buy_item
            buy_button.grid(row=current_row, column=3, padx=5, pady=3, sticky="e")
            current_row += 1
    
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
            # item_data_compra já é uma cópia do item da loja
            tipo_inv = item_data_compra.get("tipo_item_para_inventario", "item_geral")

            if tipo_inv == "arma":
                # As chaves devem ser consistentes com o que a CombatTab espera
                # Ex: 'nome', 'dano', 'atributo_chave', 'tipo_dano', 'empunhadura', 'alcance'
                self.personagem.armas_inventario.append(item_data_compra)
            elif tipo_inv == "armadura":
                # Adiciona à lista de itens gerais com detalhes relevantes
                self.personagem.itens_gerais.append({
                    "nome": item_data_compra.get("nome"), 
                    "quantity": 1, 
                    "weight": "", # Peso pode ser adicionado em items_data.py se necessário
                    "description": f"Tipo: {item_data_compra.get('tipo_armadura')}, RD: {item_data_compra.get('rd')}"
                })
                # Se quiser que a armadura comprada seja automaticamente equipada e atualize RD total:
                # self.personagem.armadura_equipada = {"nome": item_data_compra.get("nome"), "rd_fornecida": item_data_compra.get("rd",0)}
                # self.personagem.rd_total += item_data_compra.get("rd",0) # Ou lógica mais complexa
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
                    except ValueError: # Caso quantity não seja um número
                        found_item_in_inventory["quantity"] = 1 
                else:
                    self.personagem.itens_gerais.append({
                        "nome": item_data_compra.get("nome"), 
                        "quantity": 1, 
                        "weight": item_data_compra.get("peso_estimado",""), 
                        "description": item_data_compra.get("observacoes", "") # Adicionar observações se houver
                    })

            self.app_ui.show_feedback_message(f"'{item_data_compra.get('nome')}' comprado!", 2000)
            self.update_character_currency_display()
            # Notifica outras abas para recarregar dados
            self.app_ui.inventory_tab.load_data_from_personagem()
            self.app_ui.combat_tab.load_data_from_personagem() # Para atualizar armas e RD se armadura equipada mudar
        else:
            self.app_ui.show_feedback_message("Moedas insuficientes!", 2000)

    # ... (Restante da classe, incluindo populate_abilities_list, handle_ability_choice, etc.)
    # As otimizações principais para a parte de habilidades serão aplicadas abaixo.

    def populate_abilities_list(self) -> None:
        """Popula a lista de habilidades disponíveis para o personagem."""
        for widget in self.abilities_scroll_frame.winfo_children():
            widget.destroy()
        self.grupos_renderizados.clear() # Limpa dados de grupos anteriores

        classe = self.personagem.classe_principal
        subclasse = self.personagem.sub_classe
        nivel_personagem = self.personagem.nivel

        if not classe or not ABILITIES_DATA.get(classe):
            ctk.CTkLabel(master=self.abilities_scroll_frame, text="Selecione uma Classe Principal na aba 'Principal'.").pack(pady=10)
            return

        habilidades_para_renderizar: List[Dict[str, Any]] = []

        # Habilidades Base da Classe
        for ability in ABILITIES_DATA[classe].get("base", []):
            if ability.get("nivel_req", 1) <= nivel_personagem:
                habilidades_para_renderizar.append(ability)
        
        # Habilidades da Subclasse
        if subclasse and "subclasses" in ABILITIES_DATA[classe] and subclasse in ABILITIES_DATA[classe]["subclasses"]:
            for ability in ABILITIES_DATA[classe]["subclasses"][subclasse].get("habilidades", []):
                if ability.get("nivel_req", 1) <= nivel_personagem:
                    habilidades_para_renderizar.append(ability)
        
        if not habilidades_para_renderizar:
            ctk.CTkLabel(master=self.abilities_scroll_frame, text="Nenhuma habilidade disponível para esta combinação.").pack(pady=10)
            return

        # Renderiza habilidades
        for ability_data in habilidades_para_renderizar:
            grupo_escolha = ability_data.get("grupo_escolha")

            if grupo_escolha:
                if grupo_escolha not in self.grupos_renderizados:
                    limite = ability_data.get("limite_escolha", 1) # Pega o limite da primeira habilidade do grupo
                    frame_grupo = ctk.CTkFrame(self.abilities_scroll_frame, border_width=1)
                    frame_grupo.pack(fill="x", pady=(10,2), padx=2)
                    
                    nome_grupo_display = grupo_escolha.replace('_lvl1', ' (Nível 1)').replace('_', ' ').title()
                    ctk.CTkLabel(master=frame_grupo, text=f"Escolha {limite} de: {nome_grupo_display}", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=5, pady=(2,5))
                    
                    self.grupos_renderizados[grupo_escolha] = {"frame": frame_grupo, "vars": [], "limite": limite, "opcoes_data": []}
                
                var_escolha = tkinter.BooleanVar()
                habilidade_ja_escolhida = any(
                    h.get('nome') == ability_data.get('nome') and h.get('grupo_escolha_origem') == grupo_escolha 
                    for h in self.personagem.magias_habilidades
                )
                var_escolha.set(habilidade_ja_escolhida)
                
                chk = ctk.CTkCheckBox(
                    master=self.grupos_renderizados[grupo_escolha]["frame"], 
                    text=f"{ability_data.get('nome')} - {ability_data.get('descricao', '')[:60]}... (Custo: {ability_data.get('custo','N/A')})", 
                    wraplength=500,
                    justify="left"
                )
                chk.configure(
                    variable=var_escolha,
                    command=lambda v=var_escolha, ab_data=ability_data, g_nome=grupo_escolha: self.handle_ability_choice(v, ab_data, g_nome)
                )
                chk.pack(anchor="w", padx=5, pady=2)
                
                # Adiciona a referência do checkbox e sua variável aos dados do grupo
                self.grupos_renderizados[grupo_escolha]["opcoes_data"].append({
                    "checkbox": chk,
                    "var": var_escolha,
                    "ability_data": ability_data
                })
            
            else: # Habilidades não agrupadas
                frame_habilidade = ctk.CTkFrame(self.abilities_scroll_frame)
                frame_habilidade.pack(fill="x", pady=2, padx=2)
                frame_habilidade.columnconfigure(0, weight=3); frame_habilidade.columnconfigure(1, weight=5) 
                frame_habilidade.columnconfigure(2, weight=0) 

                nome_display = f"{ability_data.get('nome')}"
                if ability_data.get('nivel_req', 1) > 1:
                    nome_display += f" (Nível {ability_data.get('nivel_req')})"

                ctk.CTkLabel(master=frame_habilidade, text=nome_display, anchor="w", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(master=frame_habilidade, text=f"{ability_data.get('descricao', '')[:80]}...", anchor="w", wraplength=350, justify="left").grid(row=0, column=1, padx=5, pady=2, sticky="ew") # Aumentado wraplength
                
                habilidade_ja_adquirida = any(h.get('nome') == ability_data.get('nome') for h in self.personagem.magias_habilidades if h.get("grupo_escolha_origem") is None) # Checa apenas não-agrupadas
                
                tipos_automaticos_ou_passivos = ["Passiva de Classe", "Passiva de Arquétipo", "Passiva de Caminho", "Escolha de Subclasse"]
                status_text = ""
                
                if ability_data.get("tipo") in tipos_automaticos_ou_passivos:
                    status_text = "Automática"
                    if ability_data.get("tipo") == "Escolha de Subclasse" and not self.personagem.sub_classe:
                        status_text = "Escolha Subclasse"
                    elif not habilidade_ja_adquirida and ability_data.get("tipo") != "Escolha de Subclasse":
                         # Adiciona automaticamente se for passiva e ainda não estiver lá
                        self.learn_ability(ability_data.copy(), is_auto_learn=True)
                        habilidade_ja_adquirida = True # Atualiza status para "Adquirida"
                
                if habilidade_ja_adquirida and ability_data.get("tipo") not in tipos_automaticos_ou_passivos : # Se foi aprendida manualmente
                    status_text = "Adquirida"


                if status_text:
                    ctk.CTkLabel(master=frame_habilidade, text=status_text, text_color="gray", width=80).grid(row=0, column=2, padx=5, pady=2, sticky="e")
                elif not habilidade_ja_adquirida : # Se não é automática e não foi adquirida, mostra botão Aprender
                    btn_learn = ctk.CTkButton(master=frame_habilidade, text="Aprender", width=80,
                                              command=lambda ab=ability_data.copy(): self.learn_ability(ab)) # Passa cópia
                    btn_learn.grid(row=0, column=2, padx=5, pady=2, sticky="e")
                else: # Se é adquirida mas não automática (foi aprendida antes)
                     ctk.CTkLabel(master=frame_habilidade, text="Adquirida", text_color="gray", width=80).grid(row=0, column=2, padx=5, pady=2, sticky="e")


        # Atualizar estados dos checkboxes para cada grupo
        for nome_grupo, dados_grupo_dict in self.grupos_renderizados.items():
            self.update_checkbox_states_for_group(nome_grupo)


    def handle_ability_choice(self, bool_var: tkinter.BooleanVar, ability_data: Dict[str, Any], group_name: str) -> None:
        """Lida com a seleção/desseleção de uma habilidade de um grupo."""
        dados_grupo = self.grupos_renderizados.get(group_name)
        if not dados_grupo:
            return

        limite_do_grupo_atual = dados_grupo["limite"]
        habilidades_atuais_personagem = self.personagem.magias_habilidades
        
        if bool_var.get():  # Se está marcando
            escolhidas_neste_grupo_no_personagem = sum(
                1 for h_pers in habilidades_atuais_personagem 
                if h_pers.get("grupo_escolha_origem") == group_name
            )

            if escolhidas_neste_grupo_no_personagem < limite_do_grupo_atual:
                # Verifica se esta habilidade específica já foi adicionada deste grupo
                if not any(h.get('nome') == ability_data.get('nome') and h.get('grupo_escolha_origem') == group_name for h in habilidades_atuais_personagem):
                    ability_copy = ability_data.copy()
                    ability_copy["grupo_escolha_origem"] = group_name # Marca a origem do grupo
                    self.personagem.magias_habilidades.append(ability_copy)
                    self.app_ui.show_feedback_message(f"'{ability_data.get('nome')}' selecionada.", 1500)
            else:
                bool_var.set(False)  # Desmarca, pois o limite foi atingido
                nome_grupo_display = group_name.replace('_lvl1', ' Nível 1').replace('_', ' ').title()
                self.app_ui.show_feedback_message(f"Limite de {limite_do_grupo_atual} para '{nome_grupo_display}' atingido.", 2000)
        else:  # Se está desmarcando
            self.personagem.magias_habilidades = [
                h for h in habilidades_atuais_personagem
                if not (h.get('nome') == ability_data.get('nome') and h.get('grupo_escolha_origem') == group_name)
            ]
            self.app_ui.show_feedback_message(f"'{ability_data.get('nome')}' desmarcada.", 1500)

        # Atualiza o estado dos checkboxes apenas para este grupo
        self.update_checkbox_states_for_group(group_name)
        self.app_ui.magic_tab.load_data_from_personagem() # Atualiza a aba de magia

    def update_checkbox_states_for_group(self, group_name: str) -> None:
        """Atualiza o estado (habilitado/desabilitado) dos checkboxes em um grupo específico."""
        group_data_dict = self.grupos_renderizados.get(group_name)
        if not group_data_dict or not isinstance(group_data_dict.get("vars"), list):
            return

        # Conta quantas habilidades deste grupo estão atualmente selecionadas pelo personagem
        habilidades_atuais_personagem = self.personagem.magias_habilidades
        escolhidas_count = sum(1 for h_pers in habilidades_atuais_personagem if h_pers.get("grupo_escolha_origem") == group_name)
        limite = group_data_dict.get("limite", 1)

        for item_info in group_data_dict.get("opcoes_data", []):
            checkbox_widget = item_info.get("checkbox")
            var_atual = item_info.get("var") # A BooleanVar associada
            if isinstance(checkbox_widget, ctk.CTkCheckBox) and isinstance(var_atual, tkinter.BooleanVar):
                if escolhidas_count >= limite and not var_atual.get(): # Se limite atingido e esta não está marcada
                    checkbox_widget.configure(state="disabled")
                else:
                    checkbox_widget.configure(state="normal")

    def learn_ability(self, ability_data: Dict[str, Any], is_auto_learn: bool = False) -> None:
        """Adiciona uma habilidade individual (não de grupo) ao personagem."""
        # Verifica se a habilidade (não agrupada) já foi adicionada
        if not any(h.get('nome') == ability_data.get('nome') and h.get("grupo_escolha_origem") is None 
                   for h in self.personagem.magias_habilidades):
            
            ability_copy = ability_data.copy() # Trabalha com uma cópia
            self.personagem.magias_habilidades.append(ability_copy)
            
            if not is_auto_learn:
                self.app_ui.show_feedback_message(f"Habilidade '{ability_data.get('nome')}' aprendida!", 2000)
                # Atualiza a lista de habilidades na UI para refletir o status "Adquirida"
                self.populate_abilities_list() # Redesenha para mostrar como "Adquirida"
            
            self.app_ui.magic_tab.load_data_from_personagem() # Atualiza a aba de Magia
        elif not is_auto_learn: # Se tentou aprender manualmente algo já conhecido
            self.app_ui.show_feedback_message("Habilidade já conhecida.", 2000)