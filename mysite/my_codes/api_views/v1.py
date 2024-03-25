from io import BytesIO

from PIL import Image, UnidentifiedImageError
from PIL.Image import DecompressionBombError
from django.views.decorators.csrf import csrf_exempt

from my_codes.utils import ApiHttpResponse

from mysite.settings import MEDIA_ROOT

from my_codes.models import Post


@csrf_exempt
def user_upload_avatar(request):
    if request.method != 'POST':
        return ApiHttpResponse(status=405, error_message='Method not allowed. Use POST.')

    uploaded_file = request.FILES.get('avatar', None)

    if not uploaded_file:
        return ApiHttpResponse(status=400, error_message='File is not found.')

    if not uploaded_file.content_type.startswith('image/'):
        return ApiHttpResponse(status=415, error_message='File is not image.')

    user = request.user

    if not user.is_authenticated:
        return ApiHttpResponse(status=401, error_message='Unauthorized.')

    try:
        with BytesIO(uploaded_file.read()) as f:
            image = Image.open(f)
            image.verify()

            image = Image.open(f)

            image = image.resize((256, 256), Image.Resampling.LANCZOS)

            path = MEDIA_ROOT + '/avatars/' + str(user.id) + '.png'

            image.save(path)
        return ApiHttpResponse(status=200)
    except [UnidentifiedImageError, EOFError, DecompressionBombError]:
        return ApiHttpResponse(status=400, error_message='Image is invalid.')
    except Exception:
        return ApiHttpResponse(status=500, error_message='Server error.')


@csrf_exempt
def user_publish_post(request):
    if request.method != 'POST':
        return ApiHttpResponse(status=405, error_message='Method not allowed. Use POST.')

    user = request.user

    if not user.is_authenticated:
        return ApiHttpResponse(status=401, error_message='Unauthorized.')

    post = Post()
    post.user = request.user
    post.text = request.POST.get('text', '')
    post.save()

    """for uploaded_file in request.FILES:
        try:
            if uploaded_file.content_type.startswith('image/'):
                with BytesIO(uploaded_file.read()) as f:
                    image = Image.open(f)
                    image.verify()

                    image = Image.open(f)

                    image = image.resize((256, 256), Image.Resampling.LANCZOS)

                    path = MEDIA_ROOT + '/avatars/' + str(user.id) + '.png'

                    image.save(path)
                return ApiHttpResponse(status=200)
        except Exception:
            return ApiHttpResponse(status=400, error_message='File is invalid.')
    """