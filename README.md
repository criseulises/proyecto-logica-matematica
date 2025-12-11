# SmartPlannerX 🎓

Sistema Inteligente de Generación de Horarios Académicos

**Equipo 3:**
- Cristian E. Sánchez R. (25-0688)
- Hansel Augusto Pérez (25-0461)
- Lia De Oleo (25-0673)
- Juan José Cruz Romero (25-0888)
- Samir Gonzalez (25-0808)
- Alejandro Bruno (25-0947)
- Daniel Osvaldo Lopez (25-0655)

---

## 📋 Descripción

SmartPlannerX es una aplicación web desarrollada con Flask que permite a instituciones educativas y estudiantes gestionar y generar horarios académicos de manera inteligente, evitando conflictos de horarios mediante algoritmos de backtracking.

### Características Principales

- **🏛️ Panel de Institución**: Gestión centralizada de materias y secciones
- **👨‍🎓 Panel de Estudiante**: Selección de materias y generación de horarios personalizados
- **📊 Panel de Proyección**: Planificación de materias futuras
- **🤖 Asistente con IA**: Interpreta lenguaje natural para agregar materias
- **📁 Importación de Archivos**: Soporte para Excel (.xlsx, .xls) y JSON
- **🔍 Algoritmo Inteligente**: Usa backtracking para encontrar todas las combinaciones válidas sin conflictos

---

## 🚀 Instalación y Configuración

### Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar el repositorio** (o descargar el proyecto)
   ```bash
   cd Proyecto---Logica-Matematica
   ```

2. **Crear un entorno virtual**
   ```bash
   python3 -m venv venv
   ```

3. **Activar el entorno virtual**

   En macOS/Linux:
   ```bash
   source venv/bin/activate
   ```

   En Windows:
   ```bash
   venv\Scripts\activate
   ```

4. **Instalar las dependencias**
   ```bash
   pip install -r requirements.txt
   ```

---

## ▶️ Cómo Ejecutar el Proyecto

1. **Asegúrate de que el entorno virtual esté activado**

   Deberías ver `(venv)` al inicio de tu línea de comando.

2. **Ejecutar la aplicación**
   ```bash
   python app.py
   ```

3. **Abrir en el navegador**

   Accede a: [http://localhost:5200](http://localhost:5200)

4. **Detener el servidor**

   Presiona `Ctrl + C` en la terminal

---

## 📖 Guía de Uso

### 1. Página de Inicio
Al acceder a la aplicación, encontrarás tres opciones:

#### 🏛️ Institución
- **Propósito**: Agregar y gestionar el catálogo completo de materias
- **Funcionalidades**:
  - Agregar materias mediante asistente rápido (lenguaje natural)
  - Entrada manual con formulario
  - Importar archivos Excel o JSON
  - Ver vista previa del catálogo
  - Eliminar materias y secciones

**Ejemplo de uso del asistente:**
```
Calculo 101 Lunes,Miercoles 8-10
```

#### 👨‍🎓 Estudiante
- **Propósito**: Seleccionar materias del catálogo institucional
- **Funcionalidades**:
  - Ver todas las materias disponibles
  - Seleccionar secciones específicas mediante checkboxes
  - Generar horarios sin conflictos
  - Navegar entre múltiples soluciones válidas

#### 📊 Proyección
- **Propósito**: Planificar materias futuras de manera personal
- **Funcionalidades**:
  - Agregar materias personales (separadas del catálogo institucional)
  - Importar archivos Excel o JSON
  - Simular diferentes combinaciones de horarios
  - Limpiar proyección completa

### 2. Formato de Archivos

#### JSON
```json
{
  "BLOQUE_ID": {
    "materias": [
      {
        "codigo": "EGC154",
        "nombre": "Cálculo I",
        "seccion": "01",
        "horarios": [
          {
            "dia": "LUNES",
            "hora": "05:00 PM / 08:00 PM"
          }
        ]
      }
    ]
  }
}
```

#### Excel
Columnas requeridas:
- `Código`: Código de la materia (ej: EGC154)
- `Materia`: Nombre de la materia
- `Sección`: Número de sección
- `Día`: Día de la semana (LUNES, MARTES, etc.)
- `Horario`: Formato "HH:MM AM/PM / HH:MM AM/PM"

---

## 🏗️ Estructura del Proyecto

```
Proyecto---Logica-Matematica/
├── app.py                    # Aplicación principal Flask
├── requirements.txt          # Dependencias del proyecto
├── .gitignore               # Archivos ignorados por Git
├── README.md                # Este archivo
│
├── src/
│   ├── __init__.py          # Inicializador del módulo
│   ├── logic.py             # Lógica de negocio (backtracking)
│   ├── parser.py            # Parser de lenguaje natural
│   └── file_parser.py       # Parser de archivos Excel/JSON
│
├── templates/               # Plantillas HTML
│   ├── home.html           # Página de inicio
│   ├── institucion.html    # Panel de institución
│   ├── estudiante.html     # Panel de estudiante
│   └── proyeccion.html     # Panel de proyección
│
├── static/                  # Archivos estáticos
│   ├── style.css           # Estilos CSS
│   └── script.js           # JavaScript principal
│
└── uploads/                 # Carpeta temporal para archivos
```

---

## 🧮 Algoritmos Implementados

### 1. Backtracking (Recursión)
Algoritmo recursivo que explora todas las combinaciones posibles de secciones, retrocediendo cuando encuentra conflictos de horario.

```python
def _backtrack(self, materias_restantes, horario_actual):
    if not materias_restantes:
        self.soluciones.append(copy.copy(horario_actual))
        return

    for seccion in materia_actual.secciones:
        if self._es_valido(seccion, horario_actual):
            horario_actual.append((materia_actual.nombre, seccion))
            self._backtrack(materias_restantes[1:], horario_actual)
            horario_actual.pop()  # Backtrack
```

### 2. Teoría de Conteos (Principio Multiplicativo)
Calcula el número total de combinaciones teóricas posibles multiplicando el número de secciones disponibles por materia.

```python
def calcular_combinaciones_teoricas(self):
    total = 1
    for m in self.materias:
        total *= len(m.secciones)
    return total
```

### 3. Detección de Conflictos
Verifica si dos secciones se solapan comparando días y rangos de horas.

```python
def choca_con(self, otra_seccion):
    dias_comunes = set(self.dias) & set(otra_seccion.dias)
    if not dias_comunes:
        return False
    return (self.hora_inicio < otra_seccion.hora_fin) and
           (otra_seccion.hora_inicio < self.hora_fin)
```

---

## 🛠️ Tecnologías Utilizadas

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Librerías**:
  - `openpyxl`: Lectura de archivos Excel
  - `python-dateutil`: Manejo de fechas
- **UI/UX**:
  - FontAwesome (iconos)
  - SweetAlert2 (alertas)
  - Google Fonts (Outfit)

---

## 📝 Notas Importantes

- Los datos se almacenan en memoria (se pierden al reiniciar el servidor)
- Las materias institucionales y de proyección están separadas
- Tamaño máximo de archivo: 16MB
- Puerto por defecto: 5200

---

## 🐛 Solución de Problemas

### Error: "Module not found"
```bash
pip install -r requirements.txt
```

### Error: "Address already in use"
El puerto 5200 está ocupado. Cambia el puerto en `app.py`:
```python
app.run(debug=True, port=5201)  # Usar otro puerto
```

### Error al importar archivos Excel
Verifica que el archivo tenga las columnas correctas:
- Código, Materia, Sección, Día, Horario

---

## 📄 Licencia

Proyecto académico - Universidad Iberoamericana (UNIBE)

Curso: Lógica Matemática

---

## 👥 Contacto

Para preguntas o soporte, contacta a cualquier miembro del Equipo 3.

---

**Desarrollado con ❤️ por el Equipo 3**
