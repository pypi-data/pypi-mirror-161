# Simple Snake game in Python made with CatEngine
# This is a demo project designed to show some basic functionality of CatEngine


# ==// IMPORTS
from realityengine.window import Window
from realityengine.game_object import GameObject, Transform
from realityengine.audio import Sound

import random


#==// VARIABLES
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 480

GRIDSIZE = 20
GRID_WIDTH = SCREEN_HEIGHT / GRIDSIZE
GRID_HEIGHT = SCREEN_WIDTH / GRIDSIZE

head_direction = "stop"
segments = []


#==// FUNCTIONS
def draw_grid():
    for y in range(0, int(GRID_HEIGHT)):
        for x in range(0, int(GRID_WIDTH)):
            if (x + y) % 2 == 0:
                rect = GameObject(Transform((x * GRIDSIZE) + (GRIDSIZE / 2), (y * GRIDSIZE) + (GRIDSIZE / 2), GRIDSIZE, GRIDSIZE, 1, 1), ["bg"])
                rect.colour = "#5DD8E4"
                rect.layer = "back"
                rect.start()
            else:
                rect = GameObject(Transform((x * GRIDSIZE) + (GRIDSIZE / 2), (y * GRIDSIZE) + (GRIDSIZE / 2), GRIDSIZE, GRIDSIZE, 1, 1), ["bg"])
                rect.colour = "#54C2CD"
                rect.layer = "back"
                rect.start()


def move():
    if head_direction == "up":
        snake_head.transform.change_position(snake_head.transform.x, snake_head.transform.y - 20)
    elif head_direction == "down":
        snake_head.transform.change_position(snake_head.transform.x, snake_head.transform.y + 20)
    elif head_direction == "left":
        snake_head.transform.change_position(snake_head.transform.x - 20, snake_head.transform.y)
    elif head_direction == "right":
        snake_head.transform.change_position(snake_head.transform.x + 20, snake_head.transform.y)


def go_up(e):
    global head_direction
    if head_direction != "down":
        head_direction = "up"


def go_down(e):
    global head_direction
    if head_direction != "up":
        head_direction = "down"


def go_left(e):
    global head_direction
    if head_direction != "right":
        head_direction = "left"


def go_right(e):
    global head_direction
    if head_direction != "left":
        head_direction = "right"


def end_game():
    global head_direction
    snake_head.transform.change_position(wn.get_width() / 2 + (GRIDSIZE / 2), wn.get_height() / 2 - (GRIDSIZE / 2))
    head_direction = "stop"

    for segment in segments:
        segment.destroy()

    segments.clear()

    food.transform.change_position(wn.get_width() / 2 + (GRIDSIZE / 2), wn.get_height() / 2 - (GRIDSIZE / 2) - 100)

    # Play the death sound
    dead = Sound("audio/death.wav")
    dead.play()


#==// GAME LOOP
def update():
    # Check for a collision with the border
    if snake_head.transform.is_touching_border(20, SCREEN_WIDTH, SCREEN_HEIGHT, 20):
        end_game()

    # Check for a collision with the food
    if snake_head.transform.distance(food.transform) < 20:
        # Move the food to a random spot
        x = (random.randint(0, GRID_WIDTH - 1) * GRIDSIZE) - (food.transform.width / 1.5)
        y = (random.randint(0, GRID_HEIGHT - 1) * GRIDSIZE) - (food.transform.height / 1.5)
        food.transform.change_position(x, y)

        # Add a segment
        new_segment_transform = Transform(wn.get_width() / 2 + (GRIDSIZE / 2), wn.get_height() / 2 - (GRIDSIZE / 2), 15, 15, 1, 1)
        new_segment = GameObject(new_segment_transform, ["snake", "snake_body"], "segment", "#11182F", "front")
        new_segment.start()
        segments.append(new_segment)

        # Play the collect sound
        collect = Sound("audio/food_collect.wav")
        collect.play()

    
    # Move the end segments first in reverse order
    for index in range(len(segments) - 1, 0, -1):
        x = segments[index - 1].transform.x
        y = segments[index - 1].transform.y
        segments[index].transform.change_position(x, y)

    # Move segment 0 to where the head is
    if len(segments) > 0:
        x = snake_head.transform.x
        y = snake_head.transform.y
        segments[0].transform.change_position(x, y)

    move()

    # Check for a head collision with the body segments
    for segment in segments:
        if segment.transform.distance(snake_head.transform) < 20:
            end_game()


#==// MAIN
if __name__ == "__main__":
    # Set up the screen
    wn = Window(SCREEN_WIDTH, SCREEN_HEIGHT, "Snake")
    wn.set_resizable("none")
    wn.clock(100)

    draw_grid()

    # Snake Head
    snake_head_transform = Transform(wn.get_width() / 2 + (GRIDSIZE / 2), wn.get_height() / 2 - (GRIDSIZE / 2), 15, 15, 1, 1)
    snake_head = GameObject(snake_head_transform, ["snake", "snake_head"], "snake_head", "#11182F", "front")
    snake_head.start()

    # Snake food
    food_transform = Transform(wn.get_width() / 2 + (GRIDSIZE / 2), wn.get_height() / 2 - (GRIDSIZE / 2) - 100, 15, 15, 1, 1)
    food = GameObject(food_transform, ["food"], "food", "#DFA331", "front")
    food.start()

    # Keyboard
    wn.bind_key("w", go_up)
    wn.bind_key("s", go_down)
    wn.bind_key("a", go_left)
    wn.bind_key("d", go_right)

    wn.set_custom_update(update)
    wn.run()

