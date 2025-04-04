import requests
from bs4 import BeautifulSoup
import re
import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
load_dotenv()

date = input("Which year would you like to travel to? Type the data in this format YYYY-MM-DD: ")
billboard_url = "https://www.billboard.com/charts/hot-100/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
}
response = requests.get(url=f"{billboard_url}{date}", headers=headers)
soup = BeautifulSoup(response.text,"html.parser")

# Method one for getting song titles
# songs = [song.getText().strip() for song in soup.find_all("h3", class_="c-title a-no-trucate a-font-primary-bold-s u-letter-spacing-0021 lrv-u-font-size-18@tablet lrv-u-font-size-16 u-line-height-125 u-line-height-normal@mobile-max a-truncate-ellipsis u-max-width-330 u-max-width-230@tablet-only")]

# Method 2: A better method to ensure you get all the songs
song_names_spans = soup.select("li ul li h3")
song_names = [song.getText().strip() for song in song_names_spans]
artist_name_spans = soup.select("li ul li span.c-label.a-no-trucate")
artist_names = [song.getText().strip() for song in artist_name_spans]

# Sample code of how the songs list would look like if you used a for loop instead of list comprehension
# for index in range(len(song_names)):
#     title = f"{song_names[index]} - {artist_names[index]}"
#     songs.append(title)

songs_full_title = [f"{song_names[index]} - {artist_names[index]}" for index in range(len(song_names))]

# Function to remove "Featuring ..." or "Feat. ..." parts
def clean_song_title(title):
    return re.sub(r' Featuring .*', '', title, flags=re.IGNORECASE).strip()

# Process all song titles
cleaned_songs = [clean_song_title(song) for song in songs_full_title]
print(cleaned_songs)

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=os.getenv("CLIENT_ID"),
                                               client_secret=os.getenv("CLIENT_SECRET"),
                                               redirect_uri=os.getenv("URI"),
                                               scope="playlist-modify-private",
                                               show_dialog=True,
                                               cache_path="token.txt",
                                               username=os.getenv("DISPLAY_NAME")
                                               )
                     )

# # To check if all the song titles were found.
# data = []
# for track in cleaned_songs:
#     query = f"track:{track}"
#     results = sp.search(q=query, type="track", limit=1)
#     if results["tracks"]["items"]:
#         track_details = results["tracks"]["items"][0]
#         track_name = track_details["name"]
#         artist = track_details["artists"][0]["name"]
#         spotify_uri = track_details["uri"]
#         data.append(f"{track_name} : {artist} : {spotify_uri}")
#     else:
#         print(f"No Spotify URI found for {track}.")
#         continue
#
# print(len(data))


uri_list = []

for track in cleaned_songs:
    query = f"track:{track}"
    results = sp.search(q=query, type="track", limit=1)
    if results["tracks"]["items"]:
        track_details = results["tracks"]["items"][0]
        spotify_uri = track_details["uri"]
        uri_list.append(spotify_uri)
    else:
        print(f"No Spotify URI found for {track}.")
        continue

# print(uri_list)

# To get a list of all your playlists
# playlists = sp.user_playlists(user=os.getenv("USER_ID"), limit=10, offset=0)

billboard_playlist = sp.user_playlist_create(os.getenv("USER_ID"), name= f"{date} billboard top 100", public=False, description=f" Throwback to {date} billboards top 100")
billboard_playlist_id = billboard_playlist["id"]
sp.user_playlist_add_tracks(user=os.getenv("USER_ID"), playlist_id=billboard_playlist_id, tracks=uri_list)
print(f"Your playlist has been created, we managed to find a total of {len(uri_list)}/100 of the top 100 songs! ")