#!/usr/bin/env python3
"""
Módulo para verificación de versiones homologadas según estándares GCABA
"""

import re
import os
import requests
from typing import Dict, List, Optional, Union
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Versiones homologadas basadas en el estándar ES0901 v4.7
VERSIONES_HOMOLOGADAS = {
    # Lenguajes
    "php": ["8.1.30", "8.2.24"],
    "python": ["3.9.18", "3.11.7", "3.12.1"],
    "java": ["11.0.25", "17.0.13", "21.0.5"],
    "openjdk": ["11.0.25", "17.0.13", "21.0.5"],
    "nodejs": ["18.20.4", "20.16.0"],
    "node": ["18.20.4", "20.16.0"],
    
    # Frameworks Frontend
    "angular": ["17.3.12", "18.2.6"],
    "react": ["18.0.0", "18.1.0", "18.2.0"],
    "vue": ["3.3.0", "3.4.0"],
    "nextjs": ["14.1"],
    "next": ["14.1"],
    
    # Frameworks Backend
    "nestjs": ["9.4.0", "10.0.0"],
    "django": ["4.2.16", "5.0.9", "5.1.1"],
    "laravel": ["10.21.1", "11.4.0"],
    "express": ["4.19.2"],
    "fastify": ["4.28.1", "5.0.0"],
    "spring": ["3.2.10", "3.3.4"],
    "springboot": ["3.2.10", "3.3.4"],
    
    # Bibliotecas JavaScript
    "jquery": ["3.6.4", "3.7.0", "3.7.1"],
    "bootstrap": ["5.3.0", "5.3.1", "5.3.2"],
    "chart.js": ["4.3.0", "4.4.0"],
    "chartjs": ["4.3.0", "4.4.0"],
    "highcharts": ["10.3.3", "11.4.0"],
    "moment": ["2.30.0"],
    "lodash": ["4.17.21"],
    "underscore": ["1.13.6"],
    
    # Bibliotecas CSS/Diseño
    "obelisco": ["2.0.0"],
    "font-awesome": ["6.0.0", "6.1.0", "6.2.0"],
    "fontawesome": ["6.0.0", "6.1.0", "6.2.0"],
    
    # Motores de Base de Datos
    "oracle": ["19c"],
    "postgresql": ["13.16", "15.8", "16.4"],
    "postgres": ["13.16", "15.8", "16.4"],
    "mariadb": ["10.5.26"],
    "mongodb": ["6.0.16", "7.3.3"],
    "redis": ["7.2.4", "7.4.0"],
    
    # Servidores Web
    "apache": ["2.4.57"],
    "nginx": ["1.24.0"],
    "tomcat": ["10.1.25"],
    
    # Sistemas Operativos
    "rhel": ["8.7"],
    "redhat": ["8.7"],
    "android": ["9.0", "10.0", "11.0", "12.0", "13.0", "14.0"],
    "ios": ["15.0", "16.0", "17.0"],
    
    # Otras herramientas
    "openssl": ["1.1.1", "3.0.13", "3.1.15"],
    "docker": ["20.10.0", "24.0.0"],
    "kubernetes": ["1.28.0", "1.29.0"],
}

def normalizar_nombre_software(nombre: str) -> str:
    """
    Normaliza el nombre del software para la búsqueda
    """
    nombre = nombre.lower().strip()
    
    # Mapeo de nombres alternativos
    mapeo = {
        "node.js": "nodejs",
        "node js": "nodejs",
        "react.js": "react",
        "vue.js": "vue",
        "angular.js": "angular",
        "next.js": "nextjs",
        "nest.js": "nestjs",
        "express.js": "express",
        "fastify.js": "fastify",
        "spring boot": "springboot",
        "chart.js": "chartjs",
        "font awesome": "fontawesome",
        "font-awesome": "fontawesome",
        "open jdk": "openjdk",
        "red hat": "redhat",
        "red hat enterprise linux": "rhel",
    }
    
    return mapeo.get(nombre, nombre)

def extraer_version(texto: str) -> Optional[str]:
    """
    Extrae la versión de un texto usando expresiones regulares
    """
    # Patrones comunes de versiones
    patrones = [
        r'(\d+\.\d+\.\d+)',  # x.y.z
        r'(\d+\.\d+)',       # x.y
        r'(\d+)',            # x
        r'v(\d+\.\d+\.\d+)', # vx.y.z
        r'version\s*(\d+\.\d+\.\d+)', # version x.y.z
    ]
    
    for patron in patrones:
        match = re.search(patron, texto, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None

def verificar_version_compatible(version_detectada: str, versiones_homologadas: List[str]) -> bool:
    """
    Verifica si una versión detectada es compatible con las versiones homologadas
    """
    if not version_detectada or not versiones_homologadas:
        return False
    
    # Verificación exacta
    if version_detectada in versiones_homologadas:
        return True
    
    # Verificación de compatibilidad por versión mayor
    try:
        partes_detectada = [int(x) for x in version_detectada.split('.')]
        
        for version_homologada in versiones_homologadas:
            try:
                partes_homologada = [int(x) for x in version_homologada.split('.')]
                
                # Comparar versión mayor
                if len(partes_detectada) >= 1 and len(partes_homologada) >= 1:
                    if partes_detectada[0] == partes_homologada[0]:
                        # Misma versión mayor, verificar menor
                        if len(partes_detectada) >= 2 and len(partes_homologada) >= 2:
                            if partes_detectada[1] == partes_homologada[1]:
                                return True
                        else:
                            return True
                            
            except ValueError:
                continue
                
    except ValueError:
        pass
    
    return False

def buscar_version_homologada(nombre_software: str, archivo_txt: Optional[str] = None) -> Dict:
    """
    Busca si una versión de software está homologada según los estándares GCABA
    
    Args:
        nombre_software: Nombre del software a verificar
        archivo_txt: Archivo de texto con versiones (opcional)
        
    Returns:
        Dict con el resultado de la búsqueda
    """
    try:
        # Normalizar nombre del software
        nombre_normalizado = normalizar_nombre_software(nombre_software)
        
        # Extraer versión si está incluida en el nombre
        version_detectada = extraer_version(nombre_software)
        
        # Buscar en versiones homologadas
        if nombre_normalizado in VERSIONES_HOMOLOGADAS:
            versiones_disponibles = VERSIONES_HOMOLOGADAS[nombre_normalizado]
            
            resultado = {
                "software": nombre_normalizado,
                "version_detectada": version_detectada,
                "versiones_homologadas": versiones_disponibles,
                "estado": "encontrado",
                "compatible": False
            }
            
            # Verificar compatibilidad si se detectó una versión
            if version_detectada:
                resultado["compatible"] = verificar_version_compatible(
                    version_detectada, versiones_disponibles
                )
                
                if resultado["compatible"]:
                    resultado["mensaje"] = f"✅ {nombre_software} v{version_detectada} es compatible con las versiones homologadas"
                else:
                    resultado["mensaje"] = f"⚠️ {nombre_software} v{version_detectada} no está en la lista de versiones homologadas"
                    resultado["recomendacion"] = f"Versiones recomendadas: {', '.join(versiones_disponibles)}"
            else:
                resultado["mensaje"] = f"ℹ️ {nombre_software} está en el catálogo de software homologado"
                resultado["recomendacion"] = f"Versiones homologadas: {', '.join(versiones_disponibles)}"
            
            return resultado
        else:
            # Software no encontrado en el catálogo
            return {
                "software": nombre_normalizado,
                "version_detectada": version_detectada,
                "estado": "no_encontrado",
                "compatible": False,
                "mensaje": f"❌ {nombre_software} no se encuentra en el catálogo de software homologado",
                "recomendacion": "Verifique el estándar ES0901 para software homologado"
            }
            
    except Exception as e:
        logger.error(f"Error al buscar versión homologada para {nombre_software}: {str(e)}")
        return {
            "error": f"Error al verificar {nombre_software}: {str(e)}",
            "software": nombre_software,
            "estado": "error"
        }

def cargar_versiones_desde_archivo(archivo_path: str) -> bool:
    """
    Carga versiones homologadas desde un archivo de texto
    """
    try:
        if not os.path.exists(archivo_path):
            logger.warning(f"Archivo {archivo_path} no encontrado")
            return False
            
        with open(archivo_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
            
        # Procesar el contenido del archivo
        # Formato esperado: nombre_software:version1,version2,version3
        lineas = contenido.strip().split('\n')
        
        for linea in lineas:
            if ':' in linea:
                nombre, versiones = linea.split(':', 1)
                nombre = normalizar_nombre_software(nombre.strip())
                versiones_list = [v.strip() for v in versiones.split(',')]
                VERSIONES_HOMOLOGADAS[nombre] = versiones_list
                
        logger.info(f"Versiones cargadas desde {archivo_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error al cargar versiones desde archivo: {str(e)}")
        return False

def descargar_estandar_oficial() -> bool:
    """
    Descarga el estándar oficial desde la web de GCABA
    """
    try:
        url = "https://buenosaires.gob.ar/agencia-de-sistemas-de-informacion/estandares-de-la-agencia"
        
        # Nota: En un entorno real, aquí se implementaría la lógica para:
        # 1. Descargar el PDF del estándar
        # 2. Extraer las versiones homologadas
        # 3. Actualizar el diccionario VERSIONES_HOMOLOGADAS
        
        logger.info("Función de descarga de estándar oficial no implementada")
        logger.info("Utilizando versiones homologadas predeterminadas basadas en ES0901 v4.7")
        
        return True
        
    except Exception as e:
        logger.error(f"Error al descargar estándar oficial: {str(e)}")
        return False

def obtener_catalogo_completo() -> Dict:
    """
    Obtiene el catálogo completo de software homologado
    """
    return {
        "version_estandar": "ES0901 v4.7",
        "fecha_actualizacion": "Enero 2025",
        "total_software": len(VERSIONES_HOMOLOGADAS),
        "categorias": {
            "lenguajes": ["php", "python", "java", "nodejs"],
            "frameworks_frontend": ["angular", "react", "vue", "nextjs"],
            "frameworks_backend": ["nestjs", "django", "laravel", "express", "spring"],
            "bases_datos": ["oracle", "postgresql", "mariadb", "mongodb", "redis"],
            "servidores_web": ["apache", "nginx", "tomcat"],
            "bibliotecas_js": ["jquery", "bootstrap", "chart.js", "moment"],
            "sistemas_operativos": ["rhel", "android", "ios"]
        },
        "software_homologado": VERSIONES_HOMOLOGADAS
    }

def generar_reporte_verificacion(software_list: List[str]) -> Dict:
    """
    Genera un reporte de verificación para una lista de software
    """
    reporte = {
        "fecha_verificacion": "2025-01-01",
        "total_verificados": len(software_list),
        "compatibles": 0,
        "no_compatibles": 0,
        "no_encontrados": 0,
        "detalles": []
    }
    
    for software in software_list:
        resultado = buscar_version_homologada(software)
        reporte["detalles"].append(resultado)
        
        if resultado.get("estado") == "encontrado":
            if resultado.get("compatible", False):
                reporte["compatibles"] += 1
            else:
                reporte["no_compatibles"] += 1
        else:
            reporte["no_encontrados"] += 1
    
    return reporte

# Funciones de utilidad para Streamlit
def validar_version_interactiva(software: str, version: str) -> Dict:
    """
    Valida una versión específica de software de forma interactiva
    """
    software_version = f"{software} {version}" if version else software
    return buscar_version_homologada(software_version)

def obtener_versiones_recomendadas(software: str) -> List[str]:
    """
    Obtiene las versiones recomendadas para un software específico
    """
    nombre_normalizado = normalizar_nombre_software(software)
    return VERSIONES_HOMOLOGADAS.get(nombre_normalizado, [])

def es_software_homologado(software: str) -> bool:
    """
    Verifica si un software está en el catálogo homologado
    """
    nombre_normalizado = normalizar_nombre_software(software)
    return nombre_normalizado in VERSIONES_HOMOLOGADAS

if __name__ == "__main__":
    # Pruebas del módulo
    print("=== Pruebas del módulo de estándares ===")
    
    # Probar algunos casos
    casos_prueba = [
        "jquery 3.6.4",
        "bootstrap 5.3.0",
        "angular 17.3.12",
        "react 18.2.0",
        "php 8.1.30",
        "python 3.11.7",
        "software_no_existente 1.0.0"
    ]
    
    for caso in casos_prueba:
        resultado = buscar_version_homologada(caso)
        print(f"\n{caso}:")
        print(f"  Estado: {resultado.get('estado', 'N/A')}")
        print(f"  Compatible: {resultado.get('compatible', False)}")
        print(f"  Mensaje: {resultado.get('mensaje', 'N/A')}")
    
    # Mostrar catálogo completo
    print(f"\n=== Catálogo completo ===")
    catalogo = obtener_catalogo_completo()
    print(f"Total de software homologado: {catalogo['total_software']}")
    print(f"Versión del estándar: {catalogo['version_estandar']}")
    
    for categoria, software in catalogo['categorias'].items():
        print(f"\n{categoria.title()}:")
        for sw in software:
            versiones = obtener_versiones_recomendadas(sw)
            print(f"  - {sw}: {', '.join(versiones)}")
