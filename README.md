# 🐾 Pet Store POS - Chile

Sistema de Punto de Venta (POS) moderno y completo para tiendas de mascotas en Chile, con soporte para venta a granel, gestión de inventario, integración de RUT/IVA y múltiples métodos de pago.

## 📋 Descripción

Pet Store POS es una aplicación web desarrollada en Django que permite gestionar de manera eficiente las operaciones diarias de una tienda de mascotas. El sistema está optimizado para el mercado chileno con soporte nativo para:

- ✅ **Venta a Granel**: Productos vendidos por peso (kg)
- ✅ **Gestión de IVA**: Cálculo automático del 19% de IVA chileno
- ✅ **Múltiples Métodos de Pago**: Efectivo, Tarjeta, Transferencia
- ✅ **Control de Stock**: Alertas de stock bajo y gestión de inventario
- ✅ **Gestión de Lotes**: Control de fechas de vencimiento
- ✅ **Interfaz Moderna**: Diseño responsivo con Tailwind CSS
- ✅ **Búsqueda Rápida**: Por nombre, SKU o código de barras

## 🛠️ Tecnologías Utilizadas

- **Backend**: Django 6.0.2 (Python)
- **Frontend**: HTML5, Tailwind CSS, Alpine.js
- **Interactividad**: HTMX para actualizaciones dinámicas
- **Base de Datos**: SQLite (desarrollo) / PostgreSQL (producción recomendada)
- **Autenticación**: Django Auth System

## 📦 Instalación y Configuración

### Prerrequisitos

- Python 3.10 o superior
- pip (gestor de paquetes de Python)
- Git

### Paso 1: Clonar el Repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd "test pos"
```

### Paso 2: Crear Entorno Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Paso 3: Instalar Dependencias

```bash
pip install -r requirements.txt
```

Si no existe `requirements.txt`, instalar manualmente:

```bash
pip install django==6.0.2
pip install django-htmx
```

### Paso 4: Configurar Base de Datos

```bash
python manage.py makemigrations
python manage.py migrate
```

### Paso 5: Crear Superusuario

```bash
python manage.py createsuperuser
```

Sigue las instrucciones para crear un usuario administrador.

### Paso 6: Cargar Datos Iniciales (Opcional)

Si deseas cargar categorías de ejemplo:

```bash
python manage.py shell
```

```python
from inventory.models import Category
Category.objects.create(name="Alimentos")
Category.objects.create(name="Juguetes")
Category.objects.create(name="Accesorios")
Category.objects.create(name="Higiene")
exit()
```

### Paso 7: Ejecutar Servidor de Desarrollo

```bash
python manage.py runserver
```

Accede a la aplicación en: `http://127.0.0.1:8000/`

## 🚀 Uso del Sistema

### Panel de Administración

Accede al panel de Django Admin en: `http://127.0.0.1:8000/admin/`

Usa las credenciales del superusuario creado anteriormente.

### Punto de Venta (POS)

1. Navega a `/sales/` para acceder a la caja
2. Busca productos por nombre, SKU o código de barras
3. Agrega productos al carrito
4. Selecciona método de pago (Efectivo, Tarjeta, Transferencia)
5. Completa la transacción

### Gestión de Inventario

1. Navega a `/inventory/` para acceder al dashboard de inventario
2. **Productos**: Crear, editar, eliminar productos
3. **Categorías**: Organizar productos por categorías
4. **Lotes**: Controlar fechas de vencimiento

## 🔒 Buenas Prácticas de Seguridad

### Variables de Entorno

**NUNCA** subas credenciales al repositorio. Usa variables de entorno:

1. Crea un archivo `.env` en la raíz del proyecto:

```env
SECRET_KEY=tu-clave-secreta-super-segura-aqui
DEBUG=False
DATABASE_URL=postgresql://usuario:contraseña@localhost/nombre_db
ALLOWED_HOSTS=tudominio.com,www.tudominio.com
```

2. Instala `python-decouple`:

```bash
pip install python-decouple
```

3. Modifica `config/settings.py`:

```python
from decouple import config

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')
```

### Configuración de Producción

Antes de desplegar en producción:

1. **DEBUG = False**: Desactiva el modo de depuración
2. **SECRET_KEY**: Genera una clave secreta única
3. **ALLOWED_HOSTS**: Define los dominios permitidos
4. **Base de Datos**: Migra a PostgreSQL
5. **Archivos Estáticos**: Configura `STATIC_ROOT` y ejecuta `collectstatic`
6. **HTTPS**: Usa certificados SSL/TLS
7. **CSRF**: Verifica que `CSRF_COOKIE_SECURE = True`

```python
# Configuración de producción recomendada
DEBUG = False
ALLOWED_HOSTS = ['tudominio.com']
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
```

### Base de Datos en Producción

Usa PostgreSQL en lugar de SQLite:

```bash
pip install psycopg2-binary
```

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}
```

## 📁 Estructura del Proyecto

```
test pos/
├── config/              # Configuración del proyecto Django
├── core/                # Aplicación principal (utilidades)
├── inventory/           # Gestión de inventario
├── sales/               # Punto de venta y ventas
├── customers/           # Gestión de clientes
├── templates/           # Plantillas HTML
│   ├── base.html
│   ├── pos/
│   ├── inventory/
│   └── registration/
├── manage.py
└── requirements.txt
```

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Haz un fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.

## 📞 Contacto

Para consultas o soporte, contacta a: [tu-email@ejemplo.com]

---

**Desarrollado con ❤️ para tiendas de mascotas en Chile** 🇨🇱
