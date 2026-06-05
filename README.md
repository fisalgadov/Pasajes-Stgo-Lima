---
title: Pasajes Stgo Lima
emoji: ✈️
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 5.34.0
app_file: app.py
pinned: false
---

# Pasajes-Stgo-Lima

Aplicación de Hugging Face (Gradio) para visualizar pasajes Santiago → Lima del **9 al 12 de octubre de 2026**.

## Qué muestra la app

- Tabla con los pasajes disponibles, incluyendo:
  - Aerolínea
  - Número de vuelo
  - Hora de salida y llegada
  - Duración
  - Si incluye maleta
  - Precio en CLP con **link clickeable** por pasaje
- Gráfico de evolución de precios por fecha de viaje
- Panel de detalle de cada pasaje seleccionado

## Alerta por correo (< 190.000 CLP)

La app incluye un botón para verificar pasajes bajo **CLP 190.000** y enviar correo a:

- `fisalgadov@gmail.com`

Para habilitar el envío, configura variables de entorno SMTP:

- `SMTP_HOST`
- `SMTP_PORT` (opcional, por defecto `587`)
- `SMTP_USER`
- `SMTP_PASSWORD`
- `SMTP_FROM`
- `ALERT_EMAIL` (opcional, por defecto `fisalgadov@gmail.com`)

## Ejecutar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```
