# ElariaCharacterSheet/data/items_data.py

# Moeda: Ef (Elfen de Ouro), EfP (Elfen de Prata)
# 1 Ef = 10 EfP

# --- ARMAS ---
ARMAS_SIMPLES = [
    {
        "nome": "Adaga", 
        "custo_ef": 5, "custo_efp": 0, 
        "dano": "1d4", "atributo_chave": "DES", "tipo_dano": "Perf./Corte", 
        "empunhadura": "1 Mão", "alcance": "Corpo", "categoria": "Arma Simples",
        "observacoes": "" 
    }, #
    {
        "nome": "Maça Leve", 
        "custo_ef": 5, "custo_efp": 0, 
        "dano": "1d6", "atributo_chave": "FOR", "tipo_dano": "Impacto", 
        "empunhadura": "1 Mão", "alcance": "Corpo", "categoria": "Arma Simples",
        "observacoes": ""
    }, #
    {
        "nome": "Lança Curta",
        "custo_ef": 5, "custo_efp": 0, 
        "dano": "1d6", "atributo_chave": "FOR", "tipo_dano": "Perf.", 
        "empunhadura": "1 Mão", "alcance": "Corpo", "categoria": "Arma Simples",
        "observacoes": ""
    }, #
    {
        "nome": "Besta Leve", 
        "custo_ef": 5, "custo_efp": 0, 
        "dano": "1d4", "atributo_chave": "DES", "tipo_dano": "Perf.", 
        "empunhadura": "1 Mão", "alcance": "Distância", "categoria": "Arma Simples",
        "observacoes": ""
    }, #
]

ARMAS_MARCIAIS = [
    {
        "nome": "Espada Curta", 
        "custo_ef": 5, "custo_efp": 0, 
        "dano": "1d6", "atributo_chave": "DES", "tipo_dano": "Corte", 
        "empunhadura": "1 Mão", "alcance": "Corpo a Corpo", "categoria": "Arma Marcial",
        "observacoes": ""
    }, #
    {
        "nome": "Machado de Mão", 
        "custo_ef": 5, "custo_efp": 0, 
        "dano": "1d6", "atributo_chave": "FOR", "tipo_dano": "Corte", 
        "empunhadura": "1 Mão", "alcance": "Corpo a Corpo", "categoria": "Arma Marcial",
        "observacoes": ""
    }, #
    {
        "nome": "Espada Longa", 
        "custo_ef": 10, "custo_efp": 0, 
        "dano": "1d8", "atributo_chave": "FOR", "tipo_dano": "Corte", 
        "empunhadura": "2 Mãos", "alcance": "Corpo a Corpo", "categoria": "Arma Marcial",
        "observacoes": "" 
    }, #
    {
        "nome": "Machado Grande", 
        "custo_ef": 10, "custo_efp": 0, 
        "dano": "1d8", "atributo_chave": "FOR", "tipo_dano": "Corte", 
        "empunhadura": "2 Mãos", "alcance": "Corpo a Corpo", "categoria": "Arma Marcial",
        "observacoes": ""
    }, #
    {
        "nome": "Arco Longo", 
        "custo_ef": 10, "custo_efp": 0, 
        "dano": "1d6", "atributo_chave": "DES", "tipo_dano": "Perf.", 
        "empunhadura": "2 Mãos", "alcance": "Distância", "categoria": "Arma Marcial",
        "observacoes": ""
    }, #
]

# --- ARMADURAS ---
ARMADURAS = [
    {
        "nome": "Couro", 
        "custo_ef": 5, "custo_efp": 0, 
        "rd": 1, "tipo_armadura": "Leve", "penalidade_atributo": "0",
        "observacoes": ""
    }, #
    {
        "nome": "Couro Batido", 
        "custo_ef": 5, "custo_efp": 0, 
        "rd": 1, "tipo_armadura": "Leve", "penalidade_atributo": "0",
        "observacoes": ""
    }, #
    {
        "nome": "Gibão de Peles", 
        "custo_ef": 5, "custo_efp": 0, 
        "rd": 1, "tipo_armadura": "Leve", "penalidade_atributo": "0",
        "observacoes": ""
    }, #
    {
        "nome": "Cota de Malha", 
        "custo_ef": 50, "custo_efp": 0, 
        "rd": 2, "tipo_armadura": "Média", "penalidade_atributo": "-1 (Força)",
        "observacoes": ""
    }, #
    {
        "nome": "Brunea", 
        "custo_ef": 50, "custo_efp": 0, 
        "rd": 2, "tipo_armadura": "Média", "penalidade_atributo": "-1 (Destreza)",
        "observacoes": ""
    }, #
    {
        "nome": "Armadura Completa", 
        "custo_ef": 85, "custo_efp": 0, 
        "rd": 3, "tipo_armadura": "Pesada", "penalidade_atributo": "-1 (Destreza e Força)",
        "observacoes": ""
    }, #
]

# --- ESCUDOS ---
ESCUDOS = [
    {
        "nome": "Escudo de Madeira Redondo",
        "custo_ef": 6, "custo_efp": 0,
        "rd_bonus_item": 1, # RD fornecida pelo escudo em si
        "bonus_pericia_bloqueio": 1, # Bônus que poderia ser aplicado ao Valor da perícia Bloqueio
        "categoria": "Escudo",
        "observacoes": "RD +1, concede Bloqueio +1 (ao Valor da perícia)"
    },
    # Adicionar outros escudos aqui se necessário
]

# --- EQUIPAMENTO GERAL ---
EQUIPAMENTO_GERAL = [
    {"nome": "Corda (15m)", "custo_ef": 3, "custo_efp": 0, "peso_estimado": "Leve", "categoria": "Equipamento Geral"}, #
    {"nome": "Tocha (unid.)", "custo_ef": 0, "custo_efp": 2, "peso_estimado": "Mínimo", "categoria": "Equipamento Geral"}, #
    {"nome": "Ração de Viagem (dia)", "custo_ef": 0, "custo_efp": 5, "peso_estimado": "Leve", "categoria": "Equipamento Geral"}, #
    {"nome": "Kit de Cura", "custo_ef": 50, "custo_efp": 0, "peso_estimado": "Médio", "categoria": "Equipamento Geral"}, #
    {"nome": "Saco de Dormir", "custo_ef": 0, "custo_efp": 5, "peso_estimado": "Médio", "categoria": "Equipamento Geral"}, #
    {"nome": "Mochila", "custo_ef": 3, "custo_efp": 0, "peso_estimado": "Leve", "categoria": "Equipamento Geral"}, #
    {"nome": "Cantil", "custo_ef": 1, "custo_efp": 0, "peso_estimado": "Leve", "categoria": "Equipamento Geral"}, #
    {"nome": "Pederneira", "custo_ef": 0, "custo_efp": 5, "peso_estimado": "Mínimo", "categoria": "Equipamento Geral"}, #
    {"nome": "História da Paz Dourada", "custo_ef": 3, "custo_efp": 0, "peso_estimado": "Leve", "categoria": "Livro/Documento"}, #
]

# --- Lista Combinada para a Loja ---
def _preparar_itens_para_loja(lista_itens, categoria_loja_padrao, tipo_inventario_padrao):
    itens_preparados = []
    for item in lista_itens:
        novo_item = item.copy()
        novo_item["categoria_loja"] = item.get("categoria", categoria_loja_padrao) # Usa a categoria do item se existir, senão o padrão
        novo_item["tipo_item_para_inventario"] = tipo_inventario_padrao
        itens_preparados.append(novo_item)
    return itens_preparados

TODOS_ITENS_LOJA = (
    _preparar_itens_para_loja(ARMAS_SIMPLES, "Armas", "arma") +
    _preparar_itens_para_loja(ARMAS_MARCIAIS, "Armas", "arma") +
    _preparar_itens_para_loja(ARMADURAS, "Armaduras", "armadura") +
    _preparar_itens_para_loja(ESCUDOS, "Escudos", "escudo") + # Adicionando escudos à loja
    _preparar_itens_para_loja(EQUIPAMENTO_GERAL, "Equipamentos", "item_geral")
)

if __name__ == '__main__':
    # Pequeno teste para verificar os dados
    for item in TODOS_ITENS_LOJA:
        print(f"Categoria Loja: {item.get('categoria_loja')} - Item: {item.get('nome')}: {item.get('custo_ef')} Ef, {item.get('custo_efp')} EfP")
    
    print(f"\nTotal de itens na loja: {len(TODOS_ITENS_LOJA)}")