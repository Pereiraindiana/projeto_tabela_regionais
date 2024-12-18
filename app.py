import pandas as pd
import psycopg2
from psycopg2 import sql

# Função principal
def importar_dados(arquivo_csv):
    """
    Importa dados de um arquivo CSV para um banco PostgreSQL.
    Realiza tratamento de valores nulos e duplicados antes da inserção.
    """
    # 1. Carregar os dados do arquivo CSV
    try:
        df = pd.read_csv(arquivo_csv)
        print("Arquivo carregado com sucesso!")
    except Exception as e:
        print(f"Erro ao carregar o arquivo: {e}")
        return

    # 2. Tratamento de valores nulos
    print("Tratando valores nulos...")
    df['loja'] = df['loja'].fillna('NULL_LOJA_001')  # Substitui nulos na coluna 'loja'
    df = df.dropna(subset=['loja', 'regiao', 'nome'])  # Remove linhas com colunas essenciais nulas

    # 3. Remover duplicatas
    print("Removendo duplicatas...")
    df = df.drop_duplicates(subset=['loja'])

    # 4. Conexão com o banco de dados PostgreSQL
    try:
        print("Conectando ao banco de dados...")
        conn = psycopg2.connect(
            host="SEU_HOST",       # Exemplo: 'localhost' ou URL do banco
            database="SEU_BANCO",  # Nome do banco de dados
            user="SEU_USUARIO",    # Usuário do banco
            password="SUA_SENHA"   # Senha do banco
        )
        cursor = conn.cursor()

        # 5. Query de inserção segura (evita erros de duplicidade)
        insert_query = """
        INSERT INTO loja (regiao, loja, nome, pdv, operador)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (loja) DO NOTHING;
        """

        # 6. Inserir dados no banco linha por linha
        print("Inserindo dados no banco...")
        for index, row in df.iterrows():
            cursor.execute(insert_query, (row['regiao'], row['loja'], row['nome'], row['pdv'], row['operador']))

        # Commit para salvar as alterações
        conn.commit()
        print("Dados importados com sucesso!")

    except Exception as e:
        print(f"Erro durante a importação dos dados: {e}")

    finally:
        # Fechar conexão com o banco
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print("Conexão com o banco encerrada.")

# Chamada da função
if __name__ == "__main__":
    # Substitua pelo caminho do arquivo CSV exportado
    importar_dados("seuarquivo.csv")
