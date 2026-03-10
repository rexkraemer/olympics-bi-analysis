import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Olympics Dashboard",
    page_icon="🏅",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;500;600&display=swap');

:root {
    --gold: #C9A84C;
    --silver: #A8A9AD;
    --bronze: #CD7F32;
    --bg: #0A0A0A;
    --surface: #141414;
    --surface2: #1E1E1E;
    --text: #EDEDEE;
    --muted: #6B6B6B;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: var(--bg);
    color: var(--text);
}

.main { background-color: var(--bg); }
section[data-testid="stSidebar"] { background-color: var(--surface); border-right: 1px solid #2a2a2a; }

h1, h2, h3 { font-family: 'Bebas Neue', cursive; letter-spacing: 2px; }

.metric-card {
    background: var(--surface2);
    border: 1px solid #2a2a2a;
    border-radius: 12px;
    padding: 20px 24px;
    text-align: center;
}
.metric-value {
    font-family: 'Bebas Neue', cursive;
    font-size: 2.4rem;
    color: var(--gold);
    line-height: 1;
}
.metric-label {
    font-size: 0.75rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 4px;
}

.page-title {
    font-family: 'Bebas Neue', cursive;
    font-size: 3rem;
    letter-spacing: 4px;
    color: var(--gold);
    margin-bottom: 0;
}
.page-subtitle {
    font-size: 0.85rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 2rem;
}

.divider {
    height: 1px;
    background: linear-gradient(90deg, var(--gold), transparent);
    margin: 24px 0;
}

.stSelectbox > div > div { background-color: var(--surface2) !important; border-color: #2a2a2a !important; }
.stSlider > div { color: var(--text); }
div[data-testid="stMetric"] { background: var(--surface2); border-radius: 10px; padding: 12px; border: 1px solid #2a2a2a; }
div[data-testid="stMetric"] label { color: var(--muted) !important; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; }
div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: var(--gold); font-family: 'Bebas Neue', cursive; font-size: 2rem; }

.nav-pill {
    display: inline-block;
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    background: #1E1E1E;
    border: 1px solid #2a2a2a;
    color: #6B6B6B;
    margin: 2px;
}
.nav-pill.active {
    background: var(--gold);
    border-color: var(--gold);
    color: #000;
}

.section-header {
    font-family: 'Bebas Neue', cursive;
    font-size: 1.5rem;
    letter-spacing: 3px;
    color: var(--gold);
    border-bottom: 1px solid #2a2a2a;
    padding-bottom: 8px;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# ── NOC → ISO3 Mapping ────────────────────────────────────────────────────────
NOC_TO_ISO3 = {
    'AFG':'AFG','ALB':'ALB','ALG':'DZA','AND':'AND','ANG':'AGO','ANT':'ATG','ARG':'ARG',
    'ARM':'ARM','ARU':'ABW','ASA':'ASM','AUS':'AUS','AUT':'AUT','AZE':'AZE','BAH':'BHS',
    'BAN':'BGD','BAR':'BRB','BDI':'BDI','BEL':'BEL','BEN':'BEN','BER':'BMU','BHU':'BTN',
    'BIH':'BIH','BIZ':'BLZ','BLR':'BLR','BOL':'BOL','BOT':'BWA','BRA':'BRA','BRN':'BRN',
    'BUL':'BGR','BUR':'BFA','CAF':'CAF','CAM':'KHM','CAN':'CAN','CAY':'CYM','CGO':'COG',
    'CHA':'TCD','CHI':'CHL','CHN':'CHN','CIV':'CIV','CMR':'CMR','COD':'COD','COK':'COK',
    'COL':'COL','COM':'COM','CPV':'CPV','CRC':'CRI','CRO':'HRV','CUB':'CUB','CYP':'CYP',
    'CZE':'CZE','DEN':'DNK','DJI':'DJI','DMA':'DMA','DOM':'DOM','ECU':'ECU','EGY':'EGY',
    'ERI':'ERI','ESA':'SLV','ESP':'ESP','EST':'EST','ETH':'ETH','FIJ':'FJI','FIN':'FIN',
    'FRA':'FRA','FSM':'FSM','GAB':'GAB','GAM':'GMB','GBR':'GBR','GBS':'GNB','GEO':'GEO',
    'GEQ':'GNQ','GER':'DEU','GHA':'GHA','GRE':'GRC','GRN':'GRD','GUA':'GTM','GUI':'GIN',
    'GUM':'GUM','GUY':'GUY','HAI':'HTI','HON':'HND','HUN':'HUN','INA':'IDN','IND':'IND',
    'IRI':'IRN','IRL':'IRL','IRQ':'IRQ','ISL':'ISL','ISR':'ISR','ISV':'VIR','ITA':'ITA',
    'IVB':'VGB','JAM':'JAM','JOR':'JOR','JPN':'JPN','KAZ':'KAZ','KEN':'KEN','KGZ':'KGZ',
    'KIR':'KIR','KOR':'KOR','KOS':'XKX','KSA':'SAU','KUW':'KWT','LAO':'LAO','LAT':'LVA',
    'LBA':'LBY','LBR':'LBR','LCA':'LCA','LES':'LSO','LIB':'LBN','LIE':'LIE','LTU':'LTU',
    'LUX':'LUX','MAD':'MDG','MAR':'MAR','MAS':'MYS','MAW':'MWI','MDA':'MDA','MDV':'MDV',
    'MEX':'MEX','MGL':'MNG','MKD':'MKD','MLI':'MLI','MLT':'MLT','MNE':'MNE','MON':'MCO',
    'MOZ':'MOZ','MRI':'MUS','MTN':'MRT','MYA':'MMR','NAM':'NAM','NCA':'NIC','NED':'NLD',
    'NEP':'NPL','NGR':'NGA','NIG':'NER','NOR':'NOR','NRU':'NRU','NZL':'NZL','OMA':'OMN',
    'PAK':'PAK','PAN':'PAN','PAR':'PRY','PER':'PER','PHI':'PHL','PLE':'PSE','PLW':'PLW',
    'PNG':'PNG','POL':'POL','POR':'PRT','PRK':'PRK','PUR':'PRI','QAT':'QAT','ROU':'ROU',
    'RSA':'ZAF','RUS':'RUS','RWA':'RWA','SAM':'WSM','SEN':'SEN','SEY':'SYC','SGP':'SGP',
    'SKN':'KNA','SLE':'SLE','SLO':'SVN','SMR':'SMR','SOL':'SLB','SOM':'SOM','SRB':'SRB',
    'SRI':'LKA','SSD':'SSD','STP':'STP','SUD':'SDN','SUI':'CHE','SUR':'SUR','SVK':'SVK',
    'SWE':'SWE','SWZ':'SWZ','SYR':'SYR','TAN':'TZA','TGA':'TON','THA':'THA','TJK':'TJK',
    'TKM':'TKM','TLS':'TLS','TOG':'TGO','TPE':'TWN','TRI':'TTO','TUN':'TUN','TUR':'TUR',
    'TUV':'TUV','UAE':'ARE','UGA':'UGA','UKR':'UKR','URU':'URY','USA':'USA','UZB':'UZB',
    'VAN':'VUT','VEN':'VEN','VIE':'VNM','VIN':'VCT','YEM':'YEM','ZAM':'ZMB','ZIM':'ZWE',
}

CONTINENT_MAPPING = {
    'AUT':'Europa','BEL':'Europa','DEN':'Europa','FIN':'Europa','FRA':'Europa','GER':'Europa',
    'GBR':'Europa','GRE':'Europa','HUN':'Europa','ITA':'Europa','NED':'Europa','NOR':'Europa',
    'POL':'Europa','POR':'Europa','ROU':'Europa','RUS':'Europa','ESP':'Europa','SWE':'Europa',
    'SUI':'Europa','TCH':'Europa','URS':'Europa','YUG':'Europa','CRO':'Europa','CZE':'Europa',
    'EST':'Europa','LAT':'Europa','LTU':'Europa','SVK':'Europa','SLO':'Europa','BLR':'Europa',
    'UKR':'Europa','BUL':'Europa','IRL':'Europa','ISL':'Europa','LUX':'Europa','MDA':'Europa',
    'ARM':'Europa','AZE':'Europa','GEO':'Europa','KAZ':'Europa','MKD':'Europa','ALB':'Europa',
    'AND':'Europa','BIH':'Europa','CYP':'Europa','FRG':'Europa','GDR':'Europa','ISR':'Europa',
    'LIE':'Europa','MLT':'Europa','MON':'Europa','MNE':'Europa','SCG':'Europa','SRB':'Europa',
    'SMR':'Europa',
    'USA':'Amerika Nord','CAN':'Amerika Nord','MEX':'Amerika Nord','CUB':'Amerika Nord',
    'JAM':'Amerika Nord','TRI':'Amerika Nord','BAH':'Amerika Nord','DOM':'Amerika Nord',
    'HAI':'Amerika Nord','PUR':'Amerika Nord','ANT':'Amerika Nord','BAR':'Amerika Nord',
    'BIZ':'Amerika Nord','CAY':'Amerika Nord','GRN':'Amerika Nord','IVB':'Amerika Nord',
    'SKN':'Amerika Nord','LCA':'Amerika Nord','VIN':'Amerika Nord','CRC':'Amerika Nord',
    'ESA':'Amerika Nord','GUA':'Amerika Nord','HON':'Amerika Nord','NCA':'Amerika Nord',
    'PAN':'Amerika Nord',
    'BRA':'Amerika Süd','ARG':'Amerika Süd','CHI':'Amerika Süd','COL':'Amerika Süd',
    'VEN':'Amerika Süd','ECU':'Amerika Süd','PER':'Amerika Süd','URU':'Amerika Süd',
    'GUY':'Amerika Süd','BOL':'Amerika Süd','PAR':'Amerika Süd','SUR':'Amerika Süd',
    'CHN':'Asien','JPN':'Asien','KOR':'Asien','IND':'Asien','IRI':'Asien','IRQ':'Asien',
    'PRK':'Asien','MGL':'Asien','PAK':'Asien','PHI':'Asien','THA':'Asien','VIE':'Asien',
    'MAS':'Asien','SGP':'Asien','INA':'Asien','TPE':'Asien','BRN':'Asien','KUW':'Asien',
    'QAT':'Asien','KSA':'Asien','SYR':'Asien','UZB':'Asien','TJK':'Asien','TKM':'Asien',
    'KGZ':'Asien','AFG':'Asien','BAN':'Asien','CAM':'Asien','MDV':'Asien','NEP':'Asien',
    'SRI':'Asien','UAE':'Asien','YEM':'Asien','JOR':'Asien','OMA':'Asien','MYA':'Asien',
    'LAO':'Asien',
    'ETH':'Afrika','KEN':'Afrika','NGR':'Afrika','RSA':'Afrika','EGY':'Afrika','MAR':'Afrika',
    'ALG':'Afrika','TUN':'Afrika','CMR':'Afrika','GHA':'Afrika','ZIM':'Afrika','UGA':'Afrika',
    'TAN':'Afrika','SEN':'Afrika','CIV':'Afrika','MOZ':'Afrika','NAM':'Afrika','BOT':'Afrika',
    'BUR':'Afrika','CAF':'Afrika','CGO':'Afrika','DJI':'Afrika','ERI':'Afrika','GAB':'Afrika',
    'GAM':'Afrika','GEQ':'Afrika','GUI':'Afrika','GBS':'Afrika','LBA':'Afrika','LES':'Afrika',
    'LBR':'Afrika','MDG':'Afrika','MLI':'Afrika','MTN':'Afrika','MRI':'Afrika','NIG':'Afrika',
    'RWA':'Afrika','STP':'Afrika','SEY':'Afrika','SLE':'Afrika','SOM':'Afrika','SUD':'Afrika',
    'SWZ':'Afrika','TOG':'Afrika','ZAM':'Afrika','BEN':'Afrika','CPV':'Afrika','COM':'Afrika',
    'AUS':'Ozeanien','NZL':'Ozeanien','FIJ':'Ozeanien','PNG':'Ozeanien','SAM':'Ozeanien',
    'SOL':'Ozeanien','TGA':'Ozeanien','VAN':'Ozeanien','FSM':'Ozeanien','KIR':'Ozeanien',
    'NRU':'Ozeanien','PLW':'Ozeanien',
}

HOST_COUNTRIES = {
    1896:'GRE',1900:'FRA',1904:'USA',1908:'GBR',1912:'SWE',1920:'BEL',1924:'FRA',
    1928:'NED',1932:'USA',1936:'GER',1948:'GBR',1952:'FIN',1956:'AUS',1960:'ITA',
    1964:'JPN',1968:'MEX',1972:'FRG',1976:'CAN',1980:'URS',1984:'USA',1988:'KOR',
    1992:'ESP',1996:'USA',2000:'AUS',2004:'GRE',2008:'CHN',2012:'GBR',2016:'BRA',
}

PLOTLY_TEMPLATE = dict(
    layout=dict(
        paper_bgcolor='#0A0A0A',
        plot_bgcolor='#141414',
        font=dict(color='#EDEDEE', family='Inter'),
        title_font=dict(color='#C9A84C', family='Bebas Neue', size=18),
        xaxis=dict(gridcolor='#2a2a2a', zerolinecolor='#2a2a2a'),
        yaxis=dict(gridcolor='#2a2a2a', zerolinecolor='#2a2a2a'),
        legend=dict(bgcolor='#141414', bordercolor='#2a2a2a', borderwidth=1),
        margin=dict(t=60, b=40, l=40, r=20),
    )
)

GOLD = '#C9A84C'
SILVER = '#A8A9AD'
BRONZE = '#CD7F32'
ORANGE = '#E07B39'
GRAY = '#3A3A3A'

# ── Data Loading ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv('olympics.csv', sep=';')
    df = df.dropna(subset=['Height', 'Weight', 'Country'])
    df = df[df['Age'] >= 11]
    df['Medal'] = df['Medal'].fillna('Keine Medaille')
    df['Height'] = df['Height'] / 1000
    df['Weight'] = df['Weight'] / 10
    df.columns = [c.lower() for c in df.columns]
    df['bmi'] = df['weight'] / (df['height'] ** 2)
    df['hat_medaille'] = df['medal'].isin(['Gold', 'Silver', 'Bronze']).map(
        {True: 'Medaille', False: 'Keine Medaille'}
    )
    medal_points = {'Gold': 3, 'Silver': 2, 'Bronze': 1}
    df['punkte'] = df['medal'].map(medal_points).fillna(0)
    df['kontinent'] = df['noc'].map(CONTINENT_MAPPING)
    df['iso3'] = df['noc'].map(NOC_TO_ISO3)
    return df

df = load_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="page-title" style="font-size:2rem">🏅 OLYMPIA</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">DSI Analytics Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        ["🏠 Übersicht", "💪 Athletenprofil", "⚖️ Körper & Medaillen", "🌍 Geografie & Gleichstellung", "🏠 Heimvorteil"],
        label_visibility="collapsed"
    )

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    year_range = st.slider(
        "Zeitraum",
        int(df['year'].min()), int(df['year'].max()),
        (int(df['year'].min()), int(df['year'].max())),
        step=4,
    )
    sex_filter = st.selectbox("Geschlecht", ["Alle", "Männer (M)", "Frauen (F)"])
    sex_code = None if sex_filter == "Alle" else sex_filter[8]

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#6B6B6B;font-size:0.75rem">Daten: 1896 – 2016 · Sommer</div>', unsafe_allow_html=True)

# Filter
dff = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1])]
if sex_code:
    dff = dff[dff['sex'] == sex_code]

# ═══════════════════════════════════════════════════════════
# PAGE: ÜBERSICHT
# ═══════════════════════════════════════════════════════════
if page == "🏠 Übersicht":
    st.markdown('<div class="page-title">OLYMPISCHE SPIELE</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Historische Analyse 1896 – 2016</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Athleten", f"{dff['id'].nunique():,}")
    with c2:
        st.metric("Nationen", f"{dff['noc'].nunique()}")
    with c3:
        st.metric("Sportarten", f"{dff['sport'].nunique()}")
    with c4:
        medals = dff[dff['hat_medaille'] == 'Medaille']
        st.metric("Medaillenvergaben", f"{len(medals):,}")

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">ATHLETEN PRO OLYMPIADE</div>', unsafe_allow_html=True)
        participants = dff.groupby('year').size().reset_index(name='n')
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=participants['year'], y=participants['n'],
            fill='tozeroy', fillcolor='rgba(201,168,76,0.15)',
            line=dict(color=GOLD, width=2),
            mode='lines+markers', marker=dict(size=5, color=GOLD),
        ))
        fig.update_layout(**PLOTLY_TEMPLATE['layout'], height=300,
                          title="Teilnehmer (gefiltert)")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">TOP 10 NATIONEN (SCORE)</div>', unsafe_allow_html=True)
        top_nations = (dff.groupby('country')['punkte'].sum()
                       .sort_values(ascending=False).head(10).reset_index())
        fig2 = go.Figure(go.Bar(
            x=top_nations['punkte'], y=top_nations['country'],
            orientation='h',
            marker=dict(color=GOLD, opacity=0.85),
            text=top_nations['punkte'].astype(int),
            textposition='outside', textfont=dict(color='#EDEDEE', size=11),
        ))
        fig2.update_layout(**PLOTLY_TEMPLATE['layout'], height=300,
                           yaxis=dict(autorange='reversed', gridcolor='#2a2a2a'),
                           title="Performance Score (Gold=3, Silber=2, Bronze=1)")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-header">TOP 10 SPORTARTEN NACH TEILNAHMEN</div>', unsafe_allow_html=True)
    top_sports = dff['sport'].value_counts().head(10).reset_index()
    top_sports.columns = ['sport', 'count']
    fig3 = go.Figure(go.Bar(
        x=top_sports['sport'], y=top_sports['count'],
        marker=dict(
            color=top_sports['count'],
            colorscale=[[0, '#1E1E1E'], [1, GOLD]],
            showscale=False,
        ),
    ))
    fig3.update_layout(**PLOTLY_TEMPLATE['layout'], height=280)
    st.plotly_chart(fig3, use_container_width=True)


# ═══════════════════════════════════════════════════════════
# PAGE: ATHLETENPROFIL
# ═══════════════════════════════════════════════════════════
elif page == "💪 Athletenprofil":
    st.markdown('<div class="page-title">ATHLETEN-IDEALWERTE</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Körperliche Profile der Medaillengewinner nach Sportart</div>', unsafe_allow_html=True)

    col_s, col_g = st.columns([3, 1])
    with col_s:
        sports = sorted(dff['sport'].dropna().unique())
        sport = st.selectbox("Sportart", sports)
    with col_g:
        sex_local = st.selectbox("Geschlecht", ["Alle", "M", "F"], key="profile_sex")

    mask = dff['sport'] == sport
    if sex_local != "Alle":
        mask &= dff['sex'] == sex_local

    subset = dff[mask & (dff['hat_medaille'] == 'Medaille')]
    all_subset = dff[mask]

    if len(subset) < 5:
        st.warning(f"⚠️ Zu wenig Medaillengewinner für diese Auswahl (n={len(subset)})")
    else:
        metrics = {'Größe (m)': 'height', 'Gewicht (kg)': 'weight', 'BMI': 'bmi', 'Alter': 'age'}

        c1, c2, c3, c4 = st.columns(4)
        for col, (label, field) in zip([c1, c2, c3, c4], metrics.items()):
            med = subset[field].median()
            with col:
                st.metric(label, f"{med:.2f}", help=f"Median der Medaillengewinner in {sport}")

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        fig = make_subplots(rows=1, cols=4, subplot_titles=list(metrics.keys()))
        for i, (label, field) in enumerate(metrics.items(), 1):
            winners = subset[field].dropna()
            losers = all_subset[all_subset['hat_medaille'] == 'Keine Medaille'][field].dropna()

            fig.add_trace(go.Box(
                y=losers, name='Kein Medaille', showlegend=(i == 1),
                marker_color=GRAY, line_color='#555',
                boxmean=False, fillcolor='rgba(58,58,58,0.6)',
            ), row=1, col=i)
            fig.add_trace(go.Box(
                y=winners, name='Medaille', showlegend=(i == 1),
                marker_color=GOLD, line_color=GOLD,
                boxmean=False, fillcolor='rgba(201,168,76,0.4)',
            ), row=1, col=i)

        fig.update_layout(
            **PLOTLY_TEMPLATE['layout'],
            height=450,
            title=f"Verteilung: {sport} · Medaillengewinner vs. Rest",
            boxmode='group',
        )
        st.plotly_chart(fig, use_container_width=True)

        # Summary table
        st.markdown('<div class="section-header">STATISTIK-TABELLE</div>', unsafe_allow_html=True)
        rows = []
        for label, field in metrics.items():
            d = subset[field].dropna()
            rows.append({
                'Metrik': label,
                'Median': round(d.median(), 2),
                'Q25': round(d.quantile(0.25), 2),
                'Q75': round(d.quantile(0.75), 2),
                'Min': round(d.min(), 2),
                'Max': round(d.max(), 2),
                'n': len(d),
            })
        st.dataframe(pd.DataFrame(rows).set_index('Metrik'), use_container_width=True)


# ═══════════════════════════════════════════════════════════
# PAGE: KÖRPER & MEDAILLEN
# ═══════════════════════════════════════════════════════════
elif page == "⚖️ Körper & Medaillen":
    st.markdown('<div class="page-title">KÖRPER & MEDAILLENERFOLG</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Zusammenhang körperlicher Merkmale mit Medaillengewinn</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🎂 Alter", "📏 Größe", "⚖️ BMI"])

    def top15_diff(field, winner_label, loser_label):
        diff = dff.groupby(['sport', 'hat_medaille'])[field].median().unstack()
        diff.columns.name = None
        if 'Medaille' not in diff.columns or 'Keine Medaille' not in diff.columns:
            return pd.DataFrame(), pd.DataFrame()
        diff['differenz'] = diff['Medaille'] - diff['Keine Medaille']
        diff = diff.dropna()
        diff['abs_differenz'] = diff['differenz'].abs()
        diff = diff[diff['abs_differenz'] > 0]
        diff['gruppe'] = diff['differenz'].apply(lambda x: winner_label if x > 0 else loser_label)
        return diff.nlargest(15, 'abs_differenz'), diff

    with tab1:
        age_diff, _ = top15_diff('age', 'Gewinner älter', 'Gewinner jünger')
        if age_diff.empty:
            st.info("Nicht genug Daten.")
        else:
            top_sports = age_diff.index.tolist()
            df_plot = dff[dff['sport'].isin(top_sports)].copy()
            df_plot = df_plot.merge(age_diff[['gruppe']], on='sport')

            groups = df_plot['gruppe'].unique()
            colors_map = {'Medaille': GOLD, 'Keine Medaille': '#3A3A3A'}

            fig = go.Figure()
            for sport_name in top_sports:
                sub = df_plot[df_plot['sport'] == sport_name]
                for hue, col in colors_map.items():
                    d = sub[sub['hat_medaille'] == hue]['age'].dropna()
                    if len(d) == 0: continue
                    fig.add_trace(go.Box(
                        y=d, name=hue, x=[sport_name]*len(d),
                        marker_color=col, showlegend=(sport_name == top_sports[0]),
                        line_color=col, fillcolor=col.replace('#', 'rgba(').rstrip(')')+',0.4)',
                    ))
            fig.update_layout(
                **PLOTLY_TEMPLATE['layout'], height=500,
                title="Altersunterschied Gewinner vs. Nicht-Gewinner (Top 15 Sportarten)",
                xaxis_title="", yaxis_title="Alter",
                boxmode='group',
                xaxis=dict(tickangle=-45, gridcolor='#2a2a2a'),
            )
            st.plotly_chart(fig, use_container_width=True)

            st.markdown('<div class="section-header">RANKING NACH ALTERSDIFFERENZ</div>', unsafe_allow_html=True)
            display_df = age_diff[['Medaille', 'Keine Medaille', 'differenz', 'gruppe']].copy()
            display_df.columns = ['Median Gewinner', 'Median Verlierer', 'Differenz', 'Gruppe']
            display_df = display_df.round(2)
            st.dataframe(display_df, use_container_width=True)

    with tab2:
        height_diff, _ = top15_diff('height', 'Gewinner größer', 'Gewinner kleiner')
        if height_diff.empty:
            st.info("Nicht genug Daten.")
        else:
            top_sports_h = height_diff.index.tolist()
            df_plot_h = dff[dff['sport'].isin(top_sports_h)].copy()
            df_plot_h = df_plot_h.merge(height_diff[['gruppe']], on='sport')

            fig = go.Figure()
            for sport_name in top_sports_h:
                sub = df_plot_h[df_plot_h['sport'] == sport_name]
                for hue, col in {'Medaille': GOLD, 'Keine Medaille': '#3A3A3A'}.items():
                    d = sub[sub['hat_medaille'] == hue]['height'].dropna()
                    if len(d) == 0: continue
                    fig.add_trace(go.Box(
                        y=d, name=hue, x=[sport_name]*len(d),
                        marker_color=col, showlegend=(sport_name == top_sports_h[0]),
                        line_color=col,
                    ))
            fig.update_layout(
                **PLOTLY_TEMPLATE['layout'], height=500,
                title="Größenunterschied Gewinner vs. Nicht-Gewinner (Top 15 Sportarten)",
                xaxis_title="", yaxis_title="Größe (m)",
                boxmode='group',
                xaxis=dict(tickangle=-45, gridcolor='#2a2a2a'),
            )
            st.plotly_chart(fig, use_container_width=True)

    with tab3:
        bmi_diff, _ = top15_diff('bmi', 'Gewinner höherer BMI', 'Gewinner niedrigerer BMI')
        if bmi_diff.empty:
            st.info("Nicht genug Daten.")
        else:
            top_sports_b = bmi_diff.index.tolist()
            df_plot_b = dff[dff['sport'].isin(top_sports_b)].copy()
            df_plot_b = df_plot_b.merge(bmi_diff[['gruppe']], on='sport')

            fig = go.Figure()
            for sport_name in top_sports_b:
                sub = df_plot_b[df_plot_b['sport'] == sport_name]
                for hue, col in {'Medaille': GOLD, 'Keine Medaille': '#3A3A3A'}.items():
                    d = sub[sub['hat_medaille'] == hue]['bmi'].dropna()
                    if len(d) == 0: continue
                    fig.add_trace(go.Box(
                        y=d, name=hue, x=[sport_name]*len(d),
                        marker_color=col, showlegend=(sport_name == top_sports_b[0]),
                        line_color=col,
                    ))
            fig.update_layout(
                **PLOTLY_TEMPLATE['layout'], height=500,
                title="BMI-Unterschied Gewinner vs. Nicht-Gewinner (Top 15 Sportarten)",
                xaxis_title="", yaxis_title="BMI",
                boxmode='group',
                xaxis=dict(tickangle=-45, gridcolor='#2a2a2a'),
            )
            st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════════
# PAGE: GEOGRAFIE & GLEICHSTELLUNG
# ═══════════════════════════════════════════════════════════
elif page == "🌍 Geografie & Gleichstellung":
    st.markdown('<div class="page-title">GEOGRAFIE & GLEICHSTELLUNG</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Frauenanteil und Teilnahme nach Region</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📈 Frauenanteil Trend", "🗺️ Weltkarte", "🌐 Kontinente"])

    with tab1:
        gender_trend = (df.groupby(['year', 'sex']).size().unstack().fillna(0))
        gender_trend['frauenanteil'] = gender_trend['F'] / (gender_trend['F'] + gender_trend['M']) * 100

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=gender_trend.index, y=gender_trend['frauenanteil'],
            mode='lines+markers',
            line=dict(color=GOLD, width=3),
            marker=dict(size=6, color=GOLD),
            fill='tozeroy', fillcolor='rgba(201,168,76,0.1)',
            name='Frauenanteil',
        ))
        fig.add_hline(y=50, line_dash='dash', line_color='#6B6B6B', annotation_text='50% Parität',
                      annotation_font_color='#6B6B6B')
        fig.update_layout(
            **PLOTLY_TEMPLATE['layout'], height=420,
            title="Frauenanteil bei den Olympischen Spielen im Zeitverlauf",
            xaxis_title="Jahr", yaxis_title="Frauenanteil (%)",
            yaxis=dict(range=[0, 60], gridcolor='#2a2a2a'),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Männer vs. Frauen absolut
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=gender_trend.index, y=gender_trend['M'], name='Männer', marker_color='#4A90D9'))
        fig2.add_trace(go.Bar(x=gender_trend.index, y=gender_trend['F'], name='Frauen', marker_color=GOLD))
        fig2.update_layout(
            **PLOTLY_TEMPLATE['layout'], height=350,
            barmode='stack', title="Absolute Teilnehmerzahlen nach Geschlecht",
            xaxis_title="Jahr", yaxis_title="Athleten",
        )
        st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        latest_year = df['year'].max()
        gender_country = (df[df['year'] == latest_year]
                          .groupby(['noc', 'sex']).size().unstack(fill_value=0))
        gender_country['frauenanteil'] = gender_country['F'] / (gender_country['F'] + gender_country['M']) * 100
        gender_country = gender_country.reset_index()
        gender_country['iso3'] = gender_country['noc'].map(NOC_TO_ISO3)
        gender_country = gender_country.dropna(subset=['iso3'])
        gender_country['n'] = (gender_country.get('F', 0) + gender_country.get('M', 0)).astype(int)
        gender_country.loc[gender_country['n'] < 2, 'frauenanteil'] = None

        fig = go.Figure(go.Choropleth(
            locations=gender_country['iso3'],
            z=gender_country['frauenanteil'],
            customdata=np.stack([
                gender_country['noc'].values,
                gender_country['frauenanteil'].round(1).fillna(0).astype(str).values,
                gender_country['n'].astype(str).values,
            ], axis=-1),
            hovertemplate='<b>%{customdata[0]}</b><br>Frauenanteil: %{customdata[1]}%<br>Athleten: %{customdata[2]}<extra></extra>',
            colorscale=[[0, '#cc0000'], [0.5, '#ffff00'], [1, '#00cc44']],
            zmin=0, zmax=70,
            colorbar=dict(title=dict(text='Frauenanteil (%)', font=dict(color='white')), tickfont=dict(color='white')),
        ))
        fig.update_layout(
            **PLOTLY_TEMPLATE['layout'],
            title=f'Frauenanteil pro Land – Olympische Spiele {latest_year}',
            height=550,
            geo=dict(
                showframe=False, showcoastlines=True,
                projection_type='equirectangular',
                bgcolor='#111111', coastlinecolor='#333333',
                showocean=True, oceancolor='#111111',
                landcolor='#555555',
            ),
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        athletes_per_continent = (dff.groupby(['year', 'kontinent']).size()
                                  .reset_index(name='athleten').dropna())
        if athletes_per_continent.empty:
            st.info("Keine Kontinentdaten für diesen Filter.")
        else:
            fig = go.Figure()
            for kontinent in athletes_per_continent['kontinent'].unique():
                data = athletes_per_continent[athletes_per_continent['kontinent'] == kontinent].sort_values('year')
                fig.add_trace(go.Scatter(
                    x=data['year'], y=data['athleten'],
                    mode='lines+markers', name=kontinent,
                    line=dict(width=2), marker=dict(size=5),
                ))
            fig.update_layout(
                **PLOTLY_TEMPLATE['layout'], height=450,
                title='Olympia-Athleten nach Kontinent im Zeitverlauf',
                xaxis_title='Jahr', yaxis_title='Anzahl Athleten',
            )
            st.plotly_chart(fig, use_container_width=True)

            # Score per continent
            score_cont = (dff.groupby(['year', 'kontinent'])['punkte'].sum()
                          .reset_index(name='score').dropna())
            athletes_cont = athletes_per_continent.copy()
            df_score_cont = score_cont.merge(athletes_cont, on=['year', 'kontinent'])
            df_score_cont['score_pro_100'] = df_score_cont['score'] / df_score_cont['athleten'] * 100

            fig2 = go.Figure()
            for kontinent in df_score_cont['kontinent'].dropna().unique():
                data = df_score_cont[df_score_cont['kontinent'] == kontinent].sort_values('year')
                fig2.add_trace(go.Scatter(
                    x=data['year'], y=data['score_pro_100'],
                    mode='lines+markers', name=kontinent,
                    line=dict(width=2), marker=dict(size=5),
                ))
            fig2.update_layout(
                **PLOTLY_TEMPLATE['layout'], height=420,
                title='Performance Score pro 100 Athleten nach Kontinent',
                xaxis_title='Jahr', yaxis_title='Score / 100 Athleten',
            )
            st.plotly_chart(fig2, use_container_width=True)


# ═══════════════════════════════════════════════════════════
# PAGE: HEIMVORTEIL
# ═══════════════════════════════════════════════════════════
elif page == "🏠 Heimvorteil":
    st.markdown('<div class="page-title">HEIMVORTEIL</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Performance der Gastgeberländer vor, während und nach den Spielen</div>', unsafe_allow_html=True)

    medal_points = {'Gold': 3, 'Silver': 2, 'Bronze': 1}
    df_home_base = df.copy()
    df_home_base['punkte'] = df_home_base['medal'].map(medal_points).fillna(0)

    score_home = df_home_base.groupby(['year', 'noc'])['punkte'].sum().reset_index(name='score')
    athletes_home = df_home_base.groupby(['year', 'noc']).size().reset_index(name='athleten')
    df_home = score_home.merge(athletes_home, on=['year', 'noc'])
    df_home['score_pro_100'] = df_home['score'] / df_home['athleten'] * 100

    years_sorted = sorted(HOST_COUNTRIES.keys())
    results = []
    for year, noc in HOST_COUNTRIES.items():
        idx = years_sorted.index(year)
        prev_year = years_sorted[idx - 1] if idx > 0 else None
        next_year = years_sorted[idx + 1] if idx < len(years_sorted) - 1 else None

        for label, y in [('Vorherige Olympiade', prev_year), ('Als Gastgeber', year), ('Nächste Olympiade', next_year)]:
            if y is None:
                continue
            row = df_home[(df_home['noc'] == noc) & (df_home['year'] == y)]
            if len(row) > 0:
                results.append({'land': f"{noc} {year}", 'zeitpunkt': label, 'score_pro_100': row['score_pro_100'].values[0]})

    df_heimvorteil = pd.DataFrame(results)

    if df_heimvorteil.empty:
        st.info("Keine Daten verfügbar.")
    else:
        color_map = {'Vorherige Olympiade': '#6B6B6B', 'Als Gastgeber': GOLD, 'Nächste Olympiade': '#4A90D9'}
        fig = go.Figure()
        for label, color in color_map.items():
            subset_h = df_heimvorteil[df_heimvorteil['zeitpunkt'] == label]
            fig.add_trace(go.Bar(
                x=subset_h['land'], y=subset_h['score_pro_100'],
                name=label, marker_color=color, opacity=0.9,
            ))
        fig.update_layout(
            **PLOTLY_TEMPLATE['layout'], height=550,
            title='Heimvorteil: Performance Score vor, während und nach Ausrichtung',
            barmode='group', xaxis_title='', yaxis_title='Score pro 100 Athleten',
            xaxis=dict(tickangle=-45, gridcolor='#2a2a2a'),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Aggregierter Heimvorteil
        st.markdown('<div class="section-header">AGGREGIERTER HEIMVORTEIL</div>', unsafe_allow_html=True)
        pivot = df_heimvorteil.pivot_table(index='land', columns='zeitpunkt', values='score_pro_100')
        if 'Als Gastgeber' in pivot.columns and 'Vorherige Olympiade' in pivot.columns:
            pivot['heimvorteil'] = pivot['Als Gastgeber'] - pivot['Vorherige Olympiade']
            pivot = pivot.dropna(subset=['heimvorteil']).sort_values('heimvorteil', ascending=False)

            fig2 = go.Figure(go.Bar(
                x=pivot.index,
                y=pivot['heimvorteil'],
                marker=dict(
                    color=pivot['heimvorteil'],
                    colorscale=[[0, '#cc3300'], [0.5, '#333'], [1, GOLD]],
                    showscale=False,
                ),
            ))
            fig2.update_layout(
                **PLOTLY_TEMPLATE['layout'], height=380,
                title='Heimvorteil: Score-Differenz (Gastgeber – Vorherige Spiele)',
                xaxis=dict(tickangle=-45, gridcolor='#2a2a2a'),
                yaxis_title='Score-Differenz',
            )
            st.plotly_chart(fig2, use_container_width=True)

            avg_advantage = pivot['heimvorteil'].mean()
            positive_pct = (pivot['heimvorteil'] > 0).mean() * 100
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Ø Heimvorteil Score", f"{avg_advantage:+.1f}")
            with c2:
                st.metric("Länder mit positivem Effekt", f"{positive_pct:.0f}%")
            with c3:
                best = pivot['heimvorteil'].idxmax()
                st.metric("Stärkster Heimvorteil", best)
