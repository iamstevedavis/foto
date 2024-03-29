# First Party Imports #
import os
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
FULLSCREEN = config['DEFAULT'].getboolean("fullscreen", "True")
TIME_PER_PICTURE = VIEWER_CONFIG.get('timePerPicture')
NEW_PICTURE_FETCH_DELAY = VIEWER_CONFIG.get('newPictureFetchDelay')

def find_image_filenames():
    """Get a list of all files that match a one of the supported extensions

    Returns:
        array: An array of filenames that match the extension criteria
    """
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


def change_image(screen, image_filename, screen_width, screen_height):
    image = pygame.image.load(
        '{}/{}'.format(IMAGE_DIR, image_filename))
    image_height = image.get_height()
    new_width = screen_width

    # Check if image is portrait shot
    if image_height > image.get_width():
        # Check if the image is too tall
        if image_height > screen_height:
            # reduce width to keep ratio
            new_width = screen_width * (screen_height * 0.5) / screen_height
        image = pygame.transform.scale(image, (int(new_width), int(screen_height)))

    image = pygame.transform.scale(image, (int(new_width), int(screen_height)))

    screen.fill((0,0,0))
    pygame.display.update()

    screen.blit(image, ((screen_width / 2) - (new_width / 2), 0))
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

    last_image_fetch_time = datetime.now()
    image_filenames = find_image_filenames()

    if not image_filenames:
        read_email()
        image_filenames = find_image_filenames()
        if not image_filenames:
            raise SystemExit(
                "No image files found in {}.".format(IMAGE_DIR))

    # Create a new cycle
    image_filenames_array = cycle(image_filenames)
    screen_width = pygame.display.Info().current_w
    screen_height = pygame.display.Info().current_h

    if FULLSCREEN:
        screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)

    pygame.mouse.set_visible(False)
    last_image_change_time = datetime(1970, 1, 1)
    running = True
    clock = pygame.time.Clock()

    # Main event loop
    while running:
        clock.tick(1)
        # Check for key presses
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP:
                change_image(screen, next(
                    image_filenames_array), screen_width, screen_height)
                # Reset the last image change time
                last_image_change_time = datetime.now()
            if event.type == pygame.KEYUP:
                # Right arrow key to move to next image
                if event.key == pygame.K_RIGHT:
                    change_image(screen, next(
                        image_filenames_array), screen_width, screen_height)
                    # Reset the last image change time
                    last_image_change_time = datetime.now()
                    # Left arrow key to move to previous image
                if event.key == pygame.K_LEFT:
                    change_image(
                        screen, image_filenames_array.previous(), screen_width, screen_height)
                    # Reset the last image change time
                    last_image_change_time = datetime.now()
            # pygame.QUIT is the 'x' in the top right of the modal
            # which will not be present on release because there will be no modal
            # as the app will run fullscreen
            if (event.type == pygame.QUIT or
                    (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)):
                running = False

        # Check if it is time to change image
        if is_time_to_change_image(last_image_change_time):
            change_image(screen, next(image_filenames_array), screen_width, screen_height)
            last_image_change_time = datetime.now()

        # Check if it is time to fetch images
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
