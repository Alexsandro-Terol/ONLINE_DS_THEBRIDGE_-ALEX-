# 💪 FITLIFE - App Fitness con IA de Análisis Corporal

App de fitness profesional con análisis corporal por inteligencia artificial.
Stack: **Flet** (frontend) + **FastAPI** (backend) + **SQLite** + **OpenCV** + **MediaPipe** + **OpenAI Vision**

---

## 🚀 Instalación Rápida (Windows)

### 1. Crear entorno virtual
```cmd
cd C:\Users\alexs\Documents\STARTUPS\FITLIFE
python -m venv venv
venv\Scripts\activate
```

### 2. Instalar dependencias
```cmd
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
Edita el archivo `.env` y configura tu API key de OpenAI (opcional):
```
OPENAI_API_KEY=sk-tu-api-key-aqui
```
> ⚠️ Sin API key funciona igualmente usando análisis basado en MediaPipe.

### 4. Lanzar la aplicación
```cmd
python main.py
```

Esto arranca el backend FastAPI en `http://127.0.0.1:8000` y el frontend Flet automáticamente.

---

## 📂 Estructura del Proyecto

```
FITLIFE/
├── main.py                          # Launcher (arranca backend + frontend)
├── requirements.txt
├── .env                             # Variables de entorno
│
├── backend/                         # FastAPI Backend
│   ├── main.py                      # App FastAPI con todos los routers
│   ├── database.py                  # SQLAlchemy async + SQLite
│   ├── ai/                          # 🤖 MÓDULO IA
│   │   ├── body_analyzer.py         # Orquestador del pipeline IA
│   │   ├── opencv_processor.py      # Preprocesamiento de imágenes
│   │   ├── mediapipe_processor.py   # Detección de 33 landmarks corporales
│   │   ├── body_metrics.py          # Estimación de composición corporal
│   │   ├── openai_vision.py         # Análisis GPT-4 Vision
│   │   └── plan_generator.py        # Generador de planes dieta + entrenamiento
│   ├── models/                      # SQLAlchemy models
│   │   ├── user.py
│   │   ├── nutrition.py
│   │   ├── workout.py
│   │   └── body_scan.py             # Modelo de escáner corporal
│   ├── routers/                     # FastAPI routers
│   │   ├── auth.py                  # Login, registro, perfil
│   │   ├── nutrition.py             # Macros, recetas, peso
│   │   └── body_scan.py             # Análisis IA endpoints
│   ├── schemas/                     # Pydantic schemas
│   └── services/                    # Lógica de negocio
│
├── frontend/                        # Flet Frontend
│   ├── app.py                       # Router principal (todas las rutas)
│   ├── theme.py                     # Sistema de diseño (colores, tipografía)
│   ├── api_client.py                # Cliente HTTP → backend
│   ├── components/
│   │   ├── navbar.py                # Barra de navegación inferior
│   │   └── cards.py                 # Componentes reutilizables
│   └── screens/
│       ├── splash_screen.py         # Pantalla de inicio
│       ├── login_screen.py          # Login
│       ├── register_screen.py       # Registro
│       ├── onboarding_screen.py     # Datos físicos iniciales
│       ├── home_screen.py           # Dashboard principal
│       ├── calories_screen.py       # Calculadora de calorías
│       ├── body_scan_screen.py      # 📸 Subida de fotos IA
│       ├── analysis_result_screen.py # 📊 Resultados del análisis
│       └── progress_screen.py       # 📈 Seguimiento de progreso
│
├── assets/
│   ├── uploads/                     # Fotos originales subidas
│   └── processed/                   # Fotos procesadas + thumbnails
└── data/
    └── fitlife.db                   # SQLite (se crea automáticamente)
```

---

## 🤖 Pipeline de Análisis IA

```
📸 Fotos del usuario
        ↓
🔍 OpenCV Processor
   • Corrección EXIF/orientación
   • Normalización y mejora de calidad
   • Extracción de regiones corporales
        ↓
🦴 MediaPipe Pose (33 landmarks)
   • Proporciones corporales
   • Shoulder-to-Hip ratio (V-taper)
   • Análisis de postura (tilt hombros/caderas)
   • Simetría corporal (brazos, piernas, hombros)
        ↓
📊 Body Metrics Calculator
   • BMI + categoría
   • % Grasa corporal (Fórmula Deurenberg + ajustes pose)
   • Masa muscular, masa magra, masa ósea, agua
   • Score corporal global (0-100)
   • Nivel fitness (Principiante → Profesional)
   • Balance muscular por grupo (10 grupos)
   • Somatotipo (Ecto/Meso/Endomorfo)
        ↓
🤖 OpenAI GPT-4 Vision (opcional - requiere API key)
   • Análisis cualitativo de imagen
   • Validación de estimaciones
   • Insights personalizados
        ↓
📋 Plan Generator
   • Dieta personalizada (calorías + macros + horario de comidas)
   • Rutina de entrenamiento (split semanal + ejercicios)
   • Ejercicios correctivos basados en postura
   • Plan de transformación con fases
   • Resultados esperados a 4 y 12 semanas
```

---

## 🔗 API Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/auth/register` | Crear cuenta |
| POST | `/auth/login` | Iniciar sesión |
| GET  | `/auth/me` | Perfil del usuario |
| POST | `/nutrition/calculate-macros` | Calculadora de macros |
| GET  | `/nutrition/recipes` | Recetas fitness |
| POST | `/body-scan/analyze` | **🤖 Análisis corporal IA** |
| GET  | `/body-scan/history` | Historial de scans |
| GET  | `/body-scan/{id}` | Detalle de scan |
| GET  | `/body-scan/compare/{a}/{b}` | Comparar dos scans |
| GET  | `/docs` | Swagger UI completo |

---

## 📱 Pantallas de la App

| Ruta | Pantalla |
|------|----------|
| `/` | Splash (logo animado) |
| `/login` | Inicio de sesión |
| `/register` | Registro de cuenta |
| `/onboarding` | Datos físicos (3 pasos) |
| `/home` | Dashboard con resumen diario |
| `/calories` | Calculadora Mifflin-St Jeor |
| `/body-scan` | **📸 Escáner Corporal IA** |
| `/scan-result/{id}` | **📊 Resultados del análisis** |
| `/progress` | **📈 Progreso y comparativas** |

---

## ⚙️ Comandos útiles

```cmd
# Solo backend (API)
python main.py --backend

# Solo frontend (UI)
python main.py --frontend

# Frontend como web app (browser)
python main.py --web

# API docs
http://127.0.0.1:8000/docs
```

---

## 🔮 Roadmap (Próximas fases)

- [ ] Pantalla de Dieta completa (tracking diario)
- [ ] Pantalla de Entrenamientos con timer
- [ ] Seguimiento de peso con gráficos
- [ ] Recetas interactivas
- [ ] Perfil de usuario completo
- [ ] Notificaciones y recordatorios
- [ ] Exportar PDF con análisis corporal
- [ ] Comparativa fotográfica antes/después visual
- [ ] Simulación IA de transformación física futura
- [ ] Integración con wearables

---

## ⚠️ Aviso Legal

Las estimaciones de composición corporal son aproximaciones visuales basadas en algoritmos y no sustituyen valoraciones médicas profesionales (DEXA, impedanciometría, etc.). Precisión estimada: ±3-5% en grasa corporal.
