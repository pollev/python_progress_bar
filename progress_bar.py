#!/usr/bin/env python3

import curses

# Usage:
# import progress_bar                           <- Import this module
# progress_bar.enable_trapping()                <- optional to clean up properly if user presses ctrl-c
# progress_bar.setup_scroll_area()              <- create empty progress bar
# progress_bar.draw_progress_bar(10)            <- advance progress bar
# progress_bar.draw_progress_bar(40)            <- advance progress bar
# progress_bar.block_progress_bar(45)           <- turns the progress bar yellow to indicate some action is requested from the user
# progress_bar.draw_progress_bar(90)            <- advance progress bar
# progress_bar.destroy_scroll_area()            <- remove progress bar


# Constants
CODE_SAVE_CURSOR = "\033[s"
CODE_RESTORE_CURSOR = "\033[u"
CODE_CURSOR_IN_SCROLL_AREA = "\033[1A"
COLOR_FG = "\e[30m"
COLOR_BG = "\e[42m"
COLOR_BG_BLOCKED = "\e[43m"
RESTORE_FG = "\e[39m"
RESTORE_BG = "\e[49m"

# Variables
PROGRESS_BLOCKED = False
TRAPPING_ENABLED = False
TRAP_SET = False


def setup_scroll_area():
    # Setup curses support (to get information about the terminal we are running in)
    curses.setupterm()

    # If trapping is enabled, we will want to activate it whenever we setup the scroll area and remove it when we break the scroll area
    if TRAPPING_ENABLED:
        __trap_on_interrupt()

    lines = __tput("lines") - 1
    # Scroll down a bit to avoid visual glitch when the screen area shrinks by one row
    __print_control_code("\n")

    # Save cursor
    __print_control_code(CODE_SAVE_CURSOR)
    # Set scroll region (this will place the cursor in the top left)
    __print_control_code("\033[0;" + lines + "r")

    # Restore cursor but ensure its inside the scrolling area
    __print_control_code(CODE_RESTORE_CURSOR)
    __print_control_code(CODE_CURSOR_IN_SCROLL_AREA)

    # Start empty progress bar
    draw_progress_bar(0)


def destroy_scroll_area():
    lines = __tput("lines")
    # Save cursor
    __print_control_code(CODE_SAVE_CURSOR)
    # Set scroll region (this will place the cursor in the top left)
    __print_control_code("\033[0;" + lines + "r")

    # Restore cursor but ensure its inside the scrolling area
    __print_control_code(CODE_RESTORE_CURSOR)
    __print_control_code(CODE_CURSOR_IN_SCROLL_AREA)

    # We are done so clear the scroll bar
    __clear_progress_bar()

    # Scroll down a bit to avoid visual glitch when the screen area grows by one row
    __print_control_code("\n\n")

    # Once the scroll area is cleared, we want to remove any trap previously set. Otherwise, ctrl+c will exit our shell
    if TRAP_SET:
        trap - INT


def draw_progress_bar(percentage):
    global PROGRESS_BLOCKED
    lines = __tput("lines")
    # Save cursor
    __print_control_code(CODE_SAVE_CURSOR)

    # Move cursor position to last row
    __print_control_code("\033[" + lines ";0f")

    # Clear progress bar
    __tput("el")

    # Draw progress bar
    PROGRESS_BLOCKED = False
    __print_bar_text(percentage)

    # Restore cursor position
    __print_control_code(CODE_RESTORE_CURSOR)


def block_progress_bar(percentage) {
    global PROGRESS_BLOCKED
    lines = __tput("lines")
    # Save cursor
    __print_control_code($CODE_SAVE_CURSOR)

    # Move cursor position to last row
    __print_control_code("\033[$" + lines + ";0f")

    # Clear progress bar
    __tput("el")

    # Draw progress bar
    PROGRESS_BLOCKED = True
    __print_bar_text(percentage)

    # Restore cursor position
    __print_control_code(CODE_RESTORE_CURSOR)


def __clear_progress_bar():
    lines = __tput("lines")
    # Save cursor
    __print_control_codeCODE_SAVE_CURSOR)

    # Move cursor position to last row
    __print_control_code("\033[" + lines + ";0f")

    # clear progress bar
    __tput("el")

    # Restore cursor position
    __print_control_code(CODE_RESTORE_CURSOR)


def __print_bar_text(percentage):
    cols = __tput("cols")
    bar_size = cols - 17

    color = f"{COLOR_FG}{COLOR_BG}"
    if PROGRESS_BLOCKED:
        color = f"{COLOR_FG}{COLOR_BG_BLOCKED}"

    # Prepare progress bar
    complete_size = (bar_size * percentage) / 100
    remainder_size = bar_size - complete_size
    progress_bar = f"[{color}{'#' * complete_size}{RESTORE_FG}{RESTORE_BG}{'.' * remainder_size}]"

    # Print progress bar
    __print_control_code(f" Progress {percentage}% {progress_bar}")


def enable_trapping():
    global TRAPPING_ENABLED
    TRAPPING_ENABLED = True


def __trap_on_interrupt():
    # If this function is called, we setup an interrupt handler to cleanup the progress bar
    TRAP_SET="true"
    trap __cleanup_on_interrupt INT


def __cleanup_on_interrupt():
    destroy_scroll_area()
    exit()


def __tput(cmd, *args):
    print (tparm(tigetstr(cmd), *args), end='') # Emulates Unix tput


def __print_control_code(code):
    print(code, end='')


