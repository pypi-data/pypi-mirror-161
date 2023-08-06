from pathlib import Path
import urllib.parse
from django.http import Http404
from django.utils.module_loading import import_string
from django.utils.translation import ugettext_lazy as _
from django.http import JsonResponse
from django.conf import settings
from django.core.files import File
from .storage import StaticEditStorage
from io import BytesIO

from .forms import UploadFileForm
from PIL import Image


class NoImageException(Exception):
    pass


def get_storage_class():
    if hasattr(settings, 'CKEDITOR5_FILE_STORAGE'):
        return import_string(settings.CKEDITOR5_FILE_STORAGE)
    return import_string(settings.DEFAULT_FILE_STORAGE)


storage = get_storage_class()


def upload_s3(file):
    media_storage = StaticEditStorage()
    folder = getattr(settings, 'CKEDITOR_5_UPLOADS_FOLDER', 'django_ckeditor_5')
    path = f"{folder}/{file.name}"
    media_storage.save(path, file)
    file_url = media_storage.url(path)
    return file_url

def compress(image):
    im = Image.open(image)
    im_io = BytesIO() 
    #im = im.resize([500,500])
    im = im.convert("RGB")
    im = im.save(im_io,'JPEG', quality=75) 
    new_image = File(im_io, name=f"{image.name}.jpeg")
    return new_image


def image_verify(f):
    try:
        Image.open(f).verify()
    except IOError:
        raise NoImageException


def handle_uploaded_file(f):
    folder = getattr(settings, 'CKEDITOR_5_UPLOADS_FOLDER', 'django_ckeditor_5')
    uploads_path = Path(settings.MEDIA_ROOT, folder)
    fs = storage(location=uploads_path)
    filename = fs.save(f.name, f)
    return '/'.join([urllib.parse.urljoin(fs.base_url, folder), filename])


def upload_file(request):
    if request.method == 'POST' and request.user.is_staff:
        form = UploadFileForm(request.POST, request.FILES)
        try:
            image_verify(request.FILES['upload'])
        except NoImageException as ex:
            return JsonResponse({
                "error": {
                    "message": "{}".format(str(ex))
                }
            })
        if form.is_valid():
            file = compress(request.FILES['upload'])
            if settings.DEBUG is False:
                url = upload_s3(file=file)
            else:
                url = handle_uploaded_file(file)
            return JsonResponse({'url': url})
    raise Http404(_('Page not found.'))
