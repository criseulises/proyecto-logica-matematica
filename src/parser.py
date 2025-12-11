"""
Parser de Lenguaje Natural - SmartPlannerX
Interpreta texto en lenguaje natural para extraer información de horarios.

Equipo 3:
- Cristian E. Sánchez R. (25-0688)
- Hansel Augusto Pérez (25-0461)
- Lia De Oleo (25-0673)
- Juan José Cruz Romero (25-0888)
- Samir Gonzalez (25-0808)
- Alejandro Bruno (25-0947)
- Daniel Osvaldo Lopez (25-0655)
"""

import re

class SmartParser:
    """
    Clase encargada de interpretar lenguaje natural para extraer información de materias y horarios.
    """
    DIAS_MAP = {
        'lunes': 'Lunes', 'lun': 'Lunes',
        'martes': 'Martes', 'mar': 'Martes',
        'miercoles': 'Miercoles', 'miércoles': 'Miercoles', 'mie': 'Miercoles',
        'jueves': 'Jueves', 'jue': 'Jueves',
        'viernes': 'Viernes', 'vie': 'Viernes',
        'sabado': 'Sabado', 'sábado': 'Sabado', 'sab': 'Sabado'
    }

    @staticmethod
    def parse(text):
        """
        Analiza un texto y extrae: materia, sección, días y horas.
        
        Args:
            text (str): El texto de entrada del usuario.
            
        Returns:
            dict: Diccionario con 'success', 'materia', 'seccion', 'dias', 'inicio', 'fin' 
                  o 'error' en caso de fallo.
        """
        text_lower = text.lower()
        
        # 1. Detectar Días
        dias_encontrados = []
        for key, val in SmartParser.DIAS_MAP.items():
            if re.search(r'\b' + re.escape(key) + r'\b', text_lower):
                if val not in dias_encontrados:
                    dias_encontrados.append(val)
        
        if not dias_encontrados:
            return {'error': 'No entendí los días. Usa palabras completas como "Lunes".'}

        # 2. Detectar Horas (Soporte AM/PM y rangos)
        # Regex: (num)(:min)?(am/pm)? ... (num)(:min)?(am/pm)?
        horas_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\s*(?:a|-|hasta)\s*(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', text_lower)
        
        if not horas_match:
            return {'error': 'No encontré las horas. Usa formato "8 a 10" o "2:30pm a 4pm".'}
        
        try:
            inicio_h = int(horas_match.group(1))
            inicio_m = int(horas_match.group(2) or 0)
            inicio_ampm = horas_match.group(3)
            
            fin_h = int(horas_match.group(4))
            fin_m = int(horas_match.group(5) or 0)
            fin_ampm = horas_match.group(6)

            def to_24h_float(h, m, ampm):
                if ampm == 'pm' and h < 12: h += 12
                if ampm == 'am' and h == 12: h = 0
                return h + (m / 60.0)

            inicio = to_24h_float(inicio_h, inicio_m, inicio_ampm)
            fin = to_24h_float(fin_h, fin_m, fin_ampm)

            # Inferencia: si inicio > fin y no hay AM/PM explícito en fin, asumir PM
            if inicio >= fin and not fin_ampm:
                fin += 12
        except ValueError:
             return {'error': 'Error calculando horas.'}

        # 3. Detectar Sección (Número suelto)
        # Eliminamos las horas del texto para no confundir
        text_no_hours = text_lower.replace(horas_match.group(0), "")
        
        parts = text_no_hours.split()
        seccion = "Unica"
        for p in parts:
            if p.isdigit():
                seccion = p
                break # Tomar el primer número como sección

        # 4. Detectar Materia (Todo lo que no sea día, hora, sección o stopword)
        palabras_ignorar = ['agrega', 'crea', 'pon', 'el', 'la', 'los', 'las', 'de', 'a', 'y', 'materia', 'clase', 'curso', 'por', 'favor', 'tengo', 'que', 'seccion', 'del', 'al']
        palabras_ignorar += list(SmartParser.DIAS_MAP.keys())
        
        nombre_parts = []
        for p in parts:
            p_clean = p.strip('.,-')
            if p_clean not in palabras_ignorar and not p_clean.isdigit() and p_clean not in ['am', 'pm']:
                nombre_parts.append(p_clean.capitalize())
        
        nombre_materia = " ".join(nombre_parts)
        if not nombre_materia:
            nombre_materia = "Materia Desconocida"

        return {
            'success': True,
            'materia': nombre_materia,
            'seccion': seccion,
            'dias': dias_encontrados,
            'inicio': inicio,
            'fin': fin
        }
