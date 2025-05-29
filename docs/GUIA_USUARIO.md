# 📖 Guía de Usuario - Checkpoint de Seguridad GCABA

## 🎯 Introducción

Esta guía detallada te ayudará a utilizar eficientemente la herramienta de Checkpoint de Seguridad GCABA para realizar análisis previos de seguridad en aplicaciones web.

## 🚀 Inicio Rápido

### 1. Acceso a la Aplicación

1. **Abrir navegador** y navegar a la URL de la aplicación
2. **Verificar conexión** - debería ver la pantalla principal con el logo de GCABA
3. **Revisar sidebar** - panel lateral con opciones de configuración

### 2. Primer Análisis

**Pasos básicos:**

1. **Ingresar URL** en el campo "URL a analizar"
   ```
   Ejemplo: https://mi-aplicacion.buenosaires.gob.ar
   ```

2. **Completar información del proyecto** (opcional pero recomendado):
   - Nombre del proyecto: `Sistema_Gestion_Eventos`
   - Email: `desarrollador@buenosaires.gob.ar`
   - Ticket JIRA: `PROJ-123`
   - Versión: `01.00.00`

3. **Hacer clic** en "🔍 Ejecutar Análisis de Seguridad"

4. **Esperar resultados** (usualmente 30-60 segundos)

## 🔧 Configuración Detallada

### Información del Proyecto

| Campo | Descripción | Ejemplo | Obligatorio |
|-------|-------------|---------|-------------|
| Nombre del Proyecto | Identificador único del sistema | `Sistema_Gestion_Eventos_Masivos` | No |
| Email del Autor | Responsable técnico | `a-martinez@buenosaires.gob.ar` | No |
| Ticket JIRA | Referencia del ticket | `APPGESMAS-198` | No |
| Versión | Versión del sistema | `01.00.00` | No |

### Opciones de Estándares

#### 1. Estándar Predeterminado
- **Descripción**: Utiliza las versiones homologadas según ES0901 v4.7
- **Cuándo usar**: Para la mayoría de análisis estándar
- **Ventajas**: No requiere configuración adicional

#### 2. Archivo Personalizado
- **Descripción**: Carga un archivo con versiones específicas
- **Formato soportado**: `.txt` y `.pdf`
- **Cuándo usar**: Cuando se tienen estándares específicos del proyecto

**Formato del archivo .txt:**
```
jquery:3.6.4,3.7.0,3.7.1
bootstrap:5.3.0,5.3.1,5.3.2
angular:17.3.12,18.2.6
react:18.0.0,18.1.0,18.2.0
```

#### 3. Descarga Automática
- **Descripción**: Obtiene la versión más reciente desde el sitio oficial
- **URL**: https://buenosaires.gob.ar/agencia-de-sistemas-de-informacion/estandares-de-la-agencia
- **Cuándo usar**: Para asegurar los estándares más actualizados

### Configuraciones Adicionales

- **Modo Detallado**: Muestra información técnica adicional en los resultados
- **Timeout**: Tiempo máximo de espera por análisis (configurable via variables de entorno)

## 📊 Interpretación de Resultados

### Panel de Métricas

#### Métricas Principales
- **Total Pruebas**: Número total de verificaciones realizadas (siempre 14)
- **Aprobadas**: Cantidad de pruebas que pasaron ✅
- **Fallidas**: Cantidad de pruebas que no pasaron ❌
- **Estado**: Resultado final (APROBADO/NO APROBADO)

#### Criterios de Aprobación
- **APROBADO**: Todas las 14 pruebas pasaron
- **NO APROBADO**: Una o más pruebas fallaron

### Análisis Detallado

#### Estados de las Pruebas

| Icono | Estado | Descripción |
|-------|--------|-------------|
| ✅ | CUMPLE | La prueba pasó exitosamente |
| ❌ | NO CUMPLE | La prueba falló y requiere atención |

#### Categorías de Pruebas

1. **🔒 Seguridad Básica**
   - Captcha
   - X-Frame-Options
   - CORS Headers

2. **🔍 Validaciones**
   - Validación Cliente/Servidor
   - Validación de Archivos
   - Validación de Sesión

3. **🔐 Autenticación**
   - Active Directory
   - Acceso Protegido

4. **🛡️ Protección de Información**
   - Ocultación de Versiones
   - Mensajes de Error
   - Código Frontend

5. **📋 Cumplimiento de Estándares**
   - Verificación de Versiones
   - Peticiones GET
   - Acceso a Directorios

### Resumen Ejecutivo

#### Gráficos de Estado
- **Gráfico de Pastel**: Distribución porcentual de resultados
- **Gráfico de Barras**: Comparación cuantitativa

#### Recomendaciones
- **Problemas Críticos**: Lista de issues que requieren corrección inmediata
- **Sugerencias**: Mejoras recomendadas
- **Próximos Pasos**: Acciones a seguir

## 📄 Generación de Informes

### Informe PDF

#### Contenido del PDF
- **Portada**: Información del proyecto y resultado final
- **Resumen Ejecutivo**: Métricas principales y estado
- **Resultados Detallados**: Cada una de las 14 pruebas
- **Recomendaciones**: Acciones correctivas
- **Anexos**: Información técnica adicional

#### Personalización
- Logo GCABA automático
- Información del proyecto completada en sidebar
- Fecha y hora de generación
- Numeración de páginas

### Datos JSON

#### Estructura del JSON
```json
{
  "url": "https://ejemplo.com",
  "fecha": "2025-01-01T10:00:00",
  "proyecto": {
    "nombre": "Sistema_Test",
    "autor": "desarrollador@gcaba.gob.ar",
    "ticket": "PROJ-123",
    "version": "1.0.0"
  },
  "resultados": {
    "total": 14,
    "aprobadas": 12,
    "fallidas": 2,
    "estado": "NO APROBADO"
  },
  "pruebas": [
    {
      "nombre": "1. Captcha",
      "estado": "CUMPLE",
      "detalles": "Se encontró CAPTCHA: Script de reCAPTCHA detectado"
    }
  ]
}
```

#### Usos del JSON
- **Integración**: Con sistemas de gestión de proyectos
- **Automatización**: Pipelines de CI/CD
- **Análisis**: Herramientas de business intelligence
- **Histórico**: Seguimiento de mejoras

## 🎯 Casos de Uso Específicos

### Caso 1: Desarrollo Nuevo
**Escenario**: Nueva aplicación web en desarrollo

**Proceso recomendado**:
1. Ejecutar análisis en ambiente de desarrollo
2. Corregir issues críticos
3. Re-ejecutar hasta obtener APROBADO
4. Generar informe PDF para documentación
5. Proceder a testing en QA

### Caso 2: Aplicación Existente
**Escenario**: Aplicación en producción que requiere actualización

**Proceso recomendado**:
1. Analizar versión actual como baseline
2. Implementar mejoras de seguridad
3. Ejecutar análisis comparativo
4. Documentar mejoras con JSON
5. Programar deployment

### Caso 3: Auditoría de Seguridad
**Escenario**: Revisión periódica de múltiples aplicaciones

**Proceso recomendado**:
1. Crear lista de aplicaciones a auditar
2. Ejecutar análisis sistemático
3. Generar informes JSON para cada aplicación
4. Consolidar resultados en dashboard
5. Priorizar correcciones por criticidad

### Caso 4: Integración CI/CD
**Escenario**: Automatizar análisis en pipeline de despliegue

**Proceso recomendado**:
1. Configurar llamada automática desde pipeline
2. Procesar resultado JSON programáticamente
3. Bloquear deployment si estado = "NO APROBADO"
4. Generar artefactos de análisis
5. Notificar a equipo de desarrollo

## 🚨 Resolución de Problemas

### Errores Comunes

#### Error: "No se pudo conectar a la URL"
**Causas posibles**:
- URL incorrecta o inaccesible
- Aplicación requiere VPN
- Firewall bloqueando conexión
- Certificado SSL inválido

**Soluciones**:
1. Verificar URL en navegador
2. Comprobar conectividad de red
3. Contactar administrador de red
4. Usar URL alternativa o ambiente de testing

#### Error: "Timeout durante el análisis"
**Causas posibles**:
- Aplicación muy lenta
- Servidor sobrecargado
- Conexión de red lenta

**Soluciones**:
1. Reintentar el análisis
2. Verificar performance de la aplicación
3. Ejecutar en horario de menor carga
4. Contactar soporte técnico

#### Warning: "Módulo de estándares no disponible"
**Causas posibles**:
- Archivo estandar.py no encontrado
- Error en instalación de dependencias

**Soluciones**:
1. Verificar instalación completa
2. Reinstalar dependencias: `pip install -r requirements.txt`
3. Verificar permisos de archivos
4. Contactar administrador del sistema

### Limitaciones Conocidas

1. **URLs Protegidas**: No puede analizar aplicaciones que requieren autenticación
2. **JavaScript Pesado**: Aplicaciones SPA complejas pueden no analizarse completamente
3. **Redes Internas**: Requiere conectividad desde el servidor de la herramienta
4. **Certificados**: Problemas con certificados auto-firmados

### Mejores Prácticas

#### Antes del Análisis
- ✅ Verificar que la aplicación esté disponible
- ✅ Comprobar que no requiera autenticación para la página principal
- ✅ Asegurar conectividad de red
- ✅ Tener información del proyecto completa

#### Durante el Análisis
- ✅ No cerrar la ventana del navegador
- ✅ Esperar a que termine completamente
- ✅ Verificar progreso en la barra de estado
- ✅ No ejecutar múltiples análisis simultáneos

#### Después del Análisis
- ✅ Revisar todos los resultados detallados
- ✅ Generar informe PDF para documentación
- ✅ Exportar JSON si se requiere integración
- ✅ Programar correcciones basadas en prioridad

## 📞 Soporte y Contacto

### Canales de Soporte

1. **Mesa de Ayuda ASI**
   - Email: mesa-ayuda@buenosaires.gob.ar
   - Horario: Lunes a Viernes 9:00-18:00

2. **Documentación Técnica**
   - Confluence: https://confluence.gcaba.gob.ar
   - GitLab: https://gitlab.gcaba.gob.ar/asi/checkpoint-seguridad

3. **Issues y Bugs**
   - GitLab Issues: Para reportar problemas técnicos
   - Email: Contactar mesa de ayuda con detalles completos

### Información para Soporte

Cuando contacte soporte, incluya:
- URL analizada
- Mensaje de error completo
- Captura de pantalla
- Información del navegador
- Pasos para reproducir el problema

---

**Última actualización**: Enero 2025  
**Versión de la guía**: 2.0.2  
**Autor**: Agencia de Sistemas de Información - GCABA
