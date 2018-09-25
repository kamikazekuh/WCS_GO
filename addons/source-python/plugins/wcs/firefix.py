from engines.server import queue_command_string
from events import Event

@Event('player_activate')
def player_activate(event):
    userid = event.get_int('userid')
    queue_command_string('mp_disable_autokick %s' % userid)