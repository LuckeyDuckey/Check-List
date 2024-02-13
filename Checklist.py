import pygame, math, sys, cv2, numpy
from pygame.locals import *

pygame.init()
pygame.display.set_caption("Checklist")

display = pygame.display.set_mode((400, 650), 0 ,32)
clock = pygame.time.Clock()

font_small = pygame.font.SysFont("Verdana", 17)
font_big = pygame.font.SysFont("Verdana", 30)

dot = pygame.Surface((1,1))
dot.fill((255, 255, 255))

tasks = []

class task:
    def __init__(self, name):
        self.name = name
        self.complete = False

    def draw(self, surface, index, font):
        
        # Draw X at the end
        pygame.draw.line(surface, (150, 150, 150), (365, 280 + (60 * index)), (355, 290 + (60 * index)), width=3)
        pygame.draw.line(surface, (150, 150, 150), (355, 280 + (60 * index)), (365, 290 + (60 * index)), width=3)

        if not self.complete:
            
            # Draw circle
            pygame.draw.circle(surface, (175, 175, 175), (45, 285 + (60 * index)), 15, width=3)

            # Draw text
            rendered = font.render(self.name, True, (0, 0, 0))
            surface.blit(rendered, (70, 285 + (60 * index) - (rendered.get_height() * 0.5)))

        else:
            
            # Draw circle and tick
            pygame.draw.circle(surface, (255, 55, 55), (45, 285 + (60 * index)), 15)

            pygame.draw.line(surface, (255, 255, 255), (38, 284 + (60 * index)), (43, 289 + (60 * index)), width=4)
            pygame.draw.line(surface, (255, 255, 255), (43, 289 + (60 * index)), (51, 281 + (60 * index)), width=4)

            # Draw text and line through it
            rendered = font.render(self.name, True, (175, 175, 175))
            surface.blit(rendered, (70, 285 + (60 * index) - (rendered.get_height() * 0.5)))

            pygame.draw.line(surface, (150, 150, 150), (70, 285 + (60 * index)), (70 + rendered.get_width(), 285 + (60 * index)), width=2)

    def click(self, x, y, index):

        # Check if mouse is over circle
        if pygame.Rect(30, 270 + (60 * index), 30, 30).collidepoint(x, y):
            self.complete = not self.complete

class Blob:
    def __init__(self):
        self.pos = [200, 125]
        self.blob = self.generate_surface()

    def main(self, surface, mx, my):

        # Update position
        self.pos[0] += (mx - self.pos[0]) * 0.1
        self.pos[1] += (my - self.pos[1]) * 0.1

        # Render to diplay
        surface.blit(self.blob, (self.pos[0] - self.blob.get_width() / 2, self.pos[1] - self.blob.get_height() / 2))

    def generate_surface(self):
        #-------------

        # Create surface for gradient
        gradient = pygame.Surface((200, 200)).convert_alpha()
        step_size = 1.0 / 200

        # Define colors to interpolate beetween
        start_color = [255, 55, 55]
        end_color = [255, 55, 55]

        # Loop over every x co-od
        for x in range(200):

            # Calculate RGB values
            r = start_color[0] + int((end_color[0] - start_color[0]) * (x * step_size))
            g = start_color[1] + int((end_color[1] - start_color[1]) * (x * step_size))
            b = start_color[2] + int((end_color[2] - start_color[2]) * (x * step_size))

            # Render vaules
            pygame.draw.line(gradient, (r, g, b), (x, 0), (x, 200))

        #-------------
        
        # Create a new surface with an alpha channel
        mask = pygame.Surface((400, 400), pygame.SRCALPHA)

        # Calculate center position and radius
        center_x, center_y = 100, 100
        radius_x, radius_y = 75, 100

        # Draw an ellipse on the surface
        pygame.draw.ellipse(mask, (0, 0, 0, 0), (0, 0, mask.get_width(), mask.get_height()))
        pygame.draw.ellipse(mask, (255, 255, 255, 255), (center_x - radius_x, center_y - radius_y, radius_x * 2, radius_y * 2))

        # Create a new surface for the result
        ellipse_gradient = pygame.Surface((200, 200), pygame.SRCALPHA)

        # Blit the original image onto the result surface, using the alpha channel of the surface with the ellipse
        ellipse_gradient.blit(gradient, (0, 0))
        ellipse_gradient.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        #-------------

        # Make new larger surface to handle for blur
        blurred_gradient = pygame.Surface((600, 600), pygame.SRCALPHA)

        # Blit ellipse onto larger surf
        blurred_gradient.blit(ellipse_gradient, (200, 200))

        # Convert the blob surface to a NumPy array
        array = pygame.surfarray.array3d(blurred_gradient)

        # Apply Gaussian blur using OpenCV
        blurred_array = cv2.GaussianBlur(array, (601, 601), 0)

        # Convert the blurred array back to a Pygame surface
        result_gradient = pygame.surfarray.make_surface(blurred_array)

        #-------------

        return result_gradient

def drawArcCv2(surface, color, center, radius, width, end_angle):
    
    # Create cv2 surface and draw arc
    circle_image = numpy.zeros((radius * 2 + 4, radius * 2 + 4, 4), dtype = numpy.uint8)
    circle_image = cv2.ellipse(circle_image, (radius + 2, radius + 2), (radius - width // 2, radius - width // 2), 0, -90, end_angle, (*color, 255), width, lineType=cv2.LINE_AA)

    # Convert np array to pygame image
    circle_surface = pygame.image.frombuffer(circle_image.flatten(), (radius * 2 + 4, radius * 2 + 4), 'RGBA')

    # Draw final arc
    if end_angle > -90: surface.blit(circle_surface, circle_surface.get_rect(center = center), special_flags=pygame.BLEND_PREMULTIPLIED)

for i in range(5):
    tasks.append(task(f"Item {i + 1}"))

mouse_blob = Blob()

while True:

    clock.tick(30) # 30 FPS to keep system resource usage low

    # Get mouse pos
    mx, my = pygame.mouse.get_pos()

    # Set background and list
    display.fill((0, 0, 0))
    mouse_blob.main(display, mx, my)
    pygame.draw.rect(display, (255, 255, 255), pygame.Rect(10, 250, 380, 390), border_radius=10)

    for x in range(8):
            for y in range(5):
                display.blit(dot, (50 * x + 25, 50 * y + 25), special_flags=BLEND_RGB_ADD)

    # Update all the list items
    for i in range(len(tasks)):
        tasks[i].draw(display, i, font_small)

    # Get progress as percentage
    complete_percentage = sum(1 for task in tasks if task.complete) / len(tasks)

    # Draw progress Text
    rendered = font_big.render(f"{int(complete_percentage * 100)}%", True, (255,255,255))
    display.blit(rendered, (200 - (rendered.get_width() * 0.5), 125 - (rendered.get_height() * 0.5)))

    # Draw progress Circle
    pygame.draw.circle(display, (175, 175, 175), (200, 125), 80, width=10)
    drawArcCv2(display, (255, 55, 55), (200, 125), 80, 10, complete_percentage * 360 - 90)

    pygame.display.update()

    for event in pygame.event.get():
        
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        
        if event.type == MOUSEBUTTONDOWN:
            
            if event.button == 1:
                for i in range(len(tasks)):
                    tasks[i].click(mx, my, i)
