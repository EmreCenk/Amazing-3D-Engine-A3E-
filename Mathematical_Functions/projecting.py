from math import tan,radians

def convert_result(x,y,s_width,s_height):
    #the output of all the other functions take the center of the screen as the origin. Here, we convert it back such
# that the top left corner is the origin

    return [x+s_width/2,y+s_height/2]

def project_3d_point_to_2d(point,screen_width,screen_height,camera_position,orthogonal=False):



    x=point[0]
    y=point[1]
    z=point[2]

    cx=camera_position[0]
    cy = camera_position[1]
    d=camera_position[2]

    x+=cx
    y-=cy
    if z>=d:
        return [-10000,-10000]

    scale=100

    if orthogonal:
        return convert_result(
            x,y,screen_width,screen_height
        )
    return convert_result(scale*x/(z-d),        #projected x coordinate
                          scale*y/(z-d),        #projected y coordinate
                          screen_width,
                          screen_height)
def project_triangle(v1,v2,v3,screen_width,screen_height,camera_position):

    return (project_3d_point_to_2d(v1,screen_width,screen_height,camera_position),
            project_3d_point_to_2d(v2,screen_width,screen_height,camera_position),
            project_3d_point_to_2d(v3,screen_width,screen_height,camera_position))


def matrix_multiplication(matrix1,matrix2):

    #checking to see if it is possible to multiply the matrices:
    if len(matrix1[0])!=len(matrix2):
        raise ValueError("It is not possible to multiply these matrices. ")

    result = []

    rows1 = len(matrix1)
    # columns1 = len(matrix1[0])


    rows2 = len(matrix2)
    columns2 = len(matrix2[0])


    for i in range(rows1):
        current = []
        for j in range(columns2):
            current.append(0)

        result.append(current)



    for i in range(rows1):

        for j in range(columns2):

            for w in range(rows2):

                result[i][j] += matrix1[i][w] * matrix2[w][j]



    return result





if __name__ == '__main__':
    pass
    # m,mm=[[1,2,3]],[[4,3],[2,5],[6,8]]
    # print(matrix_multiplication(m,mm))