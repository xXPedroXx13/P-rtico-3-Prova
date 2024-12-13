### Requisitos
1. *Instalar o Python*:
   - Acesse [Python.org](https://www.python.org/downloads/) e baixe a versão mais recente.
   - Durante a instalação, marque a opção "Add Python to PATH".

2. *Instalar dependências do projeto*:
   - Abra o terminal ou prompt de comando.
   - Execute o seguinte comando para instalar as bibliotecas necessárias:
     bash
     pip install pandas numpy fpdf
     

3. *Obter o código e os arquivos do projeto*:
   - Certifique-se de ter os arquivos do projeto em uma pasta no seu computador. 
   - Verifique se o arquivo dados_portico.xlsx existe ou será gerado pelo script.

### Instruções para Rodar o Projeto
1. *Abrir o terminal*:
   - Navegue até a pasta onde os arquivos do projeto estão salvos. Por exemplo:
     bash
     cd caminho/para/sua/pasta
     

2. *Executar o script para gerar o modelo de dados (opcional)*:
   - Se você não tiver o arquivo dados_portico.xlsx, rode o seguinte comando para criar o modelo:
     bash
     python nome_do_script.py
     
   - Substitua nome_do_script.py pelo nome do arquivo Python que contém a função generate_excel_template.

3. *Preencher o arquivo Excel*:
   - Abra o arquivo dados_portico.xlsx gerado.
   - Insira os dados estruturais nas planilhas correspondentes:
     - *Nós*: Coordenadas dos pontos.
     - *Elementos*: Informações dos elementos estruturais.
     - *Cargas_Nodais*: Forças aplicadas nos nós.
     - *Apoios*: Restrições de movimento nos nós.

4. *Executar a análise*:
   - Após preencher o arquivo Excel, execute o script principal com:
     bash
     python nome_do_script.py
     

5. *Verificar os resultados*:
   - O script gerará um arquivo chamado resultados_analise.pdf com os resultados da análise estrutural.

### Considerações
- Certifique-se de que os dados inseridos no Excel estejam corretos para evitar erros.
- Se ocorrerem erros durante a execução, revise os dados ou consulte o log do terminal para corrigir problemas.
