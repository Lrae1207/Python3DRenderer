#include <stdio.h>
#include <string.h>
#include <stdbool.h>

// C equivalents to the python classes

struct vector3 {
    double x;
    double y;
    double z;
};

struct triangleFace {
    struct vector3 color;
    struct vector3 indices;
    struct vector3 shading_color;
    bool texture;
};

/*
    Code to replicate:

    for obj in self.objects:
            for face in obj.faces:
                    face.shading_color = (self.ambient_light.r/255, self.ambient_light.g/255, self.ambient_light.b/255)
        for light in self.objects:
            if light.type == "light":
                list = self.objects
                for obj in list:
                    if obj.visible & (obj.type != "light"):
                        vertices = []
                        for vertex in obj.vertices:
                            x, y, z = vertex.x, vertex.y, vertex.z
                            if not obj.locked:

                                vert = self.apply_changes(obj, vertex)
                                x, y, z = vert.x, vert.y, vert.z

                            vertices.append(self.perspective(light.position, light.light_direction, Vector3(x, y, z)))

                        for face in obj.faces:
                            offscreen = True
                            show = True
                            points = []
                            planepts = []
                            for index in face.indices:
                                x, y, z = vertices[index].x, vertices[index].y, vertices[index].z
                                if z < 0:
                                    show = False
                                points.append(((x * light.light_spread/z), (-y * light.light_spread/z)))
                                if (x * light.light_spread/z <= self.window.get_width()) & (y * light.light_spread/z <= self.window.get_height()):
                                    offscreen = False
                                planepts.append(Vector3(x, y, z))

                            area = shoelace(points)
                            if (area > 0) & (show & (not offscreen)):
                                dist_from_center = math.sqrt(points[0][0] * points[0][0] + points[0][1] * points[0][1])
                                distance = math.sqrt((light.position.x - planepts[0].x)*(light.position.x - planepts[0].x) + (light.position.y - planepts[0].y)*(light.position.y - planepts[0].y) + (light.position.z - planepts[0].z)*(light.position.z - planepts[0].z))
                                if dist_from_center == 0:
                                    brightness = area / distance / 999
                                else:
                                    brightness = area / distance / 10 / dist_from_center
                                r = face.shading_color[0] + (light.light_color.r/255) * brightness
                                g = face.shading_color[1] + (light.light_color.g/255) * brightness
                                b = face.shading_color[2] + (light.light_color.b/255) * brightness
                                face.shading_color = (r, g, b)
*/

// Algorithm for determining area of a polygon
// C-Implementation of the shoelace algorithm
double shoelace(char *a, char* b, int size) {
    // magic
    double *x = (double *)a;
    double *y = (double *)b;

    if (size == 0) {
        return 0;
    }

    double area = 0.0;
    for (int i = 0; i < size-1; ++i) {
        area += x[i] * y[i+1] - y[i] * x[i+1];
    }
    area += x[size-1] * y[0] - y[size-1] * x[0];
    return area;
}

float add_test(float a, float b) {
    return a + b;
}
