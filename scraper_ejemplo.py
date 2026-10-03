#!/usr/bin/env python3
"""
Scraper de ejemplo: extracción de datos web con manejo de errores,
rate limiting y exportación a CSV/JSON.

Uso:
    python scraper_ejemplo.py --url "https://ejemplo.com" --output datos.csv
"""

import argparse
import csv
import json
import logging
import random
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class Producto:
    """Estructura de datos para productos extraídos"""
    nombre: str
    precio: Optional[float]
    stock: bool
    url: str
    fecha_extraccion: str = None
    
    def __post_init__(self):
        if self.fecha_extraccion is None:
            self.fecha_extraccion = datetime.now().isoformat()


class WebScraper:
    """Scraper base con configuración de headers y rate limiting"""
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
    ]
    
    def __init__(self, delay_range: tuple = (1, 3)):
        self.session = requests.Session()
        self.delay_range = delay_range
        self._rotar_user_agent()
    
    def _rotar_user_agent(self):
        """Cambia el User-Agent para evitar detección"""
        self.session.headers.update({
            'User-Agent': random.choice(self.USER_AGENTS)
        })
    
    def _rate_limit(self):
        """Aplica delay aleatorio entre requests"""
        delay = random.uniform(*self.delay_range)
        time.sleep(delay)
    
    def fetch(self, url: str, retries: int = 3) -> Optional[BeautifulSoup]:
        """
        Obtiene y parsea HTML con reintentos automáticos
        
        Args:
            url: URL a scrapear
            retries: Número de intentos fallidos antes de abandonar
            
        Returns:
            BeautifulSoup object o None si falla
        """
        for intento in range(retries):
            try:
                self._rate_limit()
                self._rotar_user_agent()
                
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                return BeautifulSoup(response.content, 'lxml')
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Intento {intento + 1}/{retries} falló: {e}")
                if intento < retries - 1:
                    time.sleep(2 ** intento)  # Backoff exponencial
                    
        logger.error(f"Falló después de {retries} intentos: {url}")
        return None
    
    def extraer_productos(self, soup: BeautifulSoup) -> List[Producto]:
        """
        Extrae datos de productos del HTML parseado.
        Personalizar según la estructura del sitio objetivo.
        
        Returns:
            Lista de objetos Producto
        """
        productos = []
        
        # Ejemplo genérico - adaptar selectores según sitio real
        items = soup.select('.producto, .item, [data-product]')
        
        for item in items:
            try:
                nombre = item.select_one('.nombre, .titulo, h2, h3')
                precio = item.select_one('.precio, .price, [data-price]')
                stock = item.select_one('.stock, .disponible')
                
                producto = Producto(
                    nombre=nombre.text.strip() if nombre else 'N/A',
                    precio=self._limpiar_precio(precio.text if precio else None),
                    stock=self._verificar_stock(stock),
                    url=item.get('href', '')
                )
                productos.append(producto)
                
            except Exception as e:
                logger.warning(f"Error extrayendo item: {e}")
                continue
        
        logger.info(f"Extraídos {len(productos)} productos")
        return productos
    
    def _limpiar_precio(self, texto: Optional[str]) -> Optional[float]:
        """Convierte texto de precio a float"""
        if not texto:
            return None
        try:
            # Remover símbolos de moneda y separadores
            limpio = texto.replace('$', '').replace('.', '').replace(',', '.')
            return float(limpio)
        except ValueError:
            return None
    
    def _verificar_stock(self, elemento) -> bool:
        """Determina si hay stock disponible"""
        if not elemento:
            return False
        texto = elemento.text.lower()
        return 'disponible' in texto or 'stock' in texto or 'hay' in texto


class DataExporter:
    """Exporta datos extraídos a CSV o JSON"""
    
    @staticmethod
    def to_csv(productos: List[Producto], filepath: str):
        """Exporta a CSV"""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['producto', 'precio', 'stock', 'url', 'fecha_extraccion'])
            
            for p in productos:
                writer.writerow([p.nombre, p.precio, p.stock, p.url, p.fecha_extraccion])
        
        logger.info(f"CSV exportado: {filepath}")
    
    @staticmethod
    def to_json(productos: List[Producto], filepath: str):
        """Exporta a JSON"""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        datos = [
            {
                'producto': p.nombre,
                'precio': p.precio,
                'stock': p.stock,
                'url': p.url,
                'fecha_extraccion': p.fecha_extraccion
            }
            for p in productos
        ]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
        
        logger.info(f"JSON exportado: {filepath}")


def main():
    parser = argparse.ArgumentParser(description='Web Scraper de ejemplo')
    parser.add_argument('--url', required=True, help='URL objetivo')
    parser.add_argument('--output', '-o', default='output/datos.csv', help='Archivo de salida')
    parser.add_argument('--formato', choices=['csv', 'json'], default='csv')
    parser.add_argument('--delay', nargs=2, type=float, default=[1, 3], 
                       help='Rango de delay entre requests (min max)')
    
    args = parser.parse_args()
    
    # Ejecutar scraping
    scraper = WebScraper(delay_range=tuple(args.delay))
    soup = scraper.fetch(args.url)
    
    if not soup:
        logger.error("No se pudo obtener la página")
        return 1
    
    productos = scraper.extraer_productos(soup)
    
    if not productos:
        logger.warning("No se encontraron productos")
        return 0
    
    # Exportar
    exporter = DataExporter()
    if args.formato == 'csv':
        exporter.to_csv(productos, args.output)
    else:
        exporter.to_json(productos, args.output)
    
    # Resumen
    print(f"\n✅ Extracción completada: {len(productos)} productos")
    print(f"   Guardados en: {args.output}")
    
    return 0


if __name__ == '__main__':
    exit(main())
