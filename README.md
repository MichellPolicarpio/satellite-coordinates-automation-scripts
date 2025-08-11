# Scripts de Automatización - Captura Masiva de Coordenadas con API de Google

## 👨‍💻 **Autor del Proyecto**
**Michell Alexis Policarpio Moran**  
*Servicio Social en Grupo Mas Agua*  

Esta carpeta contiene **2 scripts esenciales** para automatizar la creación del dataset de detección de piscinas utilizando tecnologías modernas de procesamiento de imágenes y APIs de geolocalización.

## 🛠️ **Tecnologías y Librerías Utilizadas**

### **Lenguaje de Programación**
- **Python 3.8+** - Lenguaje principal para el desarrollo de scripts de automatización

### **Librerías Principales**
- **`requests`** - Cliente HTTP para consumir APIs REST (Google Maps Static API)
- **`PIL (Pillow)`** - Procesamiento y manipulación de imágenes
- **`json`** - Manejo de archivos de configuración y metadatos
- **`os`** - Operaciones del sistema de archivos y directorios
- **`re`** - Expresiones regulares para parsing de coordenadas DMS
- **`datetime`** - Gestión de timestamps y metadatos temporales
- **`typing`** - Anotaciones de tipos para mejor documentación del código

### **APIs y Servicios Externos**
- **Google Maps Static API** - Captura de imágenes satelitales de alta resolución
- **Google Maps Platform** - Servicios de geolocalización y coordenadas

### **Características Técnicas**
- **Formato de Imagen**: JPEG con calidad 95% para optimizar tamaño vs calidad
- **Resolución**: 50x50 píxeles (formato estándar para datasets de ML)
- **Zoom Satelital**: Nivel 19 para máxima resolución de detalle
- **Coordenadas**: Soporte para formatos decimal y DMS (Grados, Minutos, Segundos)

## 📁 Estructura Simplificada

```
scripts_automatizadores/
├── 01_coordinate_collector.py    # Recolector de coordenadas
├── 02_mass_capture.py            # Captura masiva de imágenes
├── config/                       # Configuraciones
│   ├── settings.json
│   ├── pool_coordinates.json
│   └── no_pool_coordinates.json
└── README.md                     # Este archivo
```

## 🎯 **Propósito Académico y Científico**

Estos scripts son herramientas creadas para automatizar trabajos repetitivos de recoleccion masiva de ciertos puntos de interes para la creación de un dataset para un proyecto de **Servicio Social** en **Grupo Mas Agua**, enfocado en el desarrollo de **sistemas de inteligencia artificial** para la **detección automatizada de piscinas** mediante análisis de imágenes satelitales.

### **Objetivos del Proyecto**
- **Automatización completa** del proceso de recolección de datos geográficos
- **Generación acelerada de recopilacion de imagenes satelitales** para entrenamiento de modelos de ML
- **Optimización de recursos** mediante el uso eficiente de APIs de geolocalización
- **Estándarización de formatos** para facilitar el entrenamiento de redes neuronales
- **Contribución al campo** de la teledetección y análisis de imágenes satelitales

### Paso 1: Recolectar Coordenadas
```bash
python 01_coordinate_collector.py
```

**Funcionalidades:**
- ✅ Ingreso directo de coordenadas decimales (sin conversión)
- ✅ Almacenamiento automático en `coordinates.json`
- ✅ Soporte para piscinas y áreas sin piscinas
- ✅ Interfaz interactiva y ejemplos rápidos
- ✅ Comandos: `mostrar`, `guardar`, `fin`

**Formato de entrada:**
```
19.1738, -96.1342, pool, Veracruz_Centro_Pool1
19.1800, -96.1400, no_pool, Veracruz_Industrial
```

### Paso 2: Captura Masiva
```bash
python 02_mass_capture.py
```

**Funcionalidades:**
- ✅ Captura automática de imágenes 50x50 píxeles
- ✅ Lectura desde `coordinates.json`
- ✅ Generación de variaciones por coordenada
- ✅ Organización automática en carpetas `pools/` y `no_pools/`
- ✅ Control de velocidad para evitar límites de API
- ✅ Actualización automática del estado de captura

## 📊 Resultados Esperados

Con **4 coordenadas de piscinas** y **4 coordenadas sin piscinas**, cada una con **15 variaciones**:

- **Piscinas:** 4 × (1 + 15) = **64 imágenes**
- **Sin piscinas:** 4 × (1 + 15) = **64 imágenes**
- **Total:** **128 imágenes** de 50x50 píxeles

## ⚙️ **Configuración Requerida**

### **1. API Key de Google Maps**
Edita la variable `API_KEY` en `02_mass_capture.py`:
```python
API_KEY = "TU_API_KEY_AQUI"  # Reemplaza con tu API key
```

**Pasos para obtener la API Key:**
1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita la **Maps Static API** en la biblioteca de APIs
4. Ve a **Credenciales** → **Crear credenciales** → **Clave de API**
5. Restringe la clave solo a **Maps Static API** por seguridad

### **2. Dependencias del Sistema**
```bash
# Instalación de librerías principales
pip install requests pillow

# Verificación de versiones recomendadas
pip install requests>=2.28.0
pip install Pillow>=9.0.0
```

### **3. Requisitos del Sistema**
- **Python**: 3.8 o superior
- **Memoria RAM**: Mínimo 4GB (recomendado 8GB+)
- **Almacenamiento**: 1GB libre para datasets pequeños
- **Conexión**: Internet estable para consumo de APIs
- **Sistema Operativo**: Windows, macOS o Linux

## 📋 Archivos Generados

- `coordinates.json` - Coordenadas recolectadas
- `data/train/pools/` - Imágenes de piscinas
- `data/train/no_pools/` - Imágenes sin piscinas

## 🎯 Ventajas de la Simplificación

1. **Menos complejidad** - Solo 2 scripts esenciales
2. **Sin conversión manual** - Coordenadas decimales directas
3. **Almacenamiento automático** - JSON persistente
4. **Captura masiva eficiente** - Una sola ejecución
5. **Organización automática** - Carpetas separadas por tipo

## 💡 Consejos de Uso

1. **Recolecta coordenadas** primero con el script 01
2. **Verifica el JSON** antes de la captura masiva
3. **Configura tu API key** en el script 02
4. **Ejecuta la captura** y espera a que termine
5. **Revisa las carpetas** `data/train/` para verificar los resultados

¡Listo para acelerar la recoleccion de imagenes para tu dataset! 🎉

## 📞 **Contacto y Soporte**

**Autor:** Michell Alexis Policarpio Moran    
**Tecnologías:** Python, APIs de Google Maps, Procesamiento de Imágenes

---

*Estos scripts demuestran la aplicación práctica de par automatizar tareas repetitivas como la recoleccion másiva de imagenes para un determinado dataset con imagenes satelitales.* 🚀
