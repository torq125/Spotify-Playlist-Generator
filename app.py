from flask import Flask, render_template, redirect, url_for, request, session, jsonify
import recommendations as r
from spotipy.oauth2 import SpotifyOAuth
import spotipy
import time

app = Flask(__name__)
app.secret_key = '6338313224e06a8f7007fa12'

CLIENT_ID = "9e58a90985b5456097e313ae15f18c3a"
CLIENT_SECRET = "6b59e20e226f4de59da184d96ea89180"
SCOPE = "user-library-read user-read-recently-played user-top-read user-follow-read playlist-read-collaborative playlist-read-private playlist-modify-public playlist-modify-private user-read-private user-read-email"

TOKEN_INFO = ""

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/login")
def connectSpotify():
    auth_url = create_spotify_oauth().get_authorize_url()
    return redirect(auth_url)

@app.route("/redirect")
def redirect_page():
    session.clear()
    auth_code = request.args.get('code')
    token_info = create_spotify_oauth().get_access_token(code=auth_code)
    session['TOKEN_INFO'] = token_info
    return redirect(url_for("get_playlists", external=True))

@app.route("/user-playlists", methods = ['GET', 'POST'])
def get_playlists():
    try:
        token_info = get_token()
        sp = spotipy.Spotify(auth=token_info['access_token'])
        playlists = r.fetch_playlists(sp)
        return render_template('index.html', playlist_names=playlists)
    except Exception as e:
        print(f"User Not Logged In! Error {e}")
        return redirect(url_for('index'))
    
@app.route("/get-recommendations", methods=['POST', 'GET'])
def get_recommendations():
    try:
        response = request.get_json()
        ids = r.generate_recommendation(response['id']).tolist()
            # print("Type:-", type(recommendations))
            # print(recommendations)
        token_info = get_token()
        sp = spotipy.Spotify(auth=token_info['access_token'])
        recommended_tracks = [{'track_uri': track['uri'], 'name': track['name']} for track in sp.tracks(tracks=ids)['tracks']]
        # print(recommended_tracks)
        return jsonify({"tracks": recommended_tracks})    

    except Exception as e:
        print(f"Unable to generate recommendations. Error:-{e}")
        return jsonify({"error": "Unable to generate recommendations."}), 500

@app.route("/save-playlist", methods=['GET', 'POST'])
def save_playlist():
    try:
        response = request.get_json()
        # print(response)
        token_info = get_token()
        sp = spotipy.Spotify(auth=token_info['access_token'])
        username = sp.current_user()['id']
        # print("username:-", username)
        # print('token:-', token_info['access_token'])

        # playlist created
        playlist_id = sp.user_playlist_create(user=username, name=response['name'], description="From Python!")['id']
        
        # adding songs to the playlist using the track_uris
        sp.playlist_add_items(playlist_id=playlist_id, items=response['track_uris'])
        print("Task Done!")

        return jsonify({"Status": "ok"}), 200
    except Exception as e:
        print(f"Unable to generate recommendations. Error:-{e}")
        return jsonify({"error": "Unable to generate recommendations."}), 500

def get_token():
    token_info = session['TOKEN_INFO']
    if not token_info:
        return redirect(url_for("index", external=True))

    current_time = int(time.time())

    is_expired = token_info['expires_at'] - current_time <= 60
    if is_expired:
        spotify_auth = create_spotify_oauth()
        token_info = spotify_auth.refresh_access_token(token_info['refresh_token'])
        #print(token_info)
    return token_info

def create_spotify_oauth():
    return SpotifyOAuth(client_id=CLIENT_ID,
                        client_secret=CLIENT_SECRET,
                        scope = SCOPE,
                        redirect_uri=url_for('redirect_page', _external=True),
                        show_dialog=True)

if __name__ == "__main__":
    app.debug = True
    app.run()