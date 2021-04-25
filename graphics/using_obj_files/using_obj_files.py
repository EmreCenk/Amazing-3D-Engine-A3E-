from graphics.shapes_2d import shape
from graphics.using_obj_files.parse_obj_files import parse_triangle_list


class obj_mesh(shape):

    def __init__(self, path_to_object, camera_position, color = (255,255,255)):
        super().__init__(color)
        self.path_to_object = path_to_object
        self.create_attributes(camera_position)

    def create_attributes(self, camera_position):
        self.triangles,self.vertices, self.normalized_and_translated_vertices = parse_triangle_list(self.path_to_object,
                                                                                                    camera_position,
                                                                                                    color = self.color)


    def wireframe_draw(self,window,camera_position,orthogonal=False): #We re-write the wireframe_draw function since
    #the original wireframe_drwa function uses edges (.obj does not have edges as afr as I know)

        for tri in self.triangles:
            tri.wireframe_draw(window,camera_position, orthogonal=orthogonal)
