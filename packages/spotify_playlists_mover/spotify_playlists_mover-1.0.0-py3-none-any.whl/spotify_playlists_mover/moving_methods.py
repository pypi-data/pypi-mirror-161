import spotipy
from spotipy.oauth2 import SpotifyImplicitGrant
import base64
import requests
# from pprint import pprint

CLIENT_ID= "f22a36cd6eed407f88ce13a771388461"
REDIRECT_URI= "http://localhost:8080"


def download_from_origin():
	print("Login to Origin account")
	sp_from= spotipy.Spotify(auth_manager=SpotifyImplicitGrant(client_id=CLIENT_ID, redirect_uri=REDIRECT_URI, scope="user-library-read"))
	print("\n\nOrigin account:", sp_from.me()['display_name'])

	# Playlists
	print("Downloading playlists...")
	result= sp_from.current_user_playlists()	# dict output -> list playlists -> dict playlist
	playlists= result['items']
	while result['next']:	# pages after first
		result= sp_from.next(result)
		playlists.extend(result['items'])
	# print(playlists[0]['id'])
	# pprint(playlists)

	for playlist in playlists:
		# playlist dictionary playlist:[track_list]
		result= sp_from.playlist_tracks(playlist)
		playlist_tracks= result['items']
		while result['next']:
			result= sp_from.next(result)
			playlist_tracks.extend(result['items'])
		track_list= []
		for track in playlist_tracks:
			track_list.append(track['track']['uri'])
		playlist['track_list']= track_list


	# Saved tracks
	print("Downloading saved tracks...")
	result= sp_from.current_user_saved_tracks()
	saved_tracks= result['items']
	while result['next']:
		result= sp_from.next(result)
		saved_tracks.extend(result['items'])
	saved_tracks_list= []
	for saved_track in saved_tracks:
		saved_tracks_list.append(saved_track['track']['id'])

	return (playlists, saved_tracks_list)	# return tuple of playlists and saved tracks


def upload_to_destination(playlists_dict_and_saved_tracks_list_tuple):
	playlists_dict= playlists_dict_and_saved_tracks_list_tuple[0]
	saved_tracks_list= playlists_dict_and_saved_tracks_list_tuple[1]

	print("Log in to Destination account")
	sp_to= spotipy.Spotify(auth_manager=SpotifyImplicitGrant(client_id=CLIENT_ID, redirect_uri=REDIRECT_URI, scope="playlist-modify-public playlist-modify-private ugc-image-upload user-library-modify"))
	print("\n\nDestination account:", sp_to.me()['display_name'])

	# Playlists
	print("Uploading playlists...")
	for playlist in playlists_dict:
		if playlist['track_list']:
			# Create playlist
			new_playlist= sp_to.user_playlist_create(sp_to.me()['id'], playlist['name'], public= playlist['public'], collaborative= playlist['collaborative'], description= playlist['description'])

			# Set thumbnail
			if playlist['images']:
				thumbnail_b64= base64.b64encode(requests.get(playlist['images'][0]['url']).content)
				try:
					sp_to.playlist_upload_cover_image(new_playlist['id'], thumbnail_b64)
				except:
					print("Error uploading thumbnail of \"" + playlist['name'] + "\" playlist; skipping...")

			# Set tracks
			list_49= split_every_49(playlist['track_list'])	# You can add a maximum of 100 tracks per request
			for chunk in list_49:
				sp_to.playlist_add_items(new_playlist['id'], chunk)
		else:
			print("Playlist \"" + playlist['name'] + "\" has no tracks; skipping...")


	# Saved tracks
	print("Uploading saved tracks...")
	list_49= split_every_49(saved_tracks_list)	# You can add a maximum of 50 tracks per request
	for chunk in list_49:
		sp_to.current_user_saved_tracks_add(chunk)



def split_every_49(list):
	return [list[i:i + 49] for i in range(0, len(list), 49)]