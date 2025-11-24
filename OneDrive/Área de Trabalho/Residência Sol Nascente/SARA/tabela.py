import sqlite3

# 1- Conectar ao banco de dados:
conexao = sqlite3.connect('banco.db')

# 2- Criando o cursor
cursor = conexao.cursor()

# 3- Criando a tabela
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS pontos (
        id   INTEGER PRIMARY KEY AUTOINCREMENT,
        pin  INTEGER NOT NULL,
        nome TEXT    NOT NULL,
        pnrs TEXT,
        lat  REAL    NOT NULL,
        long REAL    NOT NULL
    );
    """
)

# 4- Fechar conexão
conexao.commit()
conexao.close()
print("Tabela foi criada com sucesso")
