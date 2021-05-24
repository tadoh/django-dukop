from . import models


def dukop_sphere(request):
    print(models.Sphere.get_all_cached)
    return {
        "SPHERE": request.sphere,
        "SPHERES": models.Sphere.get_all_cached(),
    }
