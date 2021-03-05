# First Party Imports #
import os
import time
from datetime import datetime

# Third Party Imports #
import configparser
import pygame

# Local Imports #
from foto_cycle import cycle  # Small custom implementation of itertools.cycle
from foto_getter import read_email

# Set global constants from config
config = configparser.ConfigParser(interpolation=None)
config.sections()
config.read(['.env', 'config'])
VIEWER_CONFIG = config['VIEWER']
IMAGE_DIR = config['DEFAULT'].get("imageDir")
TIME_PER_PICTURE = VIEWER_CONFIG.get('timePerPicture')
NEW_PICTURE_FETCH_DELAY = VIEWER_CONFIG.get('newPictureFetchDelay')


def find_image_filenames():
    image_filenames = []
    for filename in os.listdir(IMAGE_DIR):
        if filename.lower().endswith(".bmp"):
            image_filenames.append(filename)
        if filename.lower().endswith(".gif"):
            image_filenames.append(filename)
        if filename.lower().endswith(".jpg"):
            image_filenames.append(filename)
        if filename.lower().endswith(".png"):
            image_filenames.append(filename)

    return image_filenames


def find_display_driver():
    for driver in ["fbcon", "directfb", "svgalib"]:
        if not os.getenv("SDL_VIDEODRIVER"):
            os.putenv("SDL_VIDEODRIVER", driver)
        try:
            pygame.display.init()
            return True
        except pygame.error:
            pass
    return False


def change_image(screen, image_filename, width, height):
    image = pygame.image.load(
        '{}/{}'.format(IMAGE_DIR, image_filename))
    # Is there a better function that maintains aspect ratio?
    image = pygame.transform.scale(image, (width, height))
    screen.blit(image, (0, 0))
    pygame.display.update()


def is_time_to_fetch_images(last_image_fetch_time):
    time_since_last_fetch = (
        datetime.now() - last_image_fetch_time)
    minutes_since_last_fetch = time_since_last_fetch.seconds / 60
    if minutes_since_last_fetch >= int(NEW_PICTURE_FETCH_DELAY):
        return True

    return False


def is_time_to_change_image(last_image_change_time):
    time_since_last_image_change = (
        datetime.now() - last_image_change_time)
    if time_since_last_image_change.total_seconds() > int(TIME_PER_PICTURE):
        return True

    return False


def display_image():
    if not pygame.image.get_extended():
        raise SystemExit(
            "Extended image module missing. Did you install all libsdl2 libraries from the readme?")

    pygame.init()
    if not find_display_driver():
        raise SystemExit("Failed to initialise display driver.")

    read_email()
    last_image_fetch_time = datetime.now()

    image_filenames = find_image_filenames()
    if not image_filenames:
        raise SystemExit(
            "No image files found in {}.".format(IMAGE_DIR))
    # Create a new cycle
    image_filenames_array = cycle(image_filenames)

    width = pygame.display.Info().current_w
    height = pygame.display.Info().current_h
    # Change this line to pygame.FULLSCREEN on release or use RESIZABLE when testing
    screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
    pygame.mouse.set_visible(False)
    last_image_change_time = datetime(1970, 1, 1)
    running = True

    # Main event loop
    while running:
        # Check for key presses
        for event in pygame.event.get():
            if event.type == pygame.KEYUP:
                # Right arrow key to move to next image
                if event.key == pygame.K_RIGHT:
                    change_image(screen, next(
                        image_filenames_array), width, height)
                    # Reset the last image change time
                    last_image_change_time = datetime.now()
                    # Left arrow key to move to previous image
                if event.key == pygame.K_LEFT:
                    change_image(
                        screen, image_filenames_array.previous(), width, height)
                    # Reset the last image change time
                    last_image_change_time = datetime.now()
            # pygame.QUIT is the 'x' in the top right of the modal
            # which will not be present on release because there will be no modal
            # as the app will run fullscreen
            if (event.type == pygame.QUIT or
                    (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)):
                running = False

        # Get the difference between now and the last time we changed images to see if we need to change images
        if is_time_to_change_image(last_image_change_time):
            change_image(screen, next(image_filenames_array), width, height)
            last_image_change_time = datetime.now()

        if is_time_to_fetch_images(last_image_fetch_time):
            last_image_fetch_time = datetime.now()
            read_email()
            image_filenames = find_image_filenames()
            if not image_filenames:
                raise SystemExit(
                    "No image files found in {}.".format(IMAGE_DIR))
            # Create a new cycle
            image_filenames_array = cycle(image_filenames)

    pygame.quit()


if __name__ == "__main__":
    display_image()
