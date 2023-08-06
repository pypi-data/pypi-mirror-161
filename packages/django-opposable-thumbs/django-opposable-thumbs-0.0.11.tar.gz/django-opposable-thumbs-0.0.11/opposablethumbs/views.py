from .opposablethumbs import OpposableThumbs


def opposablethumb(request):
    ot = OpposableThumbs(request.META["QUERY_STRING"])
    return ot.get_thumbnail()
