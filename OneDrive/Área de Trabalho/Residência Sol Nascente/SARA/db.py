import sqlite3
from typing import List, Optional

import pandas as pd

DB_PATH = "banco.db"


def get_connection():
    # check_same_thread=False para uso com Streamlit
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def insert_ponto(pin: int, nome: str, pnrs: str, lat: float, long: float) -> None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO pontos (pin, nome, pnrs, lat, long)
        VALUES (?, ?, ?, ?, ?)
        """,
        (pin, nome, pnrs, lat, long),
    )

    conn.commit()
    conn.close()


def fetch_pontos(pins: Optional[List[int]] = None) -> pd.DataFrame:
    conn = get_connection()

    if pins:
        placeholders = ",".join("?" * len(pins))
        query = f"""
            SELECT pin, nome, pnrs, lat, long
            FROM pontos
            WHERE pin IN ({placeholders})
        """
        df = pd.read_sql_query(query, conn, params=pins)
    else:
        query = """
            SELECT pin, nome, pnrs, lat, long
            FROM pontos
        """
        df = pd.read_sql_query(query, conn)

    conn.close()
    return df
