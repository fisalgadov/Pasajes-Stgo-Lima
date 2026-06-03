import json
import os
import smtplib
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path

import gradio as gr
import pandas as pd
import plotly.express as px

DATE_RANGE = "2026-10-09 a 2026-10-12"
ALERT_THRESHOLD_CLP = 190000
ALERT_EMAIL = os.getenv("ALERT_EMAIL", "fisalgadov@gmail.com")
ALERT_STATE_FILE = Path(os.getenv("ALERT_STATE_FILE", "/tmp/pasajes_alert_state.json"))


def get_offers() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "fecha_viaje": "2026-10-09",
                "aerolinea": "LATAM",
                "vuelo": "LA800",
                "salida": "06:15",
                "llegada": "08:05",
                "duracion": "1h 50m",
                "maleta_incluida": "Sí (23kg)",
                "precio_clp": 205000,
                "link": "https://www.latamairlines.com/cl/es/ofertas",
            },
            {
                "fecha_viaje": "2026-10-10",
                "aerolinea": "Sky Airline",
                "vuelo": "H2557",
                "salida": "10:40",
                "llegada": "12:35",
                "duracion": "1h 55m",
                "maleta_incluida": "No (solo equipaje de mano)",
                "precio_clp": 182900,
                "link": "https://www.skyairline.com/chile",
            },
            {
                "fecha_viaje": "2026-10-11",
                "aerolinea": "JetSMART",
                "vuelo": "JA710",
                "salida": "15:20",
                "llegada": "17:15",
                "duracion": "1h 55m",
                "maleta_incluida": "No (opcional)",
                "precio_clp": 189500,
                "link": "https://jetsmart.com/cl/es/",
            },
            {
                "fecha_viaje": "2026-10-12",
                "aerolinea": "LATAM",
                "vuelo": "LA804",
                "salida": "20:10",
                "llegada": "22:00",
                "duracion": "1h 50m",
                "maleta_incluida": "Sí (23kg)",
                "precio_clp": 211500,
                "link": "https://www.latamairlines.com/cl/es/ofertas",
            },
        ]
    )


def get_price_history() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"captura": "2026-06-01", "fecha_viaje": "2026-10-09", "precio_clp": 235000},
            {"captura": "2026-06-02", "fecha_viaje": "2026-10-09", "precio_clp": 219000},
            {"captura": "2026-06-03", "fecha_viaje": "2026-10-09", "precio_clp": 205000},
            {"captura": "2026-06-01", "fecha_viaje": "2026-10-10", "precio_clp": 228000},
            {"captura": "2026-06-02", "fecha_viaje": "2026-10-10", "precio_clp": 205500},
            {"captura": "2026-06-03", "fecha_viaje": "2026-10-10", "precio_clp": 182900},
            {"captura": "2026-06-01", "fecha_viaje": "2026-10-11", "precio_clp": 240000},
            {"captura": "2026-06-02", "fecha_viaje": "2026-10-11", "precio_clp": 214900},
            {"captura": "2026-06-03", "fecha_viaje": "2026-10-11", "precio_clp": 189500},
            {"captura": "2026-06-01", "fecha_viaje": "2026-10-12", "precio_clp": 252000},
            {"captura": "2026-06-02", "fecha_viaje": "2026-10-12", "precio_clp": 233500},
            {"captura": "2026-06-03", "fecha_viaje": "2026-10-12", "precio_clp": 211500},
        ]
    )


def format_currency(value: int) -> str:
    return f"{value:,.0f}".replace(",", ".")


def table_html(offers: pd.DataFrame) -> str:
    rows = []
    for _, row in offers.iterrows():
        rows.append(
            "<tr>"
            f"<td>{row['fecha_viaje']}</td>"
            f"<td>{row['aerolinea']}</td>"
            f"<td>{row['vuelo']}</td>"
            f"<td>{row['salida']}</td>"
            f"<td>{row['llegada']}</td>"
            f"<td>{row['duracion']}</td>"
            f"<td>{row['maleta_incluida']}</td>"
            f"<td><a href='{row['link']}' target='_blank'>CLP {format_currency(int(row['precio_clp']))}</a></td>"
            "</tr>"
        )
    return (
        "<table style='width:100%; border-collapse:collapse;'>"
        "<thead><tr>"
        "<th>Fecha</th><th>Aerolínea</th><th>Vuelo</th><th>Salida</th><th>Llegada</th>"
        "<th>Duración</th><th>Maleta</th><th>Precio (link)</th>"
        "</tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
    )


def build_chart(price_history: pd.DataFrame):
    chart_data = price_history.copy()
    chart_data["captura"] = pd.to_datetime(chart_data["captura"])
    return px.line(
        chart_data,
        x="captura",
        y="precio_clp",
        color="fecha_viaje",
        markers=True,
        title="Evolución de precios por fecha de viaje (CLP)",
        labels={"captura": "Fecha de captura", "precio_clp": "Precio CLP", "fecha_viaje": "Fecha viaje"},
    )


def offer_options(offers: pd.DataFrame):
    return [
        (
            f"{row.fecha_viaje} | {row.aerolinea} {row.vuelo} | CLP {format_currency(int(row.precio_clp))}",
            index,
        )
        for index, row in offers.reset_index(drop=True).iterrows()
    ]


def offer_detail(offers: pd.DataFrame, selected_index: int) -> str:
    row = offers.iloc[int(selected_index)]
    return (
        f"### Detalle del pasaje\n"
        f"- **Fecha:** {row['fecha_viaje']}\n"
        f"- **Aerolínea:** {row['aerolinea']}\n"
        f"- **Vuelo:** {row['vuelo']}\n"
        f"- **Salida:** {row['salida']}\n"
        f"- **Llegada:** {row['llegada']}\n"
        f"- **Duración:** {row['duracion']}\n"
        f"- **Maleta incluida:** {row['maleta_incluida']}\n"
        f"- **Precio actual:** CLP {format_currency(int(row['precio_clp']))}\n"
        f"- **Compra:** [Ir al link del pasaje]({row['link']})"
    )


def _load_alert_state() -> dict:
    if ALERT_STATE_FILE.exists():
        return json.loads(ALERT_STATE_FILE.read_text(encoding="utf-8"))
    return {"sent_alerts": []}


def _save_alert_state(state: dict) -> None:
    ALERT_STATE_FILE.write_text(json.dumps(state), encoding="utf-8")


def _send_email(subject: str, body: str) -> tuple[bool, str | None]:
    smtp_host = os.getenv("SMTP_HOST")
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_from = os.getenv("SMTP_FROM") or smtp_user
    smtp_port = int(os.getenv("SMTP_PORT", "587"))

    if not all([smtp_host, smtp_user, smtp_password, smtp_from]):
        return False, "Configura SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD y SMTP_FROM."

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = smtp_from
    msg["To"] = ALERT_EMAIL
    msg.set_content(body)

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
    except (smtplib.SMTPException, OSError) as exc:
        return False, f"Error SMTP: {exc}"
    return True, None


def check_and_notify(offers: pd.DataFrame) -> str:
    bargains = offers[offers["precio_clp"] < ALERT_THRESHOLD_CLP].copy()
    if bargains.empty:
        return f"No hay pasajes bajo CLP {format_currency(ALERT_THRESHOLD_CLP)} por ahora."

    state = _load_alert_state()
    known_alerts = set(state.get("sent_alerts", []))
    new_bargains = []

    for _, row in bargains.iterrows():
        key = f"{row['fecha_viaje']}|{row['aerolinea']}|{row['vuelo']}|{int(row['precio_clp'])}"
        if key not in known_alerts:
            new_bargains.append((key, row))

    if not new_bargains:
        return "Ya se enviaron alertas para los pasajes detectados bajo el umbral."

    lines = [
        f"{row['fecha_viaje']} - {row['aerolinea']} {row['vuelo']} - CLP {format_currency(int(row['precio_clp']))} - {row['link']}"
        for _, row in new_bargains
    ]
    body = (
        f"Se detectaron pasajes por debajo de CLP {format_currency(ALERT_THRESHOLD_CLP)}.\n\n"
        + "\n".join(lines)
        + f"\n\nGenerado: {datetime.now(timezone.utc).isoformat()}"
    )

    sent, error = _send_email("Alerta de pasajes Santiago-Lima", body)
    if not sent:
        return (
            "Se detectaron pasajes bajo el umbral, pero no se pudo enviar correo. "
            f"{error}"
        )

    for key, _ in new_bargains:
        known_alerts.add(key)
    _save_alert_state({"sent_alerts": sorted(known_alerts)})

    return f"Alerta enviada a {ALERT_EMAIL} para {len(new_bargains)} pasaje(s) bajo el umbral."


def refresh_dashboard():
    offers = get_offers().sort_values(["fecha_viaje", "precio_clp"]).reset_index(drop=True)
    history = get_price_history()
    options = offer_options(offers)
    default_index = options[0][1]
    detail = offer_detail(offers, default_index)
    chart = build_chart(history)
    return table_html(offers), chart, gr.update(choices=options, value=default_index), detail


def update_detail(selected_index: int):
    offers = get_offers().sort_values(["fecha_viaje", "precio_clp"]).reset_index(drop=True)
    return offer_detail(offers, selected_index)


def run_alert():
    offers = get_offers().sort_values(["fecha_viaje", "precio_clp"]).reset_index(drop=True)
    return check_and_notify(offers)


with gr.Blocks(title="Pasajes Santiago-Lima") as demo:
    gr.Markdown(
        f"# Seguimiento de pasajes Santiago → Lima\n"
        f"Rango solicitado: **{DATE_RANGE}**\n\n"
        f"Se muestra detalle de vuelos, links por precio y evolución de valores en CLP."
    )

    offers_html = gr.HTML()
    price_chart = gr.Plot()
    flight_selector = gr.Dropdown(label="Selecciona un pasaje para ver detalle")
    flight_detail = gr.Markdown()
    alert_status = gr.Markdown()
    refresh_button = gr.Button("Actualizar datos")
    alert_button = gr.Button(f"Enviar alerta si baja de CLP {format_currency(ALERT_THRESHOLD_CLP)}")

    demo.load(
        refresh_dashboard,
        outputs=[offers_html, price_chart, flight_selector, flight_detail],
    )
    refresh_button.click(
        refresh_dashboard,
        outputs=[offers_html, price_chart, flight_selector, flight_detail],
    )
    flight_selector.change(update_detail, inputs=flight_selector, outputs=flight_detail)
    alert_button.click(run_alert, outputs=alert_status)


if __name__ == "__main__":
    demo.launch()
