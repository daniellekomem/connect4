import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import pygame_menu
from pygame_menu.examples import create_example_window
from pygame_menu import sound
from random import randrange
from typing import Tuple, Any, Optional, List
import os.path as path
from game import ConnectFour

# Constants and global variables
ABOUT = [f'Connect Four Game',
         f'Author: Danielle Komem',
         f'Email: danielle.komem@gmail.com']


width = 1280
height = 800
WHITE = 255, 255, 255
BLUE = 0,0,255
RED = 255,0,0
LAVENDER = 230,230,250
BLACK = 0,0,0
FPS = 60
WINDOW_SIZE = (width, height)

clock: Optional['pygame.time.Clock'] = None
main_menu: Optional['pygame_menu.Menu'] = None
surface: Optional['pygame.Surface'] = None
player2_text_input: Optional['pygame_menu.widgets.TextInput'] = None
difficulty_selector: Optional['pygame_menu.widgets.Selector'] = None
sound_option: Optional['pygame_menu.sound.Sound'] = None

class MyGame:
  def __init__(self, name1, name2, difficulty, num_players):
    self.name1 = name1
    self.name2 = name2
    self.difficulty = difficulty
    self.num_players = num_players

game_options = MyGame( "name1", "name2", 1, 1)

def change_difficulty(value: Tuple[Any, int], difficulty: int):
    game_options.difficulty = difficulty

def change_players(value: Tuple[Any, int], num_players: str):
    # Define globals
    global player2_text_input
    global difficulty_selector
    game_options.num_players = num_players
    #NUM_PLAYERS = num_players
    if(game_options.num_players == 1):
        player2_text_input.hide()
        difficulty_selector.show()
    else:
        player2_text_input.show()
        difficulty_selector.hide() 

def name1_change(name):
    game_options.name1 = name

def name2_change(name):
    game_options.name2 = name
  
def update_menu_sound(value: Tuple, enabled: bool) -> None:
    assert isinstance(value, tuple)
    if enabled:
        main_menu.set_sound(sound_option, recursive=True)
    else:
        main_menu.set_sound(None, recursive=True)

def update_backgroung_sound(value: Tuple, enabled: bool) -> None:
    assert isinstance(value, tuple)
    if enabled:
        pygame.mixer.music.play()
    else:
        pygame.mixer.music.stop()



def play_function(font: 'pygame.font.Font'):
    #game_options.difficulty = game_options.difficulty

    # Define globals
    global main_menu
    global clock
    global surface
    #print(f'play_function: num_players={game_options.num_players}')

    if( game_options.num_players == 1):
        if game_options.difficulty == 1:
            f = font.render(f'{game_options.name1} Playing as a baby (easy)', True, WHITE)
        elif game_options.difficulty == 2:
            f = font.render(f'{game_options.name1} Playing as a kid (medium)', True, WHITE)
        elif game_options.difficulty == 3:
            f = font.render(f'{game_options.name1} Playing as a champion (hard)', True, WHITE)
        else:
            raise ValueError(f'unknown difficulty {game_options.difficulty}')
    else:
        f = font.render(f'Playing with 2 players: {game_options.name1} and {game_options.name2}', True, WHITE)
    f_esc = font.render('Press ESC to open the menu', True, WHITE)

    # Reset main menu and disable
    # You also can set another menu, like a 'pause menu', or just use the same
    # main_menu as the menu that will check all your input.
    main_menu.disable()
    main_menu.full_reset()

    app = ConnectFour( game_options.name1, game_options.name2, game_options.difficulty, game_options.num_players)
    app.game_loop(surface, clock, "play", main_menu)


def main_background():
    global surface
    surface.fill(LAVENDER)


def main():
    # -------------------------------------------------------------------------
    # Globals
    # -------------------------------------------------------------------------
    global clock
    global main_menu
    global surface
    global player2_text_input
    global difficulty_selector
    global sound_option
    
    # -------------------------------------------------------------------------
    # Set sounds
    # -------------------------------------------------------------------------
    pygame.mixer.init()
    sound_option = sound.Sound()
    # Load example sounds
    __sounds_path__ = path.join(path.dirname(path.abspath(__file__)), 'resources', 'sounds', '{0}')
    sound_option.set_sound(sound.SOUND_TYPE_CLICK_MOUSE,__sounds_path__.format('click_mouse.ogg'))
    sound_option.set_sound(sound.SOUND_TYPE_CLOSE_MENU,       __sounds_path__.format('close_menu.ogg'))
    sound_option.set_sound(sound.SOUND_TYPE_ERROR,            __sounds_path__.format('error.ogg'))
    sound_option.set_sound(sound.SOUND_TYPE_EVENT,            __sounds_path__.format('event.ogg'))
    sound_option.set_sound(sound.SOUND_TYPE_EVENT_ERROR,      __sounds_path__.format('event_error.ogg'))
    sound_option.set_sound(sound.SOUND_TYPE_KEY_ADDITION,     __sounds_path__.format('key_add.ogg'))
    sound_option.set_sound(sound.SOUND_TYPE_KEY_DELETION,     __sounds_path__.format('key_delete.ogg'))
    sound_option.set_sound(sound.SOUND_TYPE_OPEN_MENU,        __sounds_path__.format('open_menu.ogg'))
    sound_option.set_sound(sound.SOUND_TYPE_WIDGET_SELECTION, __sounds_path__.format('widget_selection.ogg'))
    sound_option.set_sound(sound.SOUND_TYPE_CLICK_TOUCH,      __sounds_path__.format('click_mouse.ogg'))
	
    pygame.mixer.music.load('resources/sounds/neon.mp3')
    pygame.mixer.music.play()
    # -------------------------------------------------------------------------
    # Create window
    # -------------------------------------------------------------------------
    surface = create_example_window('Connect Four Game', WINDOW_SIZE)
    clock = pygame.time.Clock()

    # -------------------------------------------------------------------------
    # Create menus: Play Menu
    # -------------------------------------------------------------------------
    play_menu = pygame_menu.Menu(
        height=WINDOW_SIZE[1] * 0.7,
        title='Play Menu',
        width=WINDOW_SIZE[0] * 0.75,
        theme=pygame_menu.themes.THEME_DARK.copy()
    )


    play_menu.add.text_input('Player 1 Name:', default=game_options.name1, onchange= name1_change)
    difficulty_selector = play_menu.add.selector('Select difficulty ',
                           [('Easy', 1),
                            ('Medium', 2),
                            ('Hard', 3)],
                           onchange=change_difficulty,
                           selector_id='select_difficulty')
    player2_text_input  = play_menu.add.text_input('Player 2 Name:', default=game_options.name2, onchange= name2_change)
    player2_text_input.hide()
    play_menu.add.selector('Play :', [('Play against Computer', 1), ('two-player game', 2)], onchange=change_players)
    play_menu.add.button('Start',  # When pressing return -> play(DIFFICULTY[0], font)
                         play_function,
                         pygame.font.SysFont('arial', 32)
                         )
    play_menu.add.button('Return to main menu', pygame_menu.events.BACK)

    # -------------------------------------------------------------------------
    # Create menus:About
    # -------------------------------------------------------------------------
    about_theme = pygame_menu.themes.THEME_DARK.copy()
    about_theme.widget_margin = (0, 0)

    about_menu = pygame_menu.Menu(
        height=WINDOW_SIZE[1] * 0.6,
        theme=about_theme,
        title='About',
        width=WINDOW_SIZE[0] * 0.6,
    )

    for m in ABOUT:
        about_menu.add.label(m, align=pygame_menu.locals.ALIGN_LEFT, font_size=32)
    about_menu.add.vertical_margin(30)
    about_menu.add.button('Return to menu', pygame_menu.events.BACK)

    # -------------------------------------------------------------------------
    # Create menus: Main
    # -------------------------------------------------------------------------
    main_theme = pygame_menu.themes.THEME_DARK.copy()

    main_menu = pygame_menu.Menu(
        height=WINDOW_SIZE[1] * 0.6,
        theme=main_theme,
        title='Main Menu',
        width=WINDOW_SIZE[0] * 0.6
    )

    main_menu.add.selector('Menu sounds ',
                           [('On', True),('Off', False)],
                           onchange=update_menu_sound)

    main_menu.add.selector('Music ',
                           [('On', True),('Off', False)],
                           onchange=update_backgroung_sound)

    main_menu.add.button('Play', play_menu)
    main_menu.add.button('About', about_menu)
    main_menu.add.button('Quit', pygame_menu.events.EXIT)

    main_menu.set_sound(sound_option, recursive=True)  # Apply on menu and all sub-menus
    # -------------------------------------------------------------------------
    # Main loop
    # -------------------------------------------------------------------------
    while True:

        # Tick
        clock.tick(FPS)

        # Paint background
        main_background()

        # Application events
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                exit()

        # Main menu
        if main_menu.is_enabled():
            main_menu.mainloop(surface, main_background, disable_loop=False, fps_limit=FPS)

        # Flip surface
        pygame.display.flip()


if __name__ == '__main__':
    main()