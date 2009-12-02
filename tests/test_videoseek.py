from candies2 import VideoPlayer, SeekBar
import clutter
import sys

stage = clutter.Stage()
stage.connect('destroy', clutter.main_quit)

def on_button_press(player, event):
    if event.button == 1:
        player.toggle_playing()
    else:
        is_playing = player.get_playing()
        player.set_filename(player.get_uri())
        if is_playing:
            player.play()

player = VideoPlayer()
player.set_filename(sys.argv[1])
player.set_reactive(True)
player.connect('button_press_event', on_button_press)

seek = SeekBar()
seek.set_background_color('DarkGreen')
seek.set_cursor_color('Black')
seek.set_size(630, 100)
seek.set_position(5, 500)
seek.set_reactive(True)
seek.connect('seek', player.on_seek_request)
player.connect('read', seek.on_read_request)
stage.set_size(800, 600)
stage.add(player, seek)
stage.show()

clutter.main()
