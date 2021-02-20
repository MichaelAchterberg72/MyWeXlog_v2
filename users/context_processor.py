from .models import CustomUserSettings

def theme(request):
    theme = CustomUserSettings.objects.get(talent=request.user).theme

    return {'theme': theme}
