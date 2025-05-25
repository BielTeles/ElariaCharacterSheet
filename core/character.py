# core/character.py
import json
from typing import Dict, Any, Set, List, Optional, Union

# Constantes para nomes de atributos (opcional, mas bom para evitar typos)
FORCA = "Força"
DESTREZA = "Destreza"
CONSTITUICAO = "Constituição"
INTELIGENCIA = "Inteligência"
SABEDORIA = "Sabedoria"
CARISMA = "Carisma"

# Constantes para nomes de classes (exemplo)
CLASSE_EVOCADOR = "Evocador"
CLASSE_TITA = "Titã"
CLASSE_SENTINELA = "Sentinela"
CLASSE_ELO = "Elo"


class Personagem:
    """
    Representa a ficha de um personagem no sistema Elaria RPG.
    Armazena todos os atributos, perícias, itens, magias e outras
    informações relevantes do personagem.
    """
    nome_personagem: str
    nome_jogador: str
    raca: str
    classe_principal: str
    sub_classe: str
    nivel: int
    origem: str
    divindade_patrono: str
    tendencia: str

    atributos: Dict[str, int]

    _pv_atuais: int
    _pm_atuais: int
    _vigor_atuais: int

    # Atributos internos para armazenar os máximos calculados SEM bônus raciais
    _pv_maximo_base_calculado: int
    _pm_maximo_base_calculado: int
    _vigor_maximo_calculado: int # Vigor não costuma ter bônus racial direto no máximo

    pericias_valores: Dict[str, int]
    pericias_treinadas: Set[str]

    rd_total: int
    armadura_equipada: Dict[str, Union[str, int]]
    escudo_equipado: Dict[str, str]

    armas_inventario: List[Dict[str, Any]]
    arma_equipada_principal: Optional[Dict[str, Any]]
    arma_equipada_secundaria: Optional[Dict[str, Any]]

    atributo_chave_magia: str
    cd_teste_resistencia_magia: int
    bonus_ataque_magico: str  # Idealmente int, mas mantido como str por ora devido à UI
    caminho_especializacao_magica: str
    magias_habilidades: List[Dict[str, Any]]

    moedas_ef: int
    moedas_efp: int
    itens_gerais: List[Dict[str, Any]]
    limite_carga_status: str
    notas: str

    _loaded_once: bool # Flag temporário para lógica de inicialização de PV/PM/Vigor

    def __init__(self) -> None:
        self.nome_personagem = ""
        self.nome_jogador = ""
        self.raca = ""
        self.classe_principal = ""
        self.sub_classe = ""
        self.nivel = 1
        self.origem = ""
        self.divindade_patrono = ""
        self.tendencia = ""

        self.atributos = {
            FORCA: 0, DESTREZA: 0, CONSTITUICAO: 0,
            INTELIGENCIA: 0, SABEDORIA: 0, CARISMA: 0
        }

        self._pv_maximo_base_calculado = 0
        self._pm_maximo_base_calculado = 0
        self._vigor_maximo_calculado = 0

        self._pv_atuais = 0
        self._pm_atuais = 0
        self._vigor_atuais = 0

        self.pericias_valores = {}
        self.pericias_treinadas = set()

        self.rd_total = 0
        self.armadura_equipada = {"nome": "", "rd_fornecida": 0}
        self.escudo_equipado = {"nome": "", "notas": ""}

        self.armas_inventario = []
        self.arma_equipada_principal = None
        self.arma_equipada_secundaria = None

        self.atributo_chave_magia = ""
        self.cd_teste_resistencia_magia = 0
        self.bonus_ataque_magico = "0" # UI pode precisar de string, mas int é melhor para modelo
        self.caminho_especializacao_magica = ""
        self.magias_habilidades = []

        self.moedas_ef = 0
        self.moedas_efp = 0
        self.itens_gerais = []
        self.limite_carga_status = "Normal"
        self.notas = ""

        self._loaded_once = False # Inicializa o flag
        self.recalcular_maximos()

    @property
    def pv_maximo(self) -> int:
        """Calcula os Pontos de Vida máximos, incluindo bônus raciais."""
        bonus_racial_pv = 0
        if self.raca == "Roknar": #
            # Exemplo: Roknar ganha 3 PV + 1 por nível após o 1º.
            bonus_racial_pv = 3 + (max(0, self.nivel - 1) * 1)
        return self._pv_maximo_base_calculado + bonus_racial_pv

    @property
    def pv_atuais(self) -> int:
        """Obtém os Pontos de Vida atuais."""
        return self._pv_atuais

    @pv_atuais.setter
    def pv_atuais(self, valor: int) -> None:
        """Define os Pontos de Vida atuais, com validação."""
        pv_max = self.pv_maximo # Usa a property que já tem bônus racial
        if valor > pv_max:
            self._pv_atuais = pv_max
        elif valor < 0:
            self._pv_atuais = 0
        else:
            self._pv_atuais = valor

    @property
    def pm_maximo(self) -> int:
        """Calcula os Pontos de Mana máximos, incluindo bônus raciais."""
        bonus_racial_pm = 0
        if self.raca == "Alari": #
             # Exemplo: Alari ganha +1 PM por nível.
            bonus_racial_pm = self.nivel * 1
        return self._pm_maximo_base_calculado + bonus_racial_pm

    @property
    def pm_atuais(self) -> int:
        """Obtém os Pontos de Mana atuais."""
        return self._pm_atuais

    @pm_atuais.setter
    def pm_atuais(self, valor: int) -> None:
        """Define os Pontos de Mana atuais, com validação."""
        pm_max = self.pm_maximo # Usa a property
        if valor > pm_max:
            self._pm_atuais = pm_max
        elif valor < 0:
            self._pm_atuais = 0
        else:
            self._pm_atuais = valor

    @property
    def vigor_maximo(self) -> int:
        """Calcula os Pontos de Vigor máximos."""
        # Vigor geralmente não tem bônus racial direto no máximo, mas isso pode ser adicionado se necessário.
        return self._vigor_maximo_calculado

    @property
    def vigor_atuais(self) -> int:
        """Obtém os Pontos de Vigor atuais."""
        return self._vigor_atuais

    @vigor_atuais.setter
    def vigor_atuais(self, valor: int) -> None:
        """Define os Pontos de Vigor atuais, com validação."""
        vigor_max = self.vigor_maximo # Usa a property
        if valor > vigor_max:
            self._vigor_atuais = vigor_max
        elif valor < 0:
            self._vigor_atuais = 0
        else:
            self._vigor_atuais = valor

    def recalcular_maximos(self) -> None:
        """
        Recalcula os valores máximos de PV, PM e Vigor baseados nos atributos,
        classe e nível do personagem. Os bônus raciais são aplicados nas
        propriedades `pv_maximo` e `pm_maximo`.
        Ajusta os valores atuais se excederem os novos máximos ou
        para preenchê-los na primeira carga/aumento significativo.
        """
        con = self.atributos.get(CONSTITUICAO, 0)
        try:
            nivel_atual = int(self.nivel)
            if nivel_atual < 1:
                nivel_atual = 1
        except (ValueError, TypeError):
            nivel_atual = 1  # Padrão se nível for inválido

        # --- Cálculo de PV Base ---
        pv_inicial_classe = 0
        pv_por_nivel_classe = 0
        if self.classe_principal == CLASSE_EVOCADOR:
            pv_inicial_classe = 8 + con
            pv_por_nivel_classe = 4 + con
        elif self.classe_principal == CLASSE_TITA: #
            pv_inicial_classe = 12 + con
            pv_por_nivel_classe = 6 + con
        elif self.classe_principal == CLASSE_SENTINELA: #
            pv_inicial_classe = 8 + con
            pv_por_nivel_classe = 4 + con
        elif self.classe_principal == CLASSE_ELO: #
            pv_inicial_classe = 8 + con
            pv_por_nivel_classe = 2 + con
        else:  # Padrão para classes não listadas ou nenhuma classe
            pv_inicial_classe = 6 + con # Valor base genérico
            pv_por_nivel_classe = 3 + con # Valor base genérico

        if nivel_atual == 1:
            self._pv_maximo_base_calculado = pv_inicial_classe
        else:
            self._pv_maximo_base_calculado = pv_inicial_classe + ((nivel_atual - 1) * pv_por_nivel_classe)

        # Se os PV atuais são 0 (e o personagem já foi carregado uma vez, indicando que não é uma nova ficha zerada)
        # OU se é a primeira vez que recalculamos e o máximo é > 0, preenche os PV.
        # A property setter de pv_atuais já garante que não exceda o novo máximo.
        if (self._loaded_once and self.pv_atuais == 0 and self.pv_maximo > 0) or \
           (not self._loaded_once and self.pv_maximo > 0):
            self.pv_atuais = self.pv_maximo
        else: # Garante que não exceda o máximo se o máximo diminuiu
            self.pv_atuais = min(self.pv_atuais, self.pv_maximo)


        # --- Cálculo de PM Base ---
        pm_inicial_classe = 0
        pm_por_nivel_classe = 0
        atributo_chave_pm_valor = 0

        if self.classe_principal == CLASSE_EVOCADOR: #
            # O atributo chave para Evocador pode depender da subclasse (Caminho).
            # Se atributo_chave_magia não estiver definido, usamos um padrão (e.g., Sabedoria).
            # Esta lógica pode precisar ser mais robusta se a UI permitir definir atr_chave antes da subclasse.
            atr_chave_nome = self.atributo_chave_magia if self.atributo_chave_magia else SABEDORIA
            atributo_chave_pm_valor = self.atributos.get(atr_chave_nome, 0)
            pm_inicial_classe = 6 + atributo_chave_pm_valor
            pm_por_nivel_classe = 4 + atributo_chave_pm_valor
        elif self.classe_principal == CLASSE_SENTINELA: #
            atributo_chave_pm_valor = self.atributos.get(SABEDORIA, 0)
            pm_inicial_classe = 4 + atributo_chave_pm_valor
            pm_por_nivel_classe = 2 + atributo_chave_pm_valor
        elif self.classe_principal == CLASSE_ELO: #
            atributo_chave_pm_valor = self.atributos.get(CARISMA, 0)
            pm_inicial_classe = 6 + atributo_chave_pm_valor
            pm_por_nivel_classe = 4 + atributo_chave_pm_valor
        # Titãs e outras classes podem não usar PM da mesma forma.

        if pm_inicial_classe > 0: # Só calcula se a classe usa PM
            if nivel_atual == 1:
                self._pm_maximo_base_calculado = pm_inicial_classe
            else:
                self._pm_maximo_base_calculado = pm_inicial_classe + ((nivel_atual - 1) * pm_por_nivel_classe)
        else:
            self._pm_maximo_base_calculado = 0

        if (self._loaded_once and self.pm_atuais == 0 and self.pm_maximo > 0) or \
           (not self._loaded_once and self.pm_maximo > 0):
            self.pm_atuais = self.pm_maximo
        else:
            self.pm_atuais = min(self.pm_atuais, self.pm_maximo)

        # --- Cálculo de Vigor Máximo ---
        self._vigor_maximo_calculado = 0
        if self.classe_principal == CLASSE_TITA: #
            self._vigor_maximo_calculado = 1 + con # Exemplo: Vigor inicial para Titã
            # Vigor pode aumentar com habilidades específicas, não apenas por nível base.
        
        if (self._loaded_once and self.vigor_atuais == 0 and self.vigor_maximo > 0) or \
           (not self._loaded_once and self.vigor_maximo > 0):
            self.vigor_atuais = self.vigor_maximo
        else:
            self.vigor_atuais = min(self.vigor_atuais, self.vigor_maximo)


    def atualizar_atributo(self, nome_atributo: str, valor: int) -> None:
        """Atualiza o valor de um atributo e recalcula os máximos dependentes."""
        if nome_atributo in self.atributos:
            if self.atributos[nome_atributo] != valor:
                self.atributos[nome_atributo] = valor
                self.recalcular_maximos()
        else:
            # Idealmente, isso não deveria acontecer se a UI estiver correta.
            # Considerar logar ou levantar um erro customizado.
            print(f"Erro: Atributo desconhecido '{nome_atributo}'.")

    def atualizar_nivel(self, novo_nivel_str: str) -> None:
        """Atualiza o nível do personagem e recalcula os máximos dependentes."""
        try:
            novo_nivel = int(novo_nivel_str)
            if novo_nivel < 1:
                novo_nivel = 1
            if self.nivel != novo_nivel:
                self.nivel = novo_nivel
                self.recalcular_maximos()
        except ValueError:
            print(f"Erro: Nível '{novo_nivel_str}' inválido.") # Feedback para UI seria melhor

    def atualizar_classe_principal(self, nova_classe: str) -> None:
        """Atualiza a classe principal e recalcula os máximos."""
        if self.classe_principal != nova_classe:
            self.classe_principal = nova_classe
            if self.classe_principal != CLASSE_EVOCADOR: #
                # Resetar atributo chave de magia se a classe não for Evocador
                # ou definir um padrão para outras classes se aplicável
                self.atributo_chave_magia = "" 
            self.recalcular_maximos()

    def atualizar_raca(self, nova_raca: str) -> None:
        """Atualiza a raça e recalcula os máximos."""
        if self.raca != nova_raca:
            self.raca = nova_raca
            self.recalcular_maximos()

    def atualizar_atributo_chave_magia(self, novo_atributo_chave: str) -> None:
        """Atualiza o atributo chave para magias (relevante para Evocador)."""
        if self.atributo_chave_magia != novo_atributo_chave:
            self.atributo_chave_magia = novo_atributo_chave
            if self.classe_principal == CLASSE_EVOCADOR: # Só recalcula PM se for Evocador
                self.recalcular_maximos()

    def atualizar_pericia_valor(self, nome_pericia: str, valor: int) -> None:
        """Atualiza o valor de uma perícia."""
        # Validações adicionais (e.g., valor mínimo se treinada) podem ser adicionadas aqui
        # ou na lógica da UI antes de chamar este método.
        if self.pericias_valores.get(nome_pericia) != valor:
            self.pericias_valores[nome_pericia] = valor

    def marcar_pericia_treinada(self, nome_pericia: str, eh_treinada: bool) -> None:
        """Marca uma perícia como treinada ou não."""
        if eh_treinada:
            self.pericias_treinadas.add(nome_pericia)
        else:
            self.pericias_treinadas.discard(nome_pericia)

    def to_dict(self) -> Dict[str, Any]:
        """Converte os dados do personagem para um dicionário serializável em JSON."""
        data = self.__dict__.copy()
        # Converte set para list para serialização JSON
        if 'pericias_treinadas' in data and isinstance(data['pericias_treinadas'], set): #
            data['pericias_treinadas'] = list(data['pericias_treinadas'])
        
        # Remove atributos que são calculados ou flags internos de runtime
        data.pop('_pv_maximo_base_calculado', None) #
        data.pop('_pm_maximo_base_calculado', None) #
        data.pop('_vigor_maximo_calculado', None) #
        data.pop('_loaded_once', None) # Remove o flag temporário
        return data

    @classmethod
    def from_dict(cls, data_dict: Dict[str, Any]) -> 'Personagem':
        """Cria uma instância de Personagem a partir de um dicionário."""
        personagem = cls()
        
        # Limpa listas que serão repopuladas para evitar duplicação
        # se from_dict for chamado em uma instância já existente (embora @classmethod crie uma nova).
        personagem.armas_inventario = [] #
        personagem.magias_habilidades = [] #
        personagem.itens_gerais = [] #
        
        for key, value in data_dict.items():
            if hasattr(personagem, key):
                # Trata a conversão de lista de volta para set para pericias_treinadas
                if key == 'pericias_treinadas' and isinstance(value, list): #
                    setattr(personagem, key, set(value))
                # Não atribuir diretamente propriedades que têm setters com lógica complexa
                # ou atributos que são recalculados (como os máximos base).
                elif key not in [
                    'pv_maximo', 'pm_maximo', 'vigor_maximo', # São properties
                    '_pv_maximo_base_calculado', '_pm_maximo_base_calculado', 
                    '_vigor_maximo_calculado', '_loaded_once'
                ]:
                    setattr(personagem, key, value)
        
        personagem._loaded_once = True # Sinaliza que os dados foram carregados
        personagem.recalcular_maximos()
        
        # Ajusta valores atuais após recalcular máximos, caso não tenham sido carregados
        # ou para garantir que estejam dentro dos limites.
        # Os setters das propriedades já cuidam disso.
        # Apenas garantimos que, se pv_atuais, etc. não estavam no JSON (usando valor padrão 0 do __init__),
        # eles sejam preenchidos com os máximos após o primeiro cálculo.
        # Essa lógica já está um pouco embutida no final de recalcular_maximos
        # e nos setters quando _loaded_once é True.
        
        # Se os valores atuais não vieram do JSON, eles foram inicializados como 0.
        # A recalcular_maximos chamada acima com _loaded_once=True irá preenchê-los.
        # Se vieram do JSON, os setters garantirão que estão dentro dos limites.

        delattr(personagem, '_loaded_once') # Remove o sinalizador após o uso
        return personagem