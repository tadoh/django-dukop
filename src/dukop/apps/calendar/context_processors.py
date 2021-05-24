from . import models


def dukop_sphere(request):
    return {
        "SPHERE": request.sphere,
        "SPHERES": models.Sphere.get_all_cached(),
    }
