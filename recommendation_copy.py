from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import SpotifyAPI
import json

#setting up Spotify API
client_id = '9e58a90985b5456097e313ae15f18c3a'
client_secret = '6b59e20e226f4de59da184d96ea89180'

scope = 'user-library-read user-read-recently-played user-top-read user-follow-read playlist-read-collaborative playlist-read-private'

auth_manager = SpotifyOAuth(client_id=client_id, client_secret=client_secret,
                                                       scope = scope,
                                                       redirect_uri='https://localhost:8888/callback')
sp = spotipy.Spotify(auth_manager=auth_manager)

def fetch_playlists():

    # This function get the users playlist and returns a list of dictionary with the playlist id and name

    json_data = sp.current_user_playlists()
    playlists = []

    for item in json_data['items']:
        playlists.append({'id':item['id'], 'name':item['name']})
        
    return playlists

def generate_recommendation(playlist_id, number_of_recommendations=10):

    user_playlist_vecotor = SpotifyAPI.generate_playlist_vector(playlist_id)
    songs_df = pd.read_csv(r'Kaggle Dataset 1M Spotify Songs\dataset.csv')
    normalized_songs_df = pd.read_csv(r'Kaggle Dataset 1M Spotify Songs\Normalized Dataset.csv')

    #except track_id in normalized_songs_df

    cs = cosine_similarity(user_playlist_vecotor, normalized_songs_df[normalized_songs_df.columns[2:]])
    cs = cs.flatten()
    normalized_songs_df['cosine_similarity'] = cs

    recommendation_df = normalized_songs_df.sort_values(by="cosine_similarity", ascending=False)
    recommendations = recommendation_df.head(number_of_recommendations)

    recommendations_index = recommendations.index.tolist()
    return songs_df.loc[recommendations_index]['track_id']

def main():
    playlists = fetch_playlists()
    for i in playlists:
        print(i['name'])

    selected_playlist = input("Enter the name of the playlist:-")
    for playlist in playlists:
        if playlist['name'] == selected_playlist:
            recommendations_id = generate_recommendation(playlist['id'], 20)
            break
    
    print(recommendations_id[0:4])

if __name__ == '__main__':
    main()