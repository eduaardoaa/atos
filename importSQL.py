# Importação completa do módulo 'consultaSQL'
import consultaSQL

# Obtendo os nomes das filiais
filiais = consultaSQL.obter_nmfilial()
print("Filiais encontradas:", filiais)

# Obtendo o total de vendas para uma filial
total_vendas = consultaSQL.obter_vendas_ano_anterior('FILIAL 0001')
print("Total de vendas para a filial 'FILIAL 0001' em março de 2024:", total_vendas)

# Obtendo a meta de vendas
meta_mes = consultaSQL.obter_meta_mes('FILIAL 0001') 
print(f"Meta de vendas para a filial 'FILIAL 0001' em março de 2024 (com 5% de acréscimo): {meta_mes}")

previsao = consultaSQL.obter_previsao_vendas('FILIAL 0001')
print(f"Previsão de vendas para a filial 'FILIAL 0001': {previsao}")

acumulo_vendas_ano_anterior = consultaSQL.acumulo_vendas_periodo_ano_anterior('FILIAL 0001')
print("Acumulo de vendas da filial 'FILIAL 0001' no mesmo período do ano anterior:", acumulo_vendas_ano_anterior)

acumulo_meta_ano_anterior = consultaSQL.obter_acumulo_meta_ano_anterior('FILIAL 0001')
print("Acumulo de meta de vendas da filial 'FILIAL 0001' no mesmo período do ano anterior:", acumulo_meta_ano_anterior)

acumulo_de_vendas = consultaSQL.obter_acumulo_de_vendas('FILIAL 0001')
print("Acumulo de vendas da filial 'FILIAL 0001' no mês atual:", acumulo_de_vendas)

vendas_dia_anterior = consultaSQL.obter_ultima_venda_com_valor('FILIAL 0001')
print("Vendas do dia anterior da filial 'FILIAL 0001':", vendas_dia_anterior)

percentual_crescimento_atual = consultaSQL.obter_percentual_de_crescimento_atual('FILIAL 0001')
print("Percentual de crescimento atual da filial 'FILIAL 0001':", percentual_crescimento_atual)

percentual_crescimento_meta = consultaSQL.obter_percentual_crescimento_meta('FILIAL 0001')
print("Percentual de crescimento meta da filial 'FILIAL 0001':", percentual_crescimento_meta)

vendas_mensais = consultaSQL.obter_vendas_anual_e_filial('FILIAL BELÉM')
print(vendas_mensais)
