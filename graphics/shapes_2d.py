from Mathematical_Functions.shading import get_color
from Mathematical_Functions.projecting import project_3d_point_to_2d, translate, efficient_triangle_projection
from Mathematical_Functions.coordinate_system_3d import distance, rotate_around_self ,rotate,get_normal,is_visible,normalize_triangle_vertices, normalized
import pygame
from constants import conversion

pygame.font.init()
font = pygame.font.Font(None, 50)  # Setting the font


class shape:

    def __init__(self,color):
        self.color = color
        self.triangles = [] #all shapes are represented as combined triangles. This is the list of triangles
        self.edges = []
        self.vertices = []


    def wireframe_draw(self,window,camera_position,orthogonal=False):
        height = window.get_height()
        width = window.get_width()

        for edge in self.edges:
            p1=project_3d_point_to_2d(edge[0],width,height,camera_position,orthogonal)
            p2=project_3d_point_to_2d(edge[1],width,height,camera_position,orthogonal)
            pygame.draw.line(window,start_pos=p1,end_pos=p2,color=self.color)




    def draw_faces(self,window,camera_position,orthogonal=False):
        normalized_camera = normalized(camera_position)
        to_draw = []
        for triangle in self.triangles:

            translated_vert = triangle.get_translated(camera_position)
            if is_visible(translated_vert,normalized_camera):
                to_draw.append(
                    [triangle, distance(triangle.get_centroid(),camera_position),translated_vert]
                )

        to_draw.sort(key = lambda tri: tri[1], reverse=True)

        for liste in to_draw:
            new_color = get_color(liste[0],
                                    normalized_light_source=normalized_camera
                                    , rgb_colour = self.color)

            w, h = pygame.display.get_window_size()
            coordiantes = efficient_triangle_projection(liste[2],w,h)

            pygame.draw.polygon(window,points=coordiantes,color=new_color)

    def label_wireframe_corners(self,window,camera_position, orthogonal = False):
        height = window.get_height()
        width = window.get_width()

        for vertex in self.vertices:
            prompt = str(self.vertices.index(vertex) + 1 )
            asdf = project_3d_point_to_2d(vertex, width,height,camera_position,orthogonal)
            pygame.draw.circle(window, "white", asdf, 3)
            prompt_surface = font.render(prompt, True, (255, 255, 255))


            window.blit(prompt_surface, asdf)

    def draw_all_triangles(self,window,camera_position,orthogonal=False):

        for tri in self.triangles:
            tri.wireframe_draw(window,camera_position,orthogonal=orthogonal)

    def draw_all_visible_triangles(self,window,camera_position,orthogonal = False):
        for tri in self.triangles:
            if tri.is_visible(camera_position):
                tri.wireframe_draw(window, camera_position, orthogonal=orthogonal)

    def move(self,axis,amount):
        if axis in conversion:
            axis = conversion[axis]

        #This method updates both the self.v values and the self.vertices values
        for vert in self.vertices:
            vert[axis]+=amount
        
        

    def rotate(self,axis,angle):
        for vert in self.vertices:
            rotate(vert,axis,angle)


class triangle(shape):

    def __init__(self,v1,v2,v3,color = "white"):
        super().__init__(color = color )
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3

        self.vertices = [self.v1,self.v2,self.v3]
        self.edges = [
            [self.v1,self.v2],
            [self.v2,self.v3],
            [self.v3,self.v1]
        ]


    def get_projected_coordinates(self,camera_position,orthogonal=False):
        #30 operations

        w,h = pygame.display.get_window_size()

        return project_3d_point_to_2d(self.v1,w,h,camera_position,orthogonal=orthogonal),\
               project_3d_point_to_2d(self.v2,w,h,camera_position,orthogonal=orthogonal),\
               project_3d_point_to_2d(self.v3,w,h,camera_position,orthogonal=orthogonal)



    def get_normalized(self):
        return normalize_triangle_vertices(self.vertices)

    def get_normal(self):

        return get_normal(
            normalize_triangle_vertices(self.vertices)
        )

    def get_translated(self,camera_position):
        # 9 operations
        return translate(self.v1,camera_position),\
               translate(self.v2,camera_position),\
               translate(self.v3,camera_position),

    # def is_visible(self, normalized_camera_position, camera_position):
    #     #62 operations
    #     return is_visible(triangle_vertices = self.vertices,
    #                       camera_position = camera_position,
    #                       normalized_camera_position = normalized_camera_position)

    def get_centroid(self):
        # 9 operations
        return (
            (self.v1[0] + self.v2[0] + self.v3[0]) / 3,
            (self.v1[1] + self.v2[1] + self.v3[1]) / 3,
            (self.v1[2] + self.v2[2] + self.v3[2]) / 3,

        )
class quadrilateral(shape):
    def __init__(self,v1,v2,v3,v4,_color = "white", fill_bool = False):
        #This class basically exists for the sole purpose of converting quadrilaterals to triangles

        super().__init__(color=_color)
        self.convert_to_triangles(v1,v2,v3,v4)

    def convert_to_triangles(self,v1,v2,v3,v4):

        t1=triangle(
            v1 = v1,
            v2 = v2,
            v3 = v3, color = self.color,
        )


        t2 = triangle(
                v1 = v1,
                v2 = v3,
                v3 = v4, color=self.color,
            )

        self.triangles.append(t1)
        self.triangles.append(t2)

if __name__ == '__main__':
    import graphics.shapes_3d as sh3

    shift = 1
    side = 100

    v1, v2, v3, v4, v5, v6, v7, v8 = [shift, shift, side], [side, shift, side], [side, shift, shift], [shift, shift,
                                                                                                       shift], \
                                     [shift, side, side], [side, side, side], [side, side, shift], [shift, side, shift]
    self = sh3.rectangular_prism(v1, v2, v3, v4, v5, v6, v7, v8)
    print(self.triangles[0].edges,self.edges)

    self.rotate("x",60)

    print(self.triangles[0].edges,self.edges)