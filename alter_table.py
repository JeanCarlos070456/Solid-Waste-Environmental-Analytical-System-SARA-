import sqlite3

con = sqlite3.connect("banco.db")
cur = con.cursor()

# Tenta adicionar a coluna (se já existir, vai dar erro – então tratamos)
try:
    cur.execute("ALTER TABLE pontos ADD COLUMN data_registro TEXT;")
    con.commit()
    print("Coluna data_registro adicionada.")
except Exception as e:
    print("Provavelmente a coluna já existe:", e)

con.close()
