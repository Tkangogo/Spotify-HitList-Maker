# Spotify-HitList-Maker

## Overview
This Python program creates a Spotify playlist based on the Billboard Hot 100 chart for a user-specified date. It scrapes song data from Billboard's website, searches for the songs on Spotify, and compiles them into a new playlist in the user's Spotify account.

## Features
- Scrapes the **Billboard Hot 100** chart for a given date.
- Searches for the scraped songs on **Spotify**.
- Creates a **private playlist** in the user's Spotify account.
- Adds the found songs to the playlist.
- Provides a summary of how many songs were successfully added.

## Prerequisites
Before running the script, ensure you have the following:
- Python installed (>=3.7 recommended).
- A **Spotify Developer Account** and an application set up in the **Spotify Developer Dashboard**.
- A **Billboard Hot 100** chart URL (handled automatically in the script).
- An `.env` file containing your **Spotify API credentials**:
  ```ini
  CLIENT_ID=your_spotify_client_id
  CLIENT_SECRET=your_spotify_client_secret
  URI=http://example.com
  USER_ID=your_spotify_user_id
  DISPLAY_NAME=your_spotify_display_name
  ```

## Installation
1. **Clone the repository:**
   ```sh
   git clone https://github.com/your-repository/spotify-hitlist-maker.git
   cd spotify-hitlist-maker
   ```
2. **Create a virtual environment (optional but recommended):**
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
3. **Install the required dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

## How It Works
### Step 1: User Inputs a Date
The program prompts the user to enter a date in `YYYY-MM-DD` format:
```sh
Which year would you like to travel to? Type the date in this format YYYY-MM-DD:
```
The entered date is used to access the Billboard Hot 100 chart from that time.

### Step 2: Scraping Billboard Hot 100 Data
The script fetches the Billboard Hot 100 page for the provided date using `requests` and extracts song titles and artist names using `BeautifulSoup`.
```python
response = requests.get(url=f"https://www.billboard.com/charts/hot-100/{date}", headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

song_names_spans = soup.select("li ul li h3")
song_names = [song.getText().strip() for song in song_names_spans]
artist_name_spans = soup.select("li ul li span.c-label.a-no-trucate")
artist_names = [song.getText().strip() for song in artist_name_spans]
```

### Step 3: Cleaning the Song Titles
A function removes unnecessary text like "Featuring..." from the titles to improve search accuracy on Spotify.
```python
def clean_song_title(title):
    return re.sub(r' Featuring .*', '', title, flags=re.IGNORECASE).strip()
cleaned_songs = [clean_song_title(song) for song in songs_full_title]
```

### Step 4: Connecting to Spotify
The program uses the `Spotipy` library and OAuth authentication to access the Spotify API and search for songs.
```python
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
    redirect_uri=os.getenv("URI"),
    scope="playlist-modify-private",
    show_dialog=True,
    cache_path="token.txt",
    username=os.getenv("DISPLAY_NAME")
))
```

### Step 5: Searching for Songs on Spotify
For each cleaned song title, the program searches for it on Spotify and retrieves the song's **Spotify URI**.
```python
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
```

### Step 6: Creating a Spotify Playlist
A new private playlist is created with the selected Billboard date as its name.
```python
billboard_playlist = sp.user_playlist_create(
    os.getenv("USER_ID"),
    name=f"{date} Billboard Top 100",
    public=False,
    description=f"Throwback to {date} Billboard's Top 100"
)
```

### Step 7: Adding Songs to the Playlist
The found song URIs are added to the new playlist.
```python
sp.user_playlist_add_tracks(user=os.getenv("USER_ID"), playlist_id=billboard_playlist["id"], tracks=uri_list)
print(f"Your playlist has been created, we managed to find a total of {len(uri_list)}/100 of the top 100 songs!")
```

## Running the Script
To execute the program, simply run:
```sh
python hitlist_maker.py
```
Follow the prompts to enter a date, and the program will generate your playlist automatically.

## Notes
- Some songs may not be found on Spotify, so the program might not fetch all 100 songs.
- Ensure your `.env` file is correctly configured with your Spotify credentials.

## License
This project is licensed under the MIT License.

