#!/usr/bin/env python3
"""
Pruebas unitarias para el módulo estandar.py
"""

import unittest
import sys
import os

# Agregar el directorio padre al path para importar el módulo
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from estandar import (
    buscar_version_homologada,
    normalizar_nombre_software,
    extraer_version,
    verificar_version_compatible,
    obtener_versiones_recomendadas,
    es_software_homologado,
    obtener_catalogo_completo
)

class TestEstandarModule(unittest.TestCase):
    """Pruebas para el módulo de estándares"""
    
    def test_normalizar_nombre_software(self):
        """Prueba la normalización de nombres de software"""
        casos = [
            ("jQuery", "jquery"),
            ("Node.js", "nodejs"),
            ("React.js", "react"),
            ("Angular.js", "angular"),
            ("Spring Boot", "springboot"),
            ("Font-Awesome", "fontawesome"),
            ("Red Hat Enterprise Linux", "rhel")
        ]
        
        for entrada, esperado in casos:
            with self.subTest(entrada=entrada):
                resultado = normalizar_nombre_software(entrada)
                self.assertEqual(resultado, esperado)
    
    def test_extraer_version(self):
        """Prueba la extracción de versiones"""
        casos = [
            ("jquery-3.6.4.min.js", "3.6.4"),
            ("bootstrap 5.3.0", "5.3.0"),
            ("angular version 17.3.12", "17.3.12"),
            ("react v18.2.0", "18.2.0"),
            ("python 3.11", "3.11"),
            ("software sin version", None)
        ]
        
        for entrada, esperado in casos:
            with self.subTest(entrada=entrada):
                resultado = extraer_version(entrada)
                self.assertEqual(resultado, esperado)
    
    def test_verificar_version_compatible(self):
        """Prueba la verificación de compatibilidad de versiones"""
        versiones_homologadas = ["3.6.4", "3.7.0", "3.7.1"]
        
        casos = [
            ("3.6.4", True),   # Versión exacta
            ("3.7.0", True),   # Versión exacta
            ("3.5.0", False),  # Versión no homologada
            ("4.0.0", False),  # Versión mayor no homologada
            ("", False),       # Versión vacía
        ]
        
        for version, esperado in casos:
            with self.subTest(version=version):
                resultado = verificar_version_compatible(version, versiones_homologadas)
                self.assertEqual(resultado, esperado)
    
    def test_buscar_version_homologada_software_existente(self):
        """Prueba la búsqueda de software homologado existente"""
        # Caso con versión compatible
        resultado = buscar_version_homologada("jquery 3.6.4")
        self.assertEqual(resultado["estado"], "encontrado")
        self.assertTrue(resultado["compatible"])
        self.assertIn("jquery", resultado["software"])
        
        # Caso con versión no compatible
        resultado = buscar_version_homologada("jquery 2.0.0")
        self.assertEqual(resultado["estado"], "encontrado")
        self.assertFalse(resultado["compatible"])
        
        # Caso sin versión específica
        resultado = buscar_version_homologada("jquery")
        self.assertEqual(resultado["estado"], "encontrado")
        self.assertIn("versiones_homologadas", resultado)
    
    def test_buscar_version_homologada_software_no_existente(self):
        """Prueba la búsqueda de software no homologado"""
        resultado = buscar_version_homologada("software_inventado 1.0.0")
        self.assertEqual(resultado["estado"], "no_encontrado")
        self.assertFalse(resultado["compatible"])
        self.assertIn("no se encuentra en el catálogo", resultado["mensaje"])
    
    def test_obtener_versiones_recomendadas(self):
        """Prueba la obtención de versiones recomendadas"""
        # Software existente
        versiones = obtener_versiones_recomendadas("jquery")
        self.assertIsInstance(versiones, list)
        self.assertGreater(len(versiones), 0)
        
        # Software no existente
        versiones = obtener_versiones_recomendadas("software_inventado")
        self.assertEqual(versiones, [])
    
    def test_es_software_homologado(self):
        """Prueba la verificación de software homologado"""
        # Software homologado
        self.assertTrue(es_software_homologado("jquery"))
        self.assertTrue(es_software_homologado("react"))
        self.assertTrue(es_software_homologado("python"))
        
        # Software no homologado
        self.assertFalse(es_software_homologado("software_inventado"))
    
    def test_obtener_catalogo_completo(self):
        """Prueba la obtención del catálogo completo"""
        catalogo = obtener_catalogo_completo()
        
        # Verificar estructura
        self.assertIn("version_estandar", catalogo)
        self.assertIn("total_software", catalogo)
        self.assertIn("categorias", catalogo)
        self.assertIn("software_homologado", catalogo)
        
        # Verificar contenido
        self.assertGreater(catalogo["total_software"], 0)
        self.assertIsInstance(catalogo["categorias"], dict)
        self.assertIsInstance(catalogo["software_homologado"], dict)
    
    def test_casos_reales_software(self):
        """Prueba casos reales de software comúnmente usado"""
        casos_validos = [
            "jquery 3.6.4",
            "bootstrap 5.3.0",
            "angular 17.3.12",
            "react 18.2.0",
            "php 8.1.30",
            "python 3.11.7",
            "nodejs 18.20.4"
        ]
        
        for caso in casos_validos:
            with self.subTest(caso=caso):
                resultado = buscar_version_homologada(caso)
                self.assertEqual(resultado["estado"], "encontrado")
                self.assertTrue(resultado["compatible"])
    
    def test_casos_versiones_no_homologadas(self):
        """Prueba casos con versiones no homologadas"""
        casos_no_validos = [
            "jquery 2.0.0",  # Versión antigua
            "bootstrap 4.0.0",  # Versión no homologada
            "angular 15.0.0",  # Versión no homologada
            "php 7.4.0"  # Versión no homologada
        ]
        
        for caso in casos_no_validos:
            with self.subTest(caso=caso):
                resultado = buscar_version_homologada(caso)
                self.assertEqual(resultado["estado"], "encontrado")
                self.assertFalse(resultado["compatible"])

class TestIntegracionEstandar(unittest.TestCase):
    """Pruebas de integración para el módulo de estándares"""
    
    def test_flujo_completo_verificacion(self):
        """Prueba el flujo completo de verificación"""
        # Lista de software detectado en una aplicación hipotética
        software_detectado = [
            "jquery 3.6.4",
            "bootstrap 5.3.0",
            "angular 17.3.12",
            "software_personalizado 1.0.0"
        ]
        
        resultados = []
        for software in software_detectado:
            resultado = buscar_version_homologada(software)
            resultados.append(resultado)
        
        # Verificar que se procesaron todos
        self.assertEqual(len(resultados), len(software_detectado))
        
        # Contar compatibles y no compatibles
        compatibles = sum(1 for r in resultados if r.get("compatible", False))
        no_encontrados = sum(1 for r in resultados if r.get("estado") == "no_encontrado")
        
        # Verificar resultados esperados
        self.assertEqual(compatibles, 3)  # jquery, bootstrap, angular
        self.assertEqual(no_encontrados, 1)  # software_personalizado
    
    def test_manejo_errores(self):
        """Prueba el manejo de errores"""
        # Casos que podrían causar errores
        casos_problematicos = [
            "",  # Cadena vacía
            None,  # Valor None
            "   ",  # Solo espacios
            "software con caracteres especiales !@#$%"
        ]
        
        for caso in casos_problematicos:
            with self.subTest(caso=caso):
                try:
                    # El módulo debería manejar estos casos sin lanzar excepciones
                    if caso is not None:
                        resultado = buscar_version_homologada(caso)
                        self.assertIsInstance(resultado, dict)
                        self.assertIn("estado", resultado)
                except Exception as e:
                    self.fail(f"El módulo no manejó correctamente el caso: {caso}. Error: {e}")

if __name__ == "__main__":
    # Configurar el runner de pruebas
    unittest.main(verbosity=2)
