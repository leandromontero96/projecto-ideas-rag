# 🚀 Project Ideas RAG System

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![LangChain](https://img.shields.io/badge/LangChain-121212?logo=chainlink&logoColor=white)](https://langchain.com)
[![Claude](https://img.shields.io/badge/Claude-191919?logo=anthropic&logoColor=white)](https://www.anthropic.com)

Sistema RAG (Retrieval-Augmented Generation) especializado en gestionar y consultar ideas de proyectos de análisis de datos con funcionalidades avanzadas de categorización automática, filtrado multi-dimensional y estimación de impacto.

---

## 📹 Demo

> **Nota:** Agrega aquí un GIF o video demostrativo cuando tengas la interfaz completa

## 🎯 Problema que Resuelve

Como analista de datos, tienes decenas de ideas de proyectos dispersas en PDFs, Word, notas... Este sistema las organiza automáticamente, estima su ROI, analiza complejidad y te ayuda a priorizar qué implementar primero.

## Características Principales

### Auto-Categorización Inteligente
- Sistema de 3 niveles: keywords, embeddings semánticos, y Claude LLM
- 15 categorías especializadas: prediction, classification, computer_vision, nlp, optimization, dashboard, data_engineering, y más
- Confianza scores para validar la categorización

### Análisis de Complejidad Multi-Factor
- Evalúa 5 factores: complejidad de datos, algoritmos, habilidades técnicas, integración, deployment
- Clasificación automática: básico, intermedio, avanzado
- Identificación de skills requeridos

### Estimación de Impacto y ROI
- Extracción automática de ROI, ahorro de costos, ahorro de tiempo
- Patterns regex + Claude LLM para máxima precisión
- Métricas de negocio cualitativas y cuantitativas

### Filtrado y Búsqueda Avanzada
- Filtros multi-dimensionales: categoría + tecnología + complejidad + ROI
- Búsqueda semántica con embeddings
- Modos de matching: ANY o ALL para tecnologías

### Interfaz Especializada
- Browse: Vista en grid con cards visuales
- Comparación: Compara 2-3 proyectos lado a lado
- Dashboard: Analytics agregados con gráficos interactivos
- Q&A: Sistema RAG tradicional con atribución de fuentes

## Instalación

### Requisitos Previos
- Python 3.9+
- pip
- Claude API Key (Anthropic)

### Pasos de Instalación

1. **Clonar o descargar el proyecto**
```bash
cd project-ideas-rag
```

2. **Crear entorno virtual (recomendado)**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar .env y agregar tu API key de Anthropic
# ANTHROPIC_API_KEY=your_actual_api_key_here
```

5. **Instalar modelo de spaCy (opcional, para mejor NLP)**
```bash
python -m spacy download en_core_web_sm
```

## Uso

### Iniciar la Aplicación

```bash
streamlit run app.py
```

La aplicación se abrirá en tu navegador en `http://localhost:8501`

### Flujo de Trabajo

1. **Subir Documentos**
   - Usa el sidebar para subir PDFs, Word, CSV o Excel
   - Click en "Ingest Documents" para procesar
   - El sistema automáticamente:
     - Extrae metadatos estructurados
     - Categoriza el proyecto
     - Analiza complejidad
     - Estima impacto y ROI
     - Detecta tecnologías mencionadas

2. **Explorar Proyectos**
   - Tab "Browse": Vista en cards con filtros
   - Aplica filtros por categoría, tecnología, complejidad, ROI
   - Búsqueda semántica: "machine learning para customer churn"

3. **Comparar Proyectos**
   - Tab "Compare": Selecciona 2-3 proyectos
   - Ve tabla comparativa y gráficos de radar

4. **Analizar Impacto**
   - Tab "Dashboard": Métricas agregadas
   - Distribución por categoría
   - Scatter plot complejidad vs ROI
   - Heatmap de tecnologías populares

5. **Hacer Preguntas**
   - Tab "Q&A": Pregunta sobre proyectos específicos
   - Sistema RAG responde con fuentes

## Estructura del Proyecto

```
project-ideas-rag/
├── app.py                          # Streamlit app principal
├── requirements.txt                # Dependencias
├── .env.example                    # Plantilla de configuración
├── README.md                       # Este archivo
├── project_template.md             # Plantilla para documentar ideas
│
├── src/
│   ├── config.py                   # Configuración central
│   ├── schemas.py                  # Modelos Pydantic
│   ├── metadata_extractor.py       # Extracción inteligente de metadatos
│   ├── categorizer.py              # Auto-categorización híbrida
│   ├── complexity_analyzer.py      # Análisis de complejidad
│   ├── impact_analyzer.py          # Estimación de ROI e impacto
│   ├── metadata_store.py           # Almacenamiento de metadatos
│   ├── filter_engine.py            # Motor de filtrado (a implementar)
│   ├── rag_engine.py               # Motor RAG (a implementar)
│   └── document_processor.py       # Procesamiento de docs (a implementar)
│
├── data/
│   ├── documents/                  # Documentos subidos
│   ├── vectorstore/                # ChromaDB
│   └── metadata/                   # Cache de metadatos JSON
│
└── config/
    ├── categories.json             # 15 categorías con keywords
    ├── technologies.json           # Taxonomía de 100+ tecnologías
    ├── complexity_rules.json       # Reglas de scoring de complejidad
    └── impact_metrics.json         # Patterns para extracción de ROI
```

## Plantilla de Proyecto

Usa `project_template.md` como guía para estructurar tus ideas de proyectos. Esto mejora la extracción automática de metadatos.

Secciones clave:
- **Executive Summary**: Resumen de 2-3 oraciones
- **Business Problem**: Problema a resolver
- **Technical Approach**: Tecnologías, datos, metodología
- **Expected Impact**: ROI, ahorro de costos, métricas
- **Implementation Plan**: Complejidad, esfuerzo, milestones

## Categorías Soportadas

1. **prediction**: Forecasting, regresión, predicción
2. **classification**: Clasificación binaria/multi-clase
3. **computer_vision**: Procesamiento de imágenes, object detection, OCR
4. **nlp**: Análisis de texto, sentiment analysis, NER
5. **optimization**: Optimización de recursos, rutas, scheduling
6. **dashboard**: Business intelligence, reportes, KPIs
7. **data_engineering**: ETL, pipelines, data warehouse
8. **exploratory_analysis**: EDA, análisis estadístico
9. **anomaly_detection**: Detección de fraude, outliers
10. **time_series**: Análisis temporal, forecasting
11. **recommendation**: Sistemas de recomendación
12. **clustering**: Segmentación, agrupamiento
13. **a_b_testing**: Experimentación, testing
14. **etl**: Extract, Transform, Load
15. **other**: Otros proyectos de análisis

## Tecnologías Detectadas

El sistema reconoce automáticamente 100+ tecnologías en 10 categorías:
- **Languages**: Python, R, SQL, Julia, Scala
- **ML Frameworks**: scikit-learn, TensorFlow, PyTorch, XGBoost, LightGBM
- **Data Tools**: Pandas, NumPy, Spark, Dask
- **Visualization**: Tableau, Power BI, Plotly, Matplotlib
- **Databases**: PostgreSQL, MongoDB, Snowflake, BigQuery
- **Cloud**: AWS, Azure, GCP, Databricks
- **ETL/Orchestration**: Airflow, dbt, Prefect
- **MLOps**: MLflow, Weights & Biases, SageMaker
- Y más...

## Configuración Avanzada

### Ajustar Umbral de Confianza

En `.env`:
```
CATEGORIZATION_CONFIDENCE_THRESHOLD=0.6
```
- Valores más altos (0.7-0.9): Más conservador, usa LLM con más frecuencia
- Valores más bajos (0.4-0.6): Más agresivo, confía más en keywords

### Personalizar Categorías

Edita `config/categories.json` para agregar nuevas categorías o modificar keywords y pesos.

### Agregar Tecnologías

Edita `config/technologies.json` para agregar nuevas tecnologías y aliases.

### Modificar Factores de Complejidad

Edita `config/complexity_rules.json` para ajustar pesos y umbrales.

## Troubleshooting

### Error: ANTHROPIC_API_KEY not configured
- Verifica que `.env` existe y tiene tu API key
- Formato correcto: `ANTHROPIC_API_KEY=sk-ant-...`

### No se detectan tecnologías
- Verifica que `config/technologies.json` existe
- Asegúrate que los nombres de tecnologías están escritos correctamente en tus documentos

### Categorización siempre devuelve "other"
- Verifica que `config/categories.json` existe
- Aumenta el contenido descriptivo en tus documentos
- Reduce `CATEGORIZATION_CONFIDENCE_THRESHOLD`

### ChromaDB errors
- Elimina `data/vectorstore/` y reinicia
- Asegúrate de tener permisos de escritura en el directorio

## Desarrollo

### Ejecutar Tests
```bash
pytest tests/
```

### Formatear Código
```bash
black src/ app.py
```

### Agregar Nueva Funcionalidad
1. Actualiza schemas.py si cambias la estructura de metadatos
2. Modifica los extractores/analizadores según necesites
3. Actualiza la UI en app.py
4. Documenta cambios en README

## Roadmap

- [ ] Implementar document_processor.py completo
- [ ] Implementar rag_engine.py con metadata integration
- [ ] Implementar filter_engine.py avanzado
- [ ] Crear interfaz Streamlit completa (4 tabs)
- [ ] Agregar export a Excel/PDF
- [ ] Multi-usuario con autenticación
- [ ] API REST para integración
- [ ] Recomendaciones de proyectos similares
- [ ] Timeline de implementación sugerido

## Contribuir

Las contribuciones son bienvenidas! Por favor:
1. Fork el proyecto
2. Crea un branch para tu feature
3. Haz commit de tus cambios
4. Push al branch
5. Abre un Pull Request

## Licencia

Este proyecto es de código abierto bajo la licencia MIT.

## Soporte

Para preguntas, issues o sugerencias, abre un issue en el repositorio.

---

**Desarrollado con:**
- LangChain para RAG
- ChromaDB para vectorstore
- Claude API para LLM
- Streamlit para UI
- Pydantic para validación

**Autor:** [Tu Nombre]
**Fecha:** Abril 2026
