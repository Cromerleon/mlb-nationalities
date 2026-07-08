import streamlit as st
import pandas as pd
import sqlite3 as sql
from datetime import date as dt

today = dt.today().isoformat
st.set_page_config(page_title="MLB - Jugadores por Nacionalidad" , layout="wide")

if 'tab_activa' not in st.session_state:
    st.session_state.tab_activa = "Menú Principal"


st.session_state.tab_activa = st.radio("Navegación" , ["Menu Principal" , "Nacionalidad Por Equipos"] , horizontal=True, label_visibility="collapsed")

connection = sql.connect('mlb_nacionalidades.db')
df_players = pd.read_sql_query('select * from jugadores' , connection)
connection.close()

if st.session_state.tab_activa == "Menu Principal":

    st.title("Jugadores de MLB por Nacionalidad")
    st.caption("Datos actualizados automaticamente cada día desde la MLB Stats API de los Rosters Activos (26 Man Roster)")


    st.metric("Total de jugadores activos", len(df_players))
    st.metric("Ultima actualización:" , df_players['fecha_actualizacion'].max())

    st.subheader("Jugadores por país")
    count = df_players['pais_nacimiento'].value_counts().reset_index()
    count.columns = ['País' , 'Cantidad de Jugadores']

    st.dataframe(count, use_container_width=True, hide_index=True)


elif st.session_state.tab_activa == "Nacionalidad Por Equipos":
    st.subheader("Jugadores por equipo y país")
    
    selected_team = st.selectbox("Selecciona un equipo: ",sorted(df_players['equipo_nombre'].unique()))
    
    df_team = df_players[df_players['equipo_nombre'] == selected_team]
    count_team = df_team['pais_nacimiento'].value_counts().reset_index()
    count_team.columns = ['País' , "Cantidad Jugadores"]
    

    selection = st.dataframe(
        
        count_team,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row"
        
    )
    
    if selection.selection.rows:
        selected_row = selection.selection.rows[0]
        selected_country = count_team.iloc[selected_row]['País']
        
        st.subheader(f"Jugadores de {selected_team} nacidos en {selected_country}")
        
        filtered_players = df_team[df_team['pais_nacimiento'] == selected_country][
            ['nombre', 'posicion', 'ciudad_nacimiento', 'anio_debut']
        ]
        
        filtered_players.columns = ['Nombre' , 'Posición','Ciudad','Año de Debut']
        
        st.dataframe(filtered_players, use_container_width=True, hide_index=True)