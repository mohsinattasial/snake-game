import time
from turtle import Screen
from snake import Snake
from food import Food
from scoreboard import Scoreboard

# Screen setup
screen = Screen()
screen.setup(width=600, height=600)
screen.bgcolor("black")
screen.title("Snake Game 🐍")
screen.tracer(0)

# Objects
snake = Snake()
food = Food()
scoreboard = Scoreboard()

# ✅ Controls (FIXED - more responsive)
screen.listen()
screen.onkeypress(snake.up, "Up")
screen.onkeypress(snake.down, "Down")
screen.onkeypress(snake.left, "Left")
screen.onkeypress(snake.right, "Right")

# Game loop
game_is_on = True

while game_is_on:
    screen.update()
    time.sleep(0.08)   # ✅ smoother speed
    snake.move()

    # 🍎 Food collision (FIXED)
    if snake.head.distance(food) < 15:
        food.refresh()
        snake.extend()
        scoreboard.increase()

    # 🧱 Wall collision (FIXED)
    if (
        snake.head.xcor() > 290 or
        snake.head.xcor() < -290 or
        snake.head.ycor() > 290 or
        snake.head.ycor() < -290
    ):
        game_is_on = False
        scoreboard.game_over()

    # 🐍 Tail collision (FIXED)
    for segment in snake.segments[1:]:
        if snake.head.distance(segment) < 8:
            game_is_on = False
            scoreboard.game_over()

screen.exitonclick()