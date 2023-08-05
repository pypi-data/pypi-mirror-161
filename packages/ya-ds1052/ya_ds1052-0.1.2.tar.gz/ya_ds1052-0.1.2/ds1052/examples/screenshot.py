#!/usrbin/env python
from io import BytesIO
import sys
try:
    from PIL import Image
except ModuleNotFoundError:
    print('Pillow must be insztalled to run this example.')
    sys.exit(1)
from ds1052 import DS1052

if __name__ == '__main__':
    with DS1052() as dso:
        screenshot = dso.screenshot()
        # Save as a file.
        with open('screenshot.bmp', 'wb') as f:
            f.write(screenshot)
        # Create a PIL image object and show it.
        img = Image.open(BytesIO(screenshot))
        img.show()
