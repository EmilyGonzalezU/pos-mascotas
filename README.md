# 🐾 Pet Store POS - Chile

Sistema de Punto de Venta (POS) para tiendas de mascotas en Chile. **Despliegue local**.

## 📋 Características

- ✅ Venta a granel (por peso/kg)
- ✅ Cálculo automático de IVA (19%)
- ✅ Múltiples métodos de pago: Efectivo, Tarjeta, Transferencia
- ✅ Control de stock con alertas de stock bajo
- ✅ Gestión de lotes con fechas de vencimiento
- ✅ Multi-tenant (tiendas independientes)
- ✅ Búsqueda rápida por nombre, SKU o código de barras
- ✅ Interfaz moderna con Tailwind CSS + HTMX

## 🛠️ Tecnologías

- **Backend**: Django 6.0 (Python)
- **Frontend**: HTML5, Tailwind CSS, HTMX
- **Base de Datos**: PostgreSQL 16 (via Docker)
- **Caché**: Redis 7 (via Docker)

## 📦 Instalación Local

### Prerrequisitos

- Python 3.10+
- Docker Desktop
- Node.js (para compilar Tailwind CSS)

### 1. Clonar e instalar

```bash
git clone <URL_DEL_REPOSITORIO>
cd "test pos"

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# Instalar dependencias
pip install -r requirements/production.txt
```

### 2. Iniciar servicios (PostgreSQL + Redis)

```bash
docker-compose up -d
```

### 3. Configurar base de datos

```bash
python manage.py migrate
python manage.py loaddata datadump.json   # Datos iniciales
```

### 4. Compilar estilos CSS

```bash
npm install
npm run css:build
```

### 5. Recopilar archivos estáticos

```bash
python manage.py collectstatic --noinput
```

### 6. Iniciar servidor

```bash
python manage.py runserver
```

Accede a: **http://localhost:8000/**

## 🔑 Crear usuario administrador

```bash
python manage.py createsuperuser
```

Panel admin: **http://localhost:8000/admin/**

## 📁 Estructura del Proyecto

```
test pos/
├── apps/                # Aplicaciones Django
│   ├── accounts/        # Gestión de usuarios
│   ├── core/            # Utilidades y middleware
│   ├── customers/       # Gestión de clientes
│   ├── dashboard/       # Panel de control
│   ├── inventory/       # Gestión de inventario
│   ├── sales/           # Punto de venta
│   └── tenants/         # Multi-tenancy
├── config/              # Configuración Django
│   └── settings/
│       ├── base.py      # Settings compartidos
│       └── production.py # Settings local (PostgreSQL)
├── templates/           # Plantillas HTML
├── static/              # Archivos estáticos (fuente)
├── docker-compose.yml   # PostgreSQL + Redis
├── manage.py
└── requirements/
    ├── base.txt
    └── production.txt
```

## ⚙️ Variables de entorno (opcionales)

Crea un archivo `.env` si deseas personalizar:

```env
POSTGRES_DB=pos_mascotas
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
DJANGO_SECRET_KEY=tu-clave-secreta
```

