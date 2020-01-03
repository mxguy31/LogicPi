import curses
import threading
import bin.logicpi
import bin.utilities as utilities
from bin.constants import CONST
import sys

menus = {True: ['Diagnostics', 'Pause', 'Exit'], False: ['Diagnostics', 'Resume', 'Exit']}

thread = threading.Thread(target=bin.logicpi.main_loop, daemon=True)
thread.start()

config = utilities.get_config(CONST.SYS_CONF_FILE)
if config is None:
    print('No config file was found, system is shutting down')
    sys.exit(1)

database = utilities.get_database(config)


def main_menu(menu, screen, selected_row):
    screen.clear()
    h, w = screen.getmaxyx()

    for index, text in enumerate(menu):
        x = w//2 - len(text)//2
        y = h//2 - len(menu)//2 + index
        if index == selected_row:
            screen.attron(curses.color_pair(1))
            screen.addstr(y, x, text)
            screen.attroff(curses.color_pair(1))
        else:
            screen.addstr(y, x, text)
    screen.refresh()


def main(screen):
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    current_row = 0
    running = True
    main_menu(menus[running], screen, current_row)

    while True:
        key = screen.getch()
        screen.clear()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(menus[running]) - 1:
            current_row += 1
        elif key in [10, 13]:
            if current_row == len(menus[running]) - 1:
                database.write_data(database.SYSTEM_STATUS, database.OFF)
                break
            elif current_row == len(menus[running]) - 2:
                if running:
                    database.write_data(database.SYSTEM_STATUS, database.PAUSED)
                    running = False
                else:
                    database.write_data(database.SYSTEM_STATUS, database.ON)
                    running = True

        main_menu(menus[running], screen, current_row)


# https://www.youtube.com/watch?v=BvbqI6eDh0c


curses.wrapper(main)
database.close()
thread.join()
sys.exit(0)
