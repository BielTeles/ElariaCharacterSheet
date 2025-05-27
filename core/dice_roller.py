# core/dice_roller.py
import random
import re
from typing import Tuple, List, Optional, Literal, Dict

# Constantes para tipos de rolagem
ROLL_TYPE_NORMAL = "normal"
ROLL_TYPE_ADVANTAGE = "advantage"
ROLL_TYPE_DISADVANTAGE = "disadvantage"

# Constantes para Graus de Sucesso
SUCCESS_EXTREME = "SUCESSO EXTREMO"
SUCCESS_GOOD = "SUCESSO BOM"
SUCCESS_NORMAL = "SUCESSO NORMAL"
FAILURE_NORMAL = "FRACASSO"
FAILURE_EXTREME = "FRACASSO CRÍTICO"

# Padrão Regex para parsear strings de dano como "XdY+Z", "XdY-Z", "XdY", ou "N"
# Grupo 1: (Opcional) Número de dados (X)
# Grupo 2: (Obrigatório se 'd' presente) Tipo de dado (Y)
# Grupo 3: (Opcional) Modificador base completo com sinal (+Z ou -Z)
# Grupo 4: (Alternativa) Dano fixo (N ou +N ou -N)
DAMAGE_STRING_PATTERN = re.compile(
    r"^\s*(?:(\d*)d(\d+)\s*([+-]\s*\d+)?|([+-]?\s*\d+))\s*$"
)


def roll_d20() -> int:
    """Rola um único dado de 20 faces."""
    return random.randint(1, 20)


def get_dice_for_attribute_test(attribute_value: int) -> Tuple[int, str]:
    """
    Determina quantos d20 rolar e se é vantagem ou desvantagem
    baseado no valor do atributo.
    Fonte: Elaria RPG, pág. 6 [cite: 95]

    Args:
        attribute_value: O valor do atributo.

    Returns:
        Uma tupla (num_dice, tipo_de_rolagem), onde tipo_de_rolagem
        pode ser "normal", "advantage", ou "disadvantage".
    """
    if attribute_value <= -1:
        return 2, ROLL_TYPE_DISADVANTAGE  # 2d20, pega o MENOR [cite: 95]
    elif attribute_value == 0 or attribute_value == 1:
        return 1, ROLL_TYPE_NORMAL  # 1d20 [cite: 95]
    elif attribute_value == 2 or attribute_value == 3:
        return 2, ROLL_TYPE_ADVANTAGE  # 2d20, pega o MAIOR [cite: 95]
    elif attribute_value == 4 or attribute_value == 5:
        return 3, ROLL_TYPE_ADVANTAGE  # 3d20, pega o MAIOR [cite: 95]
    elif attribute_value == 6 or attribute_value == 7:
        return 4, ROLL_TYPE_ADVANTAGE  # 4d20, pega o MAIOR [cite: 95]
    elif attribute_value == 8 or attribute_value == 9:
        return 5, ROLL_TYPE_ADVANTAGE  # 5d20, pega o MAIOR [cite: 95]
    elif attribute_value == 10 or attribute_value == 11:
        return 6, ROLL_TYPE_ADVANTAGE  # 6d20, pega o MAIOR [cite: 95]
    elif attribute_value >= 12:
        return 7, ROLL_TYPE_ADVANTAGE  # 7d20, pega o MAIOR [cite: 95]
    else:  # Caso algo inesperado, padrão para 1d20 normal
        return 1, ROLL_TYPE_NORMAL


def perform_attribute_test_roll(attribute_value: int) -> Tuple[int, List[int]]:
    """
    Realiza a rolagem de dados para um teste de atributo,
    considerando vantagem/desvantagem.

    Args:
        attribute_value: O valor do atributo sendo testado.

    Returns:
        Uma tupla contendo (resultado_final_do_d20, lista_de_todas_as_rolagens).
        O resultado_final_do_d20 é o valor a ser usado para determinar o sucesso.
    """
    num_dice, roll_type = get_dice_for_attribute_test(attribute_value)
    rolls = [roll_d20() for _ in range(num_dice)]

    final_roll: int
    if roll_type == ROLL_TYPE_ADVANTAGE:
        final_roll = max(rolls)
    elif roll_type == ROLL_TYPE_DISADVANTAGE:
        final_roll = min(rolls)
    else:  # ROLL_TYPE_NORMAL
        final_roll = rolls[0]
    return final_roll, rolls


# Fonte: Elaria RPG, Apêndice A, pág. 56 [cite: 1098]
SUCCESS_CHART: Dict[int, Dict[str, int]] = {
    1: {"Normal": 20, "Bom": float('inf'), "Extremo": float('inf')},
    2: {"Normal": 19, "Bom": 20, "Extremo": float('inf')},
    3: {"Normal": 18, "Bom": 20, "Extremo": float('inf')},
    4: {"Normal": 17, "Bom": 19, "Extremo": float('inf')},
    5: {"Normal": 16, "Bom": 19, "Extremo": 20},
    6: {"Normal": 15, "Bom": 18, "Extremo": 20}, # [cite: 1098]
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
    20: {"Normal": 2, "Bom": 11, "Extremo": 16}, # [cite: 1098]
}

# Adicionando uma forma de lidar com valores de habilidade > 20 e < 1
for i in range(21, 31):  # Exemplo até 30, ajuste se o sistema permitir valores maiores.
    if i not in SUCCESS_CHART:
        SUCCESS_CHART[i] = SUCCESS_CHART[20] # Valores > 20 usam a linha do 20.
# Para Valor de Perícia 0 (não treinado)[cite: 648, 650], usa-se a linha do Valor 1, tornando sucesso difícil.
SUCCESS_CHART[0] = SUCCESS_CHART[1]


def check_success(skill_value: int, d20_roll_result: int, natural_roll_for_crit_check: int) -> str:
    """
    Verifica o grau de sucesso de um teste.
    Fonte: Elaria RPG, pág. 39[cite: 760], Apêndice A[cite: 1098].

    Args:
        skill_value: O Valor da Perícia (ou Atributo para testes puros).
        d20_roll_result: O resultado final do d20 após vantagem/desvantagem.
        natural_roll_for_crit_check: O valor do dado que foi efetivamente usado
                                       (importante para Fracasso/Sucesso Extremo).

    Returns:
        Uma string indicando o Grau de Sucesso.
    """
    # Fracasso Extremo: Um 1 natural no d20 rolado é sempre um Fracasso Extremo [cite: 33, 764]
    if natural_roll_for_crit_check == 1:
        return FAILURE_EXTREME

    # Um 20 natural no d20 usado é um Sucesso Extremo para o ataque [cite: 838]
    # e para testes gerais[cite: 760].
    if natural_roll_for_crit_check == 20:
        return SUCCESS_EXTREME

    # Garante que usamos uma linha válida da tabela, tratando valores fora do intervalo comum.
    # skill_value pode ser 0 para perícias não treinadas.
    # A chave para SUCCESS_CHART deve ser um int.
    chart_skill_value = max(0, min(30, int(skill_value))) # Limita ao intervalo da tabela (0-30)
    targets = SUCCESS_CHART.get(chart_skill_value, SUCCESS_CHART[0]) # Fallback para linha 0 se algo der errado

    if d20_roll_result >= targets["Extremo"]:
        return SUCCESS_EXTREME
    elif d20_roll_result >= targets["Bom"]:
        return SUCCESS_GOOD
    elif d20_roll_result >= targets["Normal"]:
        return SUCCESS_NORMAL
    else:
        # Qualquer resultado abaixo do Sucesso Normal, que não seja um 1 natural, é Fracasso Normal [cite: 32]
        return FAILURE_NORMAL


def roll_generic_dice(num_dice: int, dice_type: int) -> Tuple[List[int], int]:
    """
    Rola uma quantidade específica de um tipo de dado. Ex: 3d4, 2d6, 1d10.

    Args:
        num_dice: A quantidade de dados a serem rolados.
        dice_type: O número de faces do dado (ex: 4, 6, 20).

    Returns:
        Uma tupla (list_of_rolls, total_sum).
        Retorna ([], 0) se os inputs forem inválidos.
    """
    if not isinstance(num_dice, int) or num_dice < 0 or \
       not isinstance(dice_type, int) or dice_type <= 0:
        if num_dice == 0 and dice_type == 0: # Permitir "0d0" para dano puramente de modificador
            return [], 0
        return [], 0  # Inputs inválidos

    rolls: List[int] = []
    total_sum = 0
    if num_dice > 0: # Só rola se houver dados a rolar
        for _ in range(num_dice):
            roll = random.randint(1, dice_type)
            rolls.append(roll)
            total_sum += roll
    return rolls, total_sum


def parse_and_roll_damage_string(damage_string: str, static_modifier: int = 0) -> Tuple[Optional[List[int]], int, int]:
    """
    Interpreta uma string de dano (ex: "1d8", "2d6+2", "1d4-1", "5") e rola os dados.

    Args:
        damage_string: A string representando o dano.
        static_modifier: Um modificador estático adicional a ser somado ao total.

    Returns:
        Uma tupla (list_of_rolls, total_sum_before_additional_mod, final_sum_with_all_mods).
        Retorna (None, 0, 0) se a string de dano for inválida.
    """
    if not isinstance(damage_string, str) or not damage_string.strip():
        return None, 0, 0

    match = DAMAGE_STRING_PATTERN.match(damage_string.strip())
    if not match:
        # Se a string não corresponder ao padrão, não é uma string de dano válida
        return None, 0, 0

    num_dice_str, dice_type_str, base_modifier_str, fixed_damage_str = match.groups()

    num_dice = 0
    dice_type = 0
    base_modifier = 0

    if fixed_damage_str is not None: # Formato "N" (dano fixo)
        try:
            base_modifier = int(fixed_damage_str.replace(" ", ""))
        except ValueError:
            return None, 0, 0 # String inválida se não for um número
    elif dice_type_str is not None: # Formato XdY[+-Z]
        try:
            num_dice = int(num_dice_str) if num_dice_str else 1
            dice_type = int(dice_type_str)
            if base_modifier_str:
                base_modifier = int(base_modifier_str.replace(" ", ""))
        except ValueError:
            return None, 0, 0 # Partes numéricas inválidas
    else:
        # Caso não previsto pelo regex, deve ser tratado como erro
        return None, 0, 0

    if num_dice < 0 or dice_type < 0: # Não pode ter dados ou tipo de dado negativo
         return None, 0, 0
    if num_dice > 0 and dice_type == 0: # "Xd" é inválido
        return None, 0, 0


    rolls, sum_of_rolls = roll_generic_dice(num_dice, dice_type)

    total_before_additional_mod = sum_of_rolls + base_modifier
    final_sum_with_all_mods = total_before_additional_mod + static_modifier

    # Regra comum: dano mínimo 0 (ou 1 se o sistema preferir para acertos que causam dano)
    # Por enquanto, vamos permitir 0, mas não negativo.
    if final_sum_with_all_mods < 0:
        final_sum_with_all_mods = 0

    return rolls if num_dice > 0 else [], total_before_additional_mod, final_sum_with_all_mods


if __name__ == "__main__":
    print("Testando o Rolador de Dados de Elaria RPG:")

    print("\n--- Teste de Atributo (perform_attribute_test_roll) ---")
    test_attributes = [-2, 0, 1, 3, 5, 7, 9, 11, 12]
    for attr_val in test_attributes:
        final_d20, all_rolls = perform_attribute_test_roll(attr_val)
        num_dice_expected, roll_type_expected = get_dice_for_attribute_test(attr_val)
        print(f"Atributo {attr_val} (Esperado: {num_dice_expected}d20, {roll_type_expected}): "
              f"Rolagens={all_rolls}, Resultado Final d20={final_d20}")

    print("\n--- Teste da Planilha de Sucessos (check_success) ---")
    # Exemplo do livro: Lyra, Atletismo 6, rolou 15 [cite: 37]
    skill_val_lyra = 6
    d20_lyra = 15 # Sucesso Normal (Normal 15+, Bom 18+, Extremo 20) [cite: 39, 41]
    print(f"Exemplo Lyra: Perícia {skill_val_lyra}, d20={d20_lyra} (natural) -> "
          f"{check_success(skill_val_lyra, d20_lyra, d20_lyra)}")

    # Outros testes
    print(f"Perícia 10, d20=10 (nat) -> {check_success(10, 10, 10)}")  # Fracasso Normal
    print(f"Perícia 10, d20=11 (nat) -> {check_success(10, 11, 11)}")  # Sucesso Normal
    print(f"Perícia 10, d20=16 (nat) -> {check_success(10, 16, 16)}")  # Sucesso Bom
    print(f"Perícia 10, d20=19 (nat) -> {check_success(10, 19, 19)}")  # Sucesso Extremo
    print(f"Perícia 10, d20=20 (nat) -> {check_success(10, 20, 20)}")  # Sucesso Extremo (por ser 20 natural)
    print(f"Perícia 10, d20=1 (nat) -> {check_success(10, 1, 1)}")    # Fracasso Extremo
    print(f"Perícia 0, d20=19 (nat) -> {check_success(0, 19, 19)}")   # Fracasso Normal (linha do 1: Normal é 20)
    print(f"Perícia 0, d20=20 (nat) -> {check_success(0, 20, 20)}")   # Sucesso Extremo (por ser 20 natural)

    print("\n--- Teste de Rolagem Genérica (roll_generic_dice) ---")
    test_rolls_generic = [
        (3, 4), (1, 20), (2, 6), (4, 10),
        (0, 6), (2, 0), (0,0) # inválidos ou casos especiais
    ]
    for n_dice, d_type in test_rolls_generic:
        rolls, total = roll_generic_dice(n_dice, d_type)
        if not (n_dice < 0 or d_type <= 0 and n_dice > 0): # Se não for input claramente inválido
            print(f"Rolando {n_dice}d{d_type}: Rolagens={rolls}, Soma={total}")
        else:
            print(f"Tentativa de rolar {n_dice}d{d_type}: Input inválido (esperado).")

    print("\n--- Teste de Parse e Rolagem de Dano (parse_and_roll_damage_string) ---")
    damage_tests = [
        ("1d8", 0), ("2d6+2", 0), ("1d4-1", 0), ("d10", 0), ("3d4", 2),
        ("1d12+1", -1), ("10", 0), ("+5", 2), ("-3", 1), ("d6+1",0),
        ("2d10-3", 1), ("  2d4 + 1  ", 0), ("-5",0), ("+0",0), ("0",0),
        ("abc", 0), ("1d", 0), ("d",0), ("2d6+",0), ("2d0", 0), ("-1d6",0)
    ]
    for dmg_str, mod in damage_tests:
        rolls, total_base, final_total = parse_and_roll_damage_string(dmg_str, mod)
        if rolls is not None:
            print(f"Dano: '{dmg_str}' + Mod. Estático: {mod} -> "
                  f"Rolagens: {rolls}, Total Base: {total_base}, Total Final: {final_total}")
        else:
            print(f"Dano: '{dmg_str}' + Mod. Estático: {mod} -> STRING INVÁLIDA")