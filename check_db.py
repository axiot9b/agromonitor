import db_config
import psycopg2

def check_database():
    print("="*60)
    print("  INSPECCIÓN DE BASE DE DATOS (NEON POSTGRESQL)")
    print("="*60)
    
    conn = db_config.get_connection()
    if not conn:
        print("❌ No se pudo conectar a la base de datos.")
        return

    try:
        cur = conn.cursor()
        
        # 1. Listar Tablas
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cur.fetchall()
        
        print(f"\nTablas encontradas: {len(tables)}")
        print("-" * 60)
        print(f"{'TABLA':<20} | {'FILAS':<10} | {'ÚLTIMO REGISTRO'}")
        print("-" * 60)
        
        for table in tables:
            table_name = table[0]
            
            # Contar filas
            cur.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cur.fetchone()[0]
            
            # Obtener última fecha (asumiendo que tienen columna timestamp)
            last_date = "N/A"
            try:
                # Intentar buscar columna de tiempo común
                cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}' AND column_name IN ('timestamp', 'created_at', 'forecast_date')")
                col_res = cur.fetchone()
                if col_res:
                    time_col = col_res[0]
                    cur.execute(f"SELECT MAX({time_col}) FROM {table_name}")
                    res = cur.fetchone()
                    if res and res[0]:
                        last_date = str(res[0])
            except:
                pass
                
            print(f"{table_name:<20} | {count:<10} | {last_date}")
            
        print("-" * 60)
        
        # 2. Ver esquema de Tablas Clave
        print("\n\nESQUEMA DETALLADO")
        for target in ['weather_data', 'ndvi_data']:
            if any(t[0] == target for t in tables):
                print(f"\n📋 Tabla: {target}")
                cur.execute(f"""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_name = '{target}'
                    ORDER BY ordinal_position
                """)
                columns = cur.fetchall()
                for col in columns:
                    print(f"  - {col[0]:<20} ({col[1]})")
        
        cur.close()
        conn.close()
        print("\n✅ Inspección finalizada.")
        
    except Exception as e:
        print(f"❌ Error durante inspección: {e}")

if __name__ == "__main__":
    check_database()
