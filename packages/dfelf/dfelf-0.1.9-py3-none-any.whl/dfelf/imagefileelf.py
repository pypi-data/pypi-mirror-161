import os
import cv2
import base64
import qrcode
from string import Template
from PIL import Image, ImageDraw, ImageFont
from ni.config import Config
from dfelf import DataFileElf
from dfelf.commons import logger, read_image
import numpy as np
import imghdr
import math
from io import BytesIO
from collections import Counter
try:
    import importlib.resources as pkg_resources
except ImportError:  # pragma: no cover
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources  # pragma: no cover
from dfelf.res import Noto_Sans_SC
DEFAULT_FONT = os.path.join(pkg_resources.files(Noto_Sans_SC), 'NotoSansSC-Regular.otf')


def most_used_color(img, left: int, upper: int, width: int, height: int):
    right = left + width
    lower = upper + height
    if isinstance(img, Image.Image):
        img_c = img.crop((left, upper, right, lower)).convert('RGB')
        count_by_color = Counter(img_c.getdata())
        return count_by_color.most_common()[0][0]
    if isinstance(img, np.ndarray):
        img_c = img[upper:lower, left:right, :]
        data = img_c.reshape(img_c.shape[0] * img_c.shape[1], img_c.shape[2])
        unique, counts = np.unique(data, axis=0, return_counts=True)
        high_freq, high_freq_element = counts.max(), unique[counts.argmax()]
        return high_freq_element
    else:
        logger.warning([3006])
        raise TypeError


def get_invert_color(img: Image.Image, left: int, upper: int, width: int, height: int):
    r, g, b = most_used_color(img, left, upper, width, height)
    color = (255 - r, 255 - g, 255 - b)
    return color


def hex_to_rgb(hex_color: str):
    color = hex_color.replace('#', '')
    return int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)


class ImageFileElf(DataFileElf):

    def __init__(self, output_dir=None, output_flag=True):
        super().__init__(output_dir, output_flag)

    def init_config(self):
        self._config = Config({
            'name': 'ImageFileElf',
            'default': {
                'favicon': {
                    'size': -1,
                    'input': 'input_filename'
                },
                'splice': {
                    'output': 'output_filename',
                    'input': [],
                    'width': 700,
                    'gap': 5,
                    'mode': 'v'
                },
                'watermark': {
                    'input': 'input_filename',
                    'output': 'output_filename',
                    'text': 'Krix.Tam',
                    'color': 'auto',
                    'font': DEFAULT_FONT,
                    'font_size': 24,
                    'x': 5,
                    'y': 5,
                    'alpha': 50
                },
                '2base64': {
                    'input': 'input_filename',
                    'css_format': False
                },
                'base64': {
                    'input': 'base64 string',
                    'output': 'output_filename'
                },
                'qrcode': {
                    'input': 'string',
                    'output': 'output_filename',
                    'border': 2,
                    'fill_color': "#000000",
                    'back_color': "#FFFFFF"
                },
                'dqrcode': {
                    'input': 'input_filename'
                },
                'resize': {
                    'input': 'input_filename',
                    'output': 'output_filename',
                    'scale': False,
                    'width': 28,
                    'height': 28,
                    'quality': 100,
                    'dpi': 1200
                },
                'crop': {
                    'input': 'input_filename',
                    'output': 'output_filename',
                    'mode': 0,
                    'location': [0, 0, 5, 5]
                },
                'fill': {
                    'input': 'input_filename',
                    'output': 'output_filename',
                    'mode': 0,
                    'location': [0, 0, 5, 5],
                    'unit': 5,
                    'type': 'M'
                }
            },
            'schema': {
                'type': 'object',
                'properties': {
                    'favicon': {
                        'type': 'object',
                        'properties': {
                            'size': {'type': 'number'},
                            'input': {'type': 'string'},
                        }
                    },
                    'splice': {
                        'type': 'object',
                        'properties': {
                            'output': {'type': 'string'},
                            'input': {
                                'type': 'array',
                                'items': {'type': 'string'}
                            },
                            'width': {'type': 'number'},
                            'gap': {'type': 'number'},
                            'mode': {
                                'type': 'string',
                                'pattern': '[aA]?[vVhH]{1}'
                            }
                        }
                    },
                    'watermark': {
                        'type': 'object',
                        'properties': {
                            'input': {'type': 'string'},
                            'output': {'type': 'string'},
                            'text': {'type': 'string'},
                            'color': {
                                'type': 'string',
                                'pattern': '([A-Fa-f0-9]{6})|(auto)'
                            },
                            'font': {'type': 'string'},
                            'font_size': {'type': 'number'},
                            'x': {'type': 'number'},
                            'y': {'type': 'number'},
                            'alpha': {
                                'type': 'number',
                                'minimum': 0,
                                'maximum': 100
                            }
                        }
                    },
                    '2base64': {
                        'type': 'object',
                        'properties': {
                            'input': {'type': 'string'},
                            'css_format': {"type": "boolean"}
                        }
                    },
                    'base64': {
                        'type': 'object',
                        'properties': {
                            'input': {'type': 'string'},
                            'output': {'type': 'string'}
                        }
                    },
                    'qrcode': {
                        'type': 'object',
                        'properties': {
                            'input': {'type': 'string'},
                            'output': {'type': 'string'},
                            'border': {
                                'type': 'integer',
                                'minimum': 0
                            },
                            'fill_color': {
                                'type': 'string',
                                'pattern': '^#[A-Fa-f0-9]{6}'
                            },
                            'back_color': {
                                'type': 'string',
                                'pattern': '^#[A-Fa-f0-9]{6}'
                            }
                        }
                    },
                    'dqrcode': {
                        'type': 'object',
                        'properties': {
                            'input': {'type': 'string'}
                        }
                    },
                    'resize': {
                        'type': 'object',
                        'properties': {
                            'input': {'type': 'string'},
                            'output': {'type': 'string'},
                            'scale': {"type": "boolean"},
                            'width': {
                                'type': 'integer',
                                'minimum': 1
                            },
                            'height': {
                                'type': 'integer',
                                'minimum': 1
                            },
                            'quality': {
                                'type': 'integer',
                                'minimum': 1,
                                'maximum': 100
                            },
                            'dpi': {'type': 'integer'}
                        }
                    },
                    'crop': {
                        'type': 'object',
                        'properties': {
                            'input': {'type': 'string'},
                            'output': {'type': 'string'},
                            'mode': {
                                'type': 'integer',
                                'minimum': 0,
                                'maximum': 1
                            },
                            'location': {
                                'type': 'array',
                                'minItems': 4,
                                'maxItems': 4,
                                'items': {'type': 'integer'}
                            }
                        }
                    },
                    'fill': {
                        'type': 'object',
                        'properties': {
                            'input': {'type': 'string'},
                            'output': {'type': 'string'},
                            'mode': {
                                'type': 'integer',
                                'minimum': 0,
                                'maximum': 1
                            },
                            'location': {
                                'type': 'array',
                                'minItems': 4,
                                'maxItems': 4,
                                'items': {'type': 'integer'}
                            },
                            'unit': {
                                'type': 'integer',
                                'minimum': 1
                            },
                            'type': {
                                'type': 'string',
                                'pattern': '(([mM]{1})|(^#[A-Fa-f0-9]{6}))'
                            }
                        }
                    }
                }
            }
        })

    def to_output(self, task_key, **kwargs):
        if task_key == 'base64':
            if self._output_flag:
                output_filename = self.get_output_path(self._config[task_key]['output'])
            else:
                output_filename = self.get_log_path(self._config[task_key]['output'])
            with open(output_filename, "wb") as fh:
                fh.write(kwargs['content'])
        else:
            if self._output_flag:
                output_filename = self.get_output_path(kwargs['filename'])
            else:
                output_filename = self.get_log_path(kwargs['filename'])
            if task_key == 'fill':
                cv2.imwrite(output_filename, kwargs['img'])
            else:
                if task_key == 'resize':
                    kwargs['img'].save(output_filename, quality=kwargs['quality'], dpi=(kwargs['dpi'], kwargs['dpi']))
                else:
                    kwargs['img'].save(output_filename)

    def to_favicon(self, input_obj: Image.Image = None, silent: bool = False, **kwargs):
        task_key = 'favicon'
        self.set_config_by_task_key(task_key, **kwargs)
        if input_obj is None:
            if self.is_default(task_key):
                return None
            else:
                input_filename = self._config[task_key]['input']
                img = Image.open(input_filename)
        else:
            img = input_obj.copy()
        if self._config.is_default([task_key, 'size']):
            icon_sizes = [16, 24, 32, 48, 64, 128, 255]
            res = []
            if silent:
                for x in icon_sizes:
                    img_resize = img.resize((x, x), Image.ANTIALIAS)
                    res.append(img_resize)
            else:
                for x in icon_sizes:
                    img_resize = img.resize((x, x), Image.ANTIALIAS)
                    output_filename = 'favicon' + str(x) + '.ico'
                    self.to_output(task_key, img=img_resize, filename=output_filename)
                    res.append(img_resize)
            return res
        else:
            favicon_size = self._config[task_key]['size']
            img_resize = img.resize((favicon_size, favicon_size), Image.ANTIALIAS)
            if silent:
                pass
            else:
                output_filename = 'favicon' + str(favicon_size) + '.ico'
                self.to_output(task_key, img=img_resize, filename=output_filename)
            return img_resize

    def splice(self, input_obj: list = None, silent: bool = False, **kwargs):
        task_key = 'splice'
        self.set_config_by_task_key(task_key, **kwargs)
        if input_obj is None:
            if self.is_default(task_key):
                return None
            else:
                num_img = len(self._config[task_key]['input'])
                input_images = []
                for i in range(num_img):
                    filename = self._config[task_key]['input'][i]
                    img = Image.open(filename)
                    input_images.append(img)
        else:
            num_img = len(input_obj)
            input_images = input_obj.copy()
        if num_img > 0:
            output_filename = self._config[task_key]['output']
            gap = self._config[task_key]['gap']
            images = []
            locations = []
            if self._config[task_key]['mode'].lower() == 'v':
                width = self._config[task_key]['width']
                width_img = 2 * gap + width
                height_img = gap
                y = gap
                locations.append(y)
                for i in range(num_img):
                    img = input_images[i].copy()
                    resize_height = int(img.size[1] * width / img.size[0])
                    height_img = height_img + resize_height + gap
                    images.append(img.resize((width, resize_height), Image.ANTIALIAS))
                    y = y + resize_height + gap
                    locations.append(y)
                ret_img = Image.new('RGBA', (width_img, height_img), (255, 255, 255))
                for i in range(num_img):
                    img = images[i]
                    loc = (gap, locations[i])
                    ret_img.paste(img, loc)
                if silent:
                    pass
                else:
                    self.to_output(task_key, img=ret_img, filename=output_filename)
                return ret_img
            elif self._config[task_key]['mode'].lower() == 'h':
                height = self._config[task_key]['width']
                width_img = gap
                height_img = 2 * gap + height
                x = gap
                locations.append(x)
                for i in range(num_img):
                    img = input_images[i].copy()
                    resize_width = int(img.size[0] * height / img.size[1])
                    width_img = width_img + resize_width + gap
                    images.append(img.resize((resize_width, height), Image.ANTIALIAS))
                    x = x + resize_width + gap
                    locations.append(x)
                ret_img = Image.new('RGBA', (width_img, height_img), (255, 255, 255))
                for i in range(num_img):
                    img = images[i]
                    loc = (locations[i], gap)
                    ret_img.paste(img, loc)
                if silent:
                    pass
                else:
                    self.to_output(task_key, img=ret_img, filename=output_filename)
                return ret_img
            elif self._config[task_key]['mode'].lower() == 'av':
                y = gap
                locations.append(y)
                width_img = 2 * gap
                max_width = 0
                for i in range(num_img):
                    img = input_images[i]
                    if img.size[0] > max_width:
                        max_width = img.size[0]
                    y = y + img.size[1] + gap
                    locations.append(y)
                width_img = width_img + max_width
                height_img = y
                ret_img = Image.new('RGBA', (width_img, height_img), (255, 255, 255))
                for i in range(num_img):
                    img = input_images[i]
                    loc = (gap, locations[i])
                    ret_img.paste(img, loc)
                if silent:
                    pass
                else:
                    self.to_output(task_key, img=ret_img, filename=output_filename)
                return ret_img
            elif self._config[task_key]['mode'].lower() == 'ah':
                x = gap
                locations.append(x)
                height_img = 2 * gap
                max_height = 0
                for i in range(num_img):
                    img = input_images[i]
                    if img.size[1] > max_height:
                        max_height = img.size[1]
                    x = x + img.size[0] + gap
                    locations.append(x)
                height_img = height_img + max_height
                width_img = x
                ret_img = Image.new('RGBA', (width_img, height_img), (255, 255, 255))
                for i in range(num_img):
                    img = input_images[i]
                    loc = (locations[i], gap)
                    ret_img.paste(img, loc)
                if silent:
                    pass
                else:
                    self.to_output(task_key, img=ret_img, filename=output_filename)
                return ret_img
        else:
            logger.warning([3000])
            return None

    def watermark(self, input_obj: Image.Image = None, silent: bool = False, **kwargs):
        task_key = 'watermark'
        self.set_config_by_task_key(task_key, **kwargs)
        if input_obj is None:
            if self.is_default(task_key):
                return None
            else:
                input_filename = self._config[task_key]['input']
                img = Image.open(input_filename)
        else:
            img = input_obj.copy()
        output_filename = self._config[task_key]['output']
        font_draw = ImageFont.truetype(self._config[task_key]['font'], self._config[task_key]['font_size'])
        text = self._config[task_key]['text']
        color = self._config[task_key]['color']
        width, height = img.size
        x = self._config[task_key]['x']
        y = self._config[task_key]['y']
        if x < 0:
            x = width + x
        if y < 0:
            y = height + y
        alpha = int(self._config[task_key]['alpha'] / 100 * 255)
        if color == 'auto':
            color = get_invert_color(img, x, y, 10, 10) + (alpha,)
        else:
            color = (int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16), alpha)
        loc = (x, y)
        txt_img = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(txt_img)
        draw.text(loc, text, fill=color, font=font_draw)
        img.paste(txt_img, (0, 0), txt_img)
        if silent:
            pass
        else:
            self.to_output(task_key, img=img, filename=output_filename)
        return img

    def qrcode(self, input_obj: str = None, silent: bool = False, **kwargs):
        task_key = 'qrcode'
        self.set_config_by_task_key(task_key, **kwargs)
        if input_obj is None:
            if self.is_default(task_key):
                return None
            else:
                input_string = self._config[task_key]['input']
        else:
            input_string = (input_obj + '.')[:-1]
        output_filename = self._config[task_key]['output']
        border_val = self._config[task_key]['border']
        f_color = self._config[task_key]['fill_color']
        b_color = self._config[task_key]['back_color']
        qr = qrcode.QRCode(border=border_val)
        qr.add_data(input_string)
        qr_image = qr.make_image(fill_color=f_color, back_color=b_color)
        if silent:
            pass
        else:
            self.to_output(task_key, img=qr_image, filename=output_filename)
        return qr_image.get_image()

    def decode_qrcode(self, input_obj=None, **kwargs):
        task_key = 'dqrcode'
        self.set_config_by_task_key(task_key, **kwargs)
        if input_obj is None:
            if self.is_default(task_key):
                return None
            else:
                input_filename = self._config[task_key]['input']
                image = cv2.imread(input_filename)
        else:
            if isinstance(input_obj, np.ndarray):
                image = input_obj.copy()
            else:
                if isinstance(input_obj, Image.Image):
                    image = read_image(input_obj)
                else:
                    logger.warning([3007])
                    raise TypeError
        detector = cv2.QRCodeDetector()
        data, vertices_array, binary_qrcode = detector.detectAndDecode(image)
        if vertices_array is None:
            logger.warning([3001])
            return None
        else:
            logger.info([3002, data])
            return data

    def to_base64(self, input_obj: bytes = None, **kwargs):
        task_key = '2base64'
        self.set_config_by_task_key(task_key, **kwargs)
        template = Template('"data:image/${extension};base64,${base64}"')
        if input_obj is None:
            if self.is_default(task_key):
                return None, None
            else:
                input_filename = self._config[task_key]['input']
                file_extension = os.path.splitext(input_filename)[1].replace('.', '')
                with open(input_filename, 'rb') as fh:
                    encoded = base64.b64encode(fh.read()).decode('ascii')
                    if self._config[task_key]['css_format']:
                        encoded = template.substitute(extension=file_extension, base64=encoded)
                    logger.info([3003, input_filename])
                    return encoded, file_extension
        else:
            buf = BytesIO(input_obj)
            buf.seek(0)
            file_extension = imghdr.what(buf)
            buf.close()
            encoded = base64.b64encode(input_obj).decode('ascii')
            if self._config[task_key]['css_format']:
                encoded = template.substitute(extension=file_extension, base64=encoded)
            logger.info([3003, '<内存对象>'])
            return encoded, file_extension

    def from_base64(self, input_obj: str = None, silent: bool = False, **kwargs):
        task_key = 'base64'
        self.set_config_by_task_key(task_key, **kwargs)
        if input_obj is None:
            if self.is_default(task_key):
                return None
            else:
                input_string = self._config[task_key]['input']
        else:
            input_string = (input_obj + '.')[:-1]
        res = base64.b64decode(input_string)
        if silent:
            pass
        else:
            self.to_output(task_key, content=res)
        buf = BytesIO(res)
        res_img = Image.open(buf)
        return res_img

    def resize(self, input_obj: Image.Image = None, silent: bool = False, **kwargs):
        task_key = 'resize'
        self.set_config_by_task_key(task_key, **kwargs)
        if input_obj is None:
            if self.is_default(task_key):
                return None
            else:
                input_filename = self._config[task_key]['input']
                img_ori = Image.open(input_filename)
        else:
            img_ori = input_obj.copy()
        output_filename = self._config[task_key]['output']
        width, height = img_ori.size
        quality = self._config[task_key]['quality']
        dpi = self._config[task_key]['dpi']
        if self._config[task_key]['scale']:
            width = math.floor(width * self._config[task_key]['width'] / 100.0)
            height = math.floor(height * self._config[task_key]['height'] / 100.0)
        else:
            width = self._config[task_key]['width']
            height = self._config[task_key]['height']
        img_resize = img_ori.resize((width, height), Image.ANTIALIAS)
        if silent:
            pass
        else:
            self.to_output(task_key, img=img_resize, filename=output_filename, quality=quality, dpi=dpi)
        return img_resize

    def crop(self, input_obj: Image.Image = None,  silent: bool = False, **kwargs):
        task_key = 'crop'
        self.set_config_by_task_key(task_key, **kwargs)
        if input_obj is None:
            if self.is_default(task_key):
                return None
            else:
                input_filename = self._config[task_key]['input']
                img_ori = Image.open(input_filename)
        else:
            img_ori = input_obj.copy()
        left = self._config[task_key]['location'][0]
        top = self._config[task_key]['location'][1]
        right = self._config[task_key]['location'][2]
        bottom = self._config[task_key]['location'][3]
        output_filename = self._config[task_key]['output']
        mode = self._config[task_key]['mode']
        if 1 == mode:
            right = left + right
            bottom = top + bottom
        if (left >= 0) and (top >= 0) and (right > left) and (bottom > top) and (right <= img_ori.size[0]) and (bottom <= img_ori.size[1]):
            img_result = img_ori.crop((left, top, right, bottom))
            if silent:
                pass
            else:
                self.to_output(task_key, img=img_result, filename=output_filename)
            return img_result
        else:
            logger.warning([3004, (left, top, right, bottom)])
            return None

    def fill(self, input_obj: np.ndarray = None, silent: bool = False, **kwargs):
        task_key = 'fill'
        self.set_config_by_task_key(task_key, **kwargs)
        if input_obj is None:
            if self.is_default(task_key):
                return None
            else:
                input_filename = self._config[task_key]['input']
                img_ori = cv2.imread(input_filename)
        else:
            img_ori = input_obj.copy()
        left = self._config[task_key]['location'][0]
        top = self._config[task_key]['location'][1]
        right = self._config[task_key]['location'][2]
        bottom = self._config[task_key]['location'][3]
        output_filename = self._config[task_key]['output']
        mode = self._config[task_key]['mode']
        unit = self._config[task_key]['unit']
        if 1 == mode:
            right = left + right
            bottom = top + bottom
        if (left >= 0) and (top >= 0) and (right > left) and (bottom > top) and (right <= img_ori.shape[1]) and (bottom <= img_ori.shape[0]):
            img_result = img_ori.copy()
            if len(self._config[task_key]['type']) == 1:
                for x in range(left, right, unit):
                    for y in range(top, bottom, unit):
                        img_result[y: y+unit, x: x+unit] = most_used_color(img_ori, x, y, unit, unit)
            else:
                r, g, b = hex_to_rgb(self._config[task_key]['type'])
                img_result[top: bottom, left: right] = [b, g, r]
            if silent:
                pass
            else:
                self.to_output(task_key, img=img_result, filename=output_filename)
            return img_result
        else:
            logger.warning([3005, (left, top, right, bottom)])
            return None
