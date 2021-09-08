import taichi as ti
from vector import *
import ray


# struct for hittable records
HitRecord = ti.types.struct(p=Point, normal=Vector, t=ti.f32, front_face=ti.i32)

@ti.func
def set_face_normal(r, outward_normal, rec: ti.template()):
    ''' pass in hit record by reference and set front face and normal '''
    rec.front_face = r.dir.dot(outward_normal) < 0.0
    rec.normal = outward_normal if rec.front_face == 1 else -outward_normal


@ti.data_oriented
class Sphere:
    ''' A class for holding data for a sphere. '''
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius

    @ti.func
    def hit(self, r, t_min, t_max, rec: ti.template()):
        ''' Intersect a ray with a given center and radius.
            Note we pass in the hit record by reference. '''
        hit = False

        oc = r.orig - self.center
        a = r.dir.norm_sqr()
        half_b = oc.dot(r.dir)
        c = oc.norm_sqr() - self.radius ** 2

        discriminant = half_b ** 2 - a * c
        # check hit only if discriminint is > 0
        if discriminant >= 0.0:
            sqrtd = ti.sqrt(discriminant)
            root = (-half_b - sqrtd) / a
            hit = (root >= t_min and root < t_max)
            if not hit:
                root = (-half_b + sqrtd) / a
                hit = (root >= t_min and root < t_max)

            if hit:
                rec.t = root
                rec.p = ray.at(r, rec.t)
                outward_normal = (rec.p - self.center) / self.radius
                set_face_normal(r, outward_normal, rec)

        return hit


@ti.data_oriented
class HittableList:
    def __init__(self):
        self.objects = []

    def add(self, object):
        self.objects.append(object)

    @ti.func
    def hit(self, r, t_min, t_max, rec: ti.template()):
        hit_anything = False
        closest_so_far = t_max
        temp_rec = HitRecord(p=Point(0.0), normal=Vector(0.0), t=0.0, front_face=1)

        for i in ti.static(range(len(self.objects))):
            if self.objects[i].hit(r, t_min, closest_so_far, temp_rec):
                hit_anything = True
                closest_so_far = temp_rec.t
                # have to manually copy the hit record
                rec.p = temp_rec.p
                rec.normal = temp_rec.normal
                rec.t = temp_rec.t
                rec.front_face = temp_rec.front_face

        return hit_anything
