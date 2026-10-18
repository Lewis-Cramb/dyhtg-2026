import pygame as pg

pg.init()

WIDTH, HEIGHT = 720, 720
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Two Legs, Zero Rhythm")

clock = pg.time.Clock()  # controls the frame rate
font = pg.font.Font(None, 36)  # default font, size 36
bold_font = pg.font.SysFont(None, 36, pg.font.Font.bold)

#  character position
x, y = 100, 500
active_leg = None  # tracks which leg moved last

# game state
score = 0
combo = 0
last_leg = None
stumbles = 0
message = "Alternate A and L to walk!"

# rhythm settings
BPM = 100  # beats per minute
BEAT_INTERVAL = 60000 / BPM  # time between beats in milliseconds
start_time = pg.time.get_ticks()  # time when rhythm starts

running = True


def check_rhythm():
    now = pg.time.get_ticks()
    elapsed = now - start_time  # time since game started

    beat_position = elapsed % BEAT_INTERVAL  # position within current beat

    # find how close the key press was to the nearest beat
    error = min(beat_position, BEAT_INTERVAL - beat_position)

    if error < 80:
        return 300, "PERFECT!"
    elif error < 150:
        return 200, "GREAT!"
    elif error < 220:
        return 100, "GOOD!"
    else:
        return 0, "MISS!"


def take_step(leg):
    global x, score, combo, last_leg
    global stumbles, active_leg, message

    # pressing the same leg twice causes a stumble
    if leg == last_leg:
        combo = 0
        stumbles += 1
        message = "STUMBLE!"
        return  # exit without moving

    points, message = check_rhythm()  # get timing score and feedback

    x += 12  # correct alternating steps move character forward

    if points > 0:
        combo += 1
        score += points
    else:
        combo = 0  # missing the beat breaks the combo

    last_leg = leg  # remember for the next step
    active_leg = leg  # used to draw the moving leg


def draw_character():
    # head
    pg.draw.circle(screen, (255, 205, 150), (x + 25, y), 20)

    # body
    pg.draw.rect(screen, (230, 80, 90), (x + 5, y + 20, 40, 60))

    # change leg positions depending on which key was pressed
    left_offset = -15 if active_leg == "left" else 0
    right_offset = 15 if active_leg == "right" else 0

    # left leg (blue)
    pg.draw.line(
        screen, (60, 150, 255),
        (x + 15, y + 80),
        (x + 15 + left_offset, y + 120),
        9
    )

    # right leg (pink)
    pg.draw.line(
        screen, (255, 100, 170),
        (x + 35, y + 80),
        (x + 35 + right_offset, y + 120),
        9
    )


while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

        if event.type == pg.KEYDOWN:  # detect individual key presses
            if event.key == pg.K_a:
                take_step("left")
            elif event.key == pg.K_l:
                take_step("right")

    screen.fill((25, 25, 35))  # clear previous frame

    # draw ground
    pg.draw.rect(screen, (80, 180, 100), (0, 620, WIDTH, 100))

    draw_character()

    # create text surfaces
    score_text = font.render(f"Score: {score}", True, "white")
    combo_text = font.render(f"Combo: {combo}", True, "white")
    stumble_text = font.render(f"Stumbles: {stumbles}", True, "white")
    if message == "MISS!" or message == "STUMBLE!":
        message_text = font.render(message, True, "red")

        if message == "STUMBLE!":
            text_pos = 300
            p1 = pg.transform.scale(pg.image.load("Picture1.png"), (200,100))
            screen.blit(p1, (text_pos-40,110))
        else:
            text_pos = 330
            p1 = pg.transform.scale(pg.image.load("Picture1.png"), (120,100))
            screen.blit(p1, (text_pos-27,110))
            
            
    elif message == "GOOD!":
        message_text = font.render(message, True, "green1")
        text_pos = 320
    elif message == "GREAT!":
        message_text = font.render(message, True, "green2")
        text_pos = 310
    elif message == "PERFECT!":
        message_text = bold_font.render(message, True, "green3")
        text_pos = 300
    else:
        message_text = font.render(message, True, "white")
        text_pos = 200


    # display text at specified coordinates
    screen.blit(score_text, (20, 20))
    screen.blit(combo_text, (300, 20))
    screen.blit(stumble_text, (560, 20))
    screen.blit(message_text, (text_pos, 150))

    # calculate progress through the current beat (0 to 1)
    elapsed = pg.time.get_ticks() - start_time
    beat_phase = (elapsed % BEAT_INTERVAL) / BEAT_INTERVAL

    # circle shrinks as the next beat approaches
    radius = 15 + int(10 * (1 - beat_phase))
    pg.draw.circle(screen, "yellow", (360, 250), radius)
    pg.draw.circle(screen, "black", (360, 250), radius-5)
    pg.draw.circle(screen, "yellow", (360, 250), 10)

    pg.display.flip()  # update the screen
    clock.tick(60)  # limit to 60 FPS

pg.quit()