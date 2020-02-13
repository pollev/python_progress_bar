#!/usr/bin/env python3

import random
import string
import time

# Import the progress bar
import progress_bar


def random_string(string_length=30):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(string_length))

def generate_some_output_and_sleep():
    print("Here is some output")
    print(random_string())
    print(random_string())
    print(random_string())
    print(random_string())
    print("\n\n------------------------------------------------------------------")
    print("\n\n Now sleeping briefly \n\n")
    time.sleep(0.3)


main():
    # Make sure that the progress bar is cleaned up when user presses ctrl+c
    progress_bar.enable_trapping()
    # Create progress bar
    progress_bar.setup_scroll_area()
    for i in range(99):
        if i == 50:
            print("waiting for user input: ")
            block_progress_bar(i)
            input("User input: ")
        else:
            generate_some_output_and_sleep()
            draw_progress_bar(i)
    destroy_scroll_area()


main()
