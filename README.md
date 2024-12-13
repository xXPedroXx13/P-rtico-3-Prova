Funcionalidades

- *Criação de Modelo de Dados em Excel*: Um modelo de entrada para informações estruturais.
- *Análise Estrutural*: Determinação de deslocamentos, reações e esforços nos elementos estruturais.
- *Geração de Relatório em PDF*: Resultados consolidados em um relatório técnico.

---

## 📋 Pré-requisitos

1. *Python*: Baixe e instale a versão mais recente [aqui](https://www.python.org/downloads/).
   - Certifique-se de marcar a opção *"Add Python to PATH"* durante a instalação.
2. *Instalar Dependências*:
   Execute o seguinte comando no terminal para instalar as bibliotecas necessárias:
   ```bash
   pip install pandas numpy fpdf

🚀 Como Rodar o Projeto
1. Clone o Repositório:
git clone [https://github.com/usuario/repo.git](https://github.com/xXPedroXx13/Portico-3a-Prova.git)
2. cd repo
3. 
4. Gerar Modelo de Dados em Excel (opcional): Se você não possui o arquivo dados_portico.xlsx, execute o script para gerar o modelo:
python app.py
5. 
6. Preencha o Arquivo Excel:
    * Nos: Adicione os identificadores e coordenadas dos nós.
    * Elementos: Insira as propriedades dos elementos estruturais.
    * Cargas_Nodais: Inclua as cargas aplicadas nos nós.
    * Apoios: Defina as restrições de movimento dos nós.
7. Execute o Script: Após preencher o arquivo Excel, rode o script principal:
python nome_do_script.py
8. 
9. Verifique o Relatório Gerado: O relatório será salvo no arquivo resultados_analise.pdf.

🛠️ Como o Código Funciona
1. Geração do Modelo de Dados
O código inclui uma função generate_excel_template que cria um modelo Excel (dados_portico.xlsx) com as seguintes planilhas:
* Nos: Coordenadas dos pontos estruturais.
* Elementos: Propriedades e conexões dos elementos.
* Cargas_Nodais: Forças aplicadas nos nós.
* Apoios: Restrições nos nós.
2. Análise Estrutural
A função principal realiza os seguintes passos:
* Matrizes de Rigidez: Calcula as matrizes locais e globais para cada elemento.
* Vetor de Forças: Determina as forças nodais equivalentes de acordo com as cargas.
* Resolução de Sistema Linear: Resolve os deslocamentos globais e calcula as reações nos apoios.
3. Esforços Locais
Com base nos deslocamentos globais, o script calcula os esforços internos em cada elemento estrutural.
4. Geração do Relatório
Um relatório detalhado é gerado em PDF com as seguintes informações:
* Matrizes de rigidez.
* Deslocamentos globais.
* Reações nos apoios.
* Esforços locais nos elementos.

📄 Estrutura do Projeto
* dados_portico.xlsx: Arquivo Excel com os dados de entrada.
* resultados_analise.pdf: Relatório gerado após a análise.
* nome_do_script.py: Código principal do projeto.

📞 Suporte
Caso encontre algum problema, sinta-se à vontade para abrir uma issue.

5. *Verificar os resultados*:
   - O script gerará um arquivo chamado resultados_analise.pdf com os resultados da análise estrutural.

### Considerações
- Certifique-se de que os dados inseridos no Excel estejam corretos para evitar erros.
- Se ocorrerem erros durante a execução, revise os dados ou consulte o log do terminal para corrigir problemas.
