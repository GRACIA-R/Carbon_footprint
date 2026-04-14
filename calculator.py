# ─────────────────────────────────────────────────────────────────────────────
# Factores de emisión — México
# Fuentes: IPCC 2006, SEMARNAT, CFE Factor de Emisión 2022 (0.432 kg CO2/kWh)
# ─────────────────────────────────────────────────────────────────────────────

# Transporte (kg CO2 por km)
FACTORES_TRANSPORTE = {
    "Automóvil propio (gasolina)":       0.192,   # IPCC promedio sedán
    "Automóvil propio (diésel)":         0.171,
    "Motocicleta":                        0.103,
    "Transporte público (camión/metro)": 0.089,
    "Bicicleta":                          0.0,
    "A pie":                              0.0,
}

# Electricidad — CFE factor 2022 (kg CO2/kWh)
FACTOR_ELECTRICIDAD = 0.432

# Gas LP — IPCC (kg CO2/kg gas LP)
FACTOR_GAS_LP = 2.983

# Vuelos (kg CO2 por vuelo, incluye factor de forzamiento radiativo x1.9)
FACTOR_VUELO_CORTO = 255    # < 3 h  (~500 km promedio, ida y vuelta incluido)
FACTOR_VUELO_LARGO = 1_100  # > 3 h  (~2000 km promedio)

# Dieta (kg CO2 por persona por día)
FACTORES_DIETA = {
    "Omnívora con carne roja frecuente (casi diario)": 7.19,
    "Omnívora moderada (carne 3–4 veces/semana)":      5.63,
    "Omnívora baja en carne (1–2 veces/semana)":       4.67,
    "Pescetariana (sin carne roja/ave)":                3.91,
    "Vegetariana":                                      3.81,
    "Vegana":                                           2.89,
}

# Desperdicio de comida (multiplicador sobre dieta)
FACTOR_DESPERDICIO = {
    "Poco o nada (termino casi todo)":       1.0,
    "Moderado (tiro algo ocasionalmente)":   1.15,
    "Bastante (tiro comida con frecuencia)": 1.35,
}

# Reciclaje (reducción en kg CO2/año)
REDUCCION_RECICLA = {
    "Sí, separo y reciclo activamente": -150,
    "Ocasionalmente":                   -50,
    "No reciclo":                        0,
}

# Composta (kg CO2/año evitados)
REDUCCION_COMPOSTA = {"Sí": -80, "No": 0}

# Digital
KG_CO2_POR_CORREO_ALMACENADO = 0.000010   # kg CO2 por correo/año
KG_CO2_POR_HORA_STREAMING = 0.036          # kg CO2 por hora (promedio CDN + dispositivo)


def calculate_footprint(data: dict) -> float:
    """
    Calcula la huella de carbono anual en toneladas de CO2 equivalente.
    """
    semanas_anio = 52

    # 1. Transporte diario al campus
    factor_transp = FACTORES_TRANSPORTE.get(data["transporte_principal"], 0.0)
    km_anuales = data["distancia_diaria_km"] * data["dias_campus_semana"] * semanas_anio
    co2_transporte = km_anuales * factor_transp  # kg

    # 2. Energía del hogar — prorrateada por personas
    personas = max(data["personas_hogar"], 1)
    co2_electricidad = (data["electricidad_kwh_mes"] * 12 * FACTOR_ELECTRICIDAD) / personas
    co2_gas = (data["gas_lp_kg_mes"] * 12 * FACTOR_GAS_LP) / personas

    # 3. Vuelos
    co2_vuelos = (
        data["vuelos_cortos_anio"] * FACTOR_VUELO_CORTO +
        data["vuelos_largos_anio"] * FACTOR_VUELO_LARGO
    )

    # 4. Dieta
    factor_dieta = FACTORES_DIETA.get(data["tipo_dieta"], 5.63)
    mult_desperdicio = FACTOR_DESPERDICIO.get(data["desperdicio_comida"], 1.0)
    co2_dieta = factor_dieta * mult_desperdicio * 365

    # 5. Residuos (reciclaje + composta)
    co2_residuos = (
        REDUCCION_RECICLA.get(data["recicla"], 0) +
        REDUCCION_COMPOSTA.get(data["compostas"], 0)
    )

    # 6. Huella digital
    co2_digital = (
        data["correos_inbox"] * KG_CO2_POR_CORREO_ALMACENADO * 365 +
        data["streaming_horas_dia"] * KG_CO2_POR_HORA_STREAMING * 365
    )

    total_kg = (
        co2_transporte + co2_electricidad + co2_gas +
        co2_vuelos + co2_dieta + co2_residuos + co2_digital
    )

    return round(max(total_kg, 0) / 1000, 3)  # convertir a toneladas


def calculate_equivalences(huella_ton: float) -> dict:
    """
    Calcula equivalencias comunicativas para la huella dada.
    """
    huella_kg = huella_ton * 1000

    return {
        # 1 árbol maduro absorbe ~21 kg CO2/año
        "arboles": round(huella_kg / 21),
        # 1 bombilla LED 10W encendida 24h = 0.24 kWh/día * 0.432 = 0.1037 kg CO2/día = ~37.8 kg/año
        "bombillas": round(huella_kg / 37.8),
        # Auto gasolina promedio emite ~0.192 kg CO2/km
        "km_carro": round(huella_kg / 0.192),
        # Reciclar 1 kg de plástico evita ~1.5 kg CO2
        "plastico_kg": round(huella_kg / 1.5),
        # Desglose por categoría (para la gráfica)
        "desglose": _desglose_placeholder(huella_ton),
    }


def _desglose_placeholder(huella_ton: float) -> dict:
    """
    Retorna el último desglose calculado (se almacena en session_state desde app.py).
    Este valor es sobrescrito por calculate_footprint_detailed si se llama.
    Se incluye aquí como fallback proporcional.
    """
    # Proporciones promedio para fallback visual
    t = huella_ton
    return {
        "transporte":   round(t * 0.22, 3),
        "vuelos":       round(t * 0.10, 3),
        "electricidad": round(t * 0.18, 3),
        "gas":          round(t * 0.12, 3),
        "dieta":        round(t * 0.35, 3),
        "residuos":     round(t * 0.03, 3),
    }


def calculate_footprint_with_breakdown(data: dict) -> tuple[float, dict]:
    """
    Versión extendida que retorna (total, desglose_por_categoria).
    """
    semanas_anio = 52
    personas = max(data["personas_hogar"], 1)

    factor_transp = FACTORES_TRANSPORTE.get(data["transporte_principal"], 0.0)
    km_anuales = data["distancia_diaria_km"] * data["dias_campus_semana"] * semanas_anio
    co2_transporte = km_anuales * factor_transp

    co2_electricidad = (data["electricidad_kwh_mes"] * 12 * FACTOR_ELECTRICIDAD) / personas
    co2_gas = (data["gas_lp_kg_mes"] * 12 * FACTOR_GAS_LP) / personas

    co2_vuelos = (
        data["vuelos_cortos_anio"] * FACTOR_VUELO_CORTO +
        data["vuelos_largos_anio"] * FACTOR_VUELO_LARGO
    )

    factor_dieta = FACTORES_DIETA.get(data["tipo_dieta"], 5.63)
    mult_desperdicio = FACTOR_DESPERDICIO.get(data["desperdicio_comida"], 1.0)
    co2_dieta = factor_dieta * mult_desperdicio * 365

    co2_residuos = (
        REDUCCION_RECICLA.get(data["recicla"], 0) +
        REDUCCION_COMPOSTA.get(data["compostas"], 0) +
        data["correos_inbox"] * KG_CO2_POR_CORREO_ALMACENADO * 365 +
        data["streaming_horas_dia"] * KG_CO2_POR_HORA_STREAMING * 365
    )

    total_kg = max(
        co2_transporte + co2_electricidad + co2_gas +
        co2_vuelos + co2_dieta + co2_residuos, 0
    )

    desglose = {
        "transporte":   round(co2_transporte / 1000, 3),
        "vuelos":       round(co2_vuelos / 1000, 3),
        "electricidad": round(co2_electricidad / 1000, 3),
        "gas":          round(co2_gas / 1000, 3),
        "dieta":        round(co2_dieta / 1000, 3),
        "residuos":     round(co2_residuos / 1000, 3),
    }

    return round(total_kg / 1000, 3), desglose
