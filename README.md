# Web Scraping & Automation Scripts

Colección de scripts Python para extracción automatizada de datos web y procesamiento de información.

## Proyectos

### 1. Scraper de Precios Competencia
Extrae precios de productos de sitios e-commerce para análisis de mercado.

### 2. Monitor de Stock
Alerta cuando productos específicos vuelven a estar disponibles.

### 3. Extractor de Datos Estructurados
Convierte HTML no estructurado en CSV/JSON limpio.

## Tecnologías

- Python 3.11+
- Requests + BeautifulSoup4
- Pandas (procesamiento de datos)
- Schedule (automatización de tareas)

## Uso rápido

```bash
pip install -r requirements.txt
python scraper_ejemplo.py --url "https://ejemplo.com" --output datos.csv
```

## Estructura

```
web-scraping-automation/
├── README.md
├── requirements.txt
├── scraper_ejemplo.py      # Script principal
├── utils/
│   ├── parser.py           # Limpieza de datos
│   └── exporter.py         # Exportación a CSV/JSON
└── output/                 # Datos extraídos
```

## Ejemplo de salida

```csv
producto,precio,stock,fecha_extraccion
Notebook Lenovo,450000,True,2026-10-03
Mouse Logitech,12000,False,2026-10-03
```

## Notas técnicas

- Respeta robots.txt y límites de rate
- Headers rotativos para evitar bloqueos
- Manejo de errores y reintentos automáticos
- Logging detallado de operaciones

## Próximos pasos

- [ ] Integración con base de datos SQLite
- [ ] Notificaciones por Telegram/Email
- [ ] Dashboard simple con Flask
- [ ] Dockerización para despliegue

---

**Desarrollado por:** Franco Palombarini  
**Contacto:** fran.palombarini.dev@gmail.com  
**LinkedIn:** linkedin.com/in/franpalombarini-dev
