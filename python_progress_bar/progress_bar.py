#!/usr/bin/env python3

import curses
import signal
import os

from time import time


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
COLOR_FG = '\033[30m'
COLOR_BG = '\033[42m'
COLOR_BG_BLOCKED = '\033[43m'
RESTORE_FG = '\033[39m'
RESTORE_BG = '\033[49m'

# Variables
PROGRESS_BLOCKED = False
TRAPPING_ENABLED = False
TRAP_SET = False
original_sigint_handler = None
CURRENT_NR_LINES = 0
START_TIME = 0
RATE_BAR = True


def get_current_nr_lines():
    stream = os.popen('tput lines')
    output = stream.read()
    return int(output)


def get_current_nr_cols():
    stream = os.popen('tput cols')
    output = stream.read()
    return int(output)


def setup_scroll_area(rate_bar=True):
    global CURRENT_NR_LINES
    global START_TIME
    global RATE_BAR

    # Enable/disable right side of progress bar with statistics
    RATE_BAR = rate_bar
    # Setup curses support (to get information about the terminal we are running in)
    curses.setupterm()

    # If trapping is enabled, we will want to activate it whenever we setup the scroll area and remove it when we break the scroll area
    if TRAPPING_ENABLED:
        __trap_on_interrupt()

    CURRENT_NR_LINES = get_current_nr_lines()
    lines = CURRENT_NR_LINES - 1
    # Scroll down a bit to avoid visual glitch when the screen area shrinks by one row
    __print_control_code("\n")

    # Save cursor
    __print_control_code(CODE_SAVE_CURSOR)
    # Set scroll region (this will place the cursor in the top left)
    __print_control_code("\033[0;" + str(lines) + "r")

    # Restore cursor but ensure its inside the scrolling area
    __print_control_code(CODE_RESTORE_CURSOR)
    __print_control_code(CODE_CURSOR_IN_SCROLL_AREA)

    # Start empty progress bar
    draw_progress_bar(0)

    # Setup start time
    START_TIME = time()


def destroy_scroll_area():
    lines = get_current_nr_lines()
    # Save cursor
    __print_control_code(CODE_SAVE_CURSOR)
    # Set scroll region (this will place the cursor in the top left)
    __print_control_code("\033[0;" + str(lines) + "r")

    # Restore cursor but ensure its inside the scrolling area
    __print_control_code(CODE_RESTORE_CURSOR)
    __print_control_code(CODE_CURSOR_IN_SCROLL_AREA)

    # We are done so clear the scroll bar
    __clear_progress_bar()

    # Scroll down a bit to avoid visual glitch when the screen area grows by one row
    __print_control_code("\n\n")

    # Once the scroll area is cleared, we want to remove any trap previously set.
    if TRAP_SET:
        signal.signal(signal.SIGINT, original_sigint_handler)


def draw_progress_bar(percentage):
    global PROGRESS_BLOCKED
    global CURRENT_NR_LINES
    lines = get_current_nr_lines()

    if lines != CURRENT_NR_LINES:
        setup_scroll_area()

    # Save cursor
    __print_control_code(CODE_SAVE_CURSOR)

    # Move cursor position to last row
    __print_control_code("\033[" + str(lines) + ";0f")

    # Clear progress bar
    __tput("el")

    # Draw progress bar
    PROGRESS_BLOCKED = False
    __print_bar_text(percentage)

    # Restore cursor position
    __print_control_code(CODE_RESTORE_CURSOR)


def block_progress_bar(percentage):
    global PROGRESS_BLOCKED
    lines = get_current_nr_lines()
    # Save cursor
    __print_control_code(CODE_SAVE_CURSOR)

    # Move cursor position to last row
    __print_control_code("\033[" + str(lines) + ";0f")

    # Clear progress bar
    __tput("el")

    # Draw progress bar
    PROGRESS_BLOCKED = True
    __print_bar_text(percentage)

    # Restore cursor position
    __print_control_code(CODE_RESTORE_CURSOR)


def __clear_progress_bar():
    lines = get_current_nr_lines()
    # Save cursor
    __print_control_code(CODE_SAVE_CURSOR)

    # Move cursor position to last row
    __print_control_code("\033[" + str(lines) + ";0f")

    # clear progress bar
    __tput("el")

    # Restore cursor position
    __print_control_code(CODE_RESTORE_CURSOR)


def __print_bar_text(percentage):
    global RATE_BAR

    color = f"{COLOR_FG}{COLOR_BG}"
    if PROGRESS_BLOCKED:
        color = f"{COLOR_FG}{COLOR_BG_BLOCKED}"

    cols = get_current_nr_cols()
    if RATE_BAR:
        # Create right side of progress bar with statistics
        r_bar = __prepare_r_bar(percentage)
        bar_size = cols - 18 - len(r_bar)
    else:
        r_bar = ""
        bar_size = cols - 17

    # Prepare progress bar
    complete_size = (bar_size * percentage) / 100
    remainder_size = bar_size - complete_size
    progress_bar = f"[{color}{'#' * int(complete_size)}{RESTORE_FG}{RESTORE_BG}{'.' * int(remainder_size)}]"

    # Print progress bar
    __print_control_code(f" Progress {percentage}% {progress_bar} {r_bar}\r")


def __prepare_r_bar(n):
    global START_TIME

    elapsed = time() - START_TIME
    elapsed_str = __format_interval(elapsed)

    # Percentage/second rate (or second/percentage if slow)
    rate = n / elapsed
    inv_rate = 1 / rate if rate else None
    rate_noinv_fmt = f"{f'{rate:5.2f}' if rate else '?'}pct/s"
    rate_inv_fmt = f"{f'{inv_rate:5.2f}' if inv_rate else '?'}s/pct"
    rate_fmt = rate_inv_fmt if inv_rate and inv_rate > 1 else rate_noinv_fmt

    # Remaining time
    remaining = (100 - n) / rate if rate else 0
    remaining_str = __format_interval(remaining) if rate else "?"

    r_bar = f"[{elapsed_str}<{remaining_str}, {rate_fmt}]"
    return r_bar


def __format_interval(t):
    h_m, s = divmod(int(t), 60)
    h, m = divmod(h_m, 60)
    if h:
        return f"{h:d}:{m:02d}:{s:02d}"
    else:
        return f"{m:02d}:{s:02d}"


def enable_trapping():
    global TRAPPING_ENABLED
    TRAPPING_ENABLED = True


def __trap_on_interrupt():
    global TRAP_SET
    global original_sigint_handler
    # If this function is called, we setup an interrupt handler to cleanup the progress bar
    TRAP_SET = True
    original_sigint_handler = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, __cleanup_on_interrupt)


def __cleanup_on_interrupt(sig, frame):
    destroy_scroll_area()
    raise KeyboardInterrupt


def __tput(cmd, *args):
    print(curses.tparm(curses.tigetstr("el")).decode(), end='')
    # print(curses.tparm(curses.tigetstr("el")).decode())


def __print_control_code(code):
    print(code, end='')
