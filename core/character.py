# core/character.py
import json

class Personagem:
    def __init__(self):
        # ... (atributos como definido anteriormente)
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
            "Força": 0, "Destreza": 0, "Constituição": 0,
            "Inteligência": 0, "Sabedoria": 0, "Carisma": 0
        }
        
        self._pv_maximo_base_calculado = 0 
        self._pm_maximo_base_calculado = 0 
        self._vigor_maximo_calculado = 0

        self.pv_atuais = 0
        self.pm_atuais = 0
        self.vigor_atuais = 0
        
        self.pericias_valores = {}
        self.pericias_treinadas = set() 

        self.rd_total = 0
        self.armadura_equipada = {"nome": "", "rd_fornecida": 0} # Dicionário simples
        self.escudo_equipado = {"nome": "", "notas": ""}       # Dicionário simples
        
        self.armas_inventario = [] # Deve ser uma lista de dicionários
        self.arma_equipada_principal = None # Deve ser um dicionário (ou referência a um da lista) ou None
        self.arma_equipada_secundaria = None # Deve ser um dicionário (ou referência a um da lista) ou None

        self.atributo_chave_magia = "" 
        self.cd_teste_resistencia_magia = 0
        self.bonus_ataque_magico = "0" # Mantido como string para consistência com UI, mas int seria melhor
        self.caminho_especializacao_magica = ""
        self.magias_habilidades = [] # Deve ser uma lista de dicionários

        self.moedas_ef = 0
        self.moedas_efp = 0
        self.itens_gerais = [] # Deve ser uma lista de dicionários
        self.limite_carga_status = "Normal"
        self.notas = ""

        self.recalcular_maximos() # Chamado no final do init

    @property
    def pv_maximo(self):
        # ... (lógica como antes)
        bonus_racial_pv = 0
        if self.raca == "Roknar":
            bonus_racial_pv = 3 + (max(0, self.nivel -1) * 1)
        return self._pv_maximo_base_calculado + bonus_racial_pv


    @property
    def pm_maximo(self):
        # ... (lógica como antes)
        bonus_racial_pm = 0
        if self.raca == "Alari":
            bonus_racial_pm = self.nivel * 1 # Assegure que self.nivel é int aqui
        return self._pm_maximo_base_calculado + bonus_racial_pm

    @property 
    def vigor_maximo(self):
        # ... (lógica como antes)
        return self._vigor_maximo_calculado


    def recalcular_maximos(self):
        # ... (lógica como antes)
        # Garanta que self.nivel e os valores em self.atributos são inteiros antes de usar em cálculos
        con = self.atributos.get("Constituição", 0)
        try:
            nivel_atual = int(self.nivel)
            if nivel_atual < 1: nivel_atual = 1
        except (ValueError, TypeError):
            nivel_atual = 1 # Padrão se nível for inválido

        # PV
        pv_inicial_classe = 0; pv_por_nivel_classe = 0
        if self.classe_principal == "Evocador": pv_inicial_classe = 8 + con; pv_por_nivel_classe = 4 + con
        elif self.classe_principal == "Titã": pv_inicial_classe = 12 + con; pv_por_nivel_classe = 6 + con
        elif self.classe_principal == "Sentinela": pv_inicial_classe = 8 + con; pv_por_nivel_classe = 4 + con
        elif self.classe_principal == "Elo": pv_inicial_classe = 8 + con; pv_por_nivel_classe = 2 + con
        else: pv_inicial_classe = 6 + con; pv_por_nivel_classe = 3 + con
        if nivel_atual == 1: self._pv_maximo_base_calculado = pv_inicial_classe
        else: self._pv_maximo_base_calculado = pv_inicial_classe + ((nivel_atual - 1) * pv_por_nivel_classe)
        
        # Ajusta PV atuais
        # Usa a property pv_maximo que já inclui bônus racial
        if self.pv_atuais > self.pv_maximo or (getattr(self, '_pv_maximo_base_calculado', 0) > 0 and self.pv_atuais == 0 and self.pv_maximo > 0 and not hasattr(self, '_loaded_once')): # Enche na primeira vez ou se aumentou
             self.pv_atuais = self.pv_maximo
        elif self.pv_atuais > self.pv_maximo:
             self.pv_atuais = self.pv_maximo


        # PM
        pm_inicial_classe = 0; pm_por_nivel_classe = 0; atributo_chave_pm_valor = 0
        # ... (lógica de PM como antes) ...
        if self.classe_principal == "Evocador":
            atr_chave = self.atributo_chave_magia if self.atributo_chave_magia else "Sabedoria" # Default para Evocador se não definido
            atributo_chave_pm_valor = self.atributos.get(atr_chave, 0)
            pm_inicial_classe = 6 + atributo_chave_pm_valor; pm_por_nivel_classe = 4 + atributo_chave_pm_valor
        elif self.classe_principal == "Sentinela":
            atributo_chave_pm_valor = self.atributos.get("Sabedoria", 0)
            pm_inicial_classe = 4 + atributo_chave_pm_valor; pm_por_nivel_classe = 2 + atributo_chave_pm_valor
        elif self.classe_principal == "Elo":
            atributo_chave_pm_valor = self.atributos.get("Carisma", 0)
            pm_inicial_classe = 6 + atributo_chave_pm_valor; pm_por_nivel_classe = 4 + atributo_chave_pm_valor
        
        if pm_inicial_classe > 0: 
            if nivel_atual == 1: self._pm_maximo_base_calculado = pm_inicial_classe
            else: self._pm_maximo_base_calculado = pm_inicial_classe + ((nivel_atual - 1) * pm_por_nivel_classe)
        else: self._pm_maximo_base_calculado = 0
        
        # Ajusta PM atuais
        if self.pm_atuais > self.pm_maximo or (getattr(self, '_pm_maximo_base_calculado', 0) > 0 and self.pm_atuais == 0 and self.pm_maximo > 0 and not hasattr(self, '_loaded_once')):
            self.pm_atuais = self.pm_maximo
        elif self.pm_atuais > self.pm_maximo:
             self.pm_atuais = self.pm_maximo


        # Vigor
        self._vigor_maximo_calculado = 0 
        if self.classe_principal == "Titã": 
            self._vigor_maximo_calculado = 1 + con 
        
        # Ajusta Vigor atuais
        if self.vigor_atuais > self.vigor_maximo or (getattr(self, '_vigor_maximo_calculado',0) > 0 and self.vigor_atuais == 0 and self.vigor_maximo > 0 and not hasattr(self, '_loaded_once')):
            self.vigor_atuais = self.vigor_maximo
        elif self.vigor_atuais > self.vigor_maximo:
            self.vigor_atuais = self.vigor_maximo


    def atualizar_atributo(self, nome_atributo, valor):
        # ... (como antes)
        if nome_atributo in self.atributos:
            try:
                val_int = int(valor)
                if self.atributos[nome_atributo] != val_int:
                    self.atributos[nome_atributo] = val_int
                    self.recalcular_maximos() 
            except ValueError: print(f"Erro: Valor '{valor}' inválido para atributo {nome_atributo}.")
        else: print(f"Erro: Atributo desconhecido '{nome_atributo}'.")


    def atualizar_nivel(self, novo_nivel_str):
        # ... (como antes)
        try:
            novo_nivel = int(novo_nivel_str)
            if novo_nivel < 1: novo_nivel = 1
            if self.nivel != novo_nivel:
                self.nivel = novo_nivel
                self.recalcular_maximos()
        except ValueError: print(f"Erro: Nível '{novo_nivel_str}' inválido.")


    def atualizar_classe_principal(self, nova_classe):
        # ... (como antes)
        if self.classe_principal != nova_classe:
            self.classe_principal = nova_classe
            # Resetar atributo chave de magia se a classe não for Evocador, ou definir um padrão
            if self.classe_principal != "Evocador":
                self.atributo_chave_magia = "" # Ou um valor padrão para outras classes se aplicável
            self.recalcular_maximos()
            
    def atualizar_raca(self, nova_raca):
        # ... (como antes)
        if self.raca != nova_raca:
            self.raca = nova_raca
            self.recalcular_maximos()

    def atualizar_atributo_chave_magia(self, novo_atributo_chave):
        # ... (como antes)
        if self.atributo_chave_magia != novo_atributo_chave:
            self.atributo_chave_magia = novo_atributo_chave
            if self.classe_principal == "Evocador": # Só recalcula se for Evocador
                self.recalcular_maximos()


    def atualizar_pericia_valor(self, nome_pericia, valor):
        # ... (como antes)
        try:
            val_int = int(valor)
            if self.pericias_valores.get(nome_pericia) != val_int:
                 self.pericias_valores[nome_pericia] = val_int
        except ValueError: print(f"Erro: Valor '{valor}' inválido para perícia {nome_pericia}.")


    def marcar_pericia_treinada(self, nome_pericia, eh_treinada):
        # ... (como antes)
        if eh_treinada: self.pericias_treinadas.add(nome_pericia)
        else: self.pericias_treinadas.discard(nome_pericia)


    def to_dict(self):
        # ... (como antes)
        data = self.__dict__.copy()
        if 'pericias_treinadas' in data and isinstance(data['pericias_treinadas'], set):
            data['pericias_treinadas'] = list(data['pericias_treinadas'])
        data.pop('_pv_maximo_base_calculado', None); data.pop('_pm_maximo_base_calculado', None); data.pop('_vigor_maximo_calculado', None)
        return data

    @classmethod
    def from_dict(cls, data_dict):
        personagem = cls()
        # Limpa listas que serão repopuladas para evitar duplicação se from_dict for chamado em uma instância existente
        personagem.armas_inventario = []
        personagem.magias_habilidades = []
        personagem.itens_gerais = []
        
        for key, value in data_dict.items():
            if hasattr(personagem, key):
                if key == 'pericias_treinadas' and isinstance(value, list):
                    setattr(personagem, key, set(value))
                elif key not in ['pv_maximo', 'pm_maximo', 'vigor_maximo', '_pv_maximo_base_calculado', '_pm_maximo_base_calculado', '_vigor_maximo_calculado']:
                    setattr(personagem, key, value)
        
        personagem._loaded_once = True # Sinalizador para lógica de encher PV/PM/Vigor atuais
        personagem.recalcular_maximos() 
        delattr(personagem, '_loaded_once') # Remove o sinalizador
        return personagem