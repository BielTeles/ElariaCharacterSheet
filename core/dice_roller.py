import random

def roll_d20():
    """Rola um único dado de 20 faces."""
    return random.randint(1, 20)

def get_dice_for_attribute_test(attribute_value):
    """
    Determina quantos d20 rolar e se é vantagem ou desvantagem
    baseado no valor do atributo.
    Retorna (num_dice, "normal" | "advantage" | "disadvantage").
    Fonte: Elaria RPG, pág. 6 [cite: 95]
    """
    if attribute_value <= -1:
        return 2, "disadvantage"  # 2d20, pega o MENOR
    elif attribute_value == 0 or attribute_value == 1:
        return 1, "normal"       # 1d20
    elif attribute_value == 2 or attribute_value == 3:
        return 2, "advantage"    # 2d20, pega o MAIOR
    elif attribute_value == 4 or attribute_value == 5:
        return 3, "advantage"    # 3d20, pega o MAIOR
    elif attribute_value == 6 or attribute_value == 7:
        return 4, "advantage"    # 4d20, pega o MAIOR
    elif attribute_value == 8 or attribute_value == 9:
        return 5, "advantage"    # 5d20, pega o MAIOR
    elif attribute_value == 10 or attribute_value == 11:
        return 6, "advantage"    # 6d20, pega o MAIOR
    elif attribute_value >= 12:
        return 7, "advantage"    # 7d20, pega o MAIOR
    else: # Caso algo inesperado, padrão para 1d20 normal
        return 1, "normal"


def perform_attribute_test_roll(attribute_value):
    """
    Realiza a rolagem de dados para um teste de atributo,
    considerando vantagem/desvantagem.
    Retorna o resultado final do d20 a ser usado e o resultado natural original
    (importante para Fracasso Extremo se for 1 no dado efetivamente usado).
    """
    num_dice, roll_type = get_dice_for_attribute_test(attribute_value)
    rolls = [roll_d20() for _ in range(num_dice)]

    if roll_type == "advantage":
        final_roll = max(rolls)
        # Se múltiplos dados resultaram no máximo (ex: dois 20s),
        # o "dado efetivamente usado" para a regra do 1 natural ainda é esse valor.
        # A regra do Fracasso Extremo (pág. 3 [cite: 33]) diz "Um 1 natural no d20 ROLADO".
        # Se a VANTAGEM evitou um 1, ótimo. Se o MAIOR resultado foi 1, então é 1.
        # A questão é qual "d20 rolado" se refere quando há múltiplos.
        # Interpretando como o dado selecionado após vantagem/desvantagem.
        # Se max(rolls) for 1, então o "dado efetivamente usado" é 1.
        return final_roll, rolls # Retornamos todos os rolls para possível log ou verificação
    elif roll_type == "disadvantage":
        final_roll = min(rolls)
        return final_roll, rolls
    else: # "normal"
        return rolls[0], rolls

# --- Lógica da Planilha de Sucessos ---

# Fonte: Elaria RPG, Apêndice A, pág. 56 [cite: 1098]
SUCCESS_CHART = {
    1: {"Normal": 20, "Bom": float('inf'), "Extremo": float('inf')}, # X é infinito
    2: {"Normal": 19, "Bom": 20, "Extremo": float('inf')},
    3: {"Normal": 18, "Bom": 20, "Extremo": float('inf')},
    4: {"Normal": 17, "Bom": 19, "Extremo": float('inf')},
    5: {"Normal": 16, "Bom": 19, "Extremo": 20},
    6: {"Normal": 15, "Bom": 18, "Extremo": 20},
    7: {"Normal": 14, "Bom": 18, "Extremo": 20},
    8: {"Normal": 13, "Bom": 17, "Extremo": 20},
    9: {"Normal": 12, "Bom": 17, "Extremo": 20},
    10: {"Normal": 11, "Bom": 16, "Extremo": 19},
    11: {"Normal": 10, "Bom": 16, "Extremo": 19},
    12: {"Normal": 9, "Bom": 15, "Extremo": 19},
    13: {"Normal": 8, "Bom": 15, "Extremo": 19},
    14: {"Normal": 7, "Bom": 14, "Extremo": 18},
    15: {"Normal": 6, "Bom": 14, "Extremo": 18},
    16: {"Normal": 5, "Bom": 13, "Extremo": 18},
    17: {"Normal": 4, "Bom": 13, "Extremo": 18},
    18: {"Normal": 3, "Bom": 12, "Extremo": 17},
    19: {"Normal": 2, "Bom": 12, "Extremo": 17},
    20: {"Normal": 2, "Bom": 11, "Extremo": 16},
    # Valores de Habilidade acima de 20 podem seguir o padrão do 20,
    # ou você pode definir uma regra de progressão se o livro especificar.
    # Por agora, vamos fazer com que valores > 20 usem a linha do 20.
}

# Adicionando uma forma de lidar com valores de habilidade > 20 e < 1
for i in range(21, 31): # Exemplo até 30, ajuste se necessário
    if i not in SUCCESS_CHART:
        SUCCESS_CHART[i] = SUCCESS_CHART[20]
# Para valores de habilidade < 1 (ex: 0 ou negativos, que não deveriam ocorrer para VALOR DE PERÍCIA)
# O livro especifica que Valor de Perícia vai de 0 (não treinado) a 20+ [cite: 648]
# E ser treinado começa com Valor 1[cite: 652]. Testes puros de atributo poderiam ser 0.
# A planilha do livro começa em 1. Se for um teste puro de atributo com valor 0,
# o livro não especifica qual linha usar. Vamos assumir que 0 usa a linha do 1,
# tornando o sucesso muito difícil (apenas com 20 natural).
SUCCESS_CHART[0] = SUCCESS_CHART[1]


def check_success(skill_value, d20_roll_result, natural_roll_for_crit_fail_check):
    """
    Verifica o grau de sucesso de um teste.
    skill_value: O Valor da Perícia (ou Atributo para testes puros).
    d20_roll_result: O resultado final do d20 após vantagem/desvantagem.
    natural_roll_for_crit_fail_check: O valor do dado que foi efetivamente selecionado (para checar o 1 natural).
                                      No caso de 1d20, é o próprio d20_roll_result.
                                      No caso de vantagem/desvantagem, é o dado que foi escolhido (max/min).
    Retorna uma string: "Fracasso Extremo", "Fracasso Normal", "Sucesso Normal", "Sucesso Bom", "Sucesso Extremo".
    """
    # Fracasso Extremo: Um 1 natural no d20 rolado é sempre um Fracasso Extremo [cite: 33]
    # O "d20 rolado" aqui é o resultado efetivamente usado após vantagem/desvantagem.
    if natural_roll_for_crit_fail_check == 1: # Checa o dado efetivamente usado
        return "Fracasso Extremo"

    # Sucesso Extremo por 20 natural [cite: 760] (O livro diz "Você rolou um 20 natural OU seu resultado...")
    # Esta regra se aplica ao Teste de Ataque para Acerto Crítico (pág. 42 [cite: 838]).
    # Para testes gerais, a pág. 3 [cite: 760] foca no resultado do d20 vs a planilha.
    # Vamos manter a regra do 20 natural como Sucesso Extremo para consistência, a menos que o livro
    # restrinja isso apenas para ataques. A pág. 39 [cite: 760] sugere que um 20 natural É um sucesso extremo.

    targets = SUCCESS_CHART.get(int(skill_value), SUCCESS_CHART[max(1, min(20, int(skill_value)))]) # Garante que usamos uma linha válida

    if d20_roll_result == 20: # 20 natural no dado final usado é um Sucesso Extremo [cite: 760]
         return "Sucesso Extremo"
    if d20_roll_result >= targets["Extremo"]:
        return "Sucesso Extremo"
    elif d20_roll_result >= targets["Bom"]:
        return "Sucesso Bom"
    elif d20_roll_result >= targets["Normal"]:
        return "Sucesso Normal"
    else:
        # Qualquer resultado no d20 abaixo do necessário para Sucesso Normal é um Fracasso Normal [cite: 32]
        return "Fracasso Normal"

def roll_generic_dice(num_dice, dice_type):
    """
    Rola uma quantidade específica de um tipo de dado.
    Ex: 3d4, 2d6, 1d10.

    Args:
        num_dice (int): A quantidade de dados a serem rolados.
        dice_type (int): O número de faces do dado (ex: 4, 6, 20).

    Returns:
        tuple: (list_of_rolls, total_sum)
               Retorna uma lista com os resultados individuais de cada dado
               e a soma total desses resultados.
               Retorna ([], 0) se os inputs forem inválidos.
    """
    if not isinstance(num_dice, int) or num_dice <= 0 or \
       not isinstance(dice_type, int) or dice_type <= 0:
        return [], 0 # Inputs inválidos

    rolls = []
    total_sum = 0
    for _ in range(num_dice):
        roll = random.randint(1, dice_type)
        rolls.append(roll)
        total_sum += roll
    return rolls, total_sum
  
def parse_and_roll_damage_string(damage_string, static_modifier=0):
    """
    Interpreta uma string de dano (ex: "1d8", "2d6+2", "1d4-1") e rola os dados.

    Args:
        damage_string (str): A string representando o dano (ex: "2d6+3").
        static_modifier (int): Um modificador estático adicional a ser somado ao total.

    Returns:
        tuple: (list_of_rolls, total_sum_before_additional_mod, final_sum_with_all_mods)
               Retorna ([], 0, 0) se a string de dano for inválida.
    """
    if not isinstance(damage_string, str) or not damage_string:
        return [], 0, 0

    original_string = damage_string # Para referência em caso de erro
    num_dice_str = ""
    dice_type_str = ""
    base_modifier_str = ""
    
    has_dice_sep = 'd' in damage_string.lower()
    
    if has_dice_sep:
        parts = damage_string.lower().split('d')
        num_dice_str = parts[0].strip()
        
        # Encontrar o final do tipo de dado e o início do modificador base
        rest_of_string = parts[1]
        modifier_sep_plus = rest_of_string.find('+')
        modifier_sep_minus = rest_of_string.find('-')

        if modifier_sep_plus != -1 and (modifier_sep_minus == -1 or modifier_sep_plus < modifier_sep_minus):
            dice_type_str = rest_of_string[:modifier_sep_plus].strip()
            base_modifier_str = rest_of_string[modifier_sep_plus:].strip()
        elif modifier_sep_minus != -1 and (modifier_sep_plus == -1 or modifier_sep_minus < modifier_sep_plus):
            dice_type_str = rest_of_string[:modifier_sep_minus].strip()
            base_modifier_str = rest_of_string[modifier_sep_minus:].strip()
        else:
            dice_type_str = rest_of_string.strip()
            base_modifier_str = "" # Nenhum modificador base na string
    else:
        # Caso a string seja apenas um número (dano fixo, sem dados)
        if damage_string.lstrip('-+').isdigit():
            num_dice_str = "0" # Sem dados para rolar
            dice_type_str = "0" # Sem tipo de dado
            base_modifier_str = damage_string.strip()
        else:
            print(f"Erro: String de dano '{original_string}' inválida (formato esperado 'XdY+Z', 'XdY-Z', 'XdY' ou 'N').")
            return [], 0, 0


    try:
        num_dice = int(num_dice_str) if num_dice_str else 1 # Se XdY, X é 1 se omitido (ex: "d6")
        if not num_dice_str and has_dice_sep: # caso como "d6"
            num_dice = 1
        elif not num_dice_str and not has_dice_sep: # caso como "+5"
             num_dice = 0


        dice_type = int(dice_type_str) if dice_type_str else 0 # Se não houver 'd', não há tipo de dado.
        base_modifier = int(base_modifier_str) if base_modifier_str else 0
    except ValueError:
        print(f"Erro: Não foi possível converter partes da string de dano '{original_string}' para números.")
        return [], 0, 0

    rolls = []
    sum_of_rolls = 0

    if num_dice > 0 and dice_type > 0:
        for _ in range(num_dice):
            roll = random.randint(1, dice_type)
            rolls.append(roll)
            sum_of_rolls += roll
    elif num_dice == 0 and dice_type == 0 and base_modifier_str: # Dano fixo, ex: "5" ou "+5"
        pass # sum_of_rolls já é 0, o modificador base será adicionado
    elif num_dice > 0 and dice_type == 0 : # Ex: "2d" ou "2d0" - inválido
        print(f"Erro: Tipo de dado inválido na string '{original_string}'.")
        return [],0,0
    # Outros casos inválidos são pegos pela conversão para int ou estrutura da string

    total_before_additional_mod = sum_of_rolls + base_modifier
    final_sum_with_all_mods = total_before_additional_mod + static_modifier
    
    # Garante que o dano final não seja negativo, a menos que o jogo permita.
    # Por padrão, vamos definir o mínimo como 0 ou 1 se houve rolagem.
    if final_sum_with_all_mods < 0 and (num_dice > 0 or base_modifier != 0 or static_modifier != 0):
        final_sum_with_all_mods = 0 
    elif final_sum_with_all_mods == 0 and (num_dice > 0 or base_modifier != 0 or static_modifier != 0) : # se o resultado for 0 mas dados foram rolados
        if num_dice > 0: # Se dados foram rolados, o dano mínimo geralmente é 1, a menos que modificadores negativos o zerem
            final_sum_with_all_mods = max(0, final_sum_with_all_mods) # Deixa 0 se os modificadores zerarem, ou 1 se for 1d4-3 por ex e der 1.
                                                                 # Regra comum: dano mínimo 1 se acertar. O livro não especifica. Ajustar se necessário.


    return rolls, total_before_additional_mod, final_sum_with_all_mods

# --- Testes Simples (para rodar diretamente este arquivo) ---
if __name__ == "__main__":
    print("Testando o Rolador de Dados de Elaria RPG:")

    print("\n--- Teste de Atributo (perform_attribute_test_roll) ---")
    test_attributes = [-2, 0, 1, 3, 5, 7, 9, 11, 12]
    for attr_val in test_attributes:
        final_d20, all_rolls = perform_attribute_test_roll(attr_val)
        num_dice_expected, roll_type_expected = get_dice_for_attribute_test(attr_val)
        print(f"Atributo {attr_val} (Esperado: {num_dice_expected}d20, {roll_type_expected}): Rolagens={all_rolls}, Resultado Final d20={final_d20}")

    print("\n--- Teste da Planilha de Sucessos (check_success) ---")
    # Exemplo do livro: Lyra, Atletismo 6, rolou 15 (Normal 15+, Bom 18+, Extremo 20) -> Sucesso Normal
    skill_val_lyra = 6
    d20_lyra = 15
    print(f"Exemplo Lyra: Perícia {skill_val_lyra}, d20={d20_lyra} -> {check_success(skill_val_lyra, d20_lyra, d20_lyra)}")

    # Outros testes
    print(f"Perícia 10, d20=10 -> {check_success(10, 10, 10)}") # Deveria ser Fracasso Normal (Normal é 11+)
    print(f"Perícia 10, d20=11 -> {check_success(10, 11, 11)}") # Sucesso Normal
    print(f"Perícia 10, d20=16 -> {check_success(10, 16, 16)}") # Sucesso Bom
    print(f"Perícia 10, d20=19 -> {check_success(10, 19, 19)}") # Sucesso Extremo
    print(f"Perícia 10, d20=20 -> {check_success(10, 20, 20)}") # Sucesso Extremo (por ser 20 natural)
    print(f"Perícia 10, d20=1 (natural 1) -> {check_success(10, 1, 1)}") # Fracasso Extremo
    print(f"Perícia 20, d20=1 (natural 1) -> {check_success(20, 1, 1)}") # Fracasso Extremo
    print(f"Perícia 20, d20=2 -> {check_success(20, 2, 2)}") # Sucesso Normal
    print(f"Perícia 1, d20=19 -> {check_success(1, 19, 19)}") # Fracasso Normal (Normal é 20)
    print(f"Perícia 1, d20=20 -> {check_success(1, 20, 20)}") # Sucesso Extremo (por ser 20 natural, e também atinge o "Normal" da tabela)

    print("\n--- Teste Completo (Atributo + Planilha) ---")
    test_attr_value = 3 # 2d20, pega o maior
    test_skill_value = 7 # Normal: 14, Bom: 18, Extremo: 20

    final_d20_comp, all_rolls_comp = perform_attribute_test_roll(test_attr_value)
    resultado_final = check_success(test_skill_value, final_d20_comp, final_d20_comp) # Passando final_d20_comp duas vezes para o check de 1 natural
    print(f"Teste: Atributo {test_attr_value}, Perícia {test_skill_value}")
    print(f"Rolagens: {all_rolls_comp}, d20 Usado: {final_d20_comp}")
    print(f"Resultado: {resultado_final}")
    
    print("\n--- Teste de Rolagem Genérica (roll_generic_dice) ---")
    test_rolls_generic = [
        (3, 4),  # 3d4
        (1, 20), # 1d20
        (2, 6),  # 2d6
        (4, 10), # 4d10
        (0, 6),  # inválido
        (2, -4)  # inválido
    ]
    for n_dice, d_type in test_rolls_generic:
        rolls, total = roll_generic_dice(n_dice, d_type)
        if rolls:
            print(f"Rolando {n_dice}d{d_type}: Rolagens={rolls}, Soma={total}")
        else:
            print(f"Tentativa de rolar {n_dice}d{d_type}: Input inválido.")

    print("\n--- Teste de Parse e Rolagem de Dano (parse_and_roll_damage_string) ---")
    damage_tests = [
        ("1d8", 0),
        ("2d6+2", 0),
        ("1d4-1", 0),
        ("d10", 0),       # 1d10
        ("3d4", 2),       # 3d4 + 2 (modificador estático)
        ("1d12+1", -1),   # 1d12 + 1 - 1
        ("10", 0),        # Dano fixo
        ("+5", 2),        # Dano fixo + modificador estático
        ("-3", 1),        # Dano fixo + modificador estático
        ("d6+1",0),
        ("2d10-3", 1),
        ("abc", 0),       # Inválido
        ("1d", 0),        # Inválido
        ("d",0),          # Inválido
        ("2d6+",0)        # Inválido
    ]
    for dmg_str, mod in damage_tests:
        rolls, total_base, final_total = parse_and_roll_damage_string(dmg_str, mod)
        if rolls or (not rolls and (total_base != 0 or final_total !=0) and dmg_str.lstrip('-+').isdigit()): # Se houve rolagens ou é dano fixo válido
            print(f"Dano: '{dmg_str}' + Modificador Estático: {mod} -> Rolagens: {rolls}, Total Base: {total_base}, Total Final: {final_total}")
        elif not rolls and total_base == 0 and final_total == 0 and not dmg_str.lstrip('-+').isdigit() and 'd' not in dmg_str: # String inválida não numérica e sem 'd'
             pass # Já impresso pela função
        elif not dmg_str.lstrip('-+').isdigit() and 'd' not in dmg_str:
            pass # erro já tratado
        elif not rolls and total_base == 0 and final_total == 0 :
             pass # Erro já tratado
