"""
AgroMonitor - API Server
Backend Flask que sirve datos del dashboard desde PostgreSQL

Ejecutar: python api_server.py
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import json

# Importar configuración de BD
from db_config import get_connection

app = Flask(__name__)
CORS(app)  # Permitir requests desde el dashboard

# ============================================
# ENDPOINTS DE LA API
# ============================================

@app.route('/')
def home():
    """Endpoint de bienvenida"""
    return jsonify({
        'name': 'AgroMonitor API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': [
            '/api/weather',
            '/api/weather/history',
            '/api/weather/dewpoint',
            '/api/weather/dewpoint/correlation',
            '/api/soil',
            '/api/soil/history',
            '/api/ndvi',
            '/api/ndvi/history',
            '/api/ndvi/daily',
            '/api/forecast',
            '/api/stats',
            '/api/soil/weather/correlation'
        ]
    })

@app.route('/api/weather')
def get_weather():
    """Obtiene el último registro de clima"""
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT timestamp, temperature_c, feels_like_c, temp_min_c, temp_max_c,
                   humidity_percent, pressure_hpa, wind_speed_ms, wind_deg,
                   clouds_percent, weather_main, weather_description, dew_point_c
            FROM weather_data
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        row = cur.fetchone()
        cur.close()
        conn.close()
        
        if row:
            return jsonify({
                'timestamp': row[0].isoformat() if row[0] else None,
                'temperature_c': float(row[1]) if row[1] else None,
                'feels_like_c': float(row[2]) if row[2] else None,
                'temp_min_c': float(row[3]) if row[3] else None,
                'temp_max_c': float(row[4]) if row[4] else None,
                'humidity_percent': row[5],
                'pressure_hpa': row[6],
                'wind_speed_ms': float(row[7]) if row[7] else None,
                'wind_deg': row[8],
                'clouds_percent': row[9],
                'weather_main': row[10],
                'weather_description': row[11],
                'dew_point_c': float(row[12]) if row[12] else None
            })
        return jsonify({'message': 'No data available'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/weather/history')
def get_weather_history():
    """Obtiene historial de clima"""
    days = request.args.get('days', 7, type=int)
    limit = request.args.get('limit', 100, type=int)
    
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT timestamp, temperature_c, humidity_percent, 
                   wind_speed_ms, weather_main
            FROM weather_data
            WHERE timestamp > NOW() - INTERVAL '%s days'
            ORDER BY timestamp DESC
            LIMIT %s
        """, (days, limit))
        
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        data = [{
            'timestamp': row[0].isoformat(),
            'temperature_c': float(row[1]) if row[1] else None,
            'humidity_percent': row[2],
            'wind_speed_ms': float(row[3]) if row[3] else None,
            'weather_main': row[4]
        } for row in rows]
        
        return jsonify({'count': len(data), 'data': data})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/soil')
def get_soil():
    """Obtiene el último registro de suelo"""
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT timestamp, soil_temp_c, soil_moisture, soil_moisture_percent
            FROM soil_data
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        row = cur.fetchone()
        cur.close()
        conn.close()
        
        if row:
            return jsonify({
                'timestamp': row[0].isoformat() if row[0] else None,
                'soil_temp_c': float(row[1]) if row[1] else None,
                'soil_moisture': float(row[2]) if row[2] else None,
                'soil_moisture_percent': float(row[3]) if row[3] else None
            })
        return jsonify({'message': 'No data available'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/soil/history')
def get_soil_history():
    """Obtiene historial de suelo"""
    days = request.args.get('days', 7, type=int)
    
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT timestamp, soil_temp_c, soil_moisture_percent
            FROM soil_data
            WHERE timestamp > NOW() - INTERVAL '%s days'
            ORDER BY timestamp DESC
        """, (days,))
        
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        data = [{
            'timestamp': row[0].isoformat(),
            'soil_temp_c': float(row[1]) if row[1] else None,
            'soil_moisture_percent': float(row[2]) if row[2] else None
        } for row in rows]
        
        return jsonify({'count': len(data), 'data': data})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ndvi')
def get_ndvi():
    """Obtiene el último registro de NDVI"""
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT timestamp, image_date, ndvi_mean, ndvi_min, ndvi_max,
                   ndvi_std, ndwi_mean, cloud_coverage, ndsi_mean, ndsi_interpretation
            FROM ndvi_data
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        row = cur.fetchone()
        cur.close()
        conn.close()
        
        if row:
            return jsonify({
                'timestamp': row[0].isoformat() if row[0] else None,
                'image_date': row[1].isoformat() if row[1] else None,
                'ndvi_mean': float(row[2]) if row[2] else None,
                'ndvi_min': float(row[3]) if row[3] else None,
                'ndvi_max': float(row[4]) if row[4] else None,
                'ndvi_std': float(row[5]) if row[5] else None,
                'ndwi_mean': float(row[6]) if row[6] else None,
                'cloud_coverage': float(row[7]) if row[7] else None,
                'ndsi_mean': float(row[8]) if row[8] else None,
                'ndsi_interpretation': row[9] if row[9] else None
            })
        return jsonify({'message': 'No data available'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ndvi/history')
def get_ndvi_history():
    """Obtiene historial de NDVI"""
    days = request.args.get('days', 30, type=int)
    
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT timestamp, image_date, ndvi_mean, ndwi_mean
            FROM ndvi_data
            WHERE timestamp > NOW() - INTERVAL '%s days'
            ORDER BY timestamp DESC
        """, (days,))
        
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        data = [{
            'timestamp': row[0].isoformat(),
            'image_date': row[1].isoformat() if row[1] else None,
            'ndvi_mean': float(row[2]) if row[2] else None,
            'ndwi_mean': float(row[3]) if row[3] else None
        } for row in rows]
        
        return jsonify({'count': len(data), 'data': data})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/forecast')
def get_forecast():
    """Obtiene el pronóstico más reciente"""
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT forecast_date, temp_min_c, temp_max_c, temp_avg_c,
                   humidity_avg, precipitation_mm
            FROM forecast_data
            WHERE forecast_date >= CURRENT_DATE
            ORDER BY forecast_date
            LIMIT 5
        """)
        
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        data = [{
            'date': row[0].isoformat(),
            'temp_min_c': float(row[1]) if row[1] else None,
            'temp_max_c': float(row[2]) if row[2] else None,
            'temp_avg_c': float(row[3]) if row[3] else None,
            'humidity_avg': row[4],
            'precipitation_mm': float(row[5]) if row[5] else None
        } for row in rows]
        
        total_precip = sum(d['precipitation_mm'] or 0 for d in data)
        
        return jsonify({
            'days': len(data),
            'total_precipitation_mm': round(total_precip, 1),
            'forecast': data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def get_stats():
    """Obtiene estadísticas generales"""
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor()
        
        # Contar registros
        stats = {}
        for table in ['weather_data', 'soil_data', 'ndvi_data', 'forecast_data']:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            stats[table.replace('_data', '_records')] = cur.fetchone()[0]
        
        # Última actualización
        cur.execute("SELECT MAX(timestamp) FROM weather_data")
        last_update = cur.fetchone()[0]
        
        cur.close()
        conn.close()
        
        return jsonify({
            'records': stats,
            'last_update': last_update.isoformat() if last_update else None,
            'database': 'Neon PostgreSQL'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/weather/dewpoint')
def get_dewpoint_daily():
    """Obtiene el punto de rocío diario"""
    days = request.args.get('days', 7, type=int)
    
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                DATE(timestamp) as date,
                AVG(dew_point_c) as avg_dewpoint,
                MIN(dew_point_c) as min_dewpoint,
                MAX(dew_point_c) as max_dewpoint,
                AVG(temperature_c) as avg_temp,
                AVG(humidity_percent) as avg_humidity
            FROM weather_data
            WHERE timestamp > NOW() - INTERVAL '%s days'
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
        """, (days,))
        
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        data = [{
            'date': row[0].isoformat(),
            'dew_point_avg': float(row[1]) if row[1] else None,
            'dew_point_min': float(row[2]) if row[2] else None,
            'dew_point_max': float(row[3]) if row[3] else None,
            'temperature_avg': float(row[4]) if row[4] else None,
            'humidity_avg': float(row[5]) if row[5] else None
        } for row in rows]
        
        return jsonify({'count': len(data), 'data': data})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ndvi/daily')
def get_ndvi_daily():
    """Obtiene estadísticas diarias de NDVI (promedio, máximo, mínimo)"""
    days = request.args.get('days', 30, type=int)
    
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                DATE(timestamp) as date,
                AVG(ndvi_mean) as avg_ndvi,
                MIN(ndvi_min) as min_ndvi,
                MAX(ndvi_max) as max_ndvi,
                AVG(ndvi_std) as std_ndvi,
                AVG(ndwi_mean) as avg_ndwi
            FROM ndvi_data
            WHERE timestamp > NOW() - INTERVAL '%s days'
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
        """, (days,))
        
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        data = [{
            'date': row[0].isoformat(),
            'ndvi_avg': float(row[1]) if row[1] else None,
            'ndvi_min': float(row[2]) if row[2] else None,
            'ndvi_max': float(row[3]) if row[3] else None,
            'ndvi_std': float(row[4]) if row[4] else None,
            'ndwi_avg': float(row[5]) if row[5] else None
        } for row in rows]
        
        return jsonify({'count': len(data), 'data': data})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/soil/weather/correlation')
def get_soil_weather_correlation():
    """Obtiene correlación entre humedad del suelo y temperatura del clima"""
    days = request.args.get('days', 7, type=int)
    
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor()
        
        # Obtener datos de suelo y clima por hora
        cur.execute("""
            SELECT 
                DATE(s.timestamp) as date,
                EXTRACT(HOUR FROM s.timestamp) as hour,
                AVG(s.soil_moisture_percent) as soil_moisture,
                AVG(s.soil_temp_c) as soil_temp,
                AVG(w.temperature_c) as air_temp,
                AVG(w.humidity_percent) as air_humidity,
                AVG(w.pressure_hpa) as pressure,
                AVG(w.wind_speed_ms) as wind_speed,
                AVG(w.clouds_percent) as clouds
            FROM soil_data s
            LEFT JOIN weather_data w ON DATE(s.timestamp) = DATE(w.timestamp) 
                AND EXTRACT(HOUR FROM s.timestamp) = EXTRACT(HOUR FROM w.timestamp)
            WHERE s.timestamp > NOW() - INTERVAL '%s days'
            GROUP BY DATE(s.timestamp), EXTRACT(HOUR FROM s.timestamp)
            ORDER BY date DESC, hour DESC
        """, (days,))
        
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        data = [{
            'date': row[0].isoformat(),
            'hour': int(row[1]),
            'soil_moisture_percent': float(row[2]) if row[2] else None,
            'soil_temp_c': float(row[3]) if row[3] else None,
            'air_temp_c': float(row[4]) if row[4] else None,
            'air_humidity_percent': float(row[5]) if row[5] else None,
            'pressure_hpa': float(row[6]) if row[6] else None,
            'wind_speed_ms': float(row[7]) if row[7] else None,
            'clouds_percent': float(row[8]) if row[8] else None
        } for row in rows]
        
        # Calcular correlaciones
        if len(data) > 1:
            import math
            
            def calculate_correlation(x, y):
                """Calcula correlación de Pearson"""
                n = len(x)
                if n < 2:
                    return None
                
                # Filtrar valores nulos
                pairs = [(x[i], y[i]) for i in range(n) if x[i] is not None and y[i] is not None]
                if len(pairs) < 2:
                    return None
                
                x_vals = [p[0] for p in pairs]
                y_vals = [p[1] for p in pairs]
                
                mean_x = sum(x_vals) / len(x_vals)
                mean_y = sum(y_vals) / len(y_vals)
                
                numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(x_vals, y_vals))
                denominator_x = sum((x - mean_x) ** 2 for x in x_vals)
                denominator_y = sum((y - mean_y) ** 2 for y in y_vals)
                
                if denominator_x == 0 or denominator_y == 0:
                    return None
                
                return numerator / math.sqrt(denominator_x * denominator_y)
            
            # Calcular correlaciones
            correlations = {
                'soil_moisture_vs_air_temp': calculate_correlation(
                    [d['soil_moisture_percent'] for d in data],
                    [d['air_temp_c'] for d in data]
                ),
                'soil_temp_vs_air_temp': calculate_correlation(
                    [d['soil_temp_c'] for d in data],
                    [d['air_temp_c'] for d in data]
                ),
                'soil_moisture_vs_air_humidity': calculate_correlation(
                    [d['soil_moisture_percent'] for d in data],
                    [d['air_humidity_percent'] for d in data]
                )
            }
        else:
            correlations = {}
        
        return jsonify({
            'count': len(data),
            'correlations': correlations,
            'data': data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/weather/dewpoint/correlation')
def get_dewpoint_correlation():
    """Obtiene correlación del punto de rocío con otros datos climáticos y de suelo"""
    days = request.args.get('days', 14, type=int)
    
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor()
        
        # Obtener datos diarios de punto de rocío, temperatura, humedad y suelo
        cur.execute("""
            SELECT 
                DATE(w.timestamp) as date,
                AVG(w.dew_point_c) as avg_dewpoint,
                AVG(w.temperature_c) as avg_temp,
                AVG(w.humidity_percent) as avg_humidity,
                AVG(s.soil_temp_c) as avg_soil_temp,
                AVG(s.soil_moisture_percent) as avg_soil_moisture
            FROM weather_data w
            LEFT JOIN soil_data s ON DATE(w.timestamp) = DATE(s.timestamp)
            WHERE w.timestamp > NOW() - INTERVAL '%s days'
                AND w.dew_point_c IS NOT NULL
            GROUP BY DATE(w.timestamp)
            ORDER BY date DESC
        """, (days,))
        
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        data = [{
            'date': row[0].isoformat(),
            'dew_point_avg': float(row[1]) if row[1] else None,
            'temperature_avg': float(row[2]) if row[2] else None,
            'humidity_avg': float(row[3]) if row[3] else None,
            'soil_temp_avg': float(row[4]) if row[4] else None,
            'soil_moisture_avg': float(row[5]) if row[5] else None
        } for row in rows]
        
        # Calcular correlaciones si hay suficientes datos
        correlations = {}
        if len(data) > 2:
            import math
            
            def calculate_correlation(x, y):
                """Calcula correlación de Pearson"""
                pairs = [(x[i], y[i]) for i in range(len(x)) if x[i] is not None and y[i] is not None]
                if len(pairs) < 2:
                    return None
                
                x_vals = [p[0] for p in pairs]
                y_vals = [p[1] for p in pairs]
                
                mean_x = sum(x_vals) / len(x_vals)
                mean_y = sum(y_vals) / len(y_vals)
                
                numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(x_vals, y_vals))
                denominator_x = sum((x - mean_x) ** 2 for x in x_vals)
                denominator_y = sum((y - mean_y) ** 2 for y in y_vals)
                
                if denominator_x == 0 or denominator_y == 0:
                    return None
                
                return round(numerator / math.sqrt(denominator_x * denominator_y), 4)
            
            correlations = {
                'dewpoint_vs_temperature': calculate_correlation(
                    [d['dew_point_avg'] for d in data],
                    [d['temperature_avg'] for d in data]
                ),
                'dewpoint_vs_humidity': calculate_correlation(
                    [d['dew_point_avg'] for d in data],
                    [d['humidity_avg'] for d in data]
                ),
                'dewpoint_vs_soil_temp': calculate_correlation(
                    [d['dew_point_avg'] for d in data],
                    [d['soil_temp_avg'] for d in data]
                ),
                'dewpoint_vs_soil_moisture': calculate_correlation(
                    [d['dew_point_avg'] for d in data],
                    [d['soil_moisture_avg'] for d in data]
                )
            }
            
            # Calcular estadísticas adicionales para análisis agrícola
            dew_temp_diffs = [(d['temperature_avg'] - d['dew_point_avg']) for d in data 
                             if d['temperature_avg'] and d['dew_point_avg']]
            
            if dew_temp_diffs:
                correlations['avg_dew_depression'] = round(sum(dew_temp_diffs) / len(dew_temp_diffs), 2)
                correlations['min_dew_depression'] = round(min(dew_temp_diffs), 2)
                correlations['condensation_risk_days'] = len([d for d in dew_temp_diffs if d < 2])
        
        return jsonify({
            'count': len(data),
            'correlations': correlations,
            'data': data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# MAIN
# ============================================

if __name__ == '__main__':
    print("=" * 50)
    print("  AgroMonitor API Server")
    print("=" * 50)
    print("  Endpoints disponibles:")
    print("    GET /api/weather              - Clima actual")
    print("    GET /api/weather/history      - Historial clima")
    print("    GET /api/weather/dewpoint     - Punto de rocío diario")
    print("    GET /api/soil                 - Suelo actual")
    print("    GET /api/soil/history         - Historial suelo")
    print("    GET /api/ndvi                 - NDVI actual")
    print("    GET /api/ndvi/history         - Historial NDVI")
    print("    GET /api/ndvi/daily           - Estadísticas diarias NDVI")
    print("    GET /api/forecast             - Pronóstico 5 días")
    print("    GET /api/stats                - Estadísticas")
    print("    GET /api/soil/weather/correlation - Correlación suelo-clima")
    print("=" * 50)
    print("  Iniciando servidor en http://localhost:5000")
    print("=" * 50 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
