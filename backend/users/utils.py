from .models import Institute


def validate_institute(request):
    instu_id = request.GET.get('instu_id')
    if not instu_id:
        return False
    try:
        institute = Institute.objects.get(instu_id=instu_id)
        return institute
    except Institute.DoesNotExist:
        return False