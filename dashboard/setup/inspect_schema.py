# -*- coding: utf-8 -*-
"""
Diagnostico de esquema: imprime todas las tablas y columnas de fleetlogix_db.
Uso:
    python inspect_schema.py
"""
import psycopg2

DSN = dict(
    host="localhost",
    port=5432,
    user="postgres",
    password="your_password",
    dbname="fleetlogix_db",
)

def main():
    conn = psycopg2.connect(**DSN)
    cur = conn.cursor()

    # 1) tablas + columnas
    cur.execute("""
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position
    """)
    rows = cur.fetchall()

    current = None
    print("=" * 70)
    print("TABLAS Y COLUMNAS DE fleetlogix_db (schema 'public')")
    print("=" * 70)
    for table, col, dtype in rows:
        if table != current:
            print(f"\n[{table}]")
            current = table
        print(f"   - {col:<35} {dtype}")

    # 2) vistas existentes
    cur.execute("""
        SELECT table_name
        FROM information_schema.views
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    views = [r[0] for r in cur.fetchall()]
    print("\n" + "=" * 70)
    print(f"VISTAS EXISTENTES ({len(views)})")
    print("=" * 70)
    for v in views:
        print(f"   * {v}")
    if not views:
        print("   (ninguna)  <-- por eso el dashboard no las encuentra")

    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
