
import pygame as pg
import random
import math
from array import array 

from obstacles import ObstacleCourse

pg.init()
pg.mixer.init()

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
course = ObstacleCourse()  # create the obstacle course

status = "playing"

# jumping vars

vel = 5
grav = 1
jmp_strgth = -20
jumping = False

BPM = 100  
BEAT_INTERVAL = 60000 / BPM  
start_time = pg.time.get_ticks()  

running = True



def make_tone(frequency, duration, volume=0.25):
    sample_rate = 22050
    samples = array("h")

    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        fade = min(1, (duration - t) * 20)

        value = int(
            32767 * volume * fade
            * math.sin(2 * math.pi * frequency * t)
        )

        samples.append(value)

    return pg.mixer.Sound(buffer=samples.tobytes())


def make_drum(kind, duration, volume=0.5):
    sample_rate = 22050
    samples = array("h")

    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        fade = max(0, 1 - t / duration)

        if kind == "kick":
            frequency = 100 * math.exp(-t * 18) + 35
            value = math.sin(2 * math.pi * frequency * t)

        elif kind == "snare":
            # Noisy, sharp hit
            noise = random.uniform(-1, 1)
            tone = math.sin(2 * math.pi * 180 * t)
            value = 0.75 * noise + 0.25 * tone

        else:
            value = random.uniform(-1, 1)

        # Make the sound fade away
        value *= fade * volume
        samples.append(int(32767 * value))

    return pg.mixer.Sound(buffer=samples.tobytes())


kick_sound = make_drum("kick", 0.22, 0.8)
snare_sound = make_drum("snare", 0.16, 0.5)
hat_sound = make_drum("hat", 0.05, 0.25)



beat_sound = make_tone(440, 0.12, 0.35)
perfect_sound = make_tone(1000, 0.15)
good_sound = make_tone(650, 0.12)
miss_sound = make_tone(180, 0.20)
stumble_sound = make_tone(100, 0.30)


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
        stumble_sound.play()
        return  # exit without moving

    points, message = check_rhythm()  # get timing score and feedback
    if points == 300:
        perfect_sound.play()
    elif points == 200 or points == 100:
        good_sound.play()
    else:
        miss_sound.play()

    x += xDist  # correct alternating steps move character forward

    if points > 0:
        combo += 1
        score += points
    else:
        combo = 0  # missing the beat breaks the combo

    last_leg = leg  # remember for the next step
    active_leg = leg  # used to draw the moving leg



def draw_character():
    # Head
    pg.draw.circle(screen, (255, 205, 150), (x + 25, y), 20)

    # Hair
    pg.draw.arc(
        screen, (65, 40, 30),
        (x + 5, y - 20, 40, 28),
        0, 3.14, 6
    )

    # Eyes
    pg.draw.circle(screen, (40, 35, 35), (x + 19, y - 3), 2)
    pg.draw.circle(screen, (40, 35, 35), (x + 31, y - 3), 2)


    pg.draw.line(screen, (65, 40, 30), (15 + x, y - 13), (23 + x, y - 8), 4)
    pg.draw.line(screen, (65, 40, 30), (27 + x, y - 8), (35 + x, y - 13), 4)


    # Smile
    pg.draw.arc(
        screen, (100, 40, 40),
        (x + 17, y + 2, 16, 10),
        3.14, 6.28, 2
    )

    # Body / T-shirt
    pg.draw.rect(
        screen, (230, 80, 90),
        (x + 5, y + 20, 40, 50),
        border_radius=8
    )

    # Arms
    pg.draw.line(
        screen, (255, 205, 150),
        (x + 8, y + 30), (x - 2, y + 55), 7
    )
    pg.draw.line(
        screen, (255, 205, 150),
        (x + 42, y + 30), (x + 52, y + 50), 7
    )

    # Leg animation
    left_offset = -15 if active_leg == "left" else 0
    right_offset = 15 if active_leg == "right" else 0

    # Left leg
    pg.draw.line(
        screen, (60, 150, 255),
        (x + 15, y + 70),
        (x + 15 + left_offset, y + 110), 9
    )

    # Right leg
    pg.draw.line(
        screen, (255, 100, 170),
        (x + 35, y + 70),
        (x + 35 + right_offset, y + 110), 9
    )

    # Trainers
    pg.draw.ellipse(
        screen, (245, 245, 245),
        (x + 15 + left_offset, y + 111, 19, 9)
    )
    pg.draw.ellipse(
        screen, (245, 245, 245),
        (x + 35 + right_offset, y + 111, 19, 9)
)

last_beat = -1

while running:
    dt = min(clock.tick(60) / 1000, 0.05)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

        if event.type == pg.KEYDOWN:  # detect individual key presses
            if status == "playing":
                if event.key == pg.K_a:
                    take_step("left")
                elif event.key == pg.K_l:
                    take_step("right")

            if event.key == pg.K_r:
                x, y = 100, 500
                velocity_y = 0
                on_ground = True
                status = "playing"
                score = 0
                combo = 0
                last_leg = None
                active_leg = None
                stumbles = 0
                message = "Alternate A and L to walk!"
                start_time = pg.time.get_ticks()

    if status == "playing":

        player_rect = pg.Rect(round(x + 5), round(y - 20), 40, 140)

        if course.check_collision(player_rect) is not None or player_rect.top > HEIGHT:
            status = "crashed"
            message = "CRASH! Press R to restart"
        elif course.reached_finish(player_rect):
            status = "won"
            message = "YOU WIN! Press R to restart"

    camera_x = round(max(0, x + 25 - 180))  # camera follows character

    
    elapsed = pg.time.get_ticks() - start_time
    current_beat = int(elapsed // BEAT_INTERVAL)

    if current_beat != last_beat:
        if current_beat % 4 == 0 or current_beat % 4 == 2:
            kick_sound.play()
        else:
            snare_sound.play()
        hat_sound.play()

        last_beat = current_beat


    screen.fill((25, 25, 35))  # clear previous frame

    # draw ground
    course.draw(screen, camera_x)

    # detect jumping
    keys = pg.key.get_pressed()
    if keys[pg.K_a] & keys[pg.K_l] and not jumping: #last clause stops flying
        jumping = True
        vel = jmp_strgth

        if jumping:
            y += vel
            vel += grav
            xDist = 20
            if y >= 500: #through floor
                y = 500
                vel = 0
                jumping=False
                xDist=12

    camera_x = round(max(0, x + 25 - 180))  # camera follows character

    screen.fill((25, 25, 35))  # clear previous frame

    # draw ground
    course.draw(screen, camera_x)

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

pg.quit()
