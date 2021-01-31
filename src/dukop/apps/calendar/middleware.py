from . import models


def sphere_middleware(get_response):
    """
    Sets the current sphere according to some cookie
    """

    def middleware(request):

        request.sphere = models.Sphere.get_by_id_or_default_cached(
            sphere_id=getattr(request.session, "dukop_sphere", None)
        )
        request.session["dukop_sphere"] = request.sphere.id
        response = get_response(request)

        return response

    return middleware
