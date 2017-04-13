import tkinter as tk
import numpy as np
import time
import os
import sys
import argparse

######### CONSTANTS ##########
R_sun = 6.957e8 # Solar Radius in meters
M_sun = 2e30 # Solar Mass in kg
year = 365.25 * 24 * 60 * 60 # 1 year in s
grav_constant = 6.67e-11
km = 10**3.0 # 1km in m
################################################################################
class Particle:
    def __init__(self, init_pos, init_vel, mass, radius, index, colour='#000000'):
        """ Initialise the parameters of the particle """

        self.position = init_pos
        self.velocity = [y * km for y in init_vel]
        self.mass = mass * M_sun
        self.radius = radius * R_sun
        self.colour = colour
        self.index = index

        self.properties()
        self.draw()

    def properties(self):
        """ Print out the properties of the particle. """

        print("Particle:", self.index)
        print("Position:", self.position)
        print("Velocity:", self.velocity)

    def draw(self):
        """ Draw the particle at its position."""

        frame.create_oval((self.position[0] * scale) - (self.radius * scale) - 2,
                          (self.position[1] * scale) - (self.radius * scale) - 2,
                          (self.position[0] * scale) + (self.radius * scale) - 2,
                          (self.position[1] * scale) + (self.radius * scale) - 2,
                          tag="Particle" + str(self.index) + "Shape",
                          fill=self.colour, disableddash=True)

    def distance_to(self, other):
        """
        Calculates the distance between itself and another particle.

        Args:
            other (particle): The particle to find the distance to.

        Returns:
            distance (float): The distance between the particles

        """

        x1 = self.position[0]
        x2 = other.position[0]

        y1 = self.position[1]
        y2 = other.position[1]

        distance = np.sqrt((x2 - x1)**2.0 + (y2 - y1)**2.0)

        return(distance)

    def update_position(self, dt, cycle, tracks=False):
        """
        Calculates the new position of the particle and moves it there.
        Also draws the tracks of the previous particle position.

        """

        dx = self.velocity[0] * dt
        dy = self.velocity[1] * dt

        self.position[0] += dx
        self.position[1] += dy

        if cycle % (2) == 0 and tracks == True:
            frame.create_oval(self.position[0] * scale - 2,
                              self.position[1] * scale - 2,
                              self.position[0] * scale + 2,
                              self.position[1] * scale + 2,
                              tag="Particle" + str(self.index) + "Track",
                              fill=self.colour, disableddash=True)

        frame.move("Particle" + str(self.index) + "Shape", 
                   dx * scale, dy * scale)

################################################################################
def gravitation(particles, dt):
    """
    Calculates the gravitational force on each particle and changes
    the velocity of the particle appropriatly. 

    """
    for p1 in particles:
        for p2 in particles:
            if p1.index != p2.index: # No self gravity
                
                # Calculate the force on the particle                
                Ftop = grav_constant * p1.mass * p2.mass
                Fbot = p1.distance_to(p2)**2.0
                F = Ftop / Fbot
                                
                # Find direction of the force
                deltaX = p2.position[0] - p1.position[0]
                deltaY = p2.position[1] - p1.position[1]
                theta = np.arctan2(deltaX, deltaY)

                # Find the x,y components of the force
                Fx = F * np.sin(theta)
                Fy = F * np.cos(theta)

                # Calculate the acceleration of the particle
                ax = Fx / p1.mass
                ay = Fy / p1.mass

                # Calculate the new velocity of the particle
                p1.velocity[0] += (ax * dt)
                p1.velocity[1] += (ay * dt)

def draw_grid(frame, window_size, box_size, tick_num, tick_length):
    """ Draws the grid lines and values around the outside of the box."""

    # Difference between adjacent tick values
    tick_jump = box_size / tick_num

    # Physical Distance between ticks on the screen
    tick_spacing = window_size / tick_num


    # Draw the tick marks
    for i in range(tick_num):
        frame.create_line(0, i * tick_spacing,
                          tick_length, i * tick_spacing,
                          tag="LeftTicks", fill="#000000")

        frame.create_line(window_size - tick_length, i * tick_spacing,
                          window_size, i * tick_spacing,
                          tag="RightTicks", fill="#000000")

        frame.create_line(i * tick_spacing, 0,
                          i * tick_spacing, tick_length, 
                          tag="TopTicks", fill="#000000")

        frame.create_line(i * tick_spacing, window_size - tick_length,
                          i * tick_spacing, window_size,
                          tag="BottomTicks", fill="#000000")

    # Annotate the tick marks with values
    for i in range(tick_num - 1):
        # Left Tick Labels
        frame.create_text(tick_length + 5, (i + 1) * tick_spacing,
                          text=str("{0:.2f}".format(((i + 1) * tick_jump)/ R_sun)) + " Rsun",
                          anchor="w")
        # Top Tick Labels
        frame.create_text((i + 1) * tick_spacing, tick_length + 5, 
                          text=str("{0:.2f}".format(((i + 1) * tick_jump)/ R_sun)) + " Rsun",
                          anchor="c")

def time_display(frame, time):
    time_box_width = 120
    time_box_height = 20
    frame.create_rectangle(window_size - time_box_width - tick_length - 30, 
                           window_size - tick_length - 30,
                           window_size - tick_length - 30, 
                           window_size - time_box_height - tick_length - 30, 
                           outline="white", fill="white")

    frame.create_text(window_size - time_box_width - tick_length - 20, 
                      window_size - tick_length - 40, 
                      text=str("{0:.5f}".format(time)) + " yr", anchor="w")

################################################################################
if __name__ == "__main__":

    # Add the arguments for the user
    parser = argparse.ArgumentParser()
    parser.add_argument("--boxsize", help="The dimentions of the box in solar \
                         radii. Default: 1000", type=int)
    parser.add_argument("--timestep", help="The length of the time step \
                         between calculations", type=float)
    parser.add_argument("--windowsize", help="The height and width of the \
                         window in pixels. Default: 1000", type=int)
    parser.add_argument("--ticknum", help="The number of ticks on each side \
                         of the window. Default: 10", type=int)
    parser.add_argument("--ticklength", help="The length of each tick on the \
                         side of the window in pixels. Default: 20", type=int)

    args = parser.parse_args()

    # Setup defults and read arguments
    if args.windowsize:
        window_size = args.windowsize
    else:
        window_size = 1000

    if args.boxsize:
        box_size = args.boxsize * R_sun
        scale = window_size/box_size
    else:
        box_size = 1000 * R_sun
        scale = window_size/box_size

    if args.timestep:
        time_step = args.timestep
    else:
        time_step = 24 * 3600 # 0.1 day in seconds

    if args.ticknum:
        tick_num = args.ticknum
    else:
        tick_num = 10 

    if args.ticklength:
        tick_length = args.ticklength
    else:
        tick_length = 20 

    # Create window and frame 
    window = tk.Tk()
    window.title("N-Body Simulation")
    frame = tk.Canvas(window, height=str(window_size), width=str(window_size))
    frame.pack()
    frame.configure(background="white")

    draw_grid(frame, window_size, box_size, tick_num, tick_length)
  
    particle0 = Particle([box_size/2, box_size/2], [0,6.65], 9.9, 300, colour="#FF0000", index=0)
    particle1 = Particle([box_size/2 - 1400 * R_sun, box_size/2], [0,-59.85], 1.1, 30, colour="#00FF00", index=1)
    particle2 = Particle([box_size/2 - 500 * R_sun, box_size/2], [0,-36.79], 1.3, 30, colour="#0000FF", index=2)

    #particles = [particle0, particle1]
    particles = [particle0, particle1, particle2]


    max_cycles = 100000
    for cycle in range(max_cycles):
        for j in range(len(particles)):
            gravitation(particles, time_step)
            particles[j].update_position(time_step, cycle, tracks=False)

            current_time = cycle * time_step / year
            time_display(frame, current_time)
            frame.update()

    tk.mainloop()