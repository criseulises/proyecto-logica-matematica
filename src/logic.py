"""
Módulo de Lógica de Negocio - SmartPlannerX
Implementa algoritmos de backtracking y teoría de conteos para generación de horarios.

Equipo 3:
- Cristian E. Sánchez R. (25-0688)
- Hansel Augusto Pérez (25-0461)
- Lia De Oleo (25-0673)
- Juan José Cruz Romero (25-0888)
- Samir Gonzalez (25-0808)
- Alejandro Bruno (25-0947)
- Daniel Osvaldo Lopez (25-0655)
"""

from itertools import product
import copy
import uuid

class Seccion:
    """
    Representa una sección de una materia con sus horarios.
    """
    def __init__(self, id_seccion, dias, hora_inicio, hora_fin):
        self.uuid = str(uuid.uuid4()) # Identificador único interno
        self.id_seccion = id_seccion
        self.dias = dias  # Lista de strings: ["Lunes", "Miercoles"]
        self.hora_inicio = hora_inicio # Entero 0-23
        self.hora_fin = hora_fin # Entero 0-23
        self.enabled = True # Nuevo: Para selección manual

    def choca_con(self, otra_seccion):
        """
        Verifica si esta sección se solapa en horario con otra.
        """
        # Verificar intersección de días
        dias_comunes = set(self.dias) & set(otra_seccion.dias)
        if not dias_comunes:
            return False
        
        # Si hay días comunes, verificar horas
        # Chocan si (StartA < EndB) y (StartB < EndA)
        return (self.hora_inicio < otra_seccion.hora_fin) and (otra_seccion.hora_inicio < self.hora_fin)

    def __repr__(self):
        return f"Sec {self.id_seccion} ({','.join(self.dias)} {self.hora_inicio}-{self.hora_fin})"

class Materia:
    """
    Representa una materia que contiene múltiples secciones posibles.
    """
    def __init__(self, nombre):
        self.nombre = nombre
        self.secciones = []

    def agregar_seccion(self, seccion):
        """
        Agrega una sección a la materia.
        
        Raises:
            ValueError: Si ya existe una sección con el mismo ID.
        """
        for s in self.secciones:
            if s.id_seccion == seccion.id_seccion:
                raise ValueError(f"La sección {seccion.id_seccion} ya existe en la materia {self.nombre}.")
        self.secciones.append(seccion)

class GeneradorHorarios:
    """
    Clase para generar todas las combinaciones posibles de horarios sin choques.
    """
    def __init__(self, materias):
        self.materias = materias
        self.soluciones = []

    def calcular_combinaciones_teoricas(self):
        """
        Principio Multiplicativo (Teoría de Conteos):
        Si una tarea se puede realizar de 'n' formas y otra de 'm' formas, 
        entonces hay n * m formas de realizar ambas.
        
        Aquí, el número total de combinaciones posibles es el producto del 
        número de secciones disponibles (y habilitadas) para cada materia.
        """
        total = 1
        for m in self.materias:
            secciones_activas = [s for s in m.secciones if s.enabled]
            if not secciones_activas:
                return 0
            total *= len(secciones_activas)
        return total

    def generar(self):
        self.soluciones = []
        # Ordenamos materias para consistencia
        materias_lista = list(self.materias)
        self._backtrack(materias_lista, [])
        return self.soluciones

    def _backtrack(self, materias_restantes, horario_actual):
        """
        Algoritmo de Recurrencia (Backtracking):
        Es una técnica algorítmica para encontrar todas las soluciones posibles 
        a un problema computacional mediante la construcción incremental de candidatos 
        a soluciones, y abandona un candidato ("backtracks") tan pronto como determina 
        que el candidato no puede completar una solución válida.
        """
        # Caso Base: No quedan materias por asignar (Solución encontrada)
        if not materias_restantes:
            self.soluciones.append(copy.copy(horario_actual))
            return

        materia_actual = materias_restantes[0]
        
        # Filtrar solo secciones habilitadas
        secciones_activas = [s for s in materia_actual.secciones if s.enabled]
        
        # Intentar cada sección de la materia actual
        for seccion in secciones_activas:
            if self._es_valido(seccion, horario_actual):
                # Paso Recursivo: Asignar sección y avanzar a la siguiente materia
                horario_actual.append((materia_actual.nombre, seccion))
                self._backtrack(materias_restantes[1:], horario_actual)
                
                # Backtracking: Deshacer el paso para probar la siguiente sección (Recurrencia)
                horario_actual.pop()

    def _es_valido(self, nueva_seccion, horario_actual):
        for _, seccion_existente in horario_actual:
            if nueva_seccion.choca_con(seccion_existente):
                return False
        return True
