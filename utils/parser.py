"""
Utilidades para limpieza y normalización de datos extraídos.
"""

import re
from typing import Optional


def limpiar_texto(texto: str) -> str:
    """
    Normaliza texto extraído de HTML.
    
    - Elimina espacios múltiples
    - Remueve caracteres especiales de control
    - Trim de espacios
    """
    if not texto:
        return ""
    
    # Reemplazar espacios múltiples
    texto = re.sub(r'\s+', ' ', texto)
    # Remover caracteres de control
    texto = ''.join(c for c in texto if c.isprintable() or c.isspace())
    return texto.strip()


def extraer_numero(texto: str) -> Optional[float]:
    """
    Extrae el primer número encontrado en un texto.
    Útil para precios, cantidades, etc.
    """
    if not texto:
        return None
    
    # Buscar patrones numéricos con decimales
    patrones = [
        r'\$\s*([\d.,]+)',  # $ 1.234,56
        r'([\d.,]+)\s*\$',  # 1.234,56 $
        r'([\d.]+,[\d]+)',    # 1.234,56
        r'([\d,]+\.[\d]+)',  # 1,234.56
        r'([\d]+)',            # 1234
    ]
    
    for patron in patrones:
        match = re.search(patron, texto)
        if match:
            numero = match.group(1)
            # Normalizar separadores
            numero = numero.replace('.', '').replace(',', '.')
            try:
                return float(numero)
            except ValueError:
                continue
    
    return None


def normalizar_url(base: str, relativa: str) -> str:
    """
    Convierte URLs relativas a absolutas.
    """
    if relativa.startswith('http'):
        return relativa
    
    from urllib.parse import urljoin
    return urljoin(base, relativa)


def truncar(texto: str, max_len: int = 100) -> str:
    """Trunca texto a longitud máxima"""
    if len(texto) <= max_len:
        return texto
    return texto[:max_len-3] + '...'
