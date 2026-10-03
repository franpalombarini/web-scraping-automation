"""
Exportación de datos a múltiples formatos.
"""

import csv
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


class Exporter:
    """Maneja exportación de datos a diferentes formatos"""
    
    @staticmethod
    def crear_directorio(filepath: str):
        """Crea directorio padre si no existe"""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def a_csv(cls, datos: List[Dict[str, Any]], filepath: str, 
              campos: List[str] = None):
        """
        Exporta lista de diccionarios a CSV.
        
        Args:
            datos: Lista de diccionarios con datos
            filepath: Ruta de archivo destino
            campos: Orden de columnas (default: keys del primer elemento)
        """
        if not datos:
            raise ValueError("No hay datos para exportar")
        
        cls.crear_directorio(filepath)
        
        if campos is None:
            campos = list(datos[0].keys())
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=campos)
            writer.writeheader()
            writer.writerows(datos)
    
    @classmethod
    def a_json(cls, datos: List[Dict[str, Any]], filepath: str,
               metadata: bool = True):
        """
        Exporta a JSON con metadata opcional.
        
        Args:
            datos: Lista a exportar
            filepath: Destino
            metadata: Incluir timestamp y total
        """
        cls.crear_directorio(filepath)
        
        estructura = {
            'datos': datos
        }
        
        if metadata:
            estructura.update({
                'fecha_exportacion': datetime.now().isoformat(),
                'total_registros': len(datos),
                'version': '1.0'
            })
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(estructura, f, ensure_ascii=False, indent=2)
    
    @classmethod
    def a_sqlite(cls, datos: List[Dict[str, Any]], db_path: str, 
                 tabla: str = 'datos'):
        """
        Exporta a base de datos SQLite.
        
        Args:
            datos: Lista de diccionarios
            db_path: Ruta del archivo .db
            tabla: Nombre de tabla a crear/usar
        """
        if not datos:
            raise ValueError("No hay datos para exportar")
        
        cls.crear_directorio(db_path)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Inferir columnas del primer registro
        columnas = list(datos[0].keys())
        tipos = {col: 'TEXT' for col in columnas}
        
        # Detectar tipos numéricos
        for key in columnas:
            valor = datos[0].get(key)
            if isinstance(valor, int):
                tipos[key] = 'INTEGER'
            elif isinstance(valor, float):
                tipos[key] = 'REAL'
        
        # Crear tabla
        cols_def = ', '.join([f"{k} {v}" for k, v in tipos.items()])
        sql = f"CREATE TABLE IF NOT EXISTS {tabla} ({cols_def})"
        cursor.execute(sql)
        
        # Insertar datos
        placeholders = ', '.join(['?' for _ in columnas])
        columnas_str = ', '.join(columnas)
        
        for fila in datos:
            valores = [fila.get(col) for col in columnas]
            sql = f"INSERT INTO {tabla} ({columnas_str}) VALUES ({placeholders})"
            cursor.execute(sql, valores)
        
        conn.commit()
        conn.close()


def exportar_multiformato(datos: List[Dict], base_path: str, 
                          formatos: List[str] = None):
    """
    Exporta a múltiples formatos simultáneamente.
    
    Ejemplo:
        datos = [{'nombre': 'A', 'precio': 100}, ...]
        exportar_multiformato(datos, 'output/reporte', ['csv', 'json', 'sqlite'])
    """
    if formatos is None:
        formatos = ['csv', 'json']
    
    resultados = {}
    
    for formato in formatos:
        try:
            if formato == 'csv':
                filepath = f"{base_path}.csv"
                Exporter.a_csv(datos, filepath)
                resultados['csv'] = filepath
                
            elif formato == 'json':
                filepath = f"{base_path}.json"
                Exporter.a_json(datos, filepath)
                resultados['json'] = filepath
                
            elif formato == 'sqlite':
                filepath = f"{base_path}.db"
                Exporter.a_sqlite(datos, filepath)
                resultados['sqlite'] = filepath
                
        except Exception as e:
            resultados[formato] = f"ERROR: {e}"
    
    return resultados
