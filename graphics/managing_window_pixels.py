import pygame
from numpy import full
from typing import Sequence
import pygame
import pyximport
pyximport.install()
from cythonized_graphics.pixels import clear_z_buffer, efficient_clear_z_buffer, fill_screen

class WindowManager:
    #This class implements a z buffer

    def __init__(self,surface, height: int = None, width:int = None, background_color: Sequence = None) :
        if background_color is None:
            background_color = (0,0,0)

        if width is None or height is None:
            self.width, self.height = pygame.display.get_window_size() #Getting the pixel width and height of the curent
            # window
        else:
            self.width, self.height = width, height
        
        self.pixel_depths = full((self.width, self.height),float("inf"))

        self.pixels = pygame.surfarray.pixels3d(surface)
        

        self.changed_pixels = [] #We store the pixels that were changed so that the program doesn't loop through
        # every single pixel when resetting z buffer

        # for i in range(self.height):
        #     current = []
        #     for j in range(self.width):
        #         current.append(0) #set all the pixel values to infinity,
        #     self.changed_pixels.append(current)
    

    def draw_pixel(self, x:Sequence, y:Sequence, color:Sequence, depth:int = 0):
        # print(len(self.pixel_depths),len(self.pixel_depths[0]), x, y)
        if self.pixel_depths[x][y]<depth:
            return 

        self.pixel_depths[x][y] = depth
        #This pixel is closer
        self.pixels[x][y] = color

    def clear_z_buffer(self, background):
        clear_z_buffer(self.pixel_depths,float("inf"))




    # def render_all_pixels(self):

    #     for index in self.changed_pixels:
    #         self.draw_pixel(index[0], index[1], self.changed_pixels[index])



    @staticmethod
    def sort_v_by_ascending(arr: Sequence) -> Sequence:
        # basically an insertions sort
        # This method uses as little operations as possible
        # This function also changes the array in place, so be very carefull when using this function

        if (arr[1][1] < arr[0][1]):
            arr[0], arr[1] = arr[1], arr[0]

        if (arr[2][1] < arr[1][1]):
            arr[1], arr[2] = arr[2], arr[1]
            if (arr[1][1] < arr[0][1]):
                arr[1], arr[0] = arr[0], arr[1]

        return arr


    def draw_horizontal_line(self, window, color, distance:int, start_position: Sequence, end_position: Sequence, ):
        # FIXME: This function does not always work
        y = round(start_position[1])
        if y<0 or y>self.height:
            return 

        
        if start_position[0]<end_position[0]:
            new_s_x, new_e_x = round(start_position[0]), round(end_position[0])
        else:
            new_e_x, new_s_x = round(start_position[0]), round(end_position[0])
        
        if new_s_x<0:
            new_s_x = 0
        while new_s_x<new_e_x+1 and new_s_x<self.width:
            try:
                self.draw_pixel(new_s_x, y, color, distance)
            except:
                # print("WTF",new_s_x,y,len(self.pixels))
                pass
            new_s_x += 1


    def flat_fill_top(self, surface, distance: int, v1: Sequence, v2: Sequence, v3: Sequence, color:Sequence = (255,255,255)):
        
        """
        v1, v2: bottom left and bottom right corners of the triangle (in any order)
        v3: top of triangle

        Assumes that the y values of v1 and v2 are the same. 
        This function uses the fact that increasing y by one increases x by the inverse slope of the line:
        y=mx+b
        (y-b)/m = x
        (y+1-b)/m = x + (1/m)
        Using this fact, we loop through all the y values given, and find the respective x values"""

        try:
            inverse_m1 = (v1[0]-v3[0]) / (v1[1] - v3[1])
            inverse_m2 = (v2[0]-v3[0]) / (v2[1] - v3[1])
        except ZeroDivisionError:
            return 

        current_x_1 = v1[0]
        current_x_2 = v2[0]
        current_y = v1[1]

        while current_y>v3[1]:
            self.draw_horizontal_line(surface,color,distance, (current_x_1, current_y), (current_x_2, current_y))
            current_y -= 1
            current_x_1 -= inverse_m1
            current_x_2 -= inverse_m2

        
    def flat_fill_bottom(self, surface, distance:int, v1: Sequence, v2: Sequence, v3: Sequence, color:Sequence = (255,255,255)):
        """Goes through the pixels of a triangle which has a side paralel to the x axis.
        Assumes that the line v1-v2 is parralel to the x axis and v3[1]>v1[1]"""
        inverse_m2 = (v2[0]-v3[0]) / (v2[1] - v3[1])
        inverse_m1 = (v1[0]-v3[0]) / (v1[1] - v3[1])

        current_x_1 = v1[0]
        current_x_2 = v2[0]
        current_y = v1[1]

        while current_y<v3[1]:
            self.draw_horizontal_line(surface,color,distance, (current_x_1, current_y), (current_x_2, current_y))
            current_y += 1
            current_x_1 += inverse_m1
            current_x_2 += inverse_m2
    
    @staticmethod
    def roundv(v):
        return [
            round(v[0]), round(v[1])
        ]
    def draw_triangle(self,surface, v1: Sequence,v2: Sequence,v3: Sequence,
                            distance:float,
                            color = (255,255,255)) -> None: 


        """ This function rasterizes the given triangle and draws each pixel onto the screen.
        The pixel is not drawn if there is anything else in that pixel which is closer.
        The algorithm basically splits the triangle into 2 triangles where each triangle has one side parallel to the x axis."""
        # FIXME: The class/function does not work when implemented into managing_graphics
        # FIXME: Function does not work for all inputs. The following vertices do not work for instance:
        # [375, 203], [242, 272], [332, 346]
        # [7, 126] [132, 135] [418, 48]
        v1, v2, v3 = self.sort_v_by_ascending([self.roundv(v1),self.roundv(v2),self.roundv(v3)])
        #Now that they have been sorted, v1.y<v2.y<v3.y


        #If there are any horizontal edges, we treat them as special cases:
        if v3[1] == v2[1]:
            self.flat_fill_top(surface,distance, v2, v3 , v1, color)
            return 
        
        if v1[1] == v2[1]:
            self.flat_fill_bottom(surface,distance, v1, v2, v3, color)
            return 

        # General case is derived by splitting the triangle into two different triangles by drawing a horizontal 
        # line from v2 to the line v1-v3
        y = v2[1]


        try:
            m =  (v1[1]-v3[1]) / (v1[0]-v3[0])
            b = v1[1] - (v1[0]*m)
            v4 = [ (y-b)/m, y ]
        except ZeroDivisionError:
            v4 = [v1[0], y]

        self.flat_fill_top(surface,distance, v2,v4,v1, color)
        self.flat_fill_bottom(surface,distance, v2,v4,v3, color)

        


        
            


if __name__ == '__main__':
    from random import randint
    from time import perf_counter
    pygame.init()

    window = pygame.display.set_mode((500,500), pygame.RESIZABLE)
    screen = WindowManager(window,500,500)

    # for i in range(2):
    #     a = [randint(0,500),randint(0,500)]
    #     b = [randint(0,500),randint(0,500)]
    #     c = [randint(0,500),randint(0,500)]
    #     col = [randint(0,255),randint(0,255),randint(0,255),]
    #     screen.draw_triangle(window, a,b,c, 0, 0, 0, col)
    screen.draw_triangle(window,[250, 312], [225, 337], [250, 338] ,0, (255,0,0))
    #    screen.draw_triangle(window,[375, 203], [242, 272], [332, 346],0, 0, 0, (255,0,0))

    # pygame.draw.polygon(window, (255,0,255), [[250, 312], [225, 337], [250, 338]])
    
    pygame.display.update()
    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                break
        
