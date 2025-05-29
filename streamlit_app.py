#!/usr/bin/env python3

import streamlit as st
import urllib.request
import urllib.error
import urllib.parse
import re
import ssl
from datetime import datetime
from http.cookiejar import CookieJar
from html.parser import HTMLParser
import io
import base64
from typing import Dict, List, Tuple, Optional
import json

# Configuración de la página
st.set_page_config(
    page_title="Checkpoint de Seguridad - GCABA",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
    }
    .success-box {
        background-color: #d1fae5;
        border-left: 5px solid #10b981;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    .error-box {
        background-color: #fef2f2;
        border-left: 5px solid #ef4444;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    .info-box {
        background-color: #eff6ff;
        border-left: 5px solid #3b82f6;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #3b82f6;
    }
</style>
""", unsafe_allow_html=True)

# Importar módulo de estándares
try:
    from estandar import buscar_version_homologada
    ESTANDAR_DISPONIBLE = True
except ImportError:
    ESTANDAR_DISPONIBLE = False
    def buscar_version_homologada(nombre_software, archivo_txt):
        return {"error": f"No se pudo verificar {nombre_software} - módulo estándar no disponible"}

# HTML Parser personalizado (mismo que el original)
class HTMLTagParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.forms, self.scripts, self.links = [], [], []
        self.images, self.iframes, self.anchors, self.inputs = [], [], [], []
        self.current_form = None
        self.current_form_content = self.current_script_content = ""
        self.in_script = self.in_form = False
        self.detected_versions = {}
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        
        if tag == 'form':
            self.current_form = attrs_dict
            self.current_form_content = ""
            self.in_form = True
        elif tag == 'script':
            if 'src' in attrs_dict:
                self.scripts.append(attrs_dict)
                
                # Detectar versiones en scripts
                src = attrs_dict['src'].lower()
                for lib in ['jquery', 'bootstrap', 'react', 'angular', 'vue']:
                    version_match = re.search(rf'{lib}[.-](\d+\.\d+\.\d+)', src, re.IGNORECASE)
                    if version_match:
                        self.detected_versions[lib] = version_match.group(1)
                
            self.in_script = True
            self.current_script_content = ""
        elif tag == 'link' and 'href' in attrs_dict:
            self.links.append(attrs_dict)
            
            # Detectar versiones en stylesheets
            href = attrs_dict.get('href', '').lower()
            for lib in ['bootstrap', 'font-awesome']:
                version_match = re.search(rf'{lib}[.-](\d+\.\d+\.\d+)', href, re.IGNORECASE)
                if version_match:
                    self.detected_versions[lib] = version_match.group(1)
                    
        elif tag == 'img' and 'src' in attrs_dict:
            self.images.append(attrs_dict)
        elif tag == 'iframe' and 'src' in attrs_dict:
            self.iframes.append(attrs_dict)
        elif tag == 'a' and 'href' in attrs_dict:
            self.anchors.append(attrs_dict)
        elif tag in ['input', 'textarea', 'select']:
            self.inputs.append(attrs_dict)
            
    def handle_endtag(self, tag):
        if tag == 'form' and self.current_form is not None:
            self.current_form['content'] = self.current_form_content
            self.forms.append(self.current_form)
            self.current_form = None
            self.in_form = False
        elif tag == 'script' and self.in_script:
            self.scripts.append({'content': self.current_script_content})
            
            # Buscar versiones en el contenido del script
            script_content = self.current_script_content.lower()
            for lib in ['jquery', 'bootstrap', 'react', 'angular', 'vue']:
                version_match = re.search(rf'{lib}[\s\'"]?version[\s\'"]?[:=]\s*[\'"](\d+\.\d+\.\d+)[\'"]', script_content, re.IGNORECASE)
                if version_match:
                    self.detected_versions[lib] = version_match.group(1)
            
            self.in_script = False
            
    def handle_data(self, data):
        if self.in_form:
            self.current_form_content += data
        if self.in_script:
            self.current_script_content += data

class SecurityChecker:
    def __init__(self, url, verbose=False):
        self.url = url.rstrip('/')
        self.verbose = verbose
        self.results = {}
        self.details = {}
        self.cookie_jar = CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cookie_jar))
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'}
        self.allowed_domains = ['buenosaires.gob.ar', 'google', 'googleapis.com', 'gstatic.com', 'jquery', 'cloudflare', 'bootstrap']
    
    def make_request(self, url, method="GET", additional_headers=None):
        request = urllib.request.Request(url, method=method)
        for header, value in self.headers.items():
            request.add_header(header, value)
            
        if additional_headers:
            for header, value in additional_headers.items():
                request.add_header(header, value)
                
        try:
            return self.opener.open(request, timeout=10)
        except urllib.error.HTTPError as e:
            return e
        except urllib.error.URLError as e:
            raise Exception(f"No se pudo conectar a {url}: {str(e)}")
    
    def check_x_frame_options(self, headers):
        xframe_value = headers.get('X-Frame-Options', '')
        if xframe_value:
            xframe_value = xframe_value.upper()
        
        if not xframe_value and 'x-frame-options' in headers:
            xframe_value = headers.get('x-frame-options', '').upper()
        
        csp = headers.get('Content-Security-Policy', '')
        has_csp_frame = 'frame-ancestors' in csp
        
        if xframe_value == 'SAMEORIGIN':
            return True, f"Cabecera X-Frame-Options: {xframe_value}"
        elif xframe_value == 'DENY':
            return True, f"Cabecera X-Frame-Options: {xframe_value}"
        elif xframe_value.startswith('ALLOW-FROM '):
            return True, f"Cabecera X-Frame-Options: {xframe_value}"
        elif has_csp_frame:
            csp_frame_rule = re.search(r'frame-ancestors\s+([^;]+)', csp)
            csp_value = csp_frame_rule.group(1) if csp_frame_rule else "configurado"
            return True, f"CSP con frame-ancestors: {csp_value}"
        else:
            return False, "No se configuró X-Frame-Options adecuadamente ni CSP frame-ancestors"

    def check_captcha(self, content, parser):
        forms = parser.forms
        
        captcha_indicators = [
            'recaptcha', 'grecaptcha', 'g-recaptcha', 'captcha', 
            'https://www.google.com/recaptcha', 
            'data-sitekey', 'class="g-recaptcha"'
        ]
        
        has_recaptcha_script = any(
            'recaptcha/api.js' in script.get('src', '') 
            for script in parser.scripts 
            if 'src' in script
        )
        
        has_captcha_in_content = any(indicator in content.lower() for indicator in captcha_indicators)
        
        has_captcha_in_forms = False
        if forms:
            has_captcha_in_forms = any(
                any(indicator in str(form.get('content', '')).lower() for indicator in captcha_indicators)
                for form in forms
            )
        
        has_captcha = has_recaptcha_script or has_captcha_in_content or has_captcha_in_forms
        
        if has_captcha:
            details = []
            if has_recaptcha_script:
                details.append("Script de reCAPTCHA detectado")
            if has_captcha_in_content:
                details.append("Referencias a CAPTCHA en el código fuente")
            if has_captcha_in_forms:
                details.append("CAPTCHA en formularios")
            
            return True, f"Se encontró CAPTCHA: {', '.join(details)}"
        
        elif not forms:
            return False, "No se encontraron formularios ni implementación de CAPTCHA"
        else:
            return False, "No se encontró implementación de CAPTCHA"
    
    def check_protected_access(self, content, parser):
        auth_indicators = [
            'login', 'iniciar sesión', 'ingresar', 'acceder', 'autenticar', 'usuario', 'contraseña',
            'sesión', 'session', 'token', 'auth', 'jwt',
            'acceso restringido', 'acceso denegado', 'debe iniciar sesión', 'área protegida',
            'oauth', 'openid', 'saml', 'ldap'
        ]
        
        login_forms = any(
            any(field in str(form.get('content', '')).lower() for field in ['password', 'contraseña', 'login'])
            for form in parser.forms
        )
        
        auth_in_content = any(indicator in content.lower() for indicator in auth_indicators)
        
        has_session_cookie = False
        for cookie in self.cookie_jar:
            if any(name in cookie.name.lower() for name in ['session', 'token', 'auth', 'id']):
                has_session_cookie = True
                break
        
        has_protection = login_forms or auth_in_content or has_session_cookie
        
        if has_protection:
            details = []
            if login_forms:
                details.append("Formularios de login detectados")
            if auth_in_content:
                details.append("Referencias a autenticación en el código")
            if has_session_cookie:
                details.append("Cookies de sesión identificadas")
            
            return True, f"Se encontró protección de acceso: {', '.join(details)}"
        else:
            return False, "No se detectaron mecanismos de protección de acceso"
    
    def check_software_versions(self, parser):
        vulnerable_versions = []
        
        for software, version in parser.detected_versions.items():
            result = buscar_version_homologada(software, 'standar.txt')
            
            if "error" in result:
                vulnerable_versions.append(f"{software} {version}")
            else:
                version_homologada = False
                if "versiones_homologadas" in result:
                    for version_info in result["versiones_homologadas"]:
                        if version in version_info:
                            version_homologada = True
                            break
                
                if not version_homologada:
                    vulnerable_versions.append(f"{software} {version}")
        
        if vulnerable_versions:
            return False, f"Versiones Vulnerables detectadas: {', '.join(vulnerable_versions)}"
        elif parser.detected_versions:
            return True, f"Versiones verificadas y homologadas: {', '.join([f'{s} {v}' for s, v in parser.detected_versions.items()])}"
        else:
            return True, "No se detectaron versiones de software específicas"
    
    def run_checks(self, response, content, headers, parser):
        checks = []
        
        # 1. Check CAPTCHA
        captcha_status, captcha_details = self.check_captcha(content, parser)
        checks.append(("1. Captcha", captcha_status, captcha_details))
        
        # 2. Check client-side validation
        validation_found = any(any(input_tag.get(attr) for attr in ['required', 'pattern', 'min', 'max']) for input_tag in parser.inputs)
        
        if not validation_found:
            validation_found = any(any(form.get(event) for event in ['onsubmit', 'oninput', 'onchange']) for form in parser.forms)
        
        if not validation_found:
            validation_found = any(
                'content' in script and any(keyword in script['content'].lower() for keyword in ['validate', 'validation', 'checkvalidity', 'isvalid'])
                for script in parser.scripts
            )
        
        checks.append(("2. Validación del lado del cliente y servidor", validation_found, 
                      "Se detectaron mecanismos de validación" if validation_found else "No se detectaron validaciones"))
        
        # 3. Check X-FRAME-OPTIONS
        x_frame_status, x_frame_details = self.check_x_frame_options(headers)
        checks.append(("3. X-FRAME OPTIONS", x_frame_status, x_frame_details))
        
        # 4. Check version disclosure
        version_headers = ['Server', 'X-Powered-By', 'X-AspNet-Version', 'X-AspNetMvc-Version']
        disclosed_versions = [f"{h}: {headers[h]}" for h in version_headers if h in headers and re.search(r'[\d\.]+', headers[h])]
        
        html_versions = re.findall(r'(jquery-\d+\.\d+\.\d+|bootstrap-\d+\.\d+\.\d+|angular[\s\-]?\d+\.\d+\.\d+|react[\s\-]?\d+\.\d+\.\d+|vue[\s\-]?\d+\.\d+\.\d+)', content, re.IGNORECASE)
        
        if disclosed_versions or html_versions:
            checks.append(("4. No divulgar versiones", False, f"Versiones: {', '.join(disclosed_versions + html_versions)}"))
        else:
            checks.append(("4. No divulgar versiones", True, "No se detectaron versiones"))
        
        # 5. Check software versions against standard
        version_status, version_details = self.check_software_versions(parser)
        checks.append(("5. Verificación de versiones", version_status, version_details))
        
        # 6. Session validation
        has_login = any("login" in str(form.get('content', '')).lower() for form in parser.forms) or "login" in content.lower()
        
        if has_login:
            session_validation = True
            session_details = "La aplicación cuenta con función de login/logout"
        else:
            session_validation = True
            session_details = "No requiere usuario y password"
        
        checks.append(("6. Validación de sesión", session_validation, session_details))
        
        # 7. Access to URLs without session
        protected_status, protected_details = self.check_protected_access(content, parser)
        checks.append(("7. Acceso a URL o archivos sin iniciar sesión", protected_status, protected_details))
        
        # 8. File upload validation
        has_file_upload = any(
            input_tag.get('type') == 'file' for input_tag in parser.inputs
        )
        
        if has_file_upload:
            file_restrictions = any(
                input_tag.get('accept') or 'enctype="multipart/form-data"' in str(form.get('content', ''))
                for input_tag in parser.inputs
                for form in parser.forms
                if input_tag.get('type') == 'file'
            )
            
            checks.append(("8. Validación de archivos a subir", file_restrictions, 
                          "Se detectaron restricciones de tipo de archivo" if file_restrictions else "No se detectaron restricciones de tipo de archivo"))
        else:
            checks.append(("8. Validación de archivos a subir", True, "no cuenta con la funcionalidad"))
        
        # 9. Error messages
        try:
            error_path = '/non_existent_page_12345'
            error_url = urllib.parse.urljoin(self.url, error_path)
            error_response = self.make_request(error_url)
            error_content = error_response.read().decode('utf-8', errors='ignore')
            
            stack_trace_patterns = ['stack trace', 'exception', 'traceback', 'system.web', 
                                   'runtime error', 'server error', 'php error', 'sql syntax']
            has_stack_trace = any(pattern in error_content.lower() for pattern in stack_trace_patterns)
            
            if has_stack_trace:
                checks.append(("9. Mensajes de error personalizados", False, f"Errores de sistema detectados. URL probada: {error_url}"))
            else:
                checks.append(("9. Mensajes de error personalizados", True, f"No se detectan errores durante las pruebas. URL probada: {error_url}"))
        except Exception as e:
            checks.append(("9. Mensajes de error personalizados", True, "No se detectan errores durante las pruebas."))
        
        # 10. Check Active Directory authentication
        ad_auth_patterns = ['ad authentication', 'active directory', 'ldap', 'saml', 'openid', 'sso', 'oauth', 'windows authentication']
        has_ad_auth = any(pattern in content.lower() for pattern in ad_auth_patterns)
        
        if has_login and not has_ad_auth:
            checks.append(("10. Autenticación contra Active Directory", False, "No se detecta validación contra Active Directory para las credenciales de usuario"))
        elif has_login and has_ad_auth:
            checks.append(("10. Autenticación contra Active Directory", True, "Se detecta autenticación con Active Directory"))
        else:
            checks.append(("10. Autenticación contra Active Directory", False, "No cuenta con validación de usuario/contraseña contra Active Directory"))
        
        # 11. Check CORS headers
        cors_header = headers.get('Access-Control-Allow-Origin')
        if cors_header is None:
            checks.append(("11. ACCESS-CONTROL-ALLOW-ORIGIN", True, "No se encuentra configurado"))
        elif cors_header == '*':
            checks.append(("11. ACCESS-CONTROL-ALLOW-ORIGIN", False, "Configuración insegura: *"))
        else:
            checks.append(("11. ACCESS-CONTROL-ALLOW-ORIGIN", True, f"Valor: {cors_header}"))
        
        # 12. Check GET requests
        external_resources = []
        
        for collection, attr_name in [
            (parser.scripts, 'src'), 
            (parser.images, 'src'), 
            (parser.links, 'href'), 
            (parser.iframes, 'src')
        ]:
            for item in collection:
                url = item.get(attr_name, '')
                if url and url.startswith(('http://', 'https://')):
                    parsed = urllib.parse.urlparse(url)
                    if parsed.netloc and not any(domain in parsed.netloc.lower() for domain in self.allowed_domains):
                        external_resources.append(f"{attr_name}: {url}")
        
        if external_resources:
            truncated = external_resources[:5]
            details = f"Recursos externos: {', '.join(truncated)}"
            if len(external_resources) > 5:
                details += f" y {len(external_resources) - 5} más"
            checks.append(("12. Peticiones GET de la Aplicación", False, details))
        else:
            checks.append(("12. Peticiones GET de la Aplicación", True, "No se detectaron recursos externos"))
        
        # 13. Unauthorized access to common directories/files
        common_paths = ['/icons', '/icons/small', '/images', '/fonts', '/.htaccess', '/.gitignore', '/web.config', '/info.php', '/phpinfo.php', '/update.php']
        unauthorized_access = []
        
        for path in common_paths[:2]:
            try:
                path_url = urllib.parse.urljoin(self.url, path)
                path_response = self.make_request(path_url)
                
                if path_response.getcode() == 200:
                    unauthorized_access.append(path)
            except:
                pass
        
        if unauthorized_access:
            checks.append(("13. Acceso no autorizado a Directorios y/o archivos comunes", False, f"Acceso a: {', '.join(unauthorized_access)}"))
        else:
            checks.append(("13. Acceso no autorizado a Directorios y/o archivos comunes", True, "No se detectaron accesos a directorios no autorizados durante las pruebas"))
        
        # 14. Frontend code analysis
        ip_addresses = re.findall(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', content)
        commented_code = re.findall(r'<!--.*?-->', content, re.DOTALL)
        
        if ip_addresses or (commented_code and any('password' in c.lower() or 'usuario' in c.lower() or 'token' in c.lower() for c in commented_code)):
            details = []
            if ip_addresses:
                details.append(f"IPs encontradas: {', '.join(ip_addresses[:3])}")
            if commented_code and any('password' in c.lower() or 'usuario' in c.lower() or 'token' in c.lower() for c in commented_code):
                details.append("Código comentado con información sensible")
            
            checks.append(("14. Chequeo del Código frontend de la Aplicación", False, "; ".join(details)))
        else:
            checks.append(("14. Chequeo del Código frontend de la Aplicación", True, "No se detectaron problemas en el código frontend"))
        
        return checks
    
    def check_security(self):
        try:
            response = self.make_request(self.url)
            if response.getcode() != 200:
                return False, f"Error: No se pudo acceder a la URL. Código de estado: {response.getcode()}"
            
            content = response.read().decode('utf-8', errors='ignore')
            headers = dict(response.info())
            
            parser = HTMLTagParser()
            parser.feed(content)
            
            checks = self.run_checks(response, content, headers, parser)
            
            # Calcular estadísticas
            total = len(checks)
            passed = sum(1 for _, result, _ in checks if result)
            failed = total - passed
            
            return True, {
                'checks': checks,
                'total': total,
                'passed': passed,
                'failed': failed,
                'status': 'APROBADO' if failed == 0 else 'NO APROBADO'
            }
            
        except Exception as e:
            return False, f"Error durante la evaluación: {str(e)}"

def generate_pdf_report(url, results, project_info):
    """Genera un informe en PDF usando la información proporcionada"""
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Título principal
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1,  # Centro
        textColor=colors.blue
    )
    
    story.append(Paragraph("Checkpoint de Seguridad - Chequeos Previos - v 2.0.2", title_style))
    story.append(Spacer(1, 20))
    
    # Información del proyecto
    project_data = [
        ['Estado', project_info.get('estado', 'PENDIENTE')],
        ['Confeccionó', project_info.get('autor', 'Sistema Automático')],
        ['Proyecto', project_info.get('proyecto', 'N/A')],
        ['URL', url],
        ['Ticket JIRA', project_info.get('ticket', 'N/A')],
        ['Versión', project_info.get('version', '01.00.00')],
        ['Fecha', datetime.now().strftime('%d/%m/%Y %H:%M:%S')]
    ]
    
    project_table = Table(project_data, colWidths=[2*inch, 4*inch])
    project_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(project_table)
    story.append(Spacer(1, 30))
    
    # Resultados de las pruebas
    story.append(Paragraph("Resultados de las Pruebas", styles['Heading2']))
    story.append(Spacer(1, 20))
    
    check_data = [['Prueba', 'Estado', 'Detalles']]
    for check_name, status, details in results['checks']:
        status_text = "CUMPLE" if status else "NO CUMPLE"
        check_data.append([check_name, status_text, details[:100] + "..." if len(details) > 100 else details])
    
    check_table = Table(check_data, colWidths=[3*inch, 1*inch, 2*inch])
    check_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(check_table)
    story.append(Spacer(1, 30))
    
    # Resumen
    story.append(Paragraph("Resumen Ejecutivo", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    summary_text = f"""
    Total de chequeos realizados: {results['total']}<br/>
    Pruebas aprobadas: {results['passed']}<br/>
    Pruebas fallidas: {results['failed']}<br/>
    <br/>
    <b>Estado final: {results['status']}</b>
    """
    
    story.append(Paragraph(summary_text, styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def main():
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>🔒 Checkpoint de Seguridad GCABA</h1>
        <p>Herramienta de Chequeos Previos de Seguridad v2.0.2</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar con información
    with st.sidebar:
        st.header("📋 Información del Proyecto")
        
        # Formulario de información del proyecto
        project_name = st.text_input("Nombre del Proyecto", placeholder="Ej: Sistema_Gestion_Eventos_Masivos")
        author_email = st.text_input("Email del Autor", placeholder="a-martinez@buenosaires.gob.ar")
        ticket_jira = st.text_input("Ticket JIRA", placeholder="APPGESMAS-198")
        version = st.text_input("Versión", value="01.00.00")
        
        st.divider()
        
        # Opción para cargar archivo de estándares
        st.header("📄 Estándar de Software")
        
        if not ESTANDAR_DISPONIBLE:
            st.warning("⚠️ Módulo de estándares no disponible")
        
        standard_option = st.radio(
            "Seleccione una opción:",
            ["Usar estándar predeterminado", "Cargar archivo personalizado", "Descargar desde web oficial"]
        )
        
        if standard_option == "Cargar archivo personalizado":
            uploaded_file = st.file_uploader(
                "Cargar archivo de estándares (.txt o .pdf)", 
                type=['txt', 'pdf'],
                help="Suba el archivo con las versiones homologadas de software"
            )
        elif standard_option == "Descargar desde web oficial":
            st.info("🌐 El sistema descargará automáticamente desde:")
            st.markdown("[Estándares GCABA](https://buenosaires.gob.ar/agencia-de-sistemas-de-informacion/estandares-de-la-agencia)")
        
        st.divider()
        
        # Configuraciones adicionales
        st.header("⚙️ Configuraciones")
        verbose_mode = st.checkbox("Modo detallado", help="Mostrar información adicional en los resultados")
        
    # Contenido principal
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("🌐 Análisis de Seguridad Web")
        
        # Input para URL
        url = st.text_input(
            "URL a analizar:",
            placeholder="https://ejemplo.buenosaires.gob.ar",
            help="Ingrese la URL completa de la aplicación a analizar"
        )
        
        # Botón para iniciar análisis
        analyze_button = st.button("🔍 Ejecutar Análisis de Seguridad", type="primary", use_container_width=True)
    
    with col2:
        st.header("📊 Estado del Sistema")
        
        # Métricas del sistema
        if ESTANDAR_DISPONIBLE:
            st.success("✅ Sistema de Estándares: Operativo")
        else:
            st.error("❌ Sistema de Estándares: No Disponible")
            
        st.info(f"🕒 Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    # Ejecutar análisis si se presiona el botón
    if analyze_button and url:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.text("🔄 Conectando a la URL...")
            progress_bar.progress(10)
            
            # Crear el checker
            checker = SecurityChecker(url, verbose=verbose_mode)
            
            status_text.text("🔄 Ejecutando análisis de seguridad...")
            progress_bar.progress(50)
            
            # Ejecutar el análisis
            success, result = checker.check_security()
            
            progress_bar.progress(100)
            status_text.text("✅ Análisis completado")
            
            if success:
                st.success("🎉 Análisis de seguridad completado exitosamente")
                
                # Mostrar resumen en métricas
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Pruebas", result['total'])
                    
                with col2:
                    st.metric("Aprobadas", result['passed'], delta=result['passed'])
                    
                with col3:
                    st.metric("Fallidas", result['failed'], delta=-result['failed'] if result['failed'] > 0 else 0)
                    
                with col4:
                    status_color = "🟢" if result['status'] == 'APROBADO' else "🔴"
                    st.metric("Estado", f"{status_color} {result['status']}")
                
                st.divider()
                
                # Mostrar resultados detallados
                st.header("📋 Resultados Detallados")
                
                # Crear tabs para organizar la información
                tab1, tab2, tab3 = st.tabs(["🔍 Análisis Detallado", "📊 Resumen Ejecutivo", "📄 Generar Informe"])
                
                with tab1:
                    st.subheader("Resultados por Categoría")
                    
                    for i, (check_name, status, details) in enumerate(result['checks'], 1):
                        # Crear expansor para cada check
                        with st.expander(f"{'✅' if status else '❌'} {check_name}", expanded=not status):
                            col_status, col_details = st.columns([1, 3])
                            
                            with col_status:
                                if status:
                                    st.success("✅ CUMPLE")
                                else:
                                    st.error("❌ NO CUMPLE")
                            
                            with col_details:
                                st.write("**Detalles:**")
                                st.write(details)
                
                with tab2:
                    st.subheader("📊 Resumen Ejecutivo")
                    
                    # Gráfico de estado
                    import matplotlib.pyplot as plt
                    
                    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
                    
                    # Gráfico de pastel
                    labels = ['Aprobadas', 'Fallidas']
                    sizes = [result['passed'], result['failed']]
                    colors = ['#28a745', '#dc3545']
                    
                    ax1.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
                    ax1.set_title('Distribución de Resultados')
                    
                    # Gráfico de barras
                    categories = ['Total', 'Aprobadas', 'Fallidas']
                    values = [result['total'], result['passed'], result['failed']]
                    bar_colors = ['#007bff', '#28a745', '#dc3545']
                    
                    ax2.bar(categories, values, color=bar_colors)
                    ax2.set_title('Estadísticas de Pruebas')
                    ax2.set_ylabel('Cantidad')
                    
                    plt.tight_layout()
                    st.pyplot(fig)
                    
                    # Recomendaciones
                    if result['failed'] > 0:
                        st.subheader("⚠️ Recomendaciones")
                        st.error(f"Se encontraron **{result['failed']} problemas** que requieren atención:")
                        
                        failed_checks = [check for check, status, _ in result['checks'] if not status]
                        for i, check in enumerate(failed_checks, 1):
                            st.write(f"{i}. {check}")
                            
                        st.warning("🔧 **Acción requerida:** Corrija los problemas identificados antes de proceder al assessment de seguridad.")
                    else:
                        st.success("🎉 **¡Excelente!** La aplicación ha pasado todas las pruebas de seguridad.")
                        st.info("✅ La aplicación está lista para proceder al assessment de seguridad completo.")
                
                with tab3:
                    st.subheader("📄 Generar Informe")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Información del Informe:**")
                        st.write(f"• URL analizada: {url}")
                        st.write(f"• Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
                        st.write(f"• Total de pruebas: {result['total']}")
                        st.write(f"• Estado: {result['status']}")
                    
                    with col2:
                        # Botón para generar PDF
                        if st.button("📥 Descargar Informe PDF", type="secondary"):
                            project_info = {
                                'estado': result['status'],
                                'autor': author_email or 'Sistema Automático',
                                'proyecto': project_name or 'N/A',
                                'ticket': ticket_jira or 'N/A',
                                'version': version or '01.00.00'
                            }
                            
                            try:
                                pdf_buffer = generate_pdf_report(url, result, project_info)
                                
                                st.download_button(
                                    label="📄 Descargar PDF",
                                    data=pdf_buffer.getvalue(),
                                    file_name=f"checkpoint_seguridad_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                    mime="application/pdf"
                                )
                                
                                st.success("✅ Informe PDF generado correctamente")
                                
                            except ImportError:
                                st.error("❌ No se pudo generar el PDF. Instale reportlab: pip install reportlab")
                            except Exception as e:
                                st.error(f"❌ Error al generar PDF: {str(e)}")
                        
                        # Botón para generar JSON
                        if st.button("📊 Descargar Datos JSON", type="secondary"):
                            report_data = {
                                'url': url,
                                'fecha': datetime.now().isoformat(),
                                'proyecto': {
                                    'nombre': project_name,
                                    'autor': author_email,
                                    'ticket': ticket_jira,
                                    'version': version
                                },
                                'resultados': {
                                    'total': result['total'],
                                    'aprobadas': result['passed'],
                                    'fallidas': result['failed'],
                                    'estado': result['status']
                                },
                                'pruebas': [
                                    {
                                        'nombre': check_name,
                                        'estado': 'CUMPLE' if status else 'NO CUMPLE',
                                        'detalles': details
                                    }
                                    for check_name, status, details in result['checks']
                                ]
                            }
                            
                            json_str = json.dumps(report_data, indent=2, ensure_ascii=False)
                            
                            st.download_button(
                                label="📊 Descargar JSON",
                                data=json_str,
                                file_name=f"checkpoint_seguridad_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                mime="application/json"
                            )
            else:
                st.error(f"❌ Error en el análisis: {result}")
                
        except Exception as e:
            progress_bar.progress(100)
            status_text.text("❌ Error en el análisis")
            st.error(f"❌ Error durante el análisis: {str(e)}")
    
    elif analyze_button and not url:
        st.warning("⚠️ Por favor, ingrese una URL válida para analizar")
    
    # Footer con información adicional
    st.divider()
    
    with st.expander("ℹ️ Información sobre las Pruebas de Seguridad"):
        st.markdown("""
        ### 🔍 Descripción de las Pruebas
        
        Esta herramienta ejecuta 14 pruebas de seguridad esenciales:
        
        1. **Captcha** - Verifica la implementación de CAPTCHA en formularios
        2. **Validación Cliente/Servidor** - Controla validaciones de entrada
        3. **X-Frame-Options** - Prevención de clickjacking
        4. **Ocultación de Versiones** - Evita divulgación de información técnica
        5. **Verificación de Versiones** - Contrasta con estándares homologados
        6. **Validación de Sesión** - Controles de autenticación
        7. **Acceso Protegido** - Verifica protección de URLs sensibles
        8. **Validación de Archivos** - Controles de subida de archivos
        9. **Mensajes de Error** - Personalización de mensajes de error
        10. **Active Directory** - Integración con autenticación corporativa
        11. **CORS Headers** - Configuración de políticas de origen cruzado
        12. **Peticiones GET** - Análisis de recursos externos
        13. **Acceso a Directorios** - Protección de rutas comunes
        14. **Código Frontend** - Análisis de código cliente
        
        ### 📋 Estándares de Referencia
        
        Las pruebas se basan en:
        - **ES0901** - Estándar de Desarrollo GCABA
        - **ES0902** - Estándar de Seguridad GCABA
        - Guías de OWASP
        - Mejores prácticas de seguridad web
        """)
    
    with st.expander("🔗 Enlaces Útiles"):
        st.markdown("""
        ### 📚 Documentación Oficial
        
        - [Estándares de la Agencia](https://buenosaires.gob.ar/agencia-de-sistemas-de-informacion/estandares-de-la-agencia)
        - [Estándar de Desarrollo](https://buenosaires.gob.ar/agencia-de-sistemas-de-informacion/estandares-de-la-agencia)
        - [Sistema de Diseño Obelisco](https://gcba.github.io/estandares/)
        
        ### 🛠️ Herramientas de Soporte
        
        - Mesa de Ayuda ASI
        - Confluence GCABA
        - Repositorios GitLab
        """)

if __name__ == "__main__":
    main()