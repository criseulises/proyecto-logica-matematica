"""
SmartPlannerX - Sistema Inteligente de Generación de Horarios Académicos

Equipo 3:
- Cristian E. Sánchez R. (25-0688)
- Hansel Augusto Pérez (25-0461)
- Lia De Oleo (25-0673)
- Juan José Cruz Romero (25-0888)
- Samir Gonzalez (25-0808)
- Alejandro Bruno (25-0947)
- Daniel Osvaldo Lopez (25-0655)
"""

from flask import Flask, render_template, request, jsonify
from src.logic import Materia, Seccion, GeneradorHorarios
from src.parser import SmartParser
from src.file_parser import FileParser
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# En Vercel, usar /tmp para uploads (único directorio escribible)
if os.environ.get('VERCEL'):
    app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
else:
    app.config['UPLOAD_FOLDER'] = 'uploads'

# Crear carpeta de uploads si no existe
try:
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
except Exception:
    pass  # En entornos read-only, ignorar error

# Almacenamiento en memoria
# Materias institucionales (compartidas)
materias_institucionales = []

# Materias de proyección personal (separadas)
materias_proyeccion = []

# === RUTAS PRINCIPALES ===

@app.route('/')
def home():
    """Página de inicio con selección de roles."""
    return render_template('home.html')

@app.route('/institucion')
def institucion():
    """Panel de institución."""
    return render_template('institucion.html')

@app.route('/estudiante')
def estudiante():
    """Panel de estudiante."""
    return render_template('estudiante.html')

@app.route('/proyeccion')
def proyeccion():
    """Panel de proyección personal."""
    return render_template('proyeccion.html')

# === API INSTITUCIÓN ===

@app.route('/api/add', methods=['POST'])
def add_section():
    """Endpoint para agregar una sección institucional."""
    data = request.json
    return _add_materia_internal(data, materias_institucionales)

@app.route('/api/delete', methods=['POST'])
def delete_materia():
    """Elimina una materia institucional completa por nombre."""
    data = request.json
    nombre = data.get('materia')
    global materias_institucionales
    materias_institucionales = [m for m in materias_institucionales if m.nombre != nombre]
    return jsonify({'message': f'Materia {nombre} eliminada'})

@app.route('/api/delete_section', methods=['POST'])
def delete_section():
    """Elimina una sección institucional específica."""
    data = request.json
    nombre_materia = data.get('materia')
    uuid_seccion = data.get('uuid')

    materia = next((m for m in materias_institucionales if m.nombre == nombre_materia), None)
    if materia:
        materia.secciones = [s for s in materia.secciones if s.uuid != uuid_seccion]
        return jsonify({'success': True, 'message': 'Sección eliminada'})

    return jsonify({'success': False, 'message': 'Materia no encontrada'})

@app.route('/api/toggle_section', methods=['POST'])
def toggle_section():
    """Toggle enabled/disabled de una sección institucional."""
    data = request.json
    nombre_materia = data.get('materia')
    uuid_seccion = data.get('uuid')
    enabled = data.get('enabled')

    materia = next((m for m in materias_institucionales if m.nombre == nombre_materia), None)
    if materia:
        seccion = next((s for s in materia.secciones if s.uuid == uuid_seccion), None)
        if seccion:
            seccion.enabled = enabled
            return jsonify({'success': True})

    return jsonify({'success': False, 'message': 'Materia o sección no encontrada'})

@app.route('/api/list', methods=['GET'])
def list_materias():
    """Lista todas las materias institucionales."""
    lista = []
    for m in materias_institucionales:
        secciones_data = []
        for s in m.secciones:
            secciones_data.append({
                'uuid': s.uuid,
                'id': s.id_seccion,
                'dias': s.dias,
                'inicio': s.hora_inicio,
                'fin': s.hora_fin,
                'enabled': s.enabled
            })
        lista.append({'nombre': m.nombre, 'secciones': secciones_data})
    return jsonify(lista)

@app.route('/api/chat', methods=['POST'])
def chat_bot():
    """Chat bot para agregar materias institucionales."""
    data = request.json
    mensaje = data.get('mensaje', '')

    resultado = SmartParser.parse(mensaje)

    if 'error' in resultado:
        return jsonify({'success': False, 'message': resultado['error']})

    _add_materia_internal(resultado, materias_institucionales)

    # Formatear mensaje de éxito
    dias_str = ", ".join(resultado['dias'])
    return jsonify({
        'success': True,
        'message': f"Agregada: {resultado['materia']} (Sec {resultado['seccion']}) [{dias_str} {resultado['inicio']}-{resultado['fin']}]"
    })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Endpoint para subir archivos Excel o JSON (institución)."""
    return _process_file_upload(materias_institucionales)

def _process_file_upload(materias_db):
    """Procesa la carga de archivos Excel o JSON."""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No se envió ningún archivo'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'success': False, 'error': 'Archivo vacío'}), 400

    filename = secure_filename(file.filename)
    file_ext = os.path.splitext(filename)[1].lower()

    if file_ext not in ['.json', '.xlsx', '.xls']:
        return jsonify({'success': False, 'error': 'Formato no soportado. Use JSON o Excel'}), 400

    try:
        if file_ext == '.json':
            # Leer contenido JSON
            content = file.read().decode('utf-8')
            result = FileParser.parse_json(content)
        else:
            # Guardar Excel temporalmente
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            result = FileParser.parse_excel(filepath)
            # Eliminar archivo temporal
            os.remove(filepath)

        if not result['success']:
            return jsonify(result), 400

        # Agregar materias al sistema
        added = 0
        errors = []

        for materia_data in result['materias']:
            try:
                response = _add_materia_internal(materia_data, materias_db)
                # Verificar si la respuesta es un error
                if isinstance(response, tuple) and response[1] >= 400:
                    errors.append(f"{materia_data['materia']}: Error al agregar")
                else:
                    added += 1
            except Exception as e:
                errors.append(f"{materia_data['materia']}: {str(e)}")

        return jsonify({
            'success': True,
            'message': f'Archivo procesado: {added} secciones agregadas',
            'total': result['count'],
            'added': added,
            'errors': len(errors),
            'error_details': errors[:5]  # Solo primeros 5 errores
        })

    except Exception as e:
        return jsonify({'success': False, 'error': f'Error procesando archivo: {str(e)}'}), 500

# === API ESTUDIANTE ===

@app.route('/api/generate_student', methods=['POST'])
def generate_student():
    """Genera horarios para estudiante basado en selecciones."""
    data = request.json
    selected_uuids = set(data.get('selected', []))

    # Crear lista temporal con solo las secciones seleccionadas
    materias_filtradas = []
    materia_map = {}

    for item in selected_uuids:
        materia_nombre, uuid = item.split('|')

        # Buscar la materia original
        materia_original = next((m for m in materias_institucionales if m.nombre == materia_nombre), None)
        if not materia_original:
            continue

        # Buscar la sección específica
        seccion_original = next((s for s in materia_original.secciones if s.uuid == uuid), None)
        if not seccion_original:
            continue

        # Crear o actualizar materia filtrada
        if materia_nombre not in materia_map:
            materia_filtrada = Materia(materia_nombre)
            materia_map[materia_nombre] = materia_filtrada
            materias_filtradas.append(materia_filtrada)
        else:
            materia_filtrada = materia_map[materia_nombre]

        # Agregar la sección
        materia_filtrada.agregar_seccion(seccion_original)

    # Generar horarios con las materias filtradas
    generador = GeneradorHorarios(materias_filtradas)
    teoricas = generador.calcular_combinaciones_teoricas()
    soluciones = generador.generar()

    return _format_solutions_response(teoricas, soluciones)

# === API PROYECCIÓN ===

@app.route('/api/proyeccion/add', methods=['POST'])
def proyeccion_add():
    """Agregar sección a proyección personal."""
    data = request.json
    return _add_materia_internal(data, materias_proyeccion)

@app.route('/api/proyeccion/delete', methods=['POST'])
def proyeccion_delete():
    """Eliminar materia de proyección."""
    data = request.json
    nombre = data.get('materia')
    global materias_proyeccion
    materias_proyeccion = [m for m in materias_proyeccion if m.nombre != nombre]
    return jsonify({'message': f'Materia {nombre} eliminada'})

@app.route('/api/proyeccion/delete_section', methods=['POST'])
def proyeccion_delete_section():
    """Eliminar sección de proyección."""
    data = request.json
    nombre_materia = data.get('materia')
    uuid_seccion = data.get('uuid')

    materia = next((m for m in materias_proyeccion if m.nombre == nombre_materia), None)
    if materia:
        materia.secciones = [s for s in materia.secciones if s.uuid != uuid_seccion]
        return jsonify({'success': True, 'message': 'Sección eliminada'})

    return jsonify({'success': False, 'message': 'Materia no encontrada'})

@app.route('/api/proyeccion/toggle_section', methods=['POST'])
def proyeccion_toggle_section():
    """Toggle enabled/disabled de sección en proyección."""
    data = request.json
    nombre_materia = data.get('materia')
    uuid_seccion = data.get('uuid')
    enabled = data.get('enabled')

    materia = next((m for m in materias_proyeccion if m.nombre == nombre_materia), None)
    if materia:
        seccion = next((s for s in materia.secciones if s.uuid == uuid_seccion), None)
        if seccion:
            seccion.enabled = enabled
            return jsonify({'success': True})

    return jsonify({'success': False, 'message': 'Materia o sección no encontrada'})

@app.route('/api/proyeccion/list', methods=['GET'])
def proyeccion_list():
    """Lista materias de proyección personal."""
    lista = []
    for m in materias_proyeccion:
        secciones_data = []
        for s in m.secciones:
            secciones_data.append({
                'uuid': s.uuid,
                'id': s.id_seccion,
                'dias': s.dias,
                'inicio': s.hora_inicio,
                'fin': s.hora_fin,
                'enabled': s.enabled
            })
        lista.append({'nombre': m.nombre, 'secciones': secciones_data})
    return jsonify(lista)

@app.route('/api/proyeccion/generate', methods=['GET'])
def proyeccion_generate():
    """Genera horarios para proyección personal."""
    generador = GeneradorHorarios(materias_proyeccion)
    teoricas = generador.calcular_combinaciones_teoricas()
    soluciones = generador.generar()

    return _format_solutions_response(teoricas, soluciones)

@app.route('/api/proyeccion/chat', methods=['POST'])
def proyeccion_chat():
    """Chat bot para agregar materias a proyección."""
    data = request.json
    mensaje = data.get('mensaje', '')

    resultado = SmartParser.parse(mensaje)

    if 'error' in resultado:
        return jsonify({'success': False, 'message': resultado['error']})

    _add_materia_internal(resultado, materias_proyeccion)

    # Formatear mensaje de éxito
    dias_str = ", ".join(resultado['dias'])
    return jsonify({
        'success': True,
        'message': f"Agregada a proyección: {resultado['materia']} (Sec {resultado['seccion']}) [{dias_str} {resultado['inicio']}-{resultado['fin']}]"
    })

@app.route('/api/proyeccion/clear', methods=['POST'])
def proyeccion_clear():
    """Limpia toda la proyección personal."""
    global materias_proyeccion
    materias_proyeccion = []
    return jsonify({'message': 'Proyección limpiada'})

@app.route('/api/proyeccion/upload', methods=['POST'])
def proyeccion_upload():
    """Endpoint para subir archivos Excel o JSON (proyección)."""
    return _process_file_upload(materias_proyeccion)

# === FUNCIONES INTERNAS ===

def _add_materia_internal(data, materias_db):
    """Función interna para agregar materia desde cualquier fuente."""
    nombre = data.get('materia')
    id_sec = str(data.get('seccion'))
    dias = data.get('dias')

    try:
        inicio = float(data.get('inicio'))
        fin = float(data.get('fin'))
    except (ValueError, TypeError):
        return jsonify({'error': 'Horas inválidas'}), 400

    if not nombre or not id_sec:
        return jsonify({'error': 'Faltan datos'}), 400

    if inicio >= fin:
        return jsonify({'error': 'La hora de inicio debe ser menor a la de fin'}), 400

    # Buscar o crear materia
    materia_obj = next((m for m in materias_db if m.nombre == nombre), None)
    if not materia_obj:
        materia_obj = Materia(nombre)
        materias_db.append(materia_obj)

    # Crear sección
    nueva_seccion = Seccion(id_sec, dias, inicio, fin)
    try:
        materia_obj.agregar_seccion(nueva_seccion)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    return jsonify({'message': f'Sección de {nombre} agregada', 'total_materias': len(materias_db)})

def _format_solutions_response(teoricas, soluciones):
    """Formatea la respuesta de soluciones para JSON."""
    def format_hour(h):
        """Convierte 14.5 a 2:30pm"""
        hours = int(h)
        minutes = int((h - hours) * 60)
        period = "am" if hours < 12 else "pm"
        if hours > 12:
            hours -= 12
        elif hours == 0:
            hours = 12

        if minutes == 0:
            return f"{hours}{period}"
        return f"{hours}:{minutes:02d}{period}"

    soluciones_json = []
    for sol in soluciones:
        horario_formateado = []
        for nombre_materia, seccion in sol:
            horario_formateado.append({
                'materia': nombre_materia,
                'seccion': seccion.id_seccion,
                'dias': seccion.dias,
                'hora': f"{format_hour(seccion.hora_inicio)}/{format_hour(seccion.hora_fin)}"
            })
        soluciones_json.append(horario_formateado)

    return jsonify({
        'teoricas': teoricas,
        'validas': len(soluciones),
        'soluciones': soluciones_json
    })

if __name__ == '__main__':
    app.run(debug=True, port=5200)
