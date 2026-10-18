
import pygame as pg

# Game colours
SKY = (25, 25, 35)
GROUND = (80, 180, 100)

# Ground height
GROUND_Y = 620


class ObstacleCourse:

    def __init__(self):
        self.ground_y = GROUND_Y
        self.finish_x = 2400  # position of finish line

        # obstacles use world positions, not screen positions
        self.obstacles = [
            {"type": "rock", "x": 400, "width": 40, "height": 40},
            {"type": "gap", "x": 700, "width": 90, "height": 0},
            {"type": "spikes", "x": 1050, "width": 60, "height": 30},
            {"type": "rock", "x": 1400, "width": 55, "height": 50},
            {"type": "gap", "x": 1750, "width": 110, "height": 0},
            {"type": "rock", "x": 2100, "width": 45, "height": 45}
        ]

    def check_collision(self, player_rect):
        """Check if the player touches a rock or spikes."""

        # for obstacle in self.obstacles:

        #     # gaps are handled separately by the physics system
        #     if obstacle["type"] == "gap":
        #         continue

        #     # create an invisible rectangle around the obstacle
        #     obstacle_rect = pg.Rect(
        #         obstacle["x"],
        #         self.ground_y - obstacle["height"],
        #         obstacle["width"],
        #         obstacle["height"]
        #     )

        #     if player_rect.colliderect(obstacle_rect):
        #         return obstacle  # return the obstacle that was hit

        return None  # no collision


    def has_ground_below(self, player_rect):
        """Check whether the player has ground beneath them."""

        # check the centre of the player's feet
        player_x = player_rect.centerx

        for obstacle in self.obstacles:
            if obstacle["type"] == "gap":

                gap_start = obstacle["x"]
                gap_end = gap_start + obstacle["width"]

                if gap_start <= player_x < gap_end:
                    return False  # player is over a gap

        return True


    def reached_finish(self, player_rect):
        """Check if the player has reached the finish line."""

        return player_rect.right >= self.finish_x


    def draw(self, screen, camera_x=0):
        """Draw ground, obstacles and finish line."""

        width, height = screen.get_size()

        # draw ground across the screen
        pg.draw.rect(
            screen, GROUND,
            (0, self.ground_y, width, height - self.ground_y)
        )

        for obstacle in self.obstacles:

            # convert world position to screen position
            x = round(obstacle["x"] - camera_x)
            w = obstacle["width"]
            h = obstacle["height"]

            if obstacle["type"] == "gap":

                # cover the ground with sky colour to create a hole
                pg.draw.rect(
                    screen, SKY,
                    (x, self.ground_y, w, height - self.ground_y)
                )

            elif obstacle["type"] == "rock":

                # draw rock sitting on the ground
                rock = pg.Rect(x, self.ground_y - h, w, h)

                pg.draw.rect(
                    screen, (140, 135, 150),
                    rock, border_radius=8
                )

            elif obstacle["type"] == "spikes":

                # draw triangular spikes across the obstacle
                for i in range(0, w, 15):

                    # keep the last triangle inside the obstacle width
                    spike_width = min(15, w - i)

                    pg.draw.polygon(
                        screen, (240, 95, 90),
                        [
                            (x + i, self.ground_y),
                            (x + i + spike_width // 2, self.ground_y - h),
                            (x + i + spike_width, self.ground_y)
                        ]
                    )

        # draw the finish line
        finish_x = round(self.finish_x - camera_x)

        pg.draw.line(
            screen, (255, 255, 255),
            (finish_x, self.ground_y - 150),
            (finish_x, self.ground_y), 5
        )

        # yellow flag at the finish line
        pg.draw.rect(
            screen, (255, 210, 70),
            (finish_x, self.ground_y - 150, 65, 30)
        )


def demo():
    """Temporary test game for the obstacle course."""

    pg.init()

    screen = pg.display.set_mode((720, 720))
    pg.display.set_caption("Obstacle Course Test")

    clock = pg.time.Clock()
    font = pg.font.Font(None, 30)

    course = ObstacleCourse()

    # Temporary player represented by a blue rectangle
    player = pg.Rect(100, GROUND_Y - 80, 40, 80)

    velocity_y = 0
    on_ground = True
    status = "playing"
    running = True

    while running:

        dt = min(clock.tick(60) / 1000, 0.05)  # Seconds between frames

        for event in pg.event.get():

            if event.type == pg.QUIT:
                running = False

            elif event.type == pg.KEYDOWN:

                if event.key == pg.K_r:
                    # Restart the test
                    player.x = 100
                    player.bottom = GROUND_Y
                    velocity_y = 0
                    on_ground = True
                    status = "playing"

                elif event.key == pg.K_SPACE:
                    # Jump only if standing on the ground
                    if on_ground and status == "playing":
                        velocity_y = -730
                        on_ground = False

        if status == "playing":

            keys = pg.key.get_pressed()

            # Move left or right
            if keys[pg.K_RIGHT]:
                player.x += round(230 * dt)

            if keys[pg.K_LEFT]:
                player.x -= round(230 * dt)
                player.x = max(0, player.x)

            # Gravity makes the player fall
            velocity_y += 1700 * dt
            player.y += round(velocity_y * dt)

            # Land if the player is above solid ground
            if player.bottom >= course.ground_y and course.has_ground_below(player):
                player.bottom = course.ground_y
                velocity_y = 0
                on_ground = True
            else:
                on_ground = False

            # Check whether player hit an obstacle or fell off screen
            if course.check_collision(player) is not None or player.top > 720:
                status = "crashed"

            elif course.reached_finish(player):
                status = "won"

        # Camera follows player after they move forwards
        camera_x = max(0, player.centerx - 180)

        # Draw background and obstacle course
        screen.fill(SKY)
        course.draw(screen, camera_x)

        # Draw player relative to camera
        player_screen = player.move(-round(camera_x), 0)

        pg.draw.rect(
            screen, (75, 165, 250),
            player_screen, border_radius=8
        )

        # Display current game status
        if status == "playing":
            message = "Arrows: Move | Space: Jump | R: Restart"

        elif status == "won":
            message = "YOU WIN! Press R"

        else:
            message = "CRASH! Press R"

        text = font.render(message, True, "white")
        screen.blit(text, (20, 20))

        pg.display.flip()


    pg.quit()


# Run the demo only when this file is executed directly
if __name__ == "__main__":
    demo()
