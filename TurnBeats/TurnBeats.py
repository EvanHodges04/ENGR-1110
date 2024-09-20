#TurnBeats.py by Alex Strickland | Owen Long | Evan Hodges | Mason Cooper

from tkinter import *
from PIL import ImageTk, Image
import playsound #for future sound implementation
import requests, time

SPOTIFY_GET_CURRENTLY_PLAYING_URL = 'https://api.spotify.com/v1/me/player/currently-playing'
SPOTIFY_GET_SONG_DETAILS_URL = 'https://api.spotify.com/v1/audio-analysis/'

#Access Token expires very often. To renew, visit https://developer.spotify.com/console/get-audio-analysis-track
ACCESS_TOKEN = 'BQCEzMgpqDAkEpytyTZnnLImlwFPjh0xH0qBXustmVGLKhPWCJH10F_uMHMicZ9mZXA8r68iuWkhw9Y46SS0RIVjHFBd8XnAGrZEW_j-DaPAstyJiEXx1w3fF9VnoA4Np2902YnPSjHvvgDW2sO7pt3u3peeNXBC9a0_bC9UYs807KwbQgdrlkNiGeXVWe97y_Sr-kc5'

toggled = False
side = "a"
interval = -1
current_track_info = []

def update_position():
        global current_track_info, current_track_id, interval, ACCESS_TOKEN, start_time
        current_track_info = get_current_track(ACCESS_TOKEN)

        if current_track_info != False:

                if current_track_info['id'] != current_track_id:
                        current_track_id = current_track_info['id']
                        start_time = time.time()

                for beat in current_track_info['beats']:
                        if beat['start']*1000 < current_track_info['progress']:
                                current_track_info['beats'].remove(beat)
                return current_track_info
        else:
                return False

def toggle_blink():
        global toggled, label, side, root, current_track_info, interval, start_time, avg_tempo
        interval += 1

        if not toggled:
                filename = ImageTk.PhotoImage(Image.open("dash.png"))
                toggled = True
        elif side == 'r':
                filename = ImageTk.PhotoImage(Image.open("dash_right.png"))
                toggled = False
        elif side == 'l':
                filename = ImageTk.PhotoImage(Image.open("dash_left.png"))
                toggled = False
        
        label.configure(image = filename)
        label.image = filename

        #print("Song time: ", current_track_info['beats'][interval]['start'])
        #print("Progress: ", current_track_info['progress'])
        #print("Actual: ", time.time() - start_time)
        #print(round(float(current_track_info['beats'][interval]['start']) - (time.time() - start_time), 2))
        root.after(int(float(current_track_info['beats'][interval]['duration'])*935), toggle_blink) #973

def get_current_track(token):
        response = requests.get(
                SPOTIFY_GET_CURRENTLY_PLAYING_URL,
                headers={
                "Authorization": f"Bearer {token}"
                }
        )

        json_resp = response.json()

        try:
                track_id = json_resp['item']['id']
        except:
                return False
        track_name = json_resp['item']['name']
        progress = json_resp['progress_ms']
        artists = [artist for artist in json_resp['item']['artists']]

        link = json_resp['item']['external_urls']['spotify']

        artist_names = ', '.join([artist['name'] for artist in artists])

        response2 = requests.get(
                SPOTIFY_GET_SONG_DETAILS_URL + track_id,
                headers = {
                "Authorization": f"Bearer {token}"
                }
        )

        json_resp2 = response2.json()
        beats = json_resp2['beats']

        current_track_info = {
           "id": track_id,
           "track_name": track_name,
           "artists": artist_names,
           "link": link,
           "progress": progress,
           "beats": beats
        }

        print(json_resp2)

        return current_track_info

def begin_analyze(s):
        global side, began, current_track_info, current_track_id, start_time

        if side != s:
                side = s
                current_track_id = None

                current_track_info = update_position()

                if current_track_info != False:
                        
                        root.after(int(float(current_track_info['beats'][0]['start']) * 935), toggle_blink)
        elif toggled:
                toggle_blink()

root = Tk()
root.title("TurnBeats")

filename = ImageTk.PhotoImage(Image.open("dash.png"))
label = Label(image=filename)
label.image = filename

label.grid(row = 0, column = 1)

button = Button(text="LEFT", command = lambda: begin_analyze('l'))
button.grid(row = 1, column = 0)

button2 = Button(text="RIGHT", command = lambda: begin_analyze('r'))
button2.grid(row = 1, column = 2)

root.mainloop()