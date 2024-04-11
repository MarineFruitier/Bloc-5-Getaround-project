import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go


### Config
st.set_page_config(
    page_title="Dashboard Getaround",
    page_icon="🚗",
    layout="wide"
)

# Introduction du Dashboard
st.markdown("""
# Analyse des retards de restitution chez Getaround

L'objectif de ce dashboard est d'analyser les retards de restitution des véhicules loués, en répondant via des visualisations à des questions telles que :

- **À quelle fréquence les conducteurs sont-ils en retard pour le prochain check-in ?** Quel est l'impact sur la réservation suivante ? Cela est-il en lien avec les annulations ?**
- **Comment se répartissent les retards entre les différents types de check-in ?**

Nous explorerons également une nouvelle fonctionnalité : **un seuil de temps minimum entre deux locations pour éviter les retards.**

Ce tableau de bord vise à fournir des données et des analyses qui aideront l'équipe de gestion de produit à prendre des décisions éclairées concernant l'implémentation de cette nouvelle fonctionnalité, tout en trouvant le juste équilibre entre la réduction des frictions liées aux retards de restitution et la maximisation des revenus pour Getaround et ses propriétaires de véhicules.
""", unsafe_allow_html=True)


# Fonctions pour charger et préparer les données
@st.cache_data
def load_data():
    df_delay = pd.read_csv('data_delay.csv')
    return df_delay

df_delay = load_data().copy()

# Début de l'application Streamlit
st.title("Getaround Dashboard 🚗")

# Ajout d'une case à cocher pour les données brutes
if st.checkbox('Afficher les données brutes'):
    st.subheader('Données Brutes')
    st.write(df_delay)

# Statistiques descriptives
st.header('Statistiques Descriptives')
col1, col2 = st.columns(2)

with col1:
    st.write("Statistiques descriptives pour df_delay:")
    st.dataframe(df_delay.describe())

with col2:
    st.write('Pourcentage de valeurs manquantes pour df_delay')
    missing_values = 100 * df_delay.isnull().sum() / df_delay.shape[0]
    st.dataframe(missing_values)


df_delay_filtered = df_delay[df_delay['delay_at_checkout_in_minutes'].between(-240, 240)]

# Création du boxplot avec Plotly
fig = go.Figure()
fig.add_trace(go.Box(y=df_delay_filtered['delay_at_checkout_in_minutes'], name='Retards'))

# Mise à jour des titres et de la mise en page
fig.update_layout(
    title="Distribution des retards au check-Out",
    yaxis_title="Retard au check-Out (minutes)",
    xaxis=dict(showgrid=False, showticklabels=False), 
    plot_bgcolor='white', 
    showlegend=False 
)

# Afficher le graphique 
st.plotly_chart(fig)

# Proportion de locations annulées par type de check-in
st.header("Proportion des locations annulées par type de Check-In")
fig_sunburst = px.sunburst(df_delay, path=['state', 'checkin_type'],
                           title="Proportion de locations annulées par type de Check-In")
st.plotly_chart(fig_sunburst)

# Relation entre le retard au check-out et le temps jusqu'au prochain check-in
st.header("Relation entre le retard au check-Out et le temps jusqu'au prochain Check-In")
fig_scatter = px.scatter(df_delay, x='delay_at_checkout_in_minutes', y='time_delta_with_previous_rental_in_minutes',
                         title="Relation entre le retard au Check-Out et le temps jusqu'au prochain Check-In",
                         labels={'delay_at_checkout_in_minutes': 'Retard au Check-Out (minutes)',
                                 'time_delta_with_previous_rental_in_minutes': 'Temps jusqu\'au prochain Check-In (minutes)'},
                         trendline="ols")
st.plotly_chart(fig_scatter)

st.header("Pourcentage de retards par type de Check-In")
col1, col2 = st.columns(2)

with col1:

    late_checkins_mobile = df_delay[(df_delay['checkin_type'] == 'mobile') & (df_delay['delay_at_checkout_in_minutes'] > 0)].shape[0]
    total_checkins_mobile = df_delay[df_delay['checkin_type'] == 'mobile'].shape[0]
    Late_perc_mobile = (late_checkins_mobile / total_checkins_mobile * 100) if total_checkins_mobile > 0 else 0

    late_checkins_connect = df_delay[(df_delay['checkin_type'] == 'connect') & (df_delay['delay_at_checkout_in_minutes'] > 0)].shape[0]
    total_checkins_connect = df_delay[df_delay['checkin_type'] == 'connect'].shape[0]
    Late_perc_connect = (late_checkins_connect / total_checkins_connect * 100) if total_checkins_connect > 0 else 0

    # Graphique de pourcentage de retard par type de check-in
    df_delay_with_late_checkouts = df_delay[df_delay['delay_at_checkout_in_minutes'] > 0]
    avg_delay_by_checkin_type = df_delay_with_late_checkouts.groupby('checkin_type')['delay_at_checkout_in_minutes'].mean().reset_index()
   
    fig_retard_pourcentage = go.Figure(data=[
        go.Bar(name='Mobile', x=['Check-in Mobile'], y=[Late_perc_mobile]),
        go.Bar(name='Connecté', x=['Check-in Connecté'], y=[Late_perc_connect])
    ])
    fig_retard_pourcentage.update_layout(title='Pourcentage de retard par type de check-in')
    st.plotly_chart(fig_retard_pourcentage)

with col2:

    df_delay_with_late_checkouts = df_delay[df_delay['delay_at_checkout_in_minutes'] > 0]
    avg_delay_by_checkin_type = df_delay_with_late_checkouts.groupby('checkin_type')['delay_at_checkout_in_minutes'].mean().reset_index()
    
    # Graphique de délai moyen du retard par type de check-in
    color_map = {
        'mobile': px.colors.qualitative.Set2[0],
        'connecté': px.colors.qualitative.Set2[1]
    }
    
    fig_delay_moyen = px.bar(avg_delay_by_checkin_type, x='checkin_type', y='delay_at_checkout_in_minutes',
                             labels={'checkin_type': 'Type de Check-in', 'delay_at_checkout_in_minutes': 'Retard moyen au check-out (minutes)'},
                             title="Retard moyen au check-out par type de check-in",
                             color='checkin_type', color_discrete_map=color_map)
    
    fig_delay_moyen.update_layout(xaxis_title="Type de Check-in", yaxis_title="Retard moyen (minutes)", plot_bgcolor="white")
    st.plotly_chart(fig_delay_moyen)


# Analyse d'impact des retards sur les locations suivantes
st.header("Impact des retards de check-Out sur les locations suivantes")
col5, col6 = st.columns([3, 1])

with col5:
    
 df_loc_consecutive = pd.merge(df_delay, df_delay, how='inner', left_on='previous_ended_rental_id', right_on='rental_id', suffixes=('', '_prev'))
 df_loc_consecutive = df_loc_consecutive.rename(columns={
    'delay_at_checkout_in_minutes': 'current_delay',
    'delay_at_checkout_in_minutes_prev': 'previous_delay',
    'checkin_type': 'current_checkin_type',
    'checkin_type_prev': 'previous_checkin_type',
    'state': 'current_state',
    'state_prev': 'previous_state'
})
 df_loc_consecutive['real_delay_between_loc_in_min'] = df_loc_consecutive['time_delta_with_previous_rental_in_minutes'] - df_loc_consecutive['previous_delay']

 # Calcul des locations impactées et des proportions
 df_impacted_loc = df_loc_consecutive[df_loc_consecutive['real_delay_between_loc_in_min'] < 0]
 df_impacted_canceled_loc = df_impacted_loc[df_impacted_loc['current_state'] == 'canceled']
 df_non_impacted_loc = df_loc_consecutive[df_loc_consecutive['real_delay_between_loc_in_min'] >= 0]
 total_cancel = len(df_loc_consecutive[df_loc_consecutive['current_state'] == 'canceled'])
 no_late_cancel = len(df_non_impacted_loc[df_non_impacted_loc['current_state'] == 'canceled'])

perc_cancellations_no_apparent_reason = (no_late_cancel / len(df_non_impacted_loc)) * 100 if len(df_non_impacted_loc) > 0 else 0
perc_cancellations_when_late = (len(df_impacted_canceled_loc) / len(df_impacted_loc)) * 100 if len(df_impacted_loc) > 0 else 0

proportion_annulations_due_to_delay = (len(df_impacted_canceled_loc) / total_cancel) * 100
proportion_annulations_other_reasons = ((total_cancel - len(df_impacted_canceled_loc)) / total_cancel) * 100

# Création du graphique 
labels = ['Annulations pour autres raisons', 'Annulations suite à du retard']
values = [proportion_annulations_other_reasons, proportion_annulations_due_to_delay]

fig = go.Figure(data=[go.Pie(labels=labels, values=values, pull=[0, 0.2])])
fig.update_traces(textinfo='percent+label')
fig.update_layout(title_text="Proportion des locations annulées : Générales vs. Suite à des retards")

st.plotly_chart(fig)

with col6:
   
    st.subheader("Chiffres Clés")
    st.write(f"Nombre de locations impactées: {len(df_impacted_loc)}")
    st.write(f"Nombre de locations annulées présentant un retard: {len(df_impacted_canceled_loc)}")
    st.write(f"Pourcentage d'annulations sans raisons apparentes: {perc_cancellations_no_apparent_reason:.2f}%")
    st.write(f"Pourcentage de locations annulées lors de retard: {perc_cancellations_when_late:.2f}%")

# Analyse de l'impact des retards de check-out sur les check-in suivants
st.header("Analyse de l'impact des retards de Check-Out sur les Check-In suivants")

df_delay['late_checkin'] = (df_delay['delay_at_checkout_in_minutes'] > df_delay['time_delta_with_previous_rental_in_minutes']).astype(int)
df_delay['late_checkin_text'] = df_delay['late_checkin'].map({1: 'Impact du retard précédent', 0: 'Sans impact du retard précédent'})
df_delay['checkin_type'] = df_delay['checkin_type'].fillna('Inconnu')
grouped_data = df_delay.groupby(['late_checkin_text', 'checkin_type'], as_index=False).size()
grouped_data = grouped_data.rename(columns={'size': 'Nombre de Check-Ins'})
grouped_data['category'] = grouped_data['late_checkin_text'] + " - " + grouped_data['checkin_type']

    
# Graphique des proportions de retards de check-out impactant les check-in
st.subheader("Proportion de Check-In tardifs selon le type de check-In")

custom_colors = {
    'Impact du retard précédent - mobile': 'red',
    'Impact du retard précédent - connecté': 'darkorange',
    'Sans impact du retard précédent - mobile': 'lightblue',
    'Sans impact du retard précédent - connecté': 'lightgreen'}

    
fig_late_checkin = px.pie(grouped_data, names='category', values='Nombre de Check-Ins',
                          title="",
                          color='category',
                          color_discrete_map=custom_colors)


st.plotly_chart(fig_late_checkin)


# Section de simulation de seuil 
# Définition de la fonction de seuil 
def simulate_threshold(max_threshold, df_loc_consecutive):
    late_avoided = []
    thresholds = list(range(0, max_threshold, 20))  
    for threshold in thresholds:
        adjusted_time_deltas = df_loc_consecutive['time_delta_with_previous_rental_in_minutes'].apply(lambda x: max(x, threshold))
        adjusted_real_delay = adjusted_time_deltas - df_loc_consecutive['previous_delay']
        late_avoided_count = (adjusted_real_delay >= 0).sum()
        late_avoided.append(late_avoided_count)
    return late_avoided, thresholds

# Visualisation des retards
st.subheader("Distribution des retards impactant les locations suivantes")

df_loc_consecutive['Canceled'] = df_loc_consecutive['current_state'].apply(lambda x: 'Annulée' if x == 'canceled' else 'Non annulée')

# Filtrer 
df_filtered = df_loc_consecutive[df_loc_consecutive['real_delay_between_loc_in_min'].between(-300, 0)]

# Création du graphique 
fig = px.histogram(df_filtered, x='real_delay_between_loc_in_min', color='Canceled',
                   barmode='group',
                   title="Distribution des retards",
                   labels={'real_delay_between_loc_in_min': 'Délai jusqu’à la prochaine location (minutes)'})

fig.update_layout(xaxis_title='Délai jusqu’à la prochaine location (minutes)',
                  yaxis_title='Nombre de locations',
                  legend_title="État de la Location",
                  legend=dict(orientation='h', yanchor='bottom', y=-0.25, xanchor='center', x=0.5))

st.plotly_chart(fig)

# Seuil  de retard pour éviter d'impacter la location suivante 

st.header("Simulation de seuil pour éviter les retards impactant les Locations suivantes")
late_avoided, thresholds = simulate_threshold(400, df_loc_consecutive)
fig_seuil_impact = px.line(x=thresholds, y=late_avoided, labels={'x':'Valeur du Seuil (min)', 'y':'Retards évités'},
                           title='Impact du seuil sur les retards évités')
fig_seuil_impact.update_traces(mode='lines+markers')
fig_seuil_impact.update_layout(title={'y':0.9, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'})
st.plotly_chart(fig_seuil_impact)

# Seuil idéal recommandé 180
st.markdown("""
    <style>
    .big-font {
        font-size:20px !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="big-font">Le seuil de délai idéal pour éviter l\'impact des prochaines locations semble se situer entre 160 et 200 minutes. Nous conseillons donc un seuil de 180 minutes.</p>', unsafe_allow_html=True)


# Message de remerciement (en gras)
st.markdown("""
    <style>
    .center-text {
        text-align: center;
        font-size:22px !important;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="center-text">Merci pour votre visite !</p>', unsafe_allow_html=True)
