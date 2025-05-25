# ElariaCharacterSheet/data/abilities_data.py
from typing import List, Dict, Any, Union, Literal

# Tipos para clareza da estrutura de dados
# Esses poderiam ser mais granulares se necessário
TipoHabilidade = Literal[
    "Escolha de Subclasse", "Habilidade de Classe", "Passiva de Classe",
    "Passiva de Caminho", "Manifestação da Terra", "Manifestação Aquática",
    "Manifestação do Vento", "Manifestação do Piromante", "Manifestação dos Luminantes",
    "Manifestação das Sombras", "Passiva de Arquétipo", "Habilidade de Arquétipo"
]
AcaoHabilidade = Literal["Passiva", "Ação Padrão", "Reação", "Ação Bônus", "Ação Livre", "N/A (parte do TR)", "Descanso Longo", "Pausa (durante Descanso Curto)", "Ação de Movimento", "Ação de Ataque"]

Habilidade = Dict[str, Union[int, str, TipoHabilidade, AcaoHabilidade, None]]
SubclasseHabilidades = Dict[str, List[Habilidade]]
SubclasseData = Dict[str, SubclasseHabilidades] # Ex: {"Caminho da Terra": {"habilidades": [...]}}
ClasseData = Dict[str, Union[str, None, int, Dict[str, Any], List[Habilidade], Dict[str, SubclasseData]]]

ABILITIES_DATA: Dict[str, ClasseData] = {
    "Evocador": {
        "atributo_chave_pm_base": "Depende do Caminho",  # SAB ou INT
        "pv_inicial": "8 + CON", "pv_por_nivel": "4 + CON",
        "pm_inicial_multiplicador": 1, "pm_por_nivel_multiplicador": 1, # Baseado em 6 + AtrChave e 4 + AtrChave
        "pericias_treinadas_escolha": {
            "quantidade": 3,
            "opcoes": ["Misticismo", "Intuição", "Percepção", "Sobrevivência", "Vontade", "Investigação"]
        },
        "base": [ # Habilidades base da classe Evocador
            {"nivel_req": 1, "nome": "Sintonia Elemental (Escolha de Caminho)", "descricao": "Escolha um dos seis Caminhos Elementais como sua subclasse (Terra, Água, Ar, Fogo, Luz ou Sombra). Esta escolha determina seu Atributo Chave para habilidades de Evocador (Sabedoria para Terra, Água, Luz; Inteligência para Ar, Fogo, Sombra).", "tipo": "Escolha de Subclasse", "acao": "Passiva"},
            {"nivel_req": 1, "nome": "Canalizar Elemento (Básico)", "descricao": "Crie um efeito menor e geralmente não ofensivo do seu elemento sintonizado (mover pequeno volume, pequena luz/sombra, pequena chama, aquecer/esfriar objeto). Dura enquanto se concentrar ou é instantâneo.", "custo": "1 PM", "acao": "Ação Padrão", "alcance": "Curto (~9m)", "tipo": "Habilidade de Classe"},
        ],
        "subclasses": {
            "Caminho da Terra": { # Atributo Chave: Sabedoria
                "habilidades": [
                    {"nivel_req": 1, "nome": "Sintonia Reforçada (Terra)", "descricao": "Aumenta sua RD contra dano em 1 ponto.", "tipo": "Passiva de Caminho", "acao": "Passiva"}, # Adicionado acao para consistência
                    {"nivel_req": 1, "nome": "Postura Inabalável", "descricao": "(Reação) Vantagem no TR contra movimento forçado ou derrubar.", "custo": "1 PM", "acao": "Reação", "tipo": "Manifestação da Terra", "grupo_escolha": "manifestacoes_terra_lvl1", "limite_escolha": 2},
                    {"nivel_req": 1, "nome": "Abraço da Terra", "descricao": "Área 1,5m dificulta movimento (TR Força CD Normal ou desloc. /2). Duração: 3 turnos.", "custo": "1 PM", "acao": "Ação Padrão", "alcance": "9m", "tipo": "Manifestação da Terra", "grupo_escolha": "manifestacoes_terra_lvl1", "limite_escolha": 2},
                    {"nivel_req": 1, "nome": "Moldar Abrigo", "descricao": "Cria cobertura para criatura Média ou menor. Duração: 3 turnos ou até ser destruída (PV = 2xNível, RD 1).", "custo": "2 PM", "acao": "Ação Padrão", "alcance": "Toque", "tipo": "Manifestação da Terra", "grupo_escolha": "manifestacoes_terra_lvl1", "limite_escolha": 2},
                    {"nivel_req": 1, "nome": "Sentido Sísmico", "descricao": "Percebe automaticamente criaturas médias+ em contato com o solo a até 9m (não voadoras/leves).", "tipo": "Passiva de Caminho", "acao": "Passiva"},
                ]
            },
            "Caminho da Água": { # Atributo Chave: Sabedoria
                "habilidades": [
                    {"nivel_req": 1, "nome": "Sintonia Reforçada (Água)", "descricao": "Prende respiração por 5 min; Vantagem em Atletismo para Nadar.", "tipo": "Passiva de Caminho", "acao": "Passiva"},
                    {"nivel_req": 1, "nome": "Forma Fluida", "descricao": "(Ação Bônus) Até próx. turno: move através de hostis, Vantagem em Acrobacia para escapar.", "custo": "1 PM", "acao": "Ação Bônus", "alcance": "Pessoal", "tipo": "Manifestação Aquática", "grupo_escolha": "manifestacoes_agua_lvl1", "limite_escolha": 2},
                    {"nivel_req": 1, "nome": "Projétil de Água", "descricao": "(Ação) Ataque de magia à distância (SAB). Dano: 1d6 + SAB (impacto).", "custo": "1 PM", "acao": "Ação Padrão", "alcance": "9m", "tipo": "Manifestação Aquática", "grupo_escolha": "manifestacoes_agua_lvl1", "limite_escolha": 2},
                    {"nivel_req": 1, "nome": "Pulso Restaurador", "descricao": "(Ação) Alvo recupera 1d4 + SAB PV. Pode tentar encerrar veneno/doença (TR Cura CD Mestre).", "custo": "2 PM", "acao": "Ação Padrão", "alcance": "Toque", "tipo": "Manifestação Aquática", "grupo_escolha": "manifestacoes_agua_lvl1", "limite_escolha": 2},
                    {"nivel_req": 1, "nome": "Sentir a Água", "descricao": "Próximo a água (3m), percebe criaturas médias+ se movendo na água a até 9m.", "tipo": "Passiva de Caminho", "acao": "Passiva"},
                ]
            },
            "Caminho do Ar": { # Atributo Chave: Inteligência
                "habilidades": [
                    {"nivel_req": 1, "nome": "Sintonia Reforçada (Ar)", "descricao": "Aumento de deslocamento base +1,5 metros.", "tipo": "Passiva de Caminho", "acao": "Passiva"},
                    {"nivel_req": 1, "nome": "Corrente Ascendente", "descricao": "(Ação Bônus) Até fim do turno: ignora terreno difícil, Vantagem em Acrobacia (equilíbrio/salto).", "custo": "1 PM", "acao": "Ação Bônus", "alcance": "Pessoal", "tipo": "Manifestação do Vento", "grupo_escolha": "manifestacoes_ar_lvl1", "limite_escolha": 2},
                    {"nivel_req": 1, "nome": "Sopro Desestabilizador", "descricao": "(Ação) Alvo TR Força (CD Normal) ou desvantagem no próx. ataque corpo a corpo.", "custo": "1 PM", "acao": "Ação Padrão", "alcance": "9m", "tipo": "Manifestação do Vento", "grupo_escolha": "manifestacoes_ar_lvl1", "limite_escolha": 2},
                    {"nivel_req": 1, "nome": "Manto de Vento", "descricao": "(Reação) Quando você ou aliado adj. é alvo de projétil físico, atacante tem 1 dado de desvantagem.", "custo": "2 PM", "acao": "Reação", "tipo": "Manifestação do Vento", "grupo_escolha": "manifestacoes_ar_lvl1", "limite_escolha": 2},
                    {"nivel_req": 1, "nome": "Sentir a Brisa", "descricao": "Vantagem em Percepção para notar criaturas voadoras, invisíveis (se perturbam ar) ou mudanças climáticas.", "tipo": "Passiva de Caminho", "acao": "Passiva"},
                ]
            },
            "Caminho do Fogo": { # Atributo Chave: Inteligência
                "habilidades": [
                    {"nivel_req": 1, "nome": "Sintonia Reforçada (Fogo)", "descricao": "Ganha Resistência a Fogo.", "tipo": "Passiva de Caminho", "acao": "Passiva"},
                    {"nivel_req": 1, "nome": "Combustão Controlada", "descricao": "(Ação) Explosão 1,5m raio. Alvos TR DES (CD Normal) ou 1d6 dano Fogo (metade se passar).", "custo": "2 PM", "acao": "Ação Padrão", "alcance": "9m", "tipo": "Manifestação do Piromante", "grupo_escolha": "manifestacoes_fogo_lvl1", "limite_escolha": 2}, # Removido duracao, pois ação é instantânea
                    {"nivel_req": 1, "nome": "Alimentar as Chamas", "descricao": "(Ação Bônus) Próximo ataque com dano de Fogo neste turno causa 1d4 de dano de Fogo adicional.", "custo": "1 PM", "acao": "Ação Bônus", "alcance": "Pessoal", "tipo": "Manifestação do Piromante", "grupo_escolha": "manifestacoes_fogo_lvl1", "limite_escolha": 2},
                    {"nivel_req": 1, "nome": "Marca Incinerante", "descricao": "(Ação) Alvo TR FOR (CD Normal) ou fica marcado. Na 1a vez que sofrer dano Fogo (próx. 2 turnos), sofre 1d4 dano Fogo add.", "custo": "1 PM", "acao": "Ação Padrão", "alcance": "Toque", "tipo": "Manifestação do Piromante", "grupo_escolha": "manifestacoes_fogo_lvl1", "limite_escolha": 2},
                    {"nivel_req": 1, "nome": "Coração Ardente", "descricao": "Vantagem em TR contra efeitos de Amedrontado.", "tipo": "Passiva de Caminho", "acao": "Passiva"},
                ]
            },
            "Caminho da Luz": { # Atributo Chave: Sabedoria
                "habilidades": [
                    {"nivel_req": 1, "nome": "Sintonia Reforçada (Luz)", "descricao": "Vantagem em Intuição para detectar mentiras de criaturas visíveis.", "tipo": "Passiva de Caminho", "acao": "Passiva"},
                    {"nivel_req": 1, "nome": "Bálsamo de Luz", "descricao": "(Ação) Alvo recupera 1d6 + SAB PV. Vantagem no próx. TR vs doença/veneno (1h).", "custo": "2 PM", "acao": "Ação Padrão", "alcance": "Toque", "tipo": "Manifestação dos Luminantes", "grupo_escolha": "manifestacoes_luz_lvl1", "limite_escolha": 2},
                    {"nivel_req": 1, "nome": "Luz Reveladora", "descricao": "Luz 1,5m raio revela invisíveis, dissipa Escuridão Mágica (CD SAB). Duração: Concentração.", "custo": "2 PM", "acao": "Ação Padrão", "alcance": "9m", "tipo": "Manifestação dos Luminantes", "grupo_escolha": "manifestacoes_luz_lvl1", "limite_escolha": 2},
                    {"nivel_req": 1, "nome": "Seta Luminosa", "descricao": "(Ação) Ataque de magia (SAB). Dano: 1d6 + SAB Radiante. Vulneráveis à luz têm desvantagem no TR vs dano.", "custo": "2 PM", "acao": "Ação Padrão", "alcance": "18m", "tipo": "Manifestação dos Luminantes", "grupo_escolha": "manifestacoes_luz_lvl1", "limite_escolha": 2},
                    {"nivel_req": 1, "nome": "Presença Serena", "descricao": "Aliados a até 1,5m recebem Vantagem em TR vs Amedrontado.", "tipo": "Passiva de Caminho", "acao": "Passiva"},
                ]
            },
            "Caminho da Sombra": { # Atributo Chave: Inteligência
                "habilidades": [
                    {"nivel_req": 1, "nome": "Sintonia Reforçada (Sombra)", "descricao": "Vantagem em Furtividade na penumbra.", "tipo": "Passiva de Caminho", "acao": "Passiva"},
                    {"nivel_req": 1, "nome": "Véu de Engano", "descricao": "(Ação) Por 1h, Vantagem em Enganação para disfarçar aparência ou criar pequena ilusão visual/som.", "custo": "2 PM", "acao": "Ação Padrão", "alcance": "Pessoal", "tipo": "Manifestação das Sombras", "grupo_escolha": "manifestacoes_sombra_lvl1", "limite_escolha": 2},
                    {"nivel_req": 1, "nome": "Toque Debilitante", "descricao": "(Ação) Alvo TR CON (CD Normal) ou 1d4 dano necrótico e desvantagem no próx. TR FOR ou DES.", "custo": "1 PM", "acao": "Ação Padrão", "alcance": "Toque", "tipo": "Manifestação das Sombras", "grupo_escolha": "manifestacoes_sombra_lvl1", "limite_escolha": 2},
                    {"nivel_req": 1, "nome": "Passo Sombrio", "descricao": "(Ação Bônus) Teleporta até 6m para espaço desocupado em penumbra/escuridão.", "custo": "2 PM", "acao": "Ação Bônus", "alcance": "Pessoal", "tipo": "Manifestação das Sombras", "grupo_escolha": "manifestacoes_sombra_lvl1", "limite_escolha": 2},
                    {"nivel_req": 1, "nome": "Mente Quieta", "descricao": "Vantagem em TR contra leitura de pensamentos ou detecção de emoções.", "tipo": "Passiva de Caminho", "acao": "Passiva"},
                ]
            }
        }
    },
    "Titã": {
        "atributo_chave_pm_base": None,  # Titãs usam Vigor
        "pv_inicial": "12 + CON", "pv_por_nivel": "6 + CON",
        "vigor_inicial": "1 + CON", "vigor_por_nivel": 0, # Vigor não aumenta por nível base, mas por habilidades
        "pericias_treinadas_escolha": {
            "quantidade": 3,
            "opcoes": ["Atletismo", "Fortitude", "Intimidação", "Luta", "Percepção", "Sobrevivência"]
        },
        "base": [
            {"nivel_req": 1, "nome": "Força Titânica", "descricao": "Adiciona FOR novamente ao dano corpo a corpo (armas de 2 mãos ou que usam FOR).", "tipo": "Passiva de Classe", "acao": "Passiva"},
            {"nivel_req": 1, "nome": "Resiliência Implacável", "descricao": "Gaste 1 Vigor para Vantagem em TR de Fortitude ou Vontade.", "custo": "1 Vigor", "acao": "N/A (parte do TR)", "tipo": "Habilidade de Classe"},
            {"nivel_req": 1, "nome": "Arquétipo de Força", "descricao": "Escolha Baluarte, Fúria Primal ou Quebra-Montanhas.", "tipo": "Escolha de Subclasse", "acao": "Passiva"},
        ],
        "subclasses": {
            "Baluarte": {
                "habilidades": [
                    {"nivel_req": 1, "nome": "Presença Protetora", "descricao": "Aliados adjacentes +1 RD contra ataques corpo a corpo.", "tipo": "Passiva de Arquétipo", "acao": "Passiva"},
                    {"nivel_req": 1, "nome": "Postura Defensiva", "descricao": "(Ação Bônus) Com escudo: RD +1, Vantagem vs mover/derrubar. Inimigos adj. TR CAR (CD Bom) ou te atacam. Dura até próx. turno.", "custo": "1 Vigor", "acao": "Ação Bônus", "tipo": "Habilidade de Arquétipo", "grupo_escolha": "baluarte_lvl1", "limite_escolha": 2},
                    {"nivel_req": 1, "nome": "Proteger Aliado", "descricao": "(Reação) Se aliado adj. é atacado, faça Teste de Bloqueio. Se Grau Sucesso >= Ataque, você é atingido.", "custo": "1 Vigor (+1 V)", "acao": "Reação", "tipo": "Habilidade de Arquétipo", "grupo_escolha": "baluarte_lvl1", "limite_escolha": 2},
                    {"nivel_req": 1, "nome": "Escudo Ecoante", "descricao": "(Reação) Ao bloquear ataque corpo a corpo com sucesso, atacante sofre 1d4 dano (vibração).", "custo": "1 Vigor (+1 V)", "acao": "Reação", "tipo": "Habilidade de Arquétipo", "grupo_escolha": "baluarte_lvl1", "limite_escolha": 2},
                    {"nivel_req": 1, "nome": "Ancorar Posição", "descricao": "(Ação Bônus) Desloc. = 0. Inimigos adj. gastam +1,5m para mover em espaço adj. Dura até próx. turno.", "custo": "1 Vigor (+1 V)", "acao": "Ação Bônus", "tipo": "Habilidade de Arquétipo", "grupo_escolha": "baluarte_lvl1", "limite_escolha": 2},
                ]
            },
            "Fúria Primal": {
                "habilidades": [
                    {"nivel_req": 1, "nome": "Ímpeto Selvagem", "descricao": "Com PV <= Metade, desloc. +1,5m no turno. Ao zerar PV inimigo, recupera 2 Vigor.", "tipo": "Passiva de Arquétipo", "acao": "Passiva"},
                    {"nivel_req": 1, "nome": "Golpe Furioso", "descricao": "(Ação Bônus) Após acertar ataque corpo a corpo, ataque adicional com mesma arma/alvo (desvantagem).", "custo": "1 Vigor (+1 V)", "acao": "Ação Bônus", "tipo": "Habilidade de Arquétipo", "grupo_escolha": "furia_primal_lvl1", "limite_escolha": 2},
                    {"nivel_req": 1, "nome": "Grito de Guerra", "descricao": "(Ação) Hostis a 9m TR Vontade (CD Normal) ou Amedrontados por 1 rodada.", "custo": "1 Vigor", "acao": "Ação Padrão", "tipo": "Habilidade de Arquétipo", "grupo_escolha": "furia_primal_lvl1", "limite_escolha": 2},
                    {"nivel_req": 1, "nome": "Ignorar a Dor", "descricao": "(Reação) Ao sofrer dano (não zerando PV), reduz dano por CON (mín 1).", "custo": "1 Vigor", "acao": "Reação", "tipo": "Habilidade de Arquétipo", "grupo_escolha": "furia_primal_lvl1", "limite_escolha": 2},
                    {"nivel_req": 1, "nome": "Avanço Implacável", "descricao": "(Ação Mov.) Move desloc. total, atravessa hostis (terr. difícil), Vantagem em FOR (Atletismo) para quebrar obstáculos. Se terminar adj. a hostil, ataque corpo a corpo como ação livre.", "custo": "1 Vigor", "acao": "Ação de Movimento", "tipo": "Habilidade de Arquétipo", "grupo_escolha": "furia_primal_lvl1", "limite_escolha": 2},
                ]
            },
            "Quebra-Montanhas": {
                "habilidades": [
                    {"nivel_req": 1, "nome": "Golpe Destruidor", "descricao": "Com arma pesada (2 mãos), ignora 1 RD do alvo.", "tipo": "Passiva de Arquétipo", "acao": "Passiva"},
                    {"nivel_req": 1, "nome": "Impacto Arrasador", "descricao": "(Ação) Ataque corpo a corpo (arma pesada 2 mãos). Se acertar, dano + FOR, alvo TR FOR (CD Normal) ou Atordoado 1 rodada.", "custo": "1 Vigor", "acao": "Ação Padrão", "tipo": "Habilidade de Arquétipo", "grupo_escolha": "quebra_montanhas_lvl1", "limite_escolha": 2},
                    {"nivel_req": 1, "nome": "Rompante Poderoso", "descricao": "(Ação Mov.) Move desloc., Vantagem em FOR (Atletismo) para derrubar portão/parede. Se terminar adj. a hostil, ataque corpo a corpo ação livre.", "custo": "N/A", "acao": "Ação de Movimento", "tipo": "Habilidade de Arquétipo", "grupo_escolha": "quebra_montanhas_lvl1", "limite_escolha": 2}, # Custo N/A se for parte da ação de movimento
                    {"nivel_req": 1, "nome": "Quebrar Escudo", "descricao": "(Ação Ataque) Contra oponente com escudo. Se acertar (CD Bom - FOR), escudo destruído (sem dano normal).", "custo": "1 Vigor", "acao": "Ação de Ataque", "tipo": "Habilidade de Arquétipo", "grupo_escolha": "quebra_montanhas_lvl1", "limite_escolha": 2},
                    {"nivel_req": 1, "nome": "Firmeza da Montanha", "descricao": "(Ação Bônus) RD 2 vs todos os danos, desloc. = 0. Dura até próx. turno.", "custo": "2 Vigor", "acao": "Ação Bônus", "tipo": "Habilidade de Arquétipo", "grupo_escolha": "quebra_montanhas_lvl1", "limite_escolha": 2},
                ]
            }
        }
    },
    "Sentinela": {
        "atributo_chave_pm_base": "Sabedoria",
        "pv_inicial": "8 + CON", "pv_por_nivel": "4 + CON",
        "pm_inicial_multiplicador": 1, "pm_por_nivel_multiplicador": 1, # Baseado em 4 + SAB e 2 + SAB
        "pericias_treinadas_escolha": {
            "quantidade": 4,
            "opcoes": ["Furtividade", "Sobrevivência", "Investigação", "Intuição", "Acrobatismo", "Atletismo", "Reflexos", "Ladinagem", "Iniciativa"]
        },
        "base": [
            {"nivel_req": 1, "nome": "Sentidos Aguçados", "descricao": "Treinado em Percepção e Iniciativa. Vantagem em Percepção para notar perigos escondidos.", "tipo": "Passiva de Classe", "acao": "Passiva"},
            {"nivel_req": 1, "nome": "Movimento do Explorador", "descricao": "Gaste 1 PM (ação livre) para ignorar penalidades de desloc. por terreno difícil até fim do turno.", "custo": "1 PM", "acao": "Ação Livre", "tipo": "Habilidade de Classe"},
            {"nivel_req": 1, "nome": "Arquétipo de Vigilância", "descricao": "Escolha Rastreador dos Ermos, Lâmina do Crepúsculo ou Olho Vigilante.", "tipo": "Escolha de Subclasse", "acao": "Passiva"},
        ],
        "subclasses": {
            "Rastreador dos Ermos": { # Atributo Chave Habilidades: SAB (implícito da classe base)
                "habilidades": [
                    {"nivel_req": 1, "nome": "Passo Leve na Mata", "descricao": "Ignora penalidades desloc. por terreno difícil natural. Treinado em Sobrevivência.", "tipo": "Passiva de Arquétipo", "acao": "Passiva"},
                    {"nivel_req": 1, "nome": "Marca do Caçador", "descricao": "(Ação Bônus) Escolha criatura visível (18m). Vantagem em Sobrevivência para rastrear e Intuição para intenções. 1 alvo por vez. Dura cena/1h.", "custo": "1 PM", "acao": "Ação Bônus", "alcance": "18m", "tipo": "Habilidade de Arquétipo", "grupo_escolha": "rastreador_lvl1", "limite_escolha": 2},
                    {"nivel_req": 1, "nome": "Disparo Preciso", "descricao": "(Ação) Com ataque à distância (arma), gaste 1 PM antes de rolar. Se acertar, dano +1d4, alvo TR FOR (CD Normal) ou desloc. -3m até fim próx. turno.", "custo": "1 PM", "acao": "Ação Padrão", "tipo": "Habilidade de Arquétipo", "grupo_escolha": "rastreador_lvl1", "limite_escolha": 2},
                    {"nivel_req": 1, "nome": "Armadilha Improvisada", "descricao": "(Ação) Cria armadilha em espaço adj. Primeira criatura M/P TR DES (CD Normal) ou Imobilizada (ação para TR FOR/DES vs CD).", "custo": "2 PM", "acao": "Ação Padrão", "tipo": "Habilidade de Arquétipo", "grupo_escolha": "rastreador_lvl1", "limite_escolha": 2},
                    {"nivel_req": 1, "nome": "Companheiro Animal (Elo Menor)", "descricao": "(Requer Descanso Longo) Forma elo com animal P/M comum. Não combativo. Realiza tarefas simples. Age no seu turno, PV próprios.", "custo": "1 PM", "acao": "Descanso Longo", "tipo": "Habilidade de Arquétipo", "grupo_escolha": "rastreador_lvl1", "limite_escolha": 2},
                ]
            },
            "Lâmina do Crepúsculo": { # Atributo Chave Habilidades: Destreza (para habilidades da subclasse)
                "habilidades": [
                    {"nivel_req": 1, "nome": "Dança das Sombras", "descricao": "Em penumbra/escuridão, desloc. +1,5m. Treinado em Furtividade.", "tipo": "Passiva de Arquétipo", "acao": "Passiva"},
                    {"nivel_req": 1, "nome": "Golpe Desorientador", "descricao": "(Ação) Ao acertar ataque corpo a corpo (arma DES), alvo TR SAB (CD Normal) ou desvantagem no próx. ataque.", "custo": "1 PM", "acao": "Ação Padrão", "tipo": "Habilidade de Arquétipo", "grupo_escolha": "lamina_crepusculo_lvl1", "limite_escolha": 2},
                    {"nivel_req": 1, "nome": "Passo Fantasma", "descricao": "(Ação Bônus) Até fim do turno, movimento não provoca Ataque de Oportunidade, pode mover através de hostis.", "custo": "1 PM", "acao": "Ação Bônus", "tipo": "Habilidade de Arquétipo", "grupo_escolha": "lamina_crepusculo_lvl1", "limite_escolha": 2},
                    {"nivel_req": 1, "nome": "Ataque Furtivo", "descricao": "(Ação Bônus) Gaste 1 PM para aumentar dado de dano em 1d4, se não estiver na visão do alvo.", "custo": "1 PM", "acao": "Ação Bônus", "tipo": "Habilidade de Arquétipo", "grupo_escolha": "lamina_crepusculo_lvl1", "limite_escolha": 2},
                    {"nivel_req": 1, "nome": "Visão Crepuscular", "descricao": "(Ação Bônus) Ganha Visão no Escuro 9m por 1h. Se já tem, alcance +9m.", "custo": "1 PM", "acao": "Ação Bônus", "tipo": "Habilidade de Arquétipo", "grupo_escolha": "lamina_crepusculo_lvl1", "limite_escolha": 2},
                ]
            },
            "Olho Vigilante": { # Atributo Chave Habilidades: Inteligência (para habilidades da subclasse)
                "habilidades": [
                    {"nivel_req": 1, "nome": "Análise Tática", "descricao": "Treinado em Investigação. Pode usar INT para Iniciativa.", "tipo": "Passiva de Arquétipo", "acao": "Passiva"},
                    {"nivel_req": 1, "nome": "Estudar Oponente", "descricao": "(Ação Bônus) TR INT ou INV vs criatura (9m). Sucesso Normal: info básica. Bom/Extremo: vulnerabilidade/resistência/tática. Vantagem no próx. ataque.", "custo": "1 PM", "acao": "Ação Bônus", "alcance": "9m", "tipo": "Habilidade de Arquétipo", "grupo_escolha": "olho_vigilante_lvl1", "limite_escolha": 2},
                    {"nivel_req": 1, "nome": "Antecipar Movimento", "descricao": "(Reação) Quando hostil move para adj., mova 1,5m (sem AdO). Não pode terminar adj. ao hostil.", "custo": "1 PM", "acao": "Reação", "tipo": "Habilidade de Arquétipo", "grupo_escolha": "olho_vigilante_lvl1", "limite_escolha": 2},
                    {"nivel_req": 1, "nome": "Ponto Fraco", "descricao": "(Ação Bônus) Gaste 1 PM, alvo atingido tem desvantagem no próx. TR CON.", "custo": "1 PM", "acao": "Ação Bônus", "tipo": "Habilidade de Arquétipo", "grupo_escolha": "olho_vigilante_lvl1", "limite_escolha": 2}, # Note que na p.26 é "IPM", assumindo erro de digitação e que é 1 PM.
                    {"nivel_req": 1, "nome": "Leitura Rápida", "descricao": "(Ação) Examina texto/cena. Vantagem no próx. TR INV ou CONH relacionado (1h).", "custo": "1 PM", "acao": "Ação Padrão", "tipo": "Habilidade de Arquétipo", "grupo_escolha": "olho_vigilante_lvl1", "limite_escolha": 2},
                ]
            }
        }
    },
    "Elo": {
        "atributo_chave_pm_base": "Carisma",
        "pv_inicial": "8 + CON", "pv_por_nivel": "2 + CON",
        "pm_inicial_multiplicador": 1, "pm_por_nivel_multiplicador": 1, # Baseado em 6 + CAR e 4 + CAR
        "pericias_treinadas_escolha": {
            "quantidade": 4,
            "opcoes": ["Diplomacia", "Enganação", "Intuição", "Atuação", "Cura", "Religião", "Vontade", "Percepção"]
        },
        "base": [
            {"nivel_req": 1, "nome": "Presença Inspiradora", "descricao": "Treinado em Diplomacia. Aliados a 3m (que veem/ouvem) +1 TR vs medo.", "tipo": "Passiva de Classe", "acao": "Passiva"},
            {"nivel_req": 1, "nome": "Elo Empático", "descricao": "(Ação, Toque) Gaste 1 PM para: Sentir Emoção superficial OU Alvo recebe PV Temp = CAR (mín 1).", "custo": "1 PM", "acao": "Ação Padrão", "alcance": "Toque", "tipo": "Habilidade de Classe"},
            {"nivel_req": 1, "nome": "Arquétipo de Ligação", "descricao": "Escolha Voz da Harmonia, Porta-Voz da Chama ou Guardião do Coração.", "tipo": "Escolha de Subclasse", "acao": "Passiva"},
        ],
        "subclasses": {
            "Voz da Harmonia": {
                "habilidades": [
                    {"nivel_req": 1, "nome": "Aura Pacificadora", "descricao": "Hostis adj. (que não sofreram hostilidade sua) desvantagem na 1ª jogada de ataque no turno.", "tipo": "Passiva de Arquétipo", "acao": "Passiva"},
                    {"nivel_req": 1, "nome": "Palavra Calmante", "descricao": "(Ação) Alvo (9m, ouve) TR Vontade (CD Normal) ou não pode realizar ações hostis no próx. turno.", "custo": "1 PM", "acao": "Ação Padrão", "alcance": "9m", "tipo": "Habilidade de Arquétipo", "grupo_escolha": "voz_harmonia_lvl1", "limite_escolha": 2},
                    {"nivel_req": 1, "nome": "Negociação Persuasiva", "descricao": "(Ação Bônus) Vantagem no próx. TR Diplomacia (até fim próx. turno).", "custo": "1 PM", "acao": "Ação Bônus", "alcance": "Pessoal", "tipo": "Habilidade de Arquétipo", "grupo_escolha": "voz_harmonia_lvl1", "limite_escolha": 2},
                    {"nivel_req": 1, "nome": "Elo Empático (Sentir Verdade)", "descricao": "(Ação, 3m) TR Intuição oposto por Enganação do alvo. Se vencer, sabe se alvo mentiu no último minuto. (Substitui efeito normal de Elo Empático).", "custo": "1 PM", "acao": "Ação Padrão", "alcance": "3m", "tipo": "Habilidade de Arquétipo", "grupo_escolha": "voz_harmonia_lvl1", "limite_escolha": 2},
                    {"nivel_req": 1, "nome": "Discurso Conciliador", "descricao": "(Ação, 9m) Você e até CAR aliados (que ouvem) Vantagem no próx. TR perícia social (10 min).", "custo": "2 PM", "acao": "Ação Padrão", "alcance": "9m", "tipo": "Habilidade de Arquétipo", "grupo_escolha": "voz_harmonia_lvl1", "limite_escolha": 2},
                ]
            },
            "Porta-Voz da Chama": {
                "habilidades": [
                    {"nivel_req": 1, "nome": "Foco na Performance", "descricao": "Treinado em Atuação. Pode usar Atuação no lugar de Diplomacia (inspirar/acalmar multidão) ou Intimidação (incitar grupo com discurso).", "tipo": "Passiva de Arquétipo", "acao": "Passiva"},
                    {"nivel_req": 1, "nome": "Comando de Batalha", "descricao": "(Ação Bônus, 9m) Aliado (ouve) usa Reação para mover metade desloc. OU fazer 1 ataque.", "custo": "1 PM", "acao": "Ação Bônus", "alcance": "9m", "tipo": "Habilidade de Arquétipo", "grupo_escolha": "porta_voz_chama_lvl1", "limite_escolha": 2},
                    {"nivel_req": 1, "nome": "Grito Motivador", "descricao": "(Ação, Raio 3m) Você e até CAR aliados (ouvem) ganham 1d6 + CAR PV Temporários.", "custo": "2 PM", "acao": "Ação Padrão", "alcance": "Raio 3m", "tipo": "Habilidade de Arquétipo", "grupo_escolha": "porta_voz_chama_lvl1", "limite_escolha": 2},
                    {"nivel_req": 1, "nome": "Performance Revigorante", "descricao": "(Pausa) Performance inspiradora (descanso breve). Até CAR aliados (ouviram) recuperam PV como descanso curto (sem gastar tempo). 1/descanso longo.", "custo": "2 PM", "acao": "Pausa (durante Descanso Curto)", "tipo": "Habilidade de Arquétipo", "grupo_escolha": "porta_voz_chama_lvl1", "limite_escolha": 2},
                    {"nivel_req": 1, "nome": "Elo Protetor (Aura)", "descricao": "(Ação Bônus) Aliados (incluindo você) a 3m recebem +1 RD vs ataques. Duração: Concentração.", "custo": "2 PM por turno", "acao": "Ação Bônus", "alcance": "Pessoal (Aura 3m)", "tipo": "Habilidade de Arquétipo", "grupo_escolha": "porta_voz_chama_lvl1", "limite_escolha": 2},
                ]
            },
            "Guardião do Coração": {
                "habilidades": [
                    {"nivel_req": 1, "nome": "Escudo Empático", "descricao": "Treinado em Cura. Você e aliados a 1,5m +1 TR Vontade vs medo/desespero.", "tipo": "Passiva de Arquétipo", "acao": "Passiva"},
                    {"nivel_req": 1, "nome": "Toque Restaurador Aprimorado", "descricao": "(Ação, Toque) Ao usar Elo Empático (Alívio Menor), alvo também recupera 1d6 PV reais.", "custo": "2 PM", "acao": "Ação Padrão", "alcance": "Toque", "tipo": "Habilidade de Arquétipo", "grupo_escolha": "guardiao_coracao_lvl1", "limite_escolha": 2},
                    {"nivel_req": 1, "nome": "Vínculo Protetor", "descricao": "(Ação, 9m) Cria vínculo com aliado. Se aliado sofrer dano, use Reação para sofrer metade do dano no lugar dele. Termina se >9m, inconsciente ou usado em outro. Duração: Concentração.", "custo": "2 PM por turno", "acao": "Ação Padrão", "alcance": "9m", "tipo": "Habilidade de Arquétipo", "grupo_escolha": "guardiao_coracao_lvl1", "limite_escolha": 2},
                    {"nivel_req": 1, "nome": "Palavras de Conforto", "descricao": "(Ação, 9m) Aliado (ouve) com condição mental menor (Ex: Amedrontado) faz novo TR Vontade vs efeito, com vantagem.", "custo": "1 PM", "acao": "Ação Padrão", "alcance": "9m", "tipo": "Habilidade de Arquétipo", "grupo_escolha": "guardiao_coracao_lvl1", "limite_escolha": 2},
                    {"nivel_req": 1, "nome": "Detectar Dor/Aflição", "descricao": "(Ação) Por min, Vantagem em Intuição/Percepção para detectar criaturas feridas, doentes, etc. (9m), mesmo escondidas (não através de barreiras).", "custo": "1 PM", "acao": "Ação Padrão", "alcance": "Pessoal (9m)", "tipo": "Habilidade de Arquétipo", "grupo_escolha": "guardiao_coracao_lvl1", "limite_escolha": 2},
                ]
            }
        }
    }
}

if __name__ == '__main__':
    # Teste para verificar a estrutura e algumas habilidades
    for classe_nome, classe_data_val in ABILITIES_DATA.items():
        if not isinstance(classe_data_val, dict): continue # Adicionado para segurança
        print(f"CLASSE: {classe_nome}")
        print(f"  Atributo Chave PM Base: {classe_data_val.get('atributo_chave_pm_base', 'N/A')}")
        print(f"  PV Inicial: {classe_data_val.get('pv_inicial', 'N/A')}")
        pm_mult = classe_data_val.get('pm_inicial_multiplicador')
        print(f"  PM Inicial Multiplicador: {pm_mult if pm_mult is not None else 'N/A (Usa Vigor)'}")
        print(f"  Vigor Inicial: {classe_data_val.get('vigor_inicial', 'N/A')}")
        
        base_abilities = classe_data_val.get("base")
        if isinstance(base_abilities, list):
            print("  Habilidades Base (Nível 1):")
            for hab in base_abilities:
                if isinstance(hab, dict) and hab.get("nivel_req") == 1:
                    print(f"    - {hab.get('nome')}: {str(hab.get('descricao',''))[:50]}... "
                          f"(Custo: {hab.get('custo', hab.get('acao', 'Passiva'))})") # Mostra ação se custo N/A
        
        subclasses_data = classe_data_val.get("subclasses")
        if isinstance(subclasses_data, dict):
            print("  Subclasses (Nível 1 - Exemplos de Habilidades):")
            for sub_nome, sub_data_val in subclasses_data.items():
                if not isinstance(sub_data_val, dict): continue
                print(f"    Subclasse: {sub_nome}")
                sub_habilidades = sub_data_val.get("habilidades")
                if isinstance(sub_habilidades, list):
                    for hab_sub in sub_habilidades:
                        if isinstance(hab_sub, dict) and hab_sub.get("nivel_req") == 1:
                             print(f"      - {hab_sub.get('nome')}: {str(hab_sub.get('descricao',''))[:40]}... "
                                   f"(Custo: {hab_sub.get('custo', hab_sub.get('acao', 'Passiva'))}, "
                                   f"Grupo: {hab_sub.get('grupo_escolha', 'N/A')})")
        print("-" * 30)