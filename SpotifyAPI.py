import spotipy
from spotipy.oauth2 import SpotifyOAuth
from sklearn.preprocessing import StandardScaler
import pandas as pd

#setting up Spotify API
client_id = '9e58a90985b5456097e313ae15f18c3a'
client_secret = '6b59e20e226f4de59da184d96ea89180'

scope = 'user-library-read user-read-recently-played user-top-read user-follow-read playlist-read-collaborative playlist-read-private'

auth_manager = SpotifyOAuth(client_id=client_id, client_secret=client_secret,
                                                       scope = scope,
                                                       redirect_uri='https://localhost:8888/callback')
sp = spotipy.Spotify(auth_manager=auth_manager)

def get_song_features(song_ids):

    # This function returns the audio_features of the tracks present in the playlist.

    # The function takes a list of track_id and processes it in batches and returns a list of dictionary along with track_id and track_name
    # which contains the tracks audio features

    songs_data = []

    batch_size = 50
    current_id = 0
    while current_id < len(song_ids):
        batch_start = current_id
        batch_end = min(len(song_ids), current_id + batch_size)

        features_data = sp.audio_features(tracks=[d['track_id'] for d in song_ids[batch_start:batch_end]])

        for features in features_data:
            features_to_extract = [ 'danceability', 'energy', 'key', 'loudness', 'speechiness',
                                    'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'time_signature' ]
            extracted_features = {feature: features[feature] for feature in features_to_extract}
            songs_data.append(extracted_features)


        current_id+=batch_size

    for id, features in zip(song_ids, songs_data):
        features.update(id)

    #print(songs_data[0])

    return songs_data

def generate_playlist_vector(playlist_id):

    # This function returns a playlist vector of the playlist selected by the user

    # The function normalizes the values and returns a normalized playlist vector

    #Getting the list of songs in the playlist
    playlist_vector = []
    playlist_data = sp.playlist_items(playlist_id=playlist_id)

    #Getting the track_id and track_name of the songs in the playlist
    song_ids = []
    for song in playlist_data['items']:
        song_ids.append({'track_id':song['track']['id'], 'track_name':song['track']['name']})

    #Getting the audio features of the songs on the playlist
    songs_data = get_song_features(song_ids)

    """for song in songs_data:
        print(song)
        break"""

    #normalizing the song_features values and summing the values to get a playlist vector which is normalized
    
    songs_data_df = pd.DataFrame(songs_data)
    exclude_columns = ['track_id', 'track_name']

    normalize_columns = [col for col in songs_data_df.columns if col not in exclude_columns]

    data_to_normalize = songs_data_df.drop(columns=exclude_columns)

    scaler = StandardScaler()
    normalize_data = scaler.fit_transform(data_to_normalize)

    normalized_songs_data_df = pd.DataFrame(normalize_data, columns=normalize_columns)

    # The sum function uses the columns as index values which causes different shape problems between the playlist
    # vector and the songs dataset

    playlist_vector = pd.DataFrame(normalized_songs_data_df.sum())
    normalized_playlist_vector = scaler.fit_transform(playlist_vector)
    
    # performing Transpose on playlist_vector so the shape of the playlist vector and the songs dataset is same
    # i.e. same no of columns

    return normalized_playlist_vector.T     #returning a tranposed vector

# def get_playlist_vector():
#     playlists = fetch_playlists()
#     for name in playlists:
#             print(name)
#             #print(name.encode('utf-8', errors='replace').decode('utf-8'))


#     select_playlist = input("Enter the Name:-")
#     for playlist in playlists:
#         if playlist['name'] == select_playlist:
#             print("User Vector Playlist:-\n", generate_playlist_vector(playlist['id']))
#             #user_playlist_vector = user_playlist_vector(playlist['id'])

if __name__ == "__main__":
    print("HI!")
