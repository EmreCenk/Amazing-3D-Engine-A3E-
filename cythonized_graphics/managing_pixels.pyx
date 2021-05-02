import pygame
from pygame import Surface
from numpy import full, array, double, ndarray, ubyte

from libc.math cimport round
from pixels import clear_z_buffer, efficient_clear_z_buffer, fill_screen

cdef class WindowManager:
    #This class implements a z buffer

    cdef int width
    cdef int height
    cdef double[:, :] pixel_depths
    cdef unsigned char[:, :, :] pixels

    
    def __init__(self, unsigned char[:, :, :] _pixels, int _height, int _width, unsigned char[:] background_color) :


        self.width = _width
        self.height = _height
        self.pixel_depths = full((self.width, self.height),float("inf"))

        self.pixels = _pixels
        
    cdef void draw_pixel(self, int x, int y, unsigned char[:] color, int depth):
        if self.pixel_depths[x][y]<=depth:
            return 

        self.pixel_depths[x][y] = depth
        self.pixels[x][y][0] = color[0]
        self.pixels[x][y][1] = color[1]
        self.pixels[x][y][2] = color[2]

    cpdef clear_z_buffer(self,):
        clear_z_buffer(self.pixel_depths,float("inf"))
    

    cdef void sort_v_by_ascending(self, float arr[3][3]):
        # basically a very efficient insertion sort
        # This method uses as little operations as possible (3 operations)
        # This function also changes the array in place, so be very carefull when using this function
        if (arr[1][1] < arr[0][1]):
            arr[0], arr[1] = arr[1], arr[0]

        if (arr[2][1] < arr[1][1]):
            arr[1], arr[2] = arr[2], arr[1]
            if (arr[1][1] < arr[0][1]):
                arr[1], arr[0] = arr[0], arr[1]



    cpdef void draw_horizontal_line(self, window, unsigned char[:] color, int distance, double[:] start_position, double[:] end_position ):


        cdef double y
        cdef double new_e_x
        cdef double new_s_x
        y = round(start_position[1])
        if y<0 or y>self.height:
            return 

        
        #Check to see which one is on the left:
        #The while loop loops from left to right (new_s_x is starting position, new_e_x is ending position)

        if start_position[0]<end_position[0]:
            new_s_x = round(start_position[0])
            new_e_x = round(end_position[0])
        else:
            new_e_x = round(start_position[0])
            new_s_x = round(end_position[0])
        
        if new_s_x<0:
            new_s_x = 0
        while new_s_x<new_e_x+1 and new_s_x<self.width:
            
            self.draw_pixel(int(new_s_x), int(y), color, distance)

            new_s_x += 1

    cpdef void flat_fill_top(self, surface, int distance, double[:] v1, double[:] v2, double[:] v3, unsigned char[:] color):
    
        
        """
        v1, v2: bottom left and bottom right corners of the triangle (in any order)
        v3: top vertex of triangle
        
        This is a helper method for the "draw_triangle" method. It is not meant to be used standalone

        Assumes that the y values of v1 and v2 are the same. 
        This function uses the fact that increasing y by one increases x by the inverse slope of the line:
        y=mx+b
        (y-b)/m = x
        (y+1-b)/m = x + (1/m)
        Using this fact, we loop through all the y values given, and find the respective x values"""
        
        cdef double inverse_m1, inverse_m2, current_x_1, current_x_2, current_y
        
        cdef double initial[2]
        cdef double final[2]

        if v1[1] == v3[1] or v2[1] == v3[1]:
            return 
        

        inverse_m1 = (v1[0]-v3[0]) / (v1[1] - v3[1])
        inverse_m2 = (v2[0]-v3[0]) / (v2[1] - v3[1])

        current_x_1 = v1[0]
        current_x_2 = v2[0]
        current_y = v1[1]

        
        while current_y>v3[1]:
            initial[0] = current_x_1
            initial[1] = current_y
            final[0] = current_x_2
            final[1] = current_y

            self.draw_horizontal_line(surface,color,distance, initial, final)
            current_y -= 1
            current_x_1 -= inverse_m1
            current_x_2 -= inverse_m2