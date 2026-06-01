#!/usr/bin/env python3
"""
NQ Market Calendar Generator
Obtiene datos de Finnhub (calendario económico + earnings)
Aplica reglas de impacto al NQ y genera data/calendar.json
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import requests

# ── Config ──────────────────────────────────────────────────────────────────
FINNHUB_KEY = os.environ.get("FINNHUB_API_KEY", "")
if not FINNHUB_KEY:
    print("Error: FINNHUB_API_KEY no configurada", file=sys.stderr)
    sys.exit(1)

DATA_PATH = Path(__file__).parent.parent / "data" / "calendar.json"

# Tickers tech relevantes para el NQ (subset representativo)
TECH_TICKERS = [
    "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA",
    "AVGO", "PEP", "COST", "CSCO", "NFLX", "AMD", "INTC",
    "QCOM", "ADBE", "TMUS", "TXN", "AMGN", "HON",
]

# ── Reglas de eventos macro ─────────────────────────────────────────────────
# Mapeo de palabras clave del evento Finnhub → reglas NQ
RULES = {
    "CPI": {
        "impacto": "ALTO",
        "desc": "Índice de precios al consumidor. Mide inflación de bienes y servicios.",
        "mayor": "📉 BEARISH — inflación alta restringe recortes de la Fed. Growth stocks (Tech) sufren.",
        "menor": "📈 BULLISH — inflación baja abre puerta a recortes. Tech y NQ se impulsan.",
        "linea": "➡️ NEUTRO — dato en línea. Atención a la lectura de la Fed; puede hablar Powell.",
        "ict": "Killzone NY 8:30–9:30. Revisar Order Block diario en NQ. Si previo BSL, esperar sweep + reversal. Verificar FVG en 1m post-noticia para entry.",
    },
    "PPI": {
        "impacto": "ALTO",
        "desc": "Índice de precios al productor. Mide inflación a nivel mayorista.",
        "mayor": "📉 BEARISH — presión inflacionaria mayorista filtra a consumidor. Cautela en NQ.",
        "menor": "📈 BULLISH — presión a la baja en costos de producción. Alivio para márgenes de Tech.",
        "linea": "➡️ NEUTRO — sin sorpresa. Mercado puede mantener sesgo previo.",
        "ict": "Complementa al CPI. Si diverge, la volatilidad puede extenderse hasta 11 AM ET. Buscar FVG en 5m/15m.",
    },
    "PCE": {
        "impacto": "ALTO",
        "desc": "Personal Consumption Expenditures. La métrica de inflación preferida por la Fed.",
        "mayor": "📉 BEARISH — Fed ve inflación persistente. Recortes descartados a corto plazo. Tech cae.",
        "menor": "📈 BULLISH — la Fed gana confianza para recortar. NQ tech dispara al alza.",
        "linea": "➡️ NEUTRO — dentro de banda esperada. Sesgo previo se mantiene.",
        "ict": "Evento de alta volatilidad. Killzone completo de NY. No operar 5 min antes/durante el release sin stop ajustado.",
    },
    "FOMC": {
        "impacto": "ALTO",
        "desc": "Reunión del Comité Federal de Mercado Abierto. Decisión de tasas + proyecciones.",
        "mayor": "📉 BEARISH — si suben tasas o hawkish guidance. NQ tech se resiente.",
        "menor": "📈 BULLISH — si recortan o dovish tone. Liquidez barata impulsa Tech.",
        "linea": "➡️ NEUTRO — sin cambio y lenguaje neutro. Mercado busca siguiente catalizador.",
        "ict": "Volatilidad extrema en conferencia de Powell (14:00 ET). Evitar operar durante statement; esperar estructura 15m post-conferencia.",
    },
    "EMPLOYMENT": {
        "impacto": "ALTO",
        "desc": "Reporte de empleo no agrícola (NFP). Mide creación de empleos en USA.",
        "mayor": "📉 BEARISH — economía fuerte obliga a Fed 'higher for longer'. Tech sufre.",
        "menor": "📈 BULLISH — debilidad laboral alivia presión sobre la Fed. NQ tech sube.",
        "linea": "➡️ NEUTRO — dato en línea con tasa natural. Sin cambio de narrativa.",
        "ict": "Primer viernes de mes, 8:30 ET. Alta volatilidad en apertura cash (9:30). Revisar sell-side liquidity en NQ antes del dato.",
    },
    "UNEMPLOYMENT": {
        "impacto": "MEDIO",
        "desc": "Tasa de desempleo. Complemento del NFP.",
        "mayor": "📉 BEARISH — desempleo alto señala debilidad económica. A corto plazo presiona NQ.",
        "menor": "📈 BULLISH — pleno empleo reafirma narrativa de aterrizaje suave.",
        "linea": "➡️ NEUTRO — dentro de rango.",
        "ict": "Leer en conjunto con NFP. Si contradicen, esperar caos 8:30–9:30. Buscar order flow post-volatilidad.",
    },
    "GDP": {
        "impacto": "ALTO",
        "desc": "Producto Interno Bruto. Crecimiento económico trimestral.",
        "mayor": "📈 BULLISH — crecimiento fuerte + inflación contenida = sweet spot para Tech.",
        "menor": "📉 BEARISH — estancamiento o recesión. Risk-off, NQ baja.",
        "linea": "➡️ NEUTRO — crecimiento moderado. Sesgo previo intacto.",
        "ict": "Trimestral (ene/abr/jul/oct). Impacto inmediato en apertura cash. Revisar weekly OB si estamos cerca de quarter-end.",
    },
    "PMI": {
        "impacto": "MEDIO",
        "desc": "Índice de Gerentes de Compras. >50 = expansión, <50 = contracción.",
        "mayor": "📈 BULLISH — expansión sectorial impulsa confianza. NQ se beneficia.",
        "menor": "📉 BEARISH — contracción en manufactura/servicios. Cautela en Tech.",
        "linea": "➡️ NEUTRO — expansión moderada.",
        "ict": "10:00 ET ISM. Si sesgo previo es bajista y PMI <50, confirma continuation. Revisar 15m FVG.",
    },
    "RETAIL": {
        "impacto": "MEDIO",
        "desc": "Ventas minoristas. Indicador de consumo y salud del gasto doméstico.",
        "mayor": "📈 BULLISH — consumo fuerte impulsa ingresos de Big Tech y e-commerce.",
        "menor": "📉 BEARISH — gasto débil reduce guidance de ingresos. Presión en AMZN, META ads, AAPL.",
        "linea": "➡️ NEUTRO — consumo estable.",
        "ict": "Impacto directo en AMZN, TSLA, WMT (no en NQ directo pero sí en sentiment).",
    },
    "DURABLE": {
        "impacto": "MEDIO",
        "desc": "Órdenes de bienes duraderos. Inversión empresarial.",
        "mayor": "📈 BULLISH — inversión empresarial alta. Beneficia a sector industrial/tech hardware.",
        "menor": "📉 BEARISH — recorte de inversión empresarial. Presiona guidance de semis y cloud capex.",
        "linea": "➡️ NEUTRO — sin cambio.",
        "ict": "Volatilidad baja. Usar como confirmación de sesgo macro.",
    },
    "HOUSING": {
        "impacto": "MEDIO",
        "desc": "Indicadores de vivienda: housing starts, building permits, home sales.",
        "mayor": "📈 BULLISH — sector construcción activo impulsa economía.",
        "menor": "📉 BEARISH — debilidad en housing reduce confianza del consumidor.",
        "linea": "➡️ NEUTRO — estable.",
        "ict": "Secundario para NQ. Revisar solo si hay sorpresa extrema.",
    },
    "CONSUMER": {
        "impacto": "MEDIO",
        "desc": "Confianza del consumidor (UMich/Conference Board).",
        "mayor": "📈 BULLISH — consumidor optimista = más gasto en tech/services.",
        "menor": "📉 BEARISH — pesimismo reduce gasto discrecional. Tech vulnerable.",
        "linea": "➡️ NEUTRO — sin dirección clara.",
        "ict": "Impacto moderado. Útil para swing bias.",
    },
    "INDUSTRIAL": {
        "impacto": "MEDIO",
        "desc": "Producción industrial / capacidad utilizada.",
        "mayor": "📈 BULLISH — producción creciente. Bueno para semis y cloud.",
        "menor": "📉 BEARISH — estancamiento industrial. Revisar demanda chips.",
        "linea": "➡️ NEUTRO",
        "ict": "Confirmador macro. No moverá el NQ solo, pero puede añadir momentum.",
    },
}

# Fallback para eventos no mapeados exactamente
FALLBACK = {
    "impacto": "MEDIO",
    "desc": "Evento macroeconómico.",
    "mayor": "📉 BEARISH — si el dato supera expectativas de forma notable, puede presionar a la Fed a mantener tasas altas.",
    "menor": "📈 BULLISH — si el dato es más débil, alivia presión sobre la Fed y beneficia al crecimiento.",
    "linea": "➡️ NEUTRO — sin sorpresa. Sesgo previo se mantiene.",
    "ict": "Revisar sesgo HTF en NQ antes del evento. Operar solo si hay setup claro post-noticia.",
}


def match_rule(event_name: str):
    name_upper = event_name.upper()
    for keyword, rule in RULES.items():
        if keyword in name_upper:
            return rule
    return FALLBACK


def et_to_co(et_time_str: str) -> str:
    """Convierte hora ET a Colombia (ET-1h en horario de verano USA)."""
    if not et_time_str:
        return ""
    try:
        # Simple: restar 1h (válido mar-nov cuando ET=UTC-4, CO=UTC-5)
        h, m = et_time_str.replace(":", ":").split(":")[:2]
        hh = int(h)
        if hh == 0:
            co_hh = 23
        else:
            co_hh = hh - 1
        return f"{co_hh:02d}:{m} CO"
    except Exception:
        return ""


def day_name_from_date(date_str: str) -> str:
    d = datetime.strptime(date_str, "%Y-%m-%d")
    days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    return days[d.weekday()]


def build_summary(eventos: list) -> str:
    if not eventos:
        return "Semana sin eventos de alto impacto. Sesgo técnico prevalece. Revisa estructura HTF y FVG del NQ."
    altos = [e for e in eventos if e.get("impacto") == "ALTO"]
    nombres = ", ".join({e["nombre"] for e in altos[:3]})
    sesgo = "cargado" if len(altos) >= 2 else "tranquilo"
    return (
        f"Semana {sesgo} para el NQ. {len(altos)} evento(s) de ALTO impacto: {nombres}. "
        "Revisa killzones de NY y London. Mantén stops ajustados en días de noticia."
    )


def fetch_economic_calendar():
    today = datetime.utcnow().date()
    from_date = today.strftime("%Y-%m-%d")
    to_date = (today + timedelta(days=14)).strftime("%Y-%m-%d")
    url = f"https://finnhub.io/api/v1/calendar/economic?from={from_date}&to={to_date}&token={FINNHUB_KEY}"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    data = r.json()
    return data.get("economicCalendar", [])


def fetch_earnings_calendar():
    today = datetime.utcnow().date()
    from_date = today.strftime("%Y-%m-%d")
    to_date = (today + timedelta(days=14)).strftime("%Y-%m-%d")
    url = f"https://finnhub.io/api/v1/calendar/earnings?from={from_date}&to={to_date}&token={FINNHUB_KEY}"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    data = r.json()
    items = data.get("earningsCalendar", [])
    # Filtrar solo tech relevantes
    filtered = [i for i in items if i.get("symbol", "").upper() in TECH_TICKERS]
    return filtered


def build_eventos(raw_events: list) -> list:
    eventos = []
    for ev in raw_events:
        name = ev.get("event", "")
        if not name:
            continue
        rule = match_rule(name)
        impact = rule["impacto"]

        # Determinar actual vs estimate
        actual = ev.get("actual", "") or None
        estimate = ev.get("estimate", "") or None
        previous = ev.get("previous", "") or None

        # Si ya salió el dato y hay actual, no mostrar como futuro principal
        # Pero igual lo incluimos para que el usuario vea qué pasó
        date_str = ev.get("date", "")
        time_str = ev.get("time", "")

        eventos.append({
            "dia": day_name_from_date(date_str),
            "hora_et": time_str or "",
            "hora_co": et_to_co(time_str),
            "nombre": name,
            "impacto": impact,
            "esperado": estimate if estimate else None,
            "anterior": previous if previous else None,
            "descripcion": rule["desc"],
            "escenarios": {
                "mayor_esperado": rule["mayor"],
                "menor_esperado": rule["menor"],
                "en_linea": rule["linea"],
            },
            "contexto_ict": rule["ict"],
        })
    return eventos


def build_earnings(raw_earnings: list) -> list:
    out = []
    for e in raw_earnings:
        out.append({
            "symbol": e.get("symbol", ""),
            "name": e.get("name", ""),
            "date": e.get("date", ""),
            "epsEstimate": e.get("epsEstimate"),
            "epsActual": e.get("epsActual"),
            "hour": e.get("hour", ""),
        })
    return out


def main():
    print("Fetching economic calendar from Finnhub...")
    try:
        raw_eco = fetch_economic_calendar()
    except Exception as e:
        print(f"Warning: could not fetch economic calendar: {e}", file=sys.stderr)
        raw_eco = []

    print("Fetching earnings calendar from Finnhub...")
    try:
        raw_earn = fetch_earnings_calendar()
    except Exception as e:
        print(f"Warning: could not fetch earnings: {e}", file=sys.stderr)
        raw_earn = []

    eventos = build_eventos(raw_eco)
    earnings = build_earnings(raw_earn)

    payload = {
        "periodo": f"Semana del {datetime.utcnow().strftime('%Y-%m-%d')}",
        "resumen_sesgo": build_summary(eventos),
        "eventos": eventos,
        "earnings": earnings,
        "updatedAt": datetime.utcnow().strftime("%H:%M UTC"),
    }

    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(eventos)} events and {len(earnings)} earnings to {DATA_PATH}")


if __name__ == "__main__":
    main()
