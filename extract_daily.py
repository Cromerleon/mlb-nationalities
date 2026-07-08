import statsapi as stp
import sqlite3 as sql
from datetime import date as dt
from collections import Counter

hoy = dt.today().isoformat()

def obtain_team_players(team_id, team_name):

    team_players = []
    
    roster = stp.get('team_roster' , {'teamId' : team_id , 'season' : '2026'})
    
    for player in roster['roster']:
        player_id = player['person']['id']
        details = stp.get('person' , {'personId' : player_id})
        info = details['people'][0]
        
        anio_debut = None
        if info.get('mlbDebutDate'):
            anio_debut = int(info['mlbDebutDate'][:4])
        
        team_players.append({
            'player_id': player_id,
            'nombre': info.get('fullName'),
            'pais_nacimiento': info.get('birthCountry'),
            'ciudad_nacimiento': info.get('birthCity'),
            'anio_debut': anio_debut,
            'equipo_id': team_id,
            'equipo_nombre': team_name,
            'posicion': player['position']['name'],
            'activo': info.get('active')
            
            
        })
    return team_players

def obtain_teams():
    
    teams = stp.get('teams' , {'sportId' : 1})
    
    return teams['teams']

def save_players(players):
    
    conexion = sql.connect('mlb_nacionalidades.db')
    cursor = conexion.cursor()

    

    for p in players:
        cursor.execute('''
            INSERT OR REPLACE INTO jugadores 
            (player_id, nombre, pais_nacimiento, ciudad_nacimiento, anio_debut, 
            equipo_id, equipo_nombre, posicion, activo, fecha_actualizacion)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            p['player_id'], p['nombre'], p['pais_nacimiento'], p['ciudad_nacimiento'],
            p['anio_debut'], p['equipo_id'], p['equipo_nombre'], p['posicion'],
            p['activo'], hoy
        ))

    conexion.commit()
    conexion.close()
    print(f"{len(players)} jugadores guardados/actualizados")

def save_history(players):
    count_countries = Counter(p['pais_nacimiento'] for p in players)

    conexion = sql.connect('mlb_nacionalidades.db')
    cursor = conexion.cursor()

    cursor.execute('delete from historial_diario where fecha = ?', (hoy,))
    
    for country, count in count_countries.items():
        cursor.execute(''' 
            
            insert into historial_diario (fecha , pais_nacimiento, cantidad_jugadores)
            values(?,?,?)        
                    
                ''',(hoy, country, count))

    conexion.commit()
    conexion.close()

    print(f"Historial guardado para {len(count_countries)} paises, fecha {hoy}")

def main():
    print("Iniciando extracción diaria...")
    
    teams = obtain_teams()
    print(f"Equipos encontrados: {len(teams)}")
    
    all_players = []
    for team in teams:
        team_players = obtain_team_players(team['id'] ,  team['name'])
        all_players.extend(team_players)
    print(f"\nTotal recolectado: {len(all_players)} jugadores")
    save_players(all_players)
    save_history(all_players)
    
    print("Proceso completado.")

if __name__ == '__main__':
    main()