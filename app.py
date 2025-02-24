import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import locale
from plotly.subplots import make_subplots
from sqlalchemy import create_engine
import plotly.figure_factory as ff
from datetime import datetime, timedelta
from prophet import Prophet

# Configuración inicial de la página
st.set_page_config(
    page_title="Análisis de Tarifas Energéticas",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS personalizado
st.markdown("""
    <style>
    .main {
        padding: 20px;
    }
    .stMetric {
        background-color: #000000;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Conexión a la base de datos
@st.cache_resource
def init_connection():
    return create_engine('mysql+mysqlconnector://root:@localhost/tarifas_energia')

# Función para cargar datos
@st.cache_data
def load_data():
    engine = init_connection()
    
    # Consultas SQL optimizadas
    query_tarifas = """
    SELECT t.*, c.nombre as categoria_nombre 
    FROM tarifa t 
    JOIN categoria c ON t.id_categoria = c.id_categoria
    ORDER BY t.periodo, c.nombre
    """
    
    query_niveles = """
    SELECT tn.*, c.nombre as categoria_nombre 
    FROM tarifa_nivel tn 
    JOIN categoria c ON tn.id_categoria = c.id_categoria
    ORDER BY tn.periodo, c.nombre
    """
    
    # Cargar datos en DataFrames
    df_tarifas = pd.read_sql(query_tarifas, engine)
    df_niveles = pd.read_sql(query_niveles, engine)
    
    # Procesamiento de fechas
    df_tarifas['fecha'] = pd.to_datetime(df_tarifas['periodo'].astype(str), format='%Y%m')
    df_niveles['fecha'] = pd.to_datetime(df_niveles['periodo'].astype(str), format='%Y%m')
    
    return df_tarifas, df_niveles

# Función para generar análisis automático
# def generar_insights(df, tipo_propiedad):
#     insights = []
    
#     cambio_medio = df[tipo_propiedad].pct_change().mean() * 100
#     if cambio_medio > 0:
#         insights.append(f"Las tarifas han aumentado en promedio un {cambio_medio:.2f}% en el periodo seleccionado.")
#     else:
#         insights.append(f"Las tarifas han disminuido en promedio un {abs(cambio_medio):.2f}% en el periodo seleccionado.")
    
#     correlaciones = df[['propiedad_epm', 'propiedad_compartido', 'propiedad_cliente']].corr()
#     correlacion_maxima = correlaciones.unstack().sort_values(ascending=False)
#     correlacion_maxima = correlacion_maxima[correlacion_maxima < 1].idxmax()
#     insights.append(f"La mayor correlación observada es entre {correlacion_maxima[0]} y {correlacion_maxima[1]}, indicando que sus tarifas tienden a moverse juntas.")
    
#     Q1, Q3 = df[tipo_propiedad].quantile([0.25, 0.75])
#     IQR = Q3 - Q1
#     outliers = df[(df[tipo_propiedad] < (Q1 - 1.5 * IQR)) | (df[tipo_propiedad] > (Q3 + 1.5 * IQR))]
#     if not outliers.empty:
#         insights.append(f"Se han detectado {len(outliers)} valores atípicos en las tarifas seleccionadas, lo que podría indicar cambios bruscos o eventos excepcionales.")
    
#     return insights

def generar_insights(df, tipo_propiedad):
    insights = []
    
    # 1. Cambio promedio porcentual
    cambio_medio = df[tipo_propiedad].pct_change().mean() * 100
    if cambio_medio > 0:
        insights.append(f"Las tarifas han aumentado en promedio un {cambio_medio:.2f}% en el periodo seleccionado.")
    else:
        insights.append(f"Las tarifas han disminuido en promedio un {abs(cambio_medio):.2f}% en el periodo seleccionado.")
    
    # 2. Correlación más fuerte entre tipos de propiedad
    correlaciones = df[['propiedad_epm', 'propiedad_compartido', 'propiedad_cliente']].corr()
    correlacion_maxima = correlaciones.unstack().sort_values(ascending=False)
    correlacion_maxima = correlacion_maxima[correlacion_maxima < 1].idxmax()
    valor_correlacion = correlaciones.loc[correlacion_maxima[0], correlacion_maxima[1]]
    insights.append(f"La mayor correlación observada es entre {correlacion_maxima[0].replace('propiedad_', '').title()} "
                   f"y {correlacion_maxima[1].replace('propiedad_', '').title()} "
                   f"(coeficiente: {valor_correlacion:.2f}), indicando que sus tarifas tienden a moverse juntas.")
    
    # 3. Detección de valores atípicos
    Q1, Q3 = df[tipo_propiedad].quantile([0.25, 0.75])
    IQR = Q3 - Q1
    outliers = df[(df[tipo_propiedad] < (Q1 - 1.5 * IQR)) | (df[tipo_propiedad] > (Q3 + 1.5 * IQR))]
    if not outliers.empty:
        fecha_max_outlier = outliers['fecha'].dt.strftime('%b %Y').iloc[0]
        insights.append(f"Se han detectado {len(outliers)} valores atípicos en las tarifas, "
                       f"como el registrado en {fecha_max_outlier}, lo que podría indicar cambios bruscos o eventos excepcionales.")
    
    # 4. Mes con mayor variación
    variacion_mensual = df.groupby('fecha')[tipo_propiedad].mean().pct_change() * 100
    if not variacion_mensual.empty:
        mes_max_variacion = variacion_mensual.idxmax().strftime('%B %Y').capitalize()
        valor_max_variacion = variacion_mensual.max()
        if valor_max_variacion > 0:
            insights.append(f"El mes con mayor aumento fue {mes_max_variacion} con una variación de +{valor_max_variacion:.2f}%.")
        else:
            insights.append(f"El mes con mayor disminución fue {mes_max_variacion} con una variación de {valor_max_variacion:.2f}%.")
    
    # 5. Categoría más volátil
    volatilidad = df.groupby('categoria_nombre')[tipo_propiedad].std()
    if not volatilidad.empty:
        categoria_volatil = volatilidad.idxmax()
        valor_volatilidad = volatilidad.max()
        insights.append(f"La categoría más volátil es '{categoria_volatil}' "
                       f"con una desviación estándar de {valor_volatilidad:,.2f} COP.")
    
    # 6. Tendencia anual
    df['año'] = df['fecha'].dt.year
    tendencia_anual = df.groupby('año')[tipo_propiedad].mean().pct_change().mean() * 100
    if tendencia_anual > 0:
        insights.append(f"La tendencia anual promedio muestra un aumento del {tendencia_anual:.2f}% por año.")
    elif tendencia_anual < 0:
        insights.append(f"La tendencia anual promedio muestra una disminución del {abs(tendencia_anual):.2f}% por año.")
    else:
        insights.append("No se observa una tendencia anual clara en las tarifas.")

    # 7. Comparación con inflación (simulada, podrías integrar datos reales)
    inflacion_promedio = 5.22  # Esto toca irlo cambiando a mano. 
    if cambio_medio > inflacion_promedio:
        insights.append(f"El aumento promedio de las tarifas ({cambio_medio:.2f}%) supera la inflación promedio "
                       f"estimada ({inflacion_promedio}%), indicando un incremento real en el costo.")
    
    return insights

# Función para predecir tarifas futuras
def predecir_tarifas(df, tipo_propiedad):
    df_pred = df[['fecha', tipo_propiedad]].rename(columns={'fecha': 'ds', tipo_propiedad: 'y'})
    modelo = Prophet()
    modelo.fit(df_pred)
    futuro = modelo.make_future_dataframe(periods=6, freq='M')
    prediccion = modelo.predict(futuro)
    return prediccion

# Función para detectar outliers
def detectar_outliers(data):
    Q1 = data.quantile(0.25)
    Q3 = data.quantile(0.75)
    IQR = Q3 - Q1
    outliers = data[(data < (Q1 - 1.5 * IQR)) | (data > (Q3 + 1.5 * IQR))]
    return outliers

# Título principal con emoji
st.title("⚡ Análisis de Tarifas Energéticas")
st.markdown("---")

# Cargar datos
df_tarifas, df_niveles = load_data()

# Sidebar para filtros
with st.sidebar:
    st.header("🔍 Filtros")
    
    # Filtro de categorías
    categorias = sorted(df_tarifas['categoria_nombre'].unique())
    categoria_seleccionada = st.multiselect(
        "Seleccionar Categorías",
        options=categorias,
        default=["ESPD*", "Estrato 1 - Rango 0 - CS", "Estrato 2 - Rango 0 - CS", "Estrato 3 - Rango 0 - CS",
                "Estrato 4 - Todo el consumo", "Estrato 5 y 6 - Todo el consumo", "Industrial y Comercial",
                "Oficial y Exentos de Contribucion"]
    )
    
    # Filtro de fechas
    fecha_min = df_tarifas['fecha'].min()
    fecha_max = df_tarifas['fecha'].max()
    fecha_rango = st.date_input(
        "Rango de Fechas",
        value=(fecha_min.date(), fecha_max.date()),
        min_value=fecha_min.date(),
        max_value=fecha_max.date()
    )
    
    # Filtro de tipo de propiedad
    tipo_propiedad = st.selectbox(
        "Tipo de Propiedad",
        ["propiedad_epm", "propiedad_compartido", "propiedad_cliente"],
        format_func=lambda x: x.replace("propiedad_", "").title()
    )

# Filtrar datos según selección
df_filtrado = df_tarifas[
    (df_tarifas['categoria_nombre'].isin(categoria_seleccionada)) &
    (df_tarifas['fecha'] >= pd.to_datetime(fecha_rango[0])) &
    (df_tarifas['fecha'] <= pd.to_datetime(fecha_rango[1]))
]

# Crear pestañas
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Evolución Temporal",
    "📊 Análisis Comparativo",
    "📉 Tendencias",
    "📑 Estadísticas",
    "🤖 Análisis Inteligente",
    "🔮 Predicción de Tarifas"
])

# Pestaña 1: Evolución Temporal
with tab1:
    st.header("Evolución de Tarifas en el Tiempo")
    
    # Gráfico de líneas temporal
    fig_evolucion = px.line(
        df_filtrado,
        x='fecha',
        y=tipo_propiedad,
        color='categoria_nombre',
        title=f'Evolución de Tarifas por Categoría ({tipo_propiedad.replace("propiedad_", "").title()})',
        labels={
            tipo_propiedad: 'Tarifa',
            'fecha': 'Fecha',
            'categoria_nombre': 'Categoría'
        }
    )
    fig_evolucion.update_layout(
        xaxis_title="Fecha",
        yaxis_title="Tarifa (COP)",
        legend_title="Categoría",
        hovermode='x unified'
    )
    st.plotly_chart(fig_evolucion, use_container_width=True)
    
    # Análisis de variación
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Variación Porcentual Tarifa")
        df_var = df_filtrado.groupby('categoria_nombre')[tipo_propiedad].agg([
            ('Inicial [$]', 'first'),
            ('Final [$]', 'last'),
            ('Variación [%]', lambda x: ((x.iloc[-1] - x.iloc[0]) / x.iloc[0] * 100))
        ]).round(2)
        st.dataframe(df_var)
    
    with col2:
        st.subheader("Estadísticas de Variación")
        df_stats = df_filtrado.groupby('categoria_nombre')[tipo_propiedad].agg([
            ('Promedio', 'mean'),
            ('Mínimo', 'min'),
            ('Máximo', 'max'),
            ('Desv. Est.', 'std')
        ]).round(2)
        st.dataframe(df_stats)

# Pestaña 2: Análisis Comparativo
with tab2:
    st.header("Comparación entre Tipos de Propiedad")
    
    # Gráfico de cajas
    fig_box = go.Figure()
    propiedades = ['propiedad_epm', 'propiedad_compartido', 'propiedad_cliente']
    
    for prop in propiedades:
        fig_box.add_trace(go.Box(
            y=df_filtrado[prop],
            name=prop.replace('propiedad_', '').title(),
            boxpoints='outliers'
        ))
    
    fig_box.update_layout(
        title='Distribución de Tarifas por Tipo de Propiedad',
        yaxis_title='Tarifa (COP)',
        showlegend=True
    )
    st.plotly_chart(fig_box, use_container_width=True)
    
    # Matriz de correlación
    st.subheader("Correlación entre Tipos de Propiedad")
    corr_matrix = df_filtrado[propiedades].corr()
    fig_corr = px.imshow(
        corr_matrix,
        labels=dict(color="Correlación"),
        title="Matriz de Correlación",
        color_continuous_scale="RdBu"
    )
    st.plotly_chart(fig_corr, use_container_width=True)

# Pestaña 3: Tendencias
with tab3:
    st.header("Análisis de Tendencias")
    
    # Tendencia general
    df_filtrado['año'] = df_filtrado['fecha'].dt.year
    df_filtrado['mes'] = df_filtrado['fecha'].dt.month
    
    # Tendencia mensual promedio
    fig_tendencia = px.line(
        df_filtrado.groupby(['año', 'mes'])[tipo_propiedad].mean().reset_index(),
        x='mes',
        y=tipo_propiedad,
        color='año',
        title=f'Tendencia Mensual por Año ({tipo_propiedad.replace("propiedad_", "").title()})',
        labels={
            tipo_propiedad: 'Tarifa Promedio',
            'mes': 'Mes',
            'año': 'Año'
        }
    )
    st.plotly_chart(fig_tendencia, use_container_width=True)
    
    # Descomposición de tendencia por categoría
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Crecimiento Anual por Categoría")
        df_crecimiento = df_filtrado.groupby(['año', 'categoria_nombre'])[tipo_propiedad].mean().unstack()
        st.dataframe(df_crecimiento.round(2))
    
    with col2:
        st.subheader("Variación Mensual Promedio")
        df_var_mensual = df_filtrado.groupby('mes')[tipo_propiedad].agg([
            ('Promedio', 'mean'),
            ('Variación', 'std')
        ]).round(2)
        st.dataframe(df_var_mensual)

    st.subheader("Mapa de Calor de Tarifas")
    df_heatmap = df_filtrado.pivot_table(values=tipo_propiedad, index='mes', columns='año', aggfunc='mean')
    fig_heatmap = px.imshow(df_heatmap, title="Tarifas Promedio por Mes y Año", labels=dict(color="Tarifa [$]"))
    st.plotly_chart(fig_heatmap)

# Pestaña 4: Estadísticas
with tab4:
    st.header("Estadísticas Detalladas")
    
    # Resumen estadístico completo
    st.subheader("Resumen Estadístico por Categoría")
    df_stats_completo = df_filtrado.groupby('categoria_nombre')[tipo_propiedad].describe()
    st.dataframe(df_stats_completo)
    
    # Análisis de outliers
    st.subheader("Detección de Valores Atípicos")
    
    outliers = df_filtrado.groupby('categoria_nombre').apply(
        lambda x: detectar_outliers(x[tipo_propiedad])
    )
    
    if not outliers.empty:
        st.dataframe(pd.DataFrame({
            'Categoría': outliers.index.get_level_values(0),
            'Valor': outliers.values,
            'Fecha': df_filtrado.loc[outliers.index.get_level_values(1), 'fecha'].values
        }))
    else:
        st.write("No se encontraron valores atípicos significativos.")

# Pestaña 5: Análisis Inteligente
with tab5:
    st.header("🤖 Análisis Inteligente de Tarifas")
    insights = generar_insights(df_filtrado, tipo_propiedad)
    for insight in insights:
        st.write(f"🔍 {insight}")

# Pestaña 6: Predicción de Tarifas
with tab6:
    st.header("🔮 Predicción de Tarifas")
    prediccion = predecir_tarifas(df_filtrado, tipo_propiedad)
    fig_pred = px.line(
        prediccion,
        x='ds',
        y='yhat',
        title="Predicción de Tarifas Energéticas",
        labels={'ds': 'Fecha', 'yhat': 'Tarifa Predicha (COP)'}
    )
    st.plotly_chart(fig_pred, use_container_width=True)
    
    # Tomar la fecha actual automáticamente
    fecha_actual = pd.to_datetime(datetime.now().date())  # Obtiene la fecha actual del sistema
    proximo_mes = fecha_actual + pd.offsets.MonthEnd(1) + pd.offsets.MonthBegin(1)
    pred_proximo_mes = prediccion[prediccion['ds'].dt.to_pydatetime() >= proximo_mes].iloc[0]
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8') 
    tarifa_predicha = pred_proximo_mes['yhat']
    fecha_predicha = pred_proximo_mes['ds'].strftime('%B %Y').capitalize()
    
    # Mostrar etiqueta con la predicción
    st.markdown(
        f"<span style='background-color: #000000; padding: 5px 10px; border-radius: 5px; font-size: 14px;'>"
        f"Predicción para {fecha_predicha}: ${tarifa_predicha:,.2f} COP"
        f"</span>",
        unsafe_allow_html=True
    )

# Métricas clave en el footer
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Tarifa Promedio",
        f"${df_filtrado[tipo_propiedad].mean():.2f}",
        f"{df_filtrado[tipo_propiedad].pct_change().mean()*100:.1f}%"
    )

with col2:
    st.metric(
        "Tarifa Máxima",
        f"${df_filtrado[tipo_propiedad].max():.2f}",
        f"Categoría: {df_filtrado.loc[df_filtrado[tipo_propiedad].idxmax(), 'categoria_nombre']}"
    )


with col3:
    # Variación máxima mensual y su mes correspondiente
    variacion_mensual = df_filtrado.groupby('fecha')[tipo_propiedad].mean().pct_change() * 100
    max_variacion_idx = variacion_mensual.idxmax()
    st.metric(
        "Mayor Variación Mensual",
        f"{variacion_mensual.max():.1f}%",
        f"Mes: {max_variacion_idx.strftime('%b %Y')}"
    )

with col4:
    # Categoría con mayor volatilidad (desviación estándar)
    volatilidad = df_filtrado.groupby('categoria_nombre')[tipo_propiedad].std()
    categoria_volatil = volatilidad.idxmax()
    st.metric(
        "Categoría Más Volátil",
        categoria_volatil,
        f"Desv. Est.: {volatilidad.max():,.2f}"
    )

# En el footer
if st.button("Descargar Datos Filtrados como CSV"):
    csv = df_filtrado.to_csv(index=False)
    st.download_button("Descargar", csv, "datos_tarifas.csv", "text/csv")

# Información adicional
st.markdown("---")
st.markdown("""
    #### Notas:
    - Los datos mostrados corresponden a las tarifas energéticas históricas.
    - Todas las tarifas están en pesos colombianos (COP).
    - Los análisis incluyen variaciones porcentuales y tendencias temporales.
    - Se ha utilizado un modelo de predicción para estimar tarifas futuras.
          
    #### Comodín:
    - **ESPD:** Empresa de Servicios Públicos Domiciliarios.
    - **CS:** Consumo Subsidiado (Alturas ≥ 1.000 msnm (0-130 kWh) | Alturas < 1.000 msnm (0-173 kWh)).
            
    #### Tarifa Horaria:
    - **Punta:** 9 a.m.-12 m - 6-9 p.m.
    - **Fuera de punta:** 0-9 a.m. - 12 m | 6 p.m. - 9 p.m.-12 p.m.
            
    #### Acerca de:
    - **Desarrollado por:** Los Tarifarios.     
""")

# Botón para limpiar caché
if st.button('Limpiar Cache'):
    st.cache_data.clear()
    st.success('Cache limpiado exitosamente')