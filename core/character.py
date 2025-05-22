# core/character.py
import json

class Personagem:
    def __init__(self):
        # Aba Principal
        self.nome_personagem = ""
        self.nome_jogador = ""
        self.raca = ""
        self.classe_principal = "" # Ex: "Evocador", "Titã", "Sentinela", "Elo"
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
        self._vigor_maximo_calculado = 0 # NOVO para Vigor Máximo

        self.pv_atuais = 0
        self.pm_atuais = 0
        self.vigor_atuais = 0 # Já existia
        
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
        self.bonus_ataque_magico = 0 
        self.caminho_especializacao_magica = ""
        self.magias_habilidades = [] 

        self.moedas_ef = 0
        self.moedas_efp = 0
        self.itens_gerais = [] 
        self.limite_carga_status = "Normal"
        self.notas = ""

        self.recalcular_maximos()

    @property
    def pv_maximo(self):
        bonus_racial_pv = 0
        if self.raca == "Roknar":
            bonus_racial_pv = 3 + (max(0, self.nivel -1) * 1)
        return self._pv_maximo_base_calculado + bonus_racial_pv

    @property
    def pm_maximo(self):
        bonus_racial_pm = 0
        if self.raca == "Alari":
            bonus_racial_pm = self.nivel * 1
        return self._pm_maximo_base_calculado + bonus_racial_pm

    @property # NOVO Property para Vigor Máximo
    def vigor_maximo(self):
        # Não há bônus raciais especificados para vigor máximo, apenas o cálculo da classe Titã.
        # Se outras classes ou raças concederem bônus, adicionar aqui.
        return self._vigor_maximo_calculado


    def recalcular_maximos(self):
        """Recalcula PV, PM e Vigor máximos e atualiza os atuais se necessário."""
        con = self.atributos.get("Constituição", 0)
        nivel_atual = self.nivel if isinstance(self.nivel, int) and self.nivel > 0 else 1

        # --- Cálculo de PV Máximo Base ---
        pv_inicial_classe = 0; pv_por_nivel_classe = 0
        if self.classe_principal == "Evocador":
            pv_inicial_classe = 8 + con; pv_por_nivel_classe = 4 + con
        elif self.classe_principal == "Titã":
            pv_inicial_classe = 12 + con; pv_por_nivel_classe = 6 + con
        elif self.classe_principal == "Sentinela":
            pv_inicial_classe = 8 + con; pv_por_nivel_classe = 4 + con
        elif self.classe_principal == "Elo":
            pv_inicial_classe = 8 + con; pv_por_nivel_classe = 2 + con
        else: pv_inicial_classe = 6 + con; pv_por_nivel_classe = 3 + con

        if nivel_atual == 1: self._pv_maximo_base_calculado = pv_inicial_classe
        else: self._pv_maximo_base_calculado = pv_inicial_classe + ((nivel_atual - 1) * pv_por_nivel_classe)
        
        if self.pv_atuais > self.pv_maximo or (self.pv_atuais == 0 and self.pv_maximo > 0) :
            self.pv_atuais = self.pv_maximo

        # --- Cálculo de PM Máximo Base ---
        pm_inicial_classe = 0; pm_por_nivel_classe = 0; atributo_chave_pm_valor = 0
        if self.classe_principal == "Evocador":
            if self.atributo_chave_magia in self.atributos:
                atributo_chave_pm_valor = self.atributos.get(self.atributo_chave_magia, 0)
            pm_inicial_classe = 6 + atributo_chave_pm_valor; pm_por_nivel_classe = 4 + atributo_chave_pm_valor
        elif self.classe_principal == "Sentinela":
            atributo_chave_pm_valor = self.atributos.get("Sabedoria", 0)
            pm_inicial_classe = 4 + atributo_chave_pm_valor; pm_por_nivel_classe = 2 + atributo_chave_pm_valor
        elif self.classe_principal == "Elo":
            atributo_chave_pm_valor = self.atributos.get("Carisma", 0)
            pm_inicial_classe = 6 + atributo_chave_pm_valor; pm_por_nivel_classe = 4 + atributo_chave_pm_valor
        
        if pm_inicial_classe > 0: # Apenas calcula se a classe usa PM
            if nivel_atual == 1: self._pm_maximo_base_calculado = pm_inicial_classe
            else: self._pm_maximo_base_calculado = pm_inicial_classe + ((nivel_atual - 1) * pm_por_nivel_classe)
        else: self._pm_maximo_base_calculado = 0

        if self.pm_atuais > self.pm_maximo or (self.pm_atuais == 0 and self.pm_maximo > 0):
            self.pm_atuais = self.pm_maximo

        # --- Cálculo de Vigor Máximo --- NOVO
        self._vigor_maximo_calculado = 0 # Zera por padrão
        if self.classe_principal == "Titã": # [cite: 362]
            # Começa com um número de Vigor igual a 1 + Constituição. [cite: 363]
            # O livro não especifica ganho de Vigor Máximo por nível.
            self._vigor_maximo_calculado = 1 + con 
        
        if self.vigor_atuais > self.vigor_maximo or (self.vigor_atuais == 0 and self.vigor_maximo > 0):
            self.vigor_atuais = self.vigor_maximo
        
        # print(f"Recalculado: PV Max: {self.pv_maximo}, PM Max: {self.pm_maximo}, Vigor Max: {self.vigor_maximo}")

    def atualizar_atributo(self, nome_atributo, valor):
        # ... (como antes, mas recalcular_maximos já é chamado)
        if nome_atributo in self.atributos:
            try:
                val_int = int(valor)
                if self.atributos[nome_atributo] != val_int:
                    self.atributos[nome_atributo] = val_int
                    self.recalcular_maximos() 
            except ValueError: print(f"Erro: Valor '{valor}' inválido para atributo {nome_atributo}.")
        else: print(f"Erro: Atributo desconhecido '{nome_atributo}'.")

    def atualizar_nivel(self, novo_nivel_str):
        # ... (como antes, mas recalcular_maximos já é chamado)
        try:
            novo_nivel = int(novo_nivel_str)
            if novo_nivel < 1: novo_nivel = 1
            if self.nivel != novo_nivel:
                self.nivel = novo_nivel
                self.recalcular_maximos()
        except ValueError: print(f"Erro: Nível '{novo_nivel_str}' inválido.")

    def atualizar_classe_principal(self, nova_classe):
        # ... (como antes, mas recalcular_maximos já é chamado)
        if self.classe_principal != nova_classe:
            self.classe_principal = nova_classe
            self.recalcular_maximos()
            
    def atualizar_raca(self, nova_raca):
        # ... (como antes, mas recalcular_maximos já é chamado)
        if self.raca != nova_raca:
            self.raca = nova_raca
            self.recalcular_maximos()

    def atualizar_atributo_chave_magia(self, novo_atributo_chave):
        # ... (como antes, mas recalcular_maximos já é chamado)
        if self.atributo_chave_magia != novo_atributo_chave:
            self.atributo_chave_magia = novo_atributo_chave
            if self.classe_principal == "Evocador":
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
        data = self.__dict__.copy()
        if 'pericias_treinadas' in data and isinstance(data['pericias_treinadas'], set):
            data['pericias_treinadas'] = list(data['pericias_treinadas'])
        data.pop('_pv_maximo_base_calculado', None)
        data.pop('_pm_maximo_base_calculado', None)
        data.pop('_vigor_maximo_calculado', None) # NOVO: Remove o calculado
        return data

    @classmethod
    def from_dict(cls, data_dict):
        personagem = cls()
        for key, value in data_dict.items():
            if hasattr(personagem, key):
                if key == 'pericias_treinadas' and isinstance(value, list):
                    setattr(personagem, key, set(value))
                # Não seta diretamente os máximos, serão recalculados.
                # Assegure-se que pv_atuais, pm_atuais, vigor_atuais são carregados.
                elif key not in ['pv_maximo', 'pm_maximo', 'vigor_maximo', 
                                 '_pv_maximo_base_calculado', '_pm_maximo_base_calculado', '_vigor_maximo_calculado']:
                    setattr(personagem, key, value)
        
        personagem.recalcular_maximos() # Garante que máximos sejam calculados após carregar
        # Ajusta os atuais para não excederem os máximos recém-calculados (já feito em recalcular_maximos)
        return personagem


if __name__ == "__main__":
    char = Personagem()
    char.nome_personagem = "Calculador Vigor"
    char.classe_principal = "Titã" 
    char.raca = "Roknar" 
    char.nivel = 2
    char.atributos["Constituição"] = 3 # Titã Vigor = 1+3 = 4

    print(f"--- Teste {char.classe_principal} Nível {char.nivel} CON {char.atributos['Constituição']} Raça {char.raca} ---")
    # recalcular_maximos() é chamado no __init__ e após mudanças relevantes
    print(f"PV Máximo: {char.pv_maximo} (Base: {char._pv_maximo_base_calculado})")
    print(f"PM Máximo: {char.pm_maximo} (Base: {char._pm_maximo_base_calculado})")
    print(f"Vigor Máximo: {char.vigor_maximo} (Base: {char._vigor_maximo_calculado})")

    char.nivel = 1
    char.atualizar_nivel("1") # Testando atualização de nível
    print(f"--- Teste Nível 1 ---")
    print(f"PV Máximo: {char.pv_maximo} (Base: {char._pv_maximo_base_calculado})")
    print(f"Vigor Máximo: {char.vigor_maximo} (Base: {char._vigor_maximo_calculado})")

    # Teste de salvamento e carregamento
    char_data = char.to_dict()
    # print(json.dumps(char_data, indent=2))
    new_char = Personagem.from_dict(char_data)
    print(f"--- Personagem Carregado: {new_char.nome_personagem} ---")
    print(f"PV Máximo Carregado: {new_char.pv_maximo}")
    print(f"PM Máximo Carregado: {new_char.pm_maximo}")
    print(f"Vigor Máximo Carregado: {new_char.vigor_maximo}")
    print(f"Vigor Atuais Carregado: {new_char.vigor_atuais}") # Deve ser igual ao máximo após recalcular