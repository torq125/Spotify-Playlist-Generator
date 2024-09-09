from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import spotipy
import SpotifyAPI
import json

def fetch_playlists(sP):

    # This function get the users playlist and returns a list of dictionary with the playlist id and name

    json_data = sP.current_user_playlists()
    playlists = []

    for item in json_data['items']:
        playlists.append({'id':item['id'], 'name':item['name']})
        
    return playlists

def generate_recommendation(playlist_id, sP, number_of_recommendations=10):

    user_playlist_vecotor = SpotifyAPI.generate_playlist_vector(playlist_id, sP)
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

# for debugging this file only
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