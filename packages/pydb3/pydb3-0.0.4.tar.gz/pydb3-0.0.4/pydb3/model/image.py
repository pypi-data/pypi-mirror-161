import base64

from pydb3.model import Blob
from pydb3.utils.request import download


def save_image(image, image_path):
    image = str(image).encode("utf-8")
    image = base64.b64decode(image)
    with open(image_path, 'wb') as fp:
        fp.write(image)


class Image(Blob):
    type = 'image'

    def __set__(self, instance, value):
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        if "path=" in value:
            value = value.split('path=')[-1]
            save_image(self._value, value)
        elif "url=" in value:
            url = value.replace('url=', '')
            self._value = base64.b64encode(download(url)).decode('utf-8')
        else:
            if not self.null and value is None:
                raise ValueError("不能为空!")
            elif not isinstance(value, str):
                raise TypeError(f"{value}必须是字符串!")
            else:
                self._value = value
