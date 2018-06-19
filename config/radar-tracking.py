"""Utils for the relations of the radar tracking model."""

def sign(p1, p2, p3):
    """Returns the position (in terms of left and right) of p1 given the line
    defined by p2 and p3.

    https://www.gamedev.net/forums/topic/295943-is-this-a-better-point-in-triangle-test-2d/

    """
    return (p1[0] - p3[0]) * (p2[1] - p3[1]) \
           - (p2[0] - p3[0]) * (p1[1] - p3[1])

def is_point_in_triangle(pt, v1, v2, v3):
    """Returns True if the 2D point pt is within the triangle defined by v1-3.

    https://www.gamedev.net/forums/topic/295943-is-this-a-better-point-in-triangle-test-2d/

    """
    b1 = sign(pt, v1, v2) < 0.0
    b2 = sign(pt, v2, v3) < 0.0
    b3 = sign(pt, v3, v1) < 0.0
    return ((b1 == b2) and (b2 == b3))

def translate(point, translation):
    """Translates a 2D point."""
    px, py = point
    tx, ty = translation
    return [px + tx, py + ty]

def rotate(origin, point, angle):
    """Rotate a 2D point counterclockwise around the given origin.

    origin -- 2D vector, origin of the rotation.
    point -- 2D vector, point to rotate.
    angle -- Angle in radians.

    https://stackoverflow.com/questions/34372480/rotate-point-about-another-point-in-degrees-python?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa

    """
    import math
    ox, oy = origin
    px, py = point
    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return [qx, qy]

def in_field_of_view(point, location, heading, radius, angle):
    # approximate field of view with a triangle
    import math
    v1 = location
    vt = translate(v1, [radius, 0])
    v2 = rotate(location, vt, heading - angle/2)
    v3 = rotate(location, vt, heading + angle/2)
    return is_point_in_triangle(point, v1, v2, v3)
