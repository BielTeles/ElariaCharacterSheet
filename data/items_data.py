# ElariaCharacterSheet/data/items_data.py
from typing import List, Dict, Any, Literal, Union

# Moeda: Ef (Elfen de Ouro), EfP (Elfen de Prata)
# 1 Ef = 10 EfP

# Definindo tipos para melhor clareza e manutenção
# Essas strings literais poderiam ser substituídas por constantes de um módulo compartilhado
TipoItemInventario = Literal["arma", "armadura", "escudo", "item_geral"]
CategoriaLoja = Literal["Armas", "Armaduras", "Escudos", "Equipamentos", "Livro/Documento"]

# Estrutura base para itens, pode ser mais específica para cada tipo se necessário
ItemBase = Dict[str, Union[str, int, float]]

# --- ARMAS ---
# Chaves padronizadas para armas, consistentes com tab_combat.py e character.py
# "nome": str
# "custo_ef": int
# "custo_efp": int
# "dano": str (e.g., "1d6", "2d4+FOR")
# "atributo_chave": str (e.g., "FOR", "DES")
# "tipo_dano": str (e.g., "Perf./Corte", "Impacto")
# "empunhadura": str (e.g., "1 Mão", "2 Mãos")
# "alcance": str (e.g., "Corpo a Corpo", "Distância")
# "categoria": str (e.g., "Arma Simples", "Arma Marcial")
# "observacoes": str (opcional)
# "pericia_ataque": str (e.g., "Corpo-a-Corpo", "Pontaria") - Adicionada para consistência com tab_combat

ARMAS_SIMPLES: List[ItemBase] = [
    {
        "nome": "Adaga",
        "custo_ef": 5, "custo_efp": 0,
        "dano": "1d4", "atributo_chave": "DES", "tipo_dano": "Perf./Corte",
        "empunhadura": "1 Mão", "alcance": "Corpo a Corpo", "categoria": "Arma Simples", "pericia_ataque": "Corpo-a-Corpo",
        "observacoes": "Pode ser arremessada (alcance curto)."
    },
    {
        "nome": "Maça Leve",
        "custo_ef": 5, "custo_efp": 0,
        "dano": "1d6", "atributo_chave": "FOR", "tipo_dano": "Impacto",
        "empunhadura": "1 Mão", "alcance": "Corpo a Corpo", "categoria": "Arma Simples", "pericia_ataque": "Corpo-a-Corpo",
        "observacoes": ""
    },
    {
        "nome": "Lança Curta",
        "custo_ef": 5, "custo_efp": 0,
        "dano": "1d6", "atributo_chave": "FOR", "tipo_dano": "Perf.",
        "empunhadura": "1 Mão", "alcance": "Corpo a Corpo", "categoria": "Arma Simples", "pericia_ataque": "Corpo-a-Corpo",
        "observacoes": "Pode ser usada com duas mãos para dano 1d8 (versátil)." # Exemplo de observação
    },
    {
        "nome": "Besta Leve",
        "custo_ef": 25, "custo_efp": 0, # Ajustado preço de exemplo
        "dano": "1d8", "atributo_chave": "DES", "tipo_dano": "Perf.", # Ajustado dano
        "empunhadura": "2 Mãos", "alcance": "Distância (24/96m)", "categoria": "Arma Simples", "pericia_ataque": "Pontaria",
        "observacoes": "Requer ação para recarregar."
    },
]

ARMAS_MARCIAIS: List[ItemBase] = [
    {
        "nome": "Espada Curta",
        "custo_ef": 10, "custo_efp": 0, # Ajustado preço
        "dano": "1d6", "atributo_chave": "DES", "tipo_dano": "Corte/Perf.", # Acuidade implícita com DES
        "empunhadura": "1 Mão", "alcance": "Corpo a Corpo", "categoria": "Arma Marcial", "pericia_ataque": "Corpo-a-Corpo",
        "observacoes": "Acuidade."
    },
    {
        "nome": "Machado de Mão",
        "custo_ef": 5, "custo_efp": 0,
        "dano": "1d6", "atributo_chave": "FOR", "tipo_dano": "Corte",
        "empunhadura": "1 Mão", "alcance": "Corpo a Corpo", "categoria": "Arma Marcial", "pericia_ataque": "Corpo-a-Corpo",
        "observacoes": "Pode ser arremessado (alcance curto)."
    },
    {
        "nome": "Espada Longa",
        "custo_ef": 15, "custo_efp": 0, # Ajustado preço
        "dano": "1d8", "atributo_chave": "FOR", "tipo_dano": "Corte",
        "empunhadura": "1 Mão", "alcance": "Corpo a Corpo", "categoria": "Arma Marcial", "pericia_ataque": "Corpo-a-Corpo",
        "observacoes": "Versátil (1d10 com duas mãos)."
    },
    {
        "nome": "Machado Grande", # Geralmente de duas mãos
        "custo_ef": 30, "custo_efp": 0,
        "dano": "1d12", "atributo_chave": "FOR", "tipo_dano": "Corte",
        "empunhadura": "2 Mãos", "alcance": "Corpo a Corpo", "categoria": "Arma Marcial", "pericia_ataque": "Corpo-a-Corpo",
        "observacoes": "Pesado."
    },
    {
        "nome": "Arco Longo",
        "custo_ef": 50, "custo_efp": 0,
        "dano": "1d8", "atributo_chave": "DES", "tipo_dano": "Perf.",
        "empunhadura": "2 Mãos", "alcance": "Distância (45/180m)", "categoria": "Arma Marcial", "pericia_ataque": "Pontaria",
        "observacoes": "Pesado."
    },
]

# --- ARMADURAS ---
# Chaves: "nome", "custo_ef", "custo_efp", "rd", "tipo_armadura", "penalidade_atributo", "observacoes"
ARMADURAS: List[ItemBase] = [
    {
        "nome": "Couro",
        "custo_ef": 10, "custo_efp": 0, # Ajustado
        "rd": 1, "tipo_armadura": "Leve", "penalidade_atributo": "0",
        "observacoes": "RD base para armaduras leves."
    },
    {
        "nome": "Couro Batido",
        "custo_ef": 45, "custo_efp": 0,
        "rd": 2, "tipo_armadura": "Leve", "penalidade_atributo": "0", # RD um pouco melhor
        "observacoes": ""
    },
    # Gibão de Peles removido para simplificar, similar a Couro
    {
        "nome": "Cota de Malha",
        "custo_ef": 75, "custo_efp": 0, # Ajustado
        "rd": 3, "tipo_armadura": "Média", "penalidade_atributo": "-1 DES (Esquiva Max +2)", # Exemplo de penalidade mais detalhada
        "observacoes": "Desvantagem em Furtividade."
    },
    # Brunea removida, pode ser similar a Cota de Malha ou especializada
    {
        "nome": "Armadura de Placas", # Nome mais comum que "Completa"
        "custo_ef": 1500, "custo_efp": 0, # Armaduras pesadas são caras
        "rd": 4, "tipo_armadura": "Pesada", "penalidade_atributo": "-1 DES (Esquiva Max +0)",
        "observacoes": "Desvantagem em Furtividade. Requer FOR mínima (e.g. 2)."
    },
]

# --- ESCUDOS ---
# Chaves: "nome", "custo_ef", "custo_efp", "rd_bonus_item", "bonus_pericia_bloqueio", "observacoes"
ESCUDOS: List[ItemBase] = [
    {
        "nome": "Escudo Leve (Broquel)", # Mais específico
        "custo_ef": 5, "custo_efp": 0,
        "rd_bonus_item": 0, # Broqueis geralmente não dão RD passiva, mas ajudam no bloqueio
        "bonus_pericia_bloqueio": 1,
        "categoria": "Escudo",
        "observacoes": "Bônus de +1 no Valor da perícia Bloqueio."
    },
    {
        "nome": "Escudo Médio (Redondo/Heater)",
        "custo_ef": 10, "custo_efp": 0,
        "rd_bonus_item": 1, # RD fornecida pelo escudo em si ao ser equipado
        "bonus_pericia_bloqueio": 2,
        "categoria": "Escudo",
        "observacoes": "Concede RD+1 (passivo). Bônus de +2 no Valor da perícia Bloqueio."
    },
]

# --- EQUIPAMENTO GERAL ---
EQUIPAMENTO_GERAL: List[ItemBase] = [
    {"nome": "Corda (15m)", "custo_ef": 1, "custo_efp": 0, "peso_estimado": "Leve", "categoria_loja": "Equipamentos"},
    {"nome": "Tocha (unid.)", "custo_ef": 0, "custo_efp": 1, "peso_estimado": "Mínimo", "categoria_loja": "Equipamentos"}, # Ajustado custo
    {"nome": "Ração de Viagem (dia)", "custo_ef": 0, "custo_efp": 5, "peso_estimado": "Leve", "categoria_loja": "Equipamentos"},
    {"nome": "Kit de Primeiros Socorros", "custo_ef": 25, "custo_efp": 0, "peso_estimado": "Leve", "categoria_loja": "Equipamentos"}, # Nome e preço ajustados
    {"nome": "Saco de Dormir", "custo_ef": 1, "custo_efp": 0, "peso_estimado": "Médio", "categoria_loja": "Equipamentos"}, # Ajustado custo
    {"nome": "Mochila", "custo_ef": 2, "custo_efp": 0, "peso_estimado": "Leve", "categoria_loja": "Equipamentos"},
    {"nome": "Cantil (água)", "custo_ef": 0, "custo_efp": 5, "peso_estimado": "Leve", "categoria_loja": "Equipamentos"}, # Ajustado custo
    {"nome": "Pederneira e Isqueiro", "custo_ef": 0, "custo_efp": 5, "peso_estimado": "Mínimo", "categoria_loja": "Equipamentos"},
    {"nome": "Livro em Branco", "custo_ef": 10, "custo_efp": 0, "peso_estimado": "Leve", "categoria_loja": "Equipamentos"},
    {"nome": "Tinta (frasco) e Pena", "custo_ef": 1, "custo_efp": 0, "peso_estimado": "Mínimo", "categoria_loja": "Equipamentos"},
    {"nome": "História da Paz Dourada", "custo_ef": 3, "custo_efp": 0, "peso_estimado": "Leve", "categoria_loja": "Livro/Documento"},
]

# --- Lista Combinada para a Loja ---
def _preparar_itens_para_loja(lista_itens: List[ItemBase],
                               categoria_loja_padrao: CategoriaLoja,
                               tipo_inventario_padrao: TipoItemInventario) -> List[ItemBase]:
    """Adiciona metadados de loja aos itens e retorna uma nova lista."""
    itens_preparados: List[ItemBase] = []
    for item_original in lista_itens:
        novo_item = item_original.copy() # Trabalha com cópia para não modificar listas originais
        novo_item["categoria_loja"] = novo_item.get("categoria_loja", categoria_loja_padrao)
        novo_item["tipo_item_para_inventario"] = tipo_inventario_padrao
        itens_preparados.append(novo_item)
    return itens_preparados

TODOS_ITENS_LOJA: List[ItemBase] = (
    _preparar_itens_para_loja(ARMAS_SIMPLES, "Armas", "arma") +
    _preparar_itens_para_loja(ARMAS_MARCIAIS, "Armas", "arma") +
    _preparar_itens_para_loja(ARMADURAS, "Armaduras", "armadura") +
    _preparar_itens_para_loja(ESCUDOS, "Escudos", "escudo") +
    _preparar_itens_para_loja(EQUIPAMENTO_GERAL, "Equipamentos", "item_geral") # Categoria já está nos itens
)

if __name__ == '__main__':
    print("--- Itens da Loja ---")
    for item in TODOS_ITENS_LOJA:
        custo_str = ""
        if item.get("custo_ef", 0) > 0: custo_str += f"{item['custo_ef']} Ef"
        if item.get("custo_efp", 0) > 0:
            if custo_str: custo_str += " "
            custo_str += f"{item['custo_efp']} EfP"
        if not custo_str: custo_str = "Grátis"
        
        print(f"Cat: {item.get('categoria_loja')} - Item: {item.get('nome')} ({item.get('tipo_item_para_inventario')}) - Custo: {custo_str}")
        if item.get('tipo_item_para_inventario') == 'arma':
            print(f"    Dano: {item.get('dano')}, Atributo: {item.get('atributo_chave')}, Perícia: {item.get('pericia_ataque')}")
        elif item.get('tipo_item_para_inventario') == 'armadura':
            print(f"    RD: {item.get('rd')}, Tipo: {item.get('tipo_armadura')}")
        elif item.get('tipo_item_para_inventario') == 'escudo':
            print(f"    RD Bônus: {item.get('rd_bonus_item')}, Bônus Bloqueio: {item.get('bonus_pericia_bloqueio')}")


    print(f"\nTotal de itens na loja: {len(TODOS_ITENS_LOJA)}")