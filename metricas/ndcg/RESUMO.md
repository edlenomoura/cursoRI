# 📊 Resumo do Projeto - Calculadora de NDCG

## ✅ O que foi criado

Este projeto fornece uma implementação didática completa do cálculo de NDCG (Normalized Discounted Cumulative Gain) com **duas variações da fórmula**, ideal para estudantes de Recuperação de Informação.

## 📁 Arquivos Criados

### 1. `calcula_ndcg.py` (Principal)
**Propósito:** Avalia e compara dois sistemas de recuperação usando ambas as versões do NDCG

**Funcionalidades:**
- ✅ Calcula NDCG usando versão padrão: `DCG = Σ((2^rel_i - 1) / log₂(i+1))`
- ✅ Calcula NDCG usando versão linear: `DCG = Σ(rel_i / i)`
- ✅ Compara os dois sistemas (Sistema 1 vs Sistema 2)
- ✅ Mostra diferenças entre as duas fórmulas para cada consulta
- ✅ Análise de concordância entre as métricas
- ✅ Tabela comparativa final
- ✅ Código bem comentado e didático

**Execução:**
```bash
python calcula_ndcg.py
```

### 2. `exemplo_calculo_manual.py` (Tutorial)
**Propósito:** Demonstra o cálculo manual passo a passo de ambas as versões do NDCG

**Funcionalidades:**
- ✅ Exemplo simples com 4 documentos
- ✅ Mostra CADA PASSO do cálculo de forma detalhada
- ✅ Explica o que cada número significa
- ✅ Compara as duas versões lado a lado
- ✅ Sugere exercícios para experimentação
- ✅ Fácil de modificar para testar outros cenários

**Execução:**
```bash
python exemplo_calculo_manual.py
```

### 3. `README.md` (Documentação)
**Propósito:** Documentação completa do projeto

**Conteúdo:**
- ✅ Explicação detalhada das duas versões do NDCG
- ✅ Tabelas comparativas
- ✅ Exemplos práticos de cálculo
- ✅ Interpretação dos resultados
- ✅ Conceitos importantes (desconto, ganho, normalização)
- ✅ Modificações possíveis (NDCG@k, visualizações, etc.)
- ✅ Exercícios e desafios para estudantes
- ✅ Questões para reflexão

### 4. `sampleFiles/` (Dados de Exemplo)
**3 arquivos JSON corrigidos:**
- `query_scores.json` - Avaliações de relevância (ground truth)
- `sistema1.json` - Resultados do Sistema 1
- `sistema2.json` - Resultados do Sistema 2

## 🎯 Principais Características

### Duas Versões de NDCG Implementadas

#### Versão Padrão (Literatura Acadêmica)
```
DCG = Σ((2^rel_i - 1) / log₂(i+1))
```
- Desconto logarítmico
- Ganho exponencial
- Mais sensível a documentos muito relevantes
- Padrão em pesquisas acadêmicas

#### Versão Linear (Simplificada)
```
DCG = Σ(rel_i / i)
```
- Desconto linear
- Ganho direto
- Mais simples de entender
- Penalização uniforme

### Funcionalidades Didáticas

1. **Código Comentado**: Cada função tem documentação explicando o que faz e por quê
2. **Saída Detalhada**: Mostra DCG, IDCG e NDCG para cada consulta
3. **Comparação Visual**: Tabelas e análises comparativas
4. **Análise de Diferenças**: Explica por que as métricas divergem ou concordam
5. **Exemplos Práticos**: Dados reais de 5 consultas com 2 sistemas
6. **Tutorial Passo a Passo**: Arquivo separado mostrando cada cálculo

## 📊 Resultados dos Exemplos

### Comparação dos Sistemas

**Versão Padrão:**
- Sistema 1: NDCG = 0.7404
- Sistema 2: NDCG = 0.8011 ✓ **Melhor**

**Versão Linear:**
- Sistema 1: NDCG = 0.7068
- Sistema 2: NDCG = 0.7762 ✓ **Melhor**

**Conclusão:** Ambas as métricas concordam que Sistema 2 é superior!

### Por Consulta

| Consulta | Descrição | S1 (Padrão) | S2 (Padrão) | Vencedor |
|----------|-----------|-------------|-------------|----------|
| 1 | Agricultura regenerativa | 0.8045 | 0.7003 | Sistema 1 |
| 2 | Criptografia quântica | 0.5213 | 0.5213 | Empate |
| 3 | Pão fermentação natural | 0.7579 | **1.0000** | Sistema 2 🏆 |
| 4 | Pontos turísticos Quioto | 0.9871 | 0.9871 | Empate |
| 5 | Exercícios lombar | 0.6313 | 0.7967 | Sistema 2 |

**Destaque:** Sistema 2 conseguiu ranking **perfeito** (NDCG = 1.0) na consulta 3!

## 🎓 Valor Pedagógico

### Para Estudantes Iniciantes
- ✅ Código didático e bem comentado
- ✅ Exemplo passo a passo super detalhado
- ✅ Documentação extensa com explicações
- ✅ Fácil de modificar e experimentar

### Para Estudantes Intermediários
- ✅ Comparação entre duas variações da métrica
- ✅ Análise de quando as métricas concordam/divergem
- ✅ Implementação completa sem bibliotecas prontas
- ✅ Exercícios e desafios sugeridos

### Para Estudantes Avançados
- ✅ Base para implementar outras variações
- ✅ Estrutura para adicionar mais métricas (MAP, P@k, etc.)
- ✅ Código modular e extensível
- ✅ Tratamento de casos especiais (docs não avaliados)

## 🔧 Customizações Possíveis

### Fáceis
- Mudar os dados de entrada (editar JSONs)
- Calcular NDCG@k (adicionar parâmetro k)
- Ativar print detalhado (descomentar linhas)

### Intermediárias
- Implementar outras funções de desconto (quadrática, raiz quadrada)
- Adicionar outras métricas (Precision@k, MAP, MRR)
- Criar visualizações (gráficos, heatmaps)

### Avançadas
- Análise estatística (testes de significância)
- Otimização de rankings
- Interface gráfica
- Comparação com bibliotecas existentes (scikit-learn, etc.)

## 💡 Conceitos Abordados

1. **DCG (Discounted Cumulative Gain)**
   - Ganho acumulado com desconto por posição
   - Duas variações: logarítmica e linear

2. **IDCG (Ideal DCG)**
   - Melhor DCG possível (ranking perfeito)
   - Base para normalização

3. **NDCG (Normalized DCG)**
   - Métrica normalizada entre 0 e 1
   - Permite comparação entre consultas diferentes

4. **Desconto Posicional**
   - Logarítmico vs Linear
   - Trade-offs entre as abordagens

5. **Função de Ganho**
   - Exponencial vs Direto
   - Impacto em documentos muito relevantes

6. **Normalização**
   - Importância de dividir pelo ideal
   - Interpretação dos valores

## 🚀 Como Usar Este Projeto

### 1. Para Aprender NDCG do Zero
```bash
# Comece pelo exemplo manual
python exemplo_calculo_manual.py

# Depois execute o programa completo
python calcula_ndcg.py

# Leia o README.md para entender os conceitos
```

### 2. Para Ensinar NDCG
- Use `exemplo_calculo_manual.py` em sala de aula
- Projete a saída passo a passo
- Peça aos alunos para modificar o ranking e prever o resultado
- Discuta as diferenças entre as duas versões

### 3. Para Avaliar Seus Próprios Sistemas
- Crie seus JSONs no formato dos exemplos
- Modifique os caminhos dos arquivos em `main()`
- Execute e analise os resultados

### 4. Para Experimentar Variações
- Modifique as funções de desconto/ganho
- Compare com as versões existentes
- Documente suas descobertas

## 📚 Referências Úteis

- Järvelin, K., & Kekäläinen, J. (2002). "Cumulated gain-based evaluation of IR techniques"
- Wikipedia: Discounted cumulative gain
- Papers com código: https://paperswithcode.com/

## ✨ Próximos Passos Sugeridos

1. Implementar outras métricas (MAP, P@k, MRR, ERR)
2. Adicionar testes unitários
3. Criar visualizações dos resultados
4. Fazer análise estatística das diferenças
5. Comparar com implementações de bibliotecas conhecidas
6. Experimentar com dados reais maiores
7. Documentar mais casos de uso

---

**Desenvolvido com propósito didático para o Curso de Recuperação de Informação**  
*Março 2026*
