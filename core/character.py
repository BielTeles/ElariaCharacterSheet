# core/character.py
import json # Adicione esta importação se ainda não estiver lá

class Personagem:
    def __init__(self):
        # ... (outros atributos como antes) ...
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
        self.pv_maximo = 0; self.pv_atuais = 0
        self.pm_maximo = 0; self.pm_atuais = 0
        self.vigor_maximo = 0; self.vigor_atuais = 0
        
        self.pericias_valores = {}
        self.pericias_treinadas = set() # Continua como set internamente

        self.rd_total = 0
        self.armadura_equipada = {"nome": "", "rd_fornecida": 0}
        self.escudo_equipado = {"nome": "", "notas": ""}
        
        self.armas_inventario = [] 
        self.arma_equipada_principal = None 
        self.arma_equipada_secundaria = None 

        self.atributo_chave_magia = ""
        self.cd_teste_resistencia_magia = 0
        self.bonus_ataque_magico = 0 # Pode ser string como "+X" ou int
        self.caminho_especializacao_magica = ""
        self.magias_habilidades = [] 

        self.moedas_ef = 0
        self.moedas_efp = 0
        self.itens_gerais = [] 
        self.limite_carga_status = "Normal"
        self.notas = ""

    def atualizar_atributo(self, nome_atributo, valor):
        if nome_atributo in self.atributos:
            try:
                self.atributos[nome_atributo] = int(valor)
                # print(f"Atributo {nome_atributo} atualizado para {valor} no objeto Personagem.")
            except ValueError:
                print(f"Erro: Valor '{valor}' inválido para atributo {nome_atributo}.")
        else:
            print(f"Erro: Atributo desconhecido '{nome_atributo}'.")

    def atualizar_pericia_valor(self, nome_pericia, valor):
        try:
            self.pericias_valores[nome_pericia] = int(valor)
            # print(f"Perícia {nome_pericia} atualizada para valor {valor} no objeto Personagem.")
        except ValueError:
            # Se não puder converter para int, talvez manter o valor antigo ou string?
            # Ou forçar para 0. Por enquanto, não faz nada se falhar.
             print(f"Erro: Valor '{valor}' inválido para perícia {nome_pericia}.")


    def marcar_pericia_treinada(self, nome_pericia, eh_treinada):
        if eh_treinada:
            self.pericias_treinadas.add(nome_pericia)
        else:
            self.pericias_treinadas.discard(nome_pericia)
        # print(f"Perícia {nome_pericia} marcada como treinada: {eh_treinada}. Treinadas: {self.pericias_treinadas}")


    def to_dict(self):
        """Converte o objeto Personagem para um dicionário serializável em JSON."""
        data = self.__dict__.copy() # Cria uma cópia para não modificar o objeto original
        # Converte o set de perícias treinadas para uma lista para ser serializável
        if 'pericias_treinadas' in data and isinstance(data['pericias_treinadas'], set):
            data['pericias_treinadas'] = list(data['pericias_treinadas'])
        
        # Se armas_inventario, arma_equipada_principal, etc., contiverem objetos customizados no futuro,
        # eles também precisarão de um método to_dict() ou serem convertidos aqui.
        # Por enquanto, estamos assumindo que são dicionários ou tipos básicos.
        return data

    @classmethod
    def from_dict(cls, data_dict):
        """Cria uma instância de Personagem a partir de um dicionário."""
        personagem = cls()
        for key, value in data_dict.items():
            if hasattr(personagem, key):
                # Converte a lista de perícias treinadas de volta para um set
                if key == 'pericias_treinadas' and isinstance(value, list):
                    setattr(personagem, key, set(value))
                else:
                    setattr(personagem, key, value)
        return personagem

if __name__ == "__main__":
    char = Personagem()
    char.nome_personagem = "Lyra Teste"
    char.atributos["Força"] = 3
    char.pericias_treinadas.add("Atletismo")
    char.pericias_treinadas.add("Furtividade")
    char.pericias_valores["Atletismo"] = 5

    char_dict_data = char.to_dict()
    print("--- Dicionário para Salvar ---")
    print(json.dumps(char_dict_data, indent=2, ensure_ascii=False))

    # Simula salvar e carregar
    loaded_char = Personagem.from_dict(char_dict_data)
    print("\n--- Personagem Carregado ---")
    print(f"Nome: {loaded_char.nome_personagem}")
    print(f"Força: {loaded_char.atributos['Força']}")
    print(f"Perícias Treinadas: {loaded_char.pericias_treinadas}") # Deve ser um set
    print(f"Atletismo Valor: {loaded_char.pericias_valores['Atletismo']}")

    # Testa se é um set
    print(f"Tipo de pericias_treinadas: {type(loaded_char.pericias_treinadas)}")