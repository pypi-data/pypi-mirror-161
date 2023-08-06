import sys
from . import moving_methods
import webbrowser
import time


def main():
	spotify_logout()
	old_account_dl= moving_methods.download_from_origin()
	spotify_logout()
	moving_methods.upload_to_destination(old_account_dl)
	print("Done!")

def spotify_logout():
	webbrowser.open('accounts.spotify.com/logout')	# logout from old account
	time.sleep(3)

if __name__ == '__main__':
	sys.exit(main())