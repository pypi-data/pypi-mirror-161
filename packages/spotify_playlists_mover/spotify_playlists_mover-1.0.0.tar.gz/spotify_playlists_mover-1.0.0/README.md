# SpotifyPlaylistsMover

This will transfer all your Spotify playlists and saved tracks to a new account

**IMPORTANT: IF YOU WANT TO USE THIS PROGRAM YOU HAVE TO GET YOUR [CLIENT ID](#how-to-get-a-client-id)**

**IMPORTANT 2**: AS OF 30 JULY 2022 "[Spotipy](http://spotipy.readthedocs.org/)" LIBRARY HAS AN ERROR, IF THIS PROGRAM IS NOT WORKING FOR YOU, TRY ADDING:
```python
if (isinstance(id,dict)) and ('uri' in id) and (id['uri']):
  id = id['uri']
```
AT THE BEGINNING OF THE `client.Spotify#_get_id` FUNCTION.
I HAVE ALREADY SUBMITTED A PULL REQUEST TO THE PROJECT: plamere/Spotipy#840.


## How to use

1. Run `pip install spotify_playlist_mover`
2. Set your client ID as environment variable: `export SPOTIPY_CLIENT_ID=<your client ID>` (see how to do it with your OS/shell) (or set it in `spotify_playlist_mover.py`)
3. The program will let you login your origin account
4. Then it will logout from origin account
5. It will let you login your destination account
6. Done!

(Otherways you can download or clone the repo, install the requirements and run by opening the folder and executing `python -m spotify_playlists_mover`)

## How to get a client id

1. Go to [Developer dashboard](https://developer.spotify.com/dashboard)
2. Create a new application with any account
3. Set `redirect_uri` to `http://localhost/`
4. Set your origin account's mail and your destination account's mail as users in the dashboard


## Disclaimer
I am not associated with [Spotify](https://www.spotify.com/), I am using their Web APIs through [Spotipy](http://spotipy.readthedocs.org/) library.