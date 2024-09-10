import os
import psycopg2
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

def db_conectar():
    try:
        # Obtém as variáveis de ambiente
        db_host = os.getenv('DB_HOST')
        db_port = os.getenv('DB_PORT')
        db_name = os.getenv('DB_NAME')
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')

        # Estabelece a conexão com o banco de dados
        conexao = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )

        print("Conexão com o banco de dados estabelecida com sucesso!")
        return conexao

    except (Exception, psycopg2.Error) as erro:
        print(f"Erro ao conectar ao banco de dados: {erro}")
        return None

def db_listarprodutos():
    # Liste os dados da tabela produtos
    # A tabela produtos tem os seguintes campos: id, nome, descricao, preco, categoria, estoque, imagem
    conexao = db_conectar()
    if conexao:
        try:
            cursor = conexao.cursor()
            cursor.execute("SELECT id, nome, descricao, preco, imagem FROM produtos")
            produtos = cursor.fetchall()
            cursor.close()
            conexao.close()
            output = []
            for produto in produtos:
                output.append({
                    "id": produto[0],
                    "nome": produto[1],
                    "descricao": produto[2],
                    "preco": produto[3],
                    "imagem": produto[4]
                })
            return output
        except (Exception, psycopg2.Error) as erro:
            print(f"Erro ao listar produtos: {erro}")
            return None
    return None

def db_listarpedidos():
    # Liste os dados da tabela pedidos
    # A tabela pedidos tem os seguintes campos: id, data, total, descricao
    conexao = db_conectar()
    if conexao:
        try:
            cursor = conexao.cursor()
            cursor.execute("SELECT id, data, total, descricao FROM pedidos")
            pedidos = cursor.fetchall()
            cursor.close()
            conexao.close()
            output = []
            for pedido in pedidos:
                output.append({
                    "id": pedido[0],
                    "data": pedido[1],
                    "total": pedido[2],
                    "descricao": pedido[3]
                })
            return output
        except (Exception, psycopg2.Error) as erro:
            print(f"Erro ao listar pedidos: {erro}")
            return None
    return None


# Exemplo de uso da função
if __name__ == "__main__":
    conexao = db_conectar()
    if conexao:
        # Faça algo com a conexão
        conexao.close()
        print("Conexão fechada.")
