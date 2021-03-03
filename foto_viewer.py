# First Party Imports #
import os
import sys
from datetime import datetime, timedelta

# Third Party Imports #
import configparser
import pygame

# Local Imports #
from foto_cycle import cycle  # Small custom implementation of itertools.cycle
from foto_getter import read_email

config = configparser.ConfigParser(interpolation=None)
config.sections()
config.read(['.env', 'config'])
viewer_config = config['VIEWER']

# Gets all images in the 'imageDir' directory filtered on the filetypes listed
# Currently only jpg files are downloaded


def find_image_filename():
    image_filenames = []
    for filename in os.listdir(config['DEFAULT'].get("imageDir")):
        if filename.lower().endswith(".bmp"):
            image_filenames.append(filename)
        if filename.lower().endswith(".gif"):
            image_filenames.append(filename)
        if filename.lower().endswith(".jpg"):
            image_filenames.append(filename)
        if filename.lower().endswith(".png"):
            image_filenames.append(filename)

    return image_filenames

# I found this on the internet and it seems to work


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

# Load the next image and update the display


def change_image(screen, image_filename, width, height):
    image = pygame.image.load(
        'files/{}'.format(image_filename))
    # Is there a better function that maintains aspect ratio?
    image = pygame.transform.scale(image, (width, height))
    screen.blit(image, (0, 0))
    pygame.display.update()

# Main function containing the main event loop


def display_image():
    # Start by fetching images
    read_email()
    last_image_fetch_time = datetime.now() - timedelta(hours=0, minutes=30)
    # Create a new cycle
    image_filenames = cycle(find_image_filename())
    if not image_filenames:
        print("No image files found")
        sys.exit()

    pygame.init()
    if not find_display_driver():
        print("Failed to initialise display driver")
        sys.exit()

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
                    change_image(screen, next(image_filenames), width, height)
                    # Reset the last image change time
                    last_image_change_time = datetime.now()
                    # Left arrow key to move to previous image
                if event.key == pygame.K_LEFT:
                    change_image(
                        screen, image_filenames.previous(), width, height)
                    # Reset the last image change time
                    last_image_change_time = datetime.now()
            # pygame.QUIT is the 'x' in the top right of the modal
            # which will not be present on release because there will be no modal
            # as the app will run fullscreen
            if (event.type == pygame.QUIT or
                    (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)):
                running = False

        # Get the difference between now and the last time we changed images to see if we need to change images
        time_since_last_image_change = (
            datetime.now() - last_image_change_time)
        if time_since_last_image_change.total_seconds() > int(viewer_config.get('timePerPicture')):
            change_image(screen, next(image_filenames), width, height)
            last_image_change_time = datetime.now()

        # Get the difference between now and the last time we fetched
        # This is currently a bug because it could be houts difference but still
        # less than 30 "minutes" apart. It should eventually correct itself
        # but would be nice to fix.
        time_since_last_fetch = (
            datetime.now().minute - last_image_fetch_time.minute)
        if time_since_last_fetch >= int(viewer_config.get('newPictureFetchDelay')):
            last_image_fetch_time = datetime.now()
            read_email()
            image_filenames = cycle(find_image_filename())

    pygame.quit()


if __name__ == "__main__":
    display_image()
