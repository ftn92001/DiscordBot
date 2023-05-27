from django.shortcuts import render

from .services.ptt_beauty import get_beauty_imgs

# Create your views here.

def home_view(request):
    image_src, image_name, urls = get_beauty_imgs(1)
    return render(request, "index.html", {
        "images": zip(image_src, image_name, urls),
    })
