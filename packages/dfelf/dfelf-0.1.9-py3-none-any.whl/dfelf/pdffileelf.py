import PyPDF2.generic
from PIL import Image
from PyPDF2.pdf import PdfFileWriter, PdfFileReader
from pdf2image import convert_from_bytes
from ni.config import Config
from dfelf import DataFileElf
from dfelf.commons import logger, is_same_image
from io import BytesIO
import shutil

HEX_REG = '{0:0{1}x}'


def is_same_pdf(file_1, file_2, ext: str = 'png', dpi: int = 300):
    df_elf = PDFFileElf()
    config = {
        'format': ext,
        'dpi': dpi,
        'pages': []
    }
    stream_1 = None
    stream_2 = None
    if isinstance(file_1, PdfFileReader):
        pdf_1 = file_1
    else:
        if isinstance(file_1, str):
            stream_1 = open(file_1, 'rb')
            pdf_1 = PdfFileReader(stream_1, strict=False)
        else:
            raise TypeError
    if isinstance(file_2, PdfFileReader):
        pdf_2 = file_2
    else:
        if isinstance(file_2, str):
            stream_2 = open(file_2, 'rb')
            pdf_2 = PdfFileReader(stream_2, strict=False)
        else:
            raise TypeError
    pages_1 = df_elf.to_image(pdf_1, True, **config)
    pages_2 = df_elf.to_image(pdf_2, True, **config)
    len_pages_1 = len(pages_1)
    len_pages_2 = len(pages_2)
    res = True
    if len_pages_1 == len_pages_2:
        for i in range(len_pages_1):
            if is_same_image(pages_1[i], pages_2[i]):
                pass
            else:
                res = False
    else:
        res = False
    if stream_1:
        stream_1.close()
    if stream_2:
        stream_2.close()
    return res


class PDFFileElf(DataFileElf):

    def __init__(self, output_dir=None, output_flag=True):
        super().__init__(output_dir, output_flag)

    def init_config(self):
        self._config = Config({
            'name': 'PDFFileElf',
            'default': {
                'reorganize': {
                    'input': 'input_filename',
                    'output': 'output_filename',
                    'pages': [1]
                },
                'image2pdf': {
                    'images': [],
                    'output': 'output_filename'
                },
                '2image': {
                    'input': 'input_filename',
                    'output': 'output_filename_prefix',
                    'format': 'png',
                    'dpi': 200,
                    'pages': [1]
                },
                'merge': {
                    'input': ['input_filename_01', 'input_filename_02'],
                    'output': 'output_filename'
                },
                'remove': {
                    'input': 'input_filename',
                    'output': 'output_filename',
                    'pages': [1]
                },
                'extract_images': {
                    'input': 'input_filename',
                    'output': 'output_filename_prefix',
                    'pages': [1]
                }
            },
            'schema': {
                'type': 'object',
                'properties': {
                    'reorganize': {
                        'type': 'object',
                        'properties': {
                            'input': {'type': 'string'},
                            'output': {'type': 'string'},
                            'pages': {
                                'type': 'array',
                                'items': {'type': 'integer'},
                                'minItems': 1
                            }
                        }
                    },
                    'image2pdf': {
                        'type': 'object',
                        'properties': {
                            'images': {
                                'type': 'array',
                                'items': {'type': 'string'}
                            },
                            'output': {'type': 'string'}
                        }
                    },
                    '2image': {
                        'type': 'object',
                        'properties': {
                            'input': {'type': 'string'},
                            'output': {'type': 'string'},
                            'format': {
                                "type": "string",
                                "enum": ['png', 'jpg', 'tif']
                            },
                            'dpi': {'type': 'integer'},
                            'pages': {
                                'type': 'array',
                                'items': {'type': 'integer'}
                            }
                        }
                    },
                    'merge': {
                        'type': 'object',
                        'properties': {
                            'input': {
                                'type': 'array',
                                'minItems': 2,
                                'items': {'type': 'string'}
                            },
                            'output': {'type': 'string'}
                        }
                    },
                    'remove': {
                        'type': 'object',
                        'properties': {
                            'input': {'type': 'string'},
                            'output': {'type': 'string'},
                            'pages': {
                                'type': 'array',
                                'items': {'type': 'integer'},
                                'minItems': 1
                            }
                        }
                    },
                    'extract_images': {
                        'type': 'object',
                        'properties': {
                            'input': {'type': 'string'},
                            'output': {'type': 'string'},
                            'pages': {
                                'type': 'array',
                                'items': {'type': 'integer'}
                            }
                        }
                    }
                }
            }
        })

    def to_output(self, task_key, **kwargs):
        if task_key == 'image2pdf':
            if self._output_flag:
                get_path = self.get_output_path
            else:
                get_path = self.get_log_path
            output_filename = get_path(self._config[task_key]['output'])
            kwargs['first_image'].save(output_filename, save_all=True, append_images=kwargs['append_images'])
        else:
            if task_key == '2image':
                kwargs['image'].save(kwargs['filename'])
            else:
                if self._output_flag:
                    get_path = self.get_output_path
                else:
                    get_path = self.get_log_path
                output_filename = get_path(self._config[task_key]['output'])
                output_stream = open(output_filename, 'wb')
                kwargs['pdf_writer'].write(output_stream)
                output_stream.close()

    def reorganize(self, input_obj: PdfFileReader = None, silent: bool = False, **kwargs):
        task_key = 'reorganize'
        self.set_config_by_task_key(task_key, **kwargs)
        if input_obj is None:
            if self.is_default(task_key):
                return None
            else:
                input_filename = self._config[task_key]['input']
                input_stream = open(input_filename, 'rb')
                pdf_file = PdfFileReader(input_stream)
        else:
            input_filename = '<内存对象>'
            pdf_file = input_obj
        pages = self._config[task_key]['pages']
        output = PdfFileWriter()
        res_output = PdfFileWriter()
        pdf_pages_len = pdf_file.getNumPages()
        ori_pages = range(1, pdf_pages_len + 1)
        for page in pages:
            if page in ori_pages:
                output.addPage(pdf_file.getPage(page - 1))
                res_output.addPage(pdf_file.getPage(page - 1))
            else:
                logger.warning([4000, input_filename, page])
        if silent:
            pass
        else:
            self.to_output(task_key, pdf_writer=output)
        if input_obj is None:
            pdf_file.stream.close()
        buf = BytesIO()
        res_output.write(buf)
        buf.seek(0)
        res = PdfFileReader(buf)
        return res

    def image2pdf(self, input_obj: list = None, silent: bool = False, **kwargs):
        task_key = 'image2pdf'
        self.set_config_by_task_key(task_key, **kwargs)
        if input_obj is None:
            if self.is_default(task_key):
                return None
            else:
                image_filenames = self._config[task_key]['images']
                num_filenames = len(image_filenames)
                if num_filenames > 0:
                    image_0 = Image.open(image_filenames[0]).convert('RGB')
                    image_list = []
                    for i in range(1, num_filenames):
                        image = Image.open(image_filenames[i]).convert('RGB')
                        image_list.append(image)
                else:
                    logger.warning([4001])
                    return None
        else:
            num_filenames = len(input_obj)
            if num_filenames > 0:
                image_0 = input_obj[0].copy().convert('RGB')
                image_list = []
                for i in range(1, num_filenames):
                    image = input_obj[i].copy().convert('RGB')
                    image_list.append(image)
            else:
                logger.warning([4001])
                return None
        if silent:
            pass
        else:
            self.to_output(task_key, first_image=image_0, append_images=image_list)
        buf = BytesIO()
        image_0.save(buf, format='PDF', save_all=True, append_images=image_list)
        buf.seek(0)
        pdf_file = PdfFileReader(buf)
        return pdf_file

    def to_image(self, input_obj: PdfFileReader = None, silent: bool = False, **kwargs):
        task_key = '2image'
        self.set_config_by_task_key(task_key, **kwargs)
        if input_obj is None:
            if self.is_default(task_key):
                return None
            else:
                input_filename = self._config[task_key]['input']
                input_stream = open(input_filename, 'rb')
                pdf_file = PdfFileReader(input_stream, strict=False)
        else:
            pdf_file = input_obj
        output_pages = self._config[task_key]['pages']
        pdf_pages_len = pdf_file.getNumPages()
        ori_pages = range(1, pdf_pages_len + 1)
        pdf_writer = PdfFileWriter()
        if (len(output_pages) == pdf_pages_len) or (0 == len(output_pages)):
            for page in ori_pages:
                pdf_writer.addPage(pdf_file.getPage(page - 1))
        else:
            for page in output_pages:
                if page in ori_pages:
                    pdf_writer.addPage(pdf_file.getPage(page - 1))
        buf = BytesIO()
        pdf_writer.write(buf)
        if input_obj is None:
            pdf_file.stream.close()
        buf.seek(0)
        pages = convert_from_bytes(buf.read(), self._config[task_key]['dpi'])
        buf.close()
        formats = {
            'png': 'PNG',
            'jpg': 'JPEG',
            'tif': 'TIFF'
        }
        output_filename_prefix = self._config[task_key]['output']
        image_format = formats[self._config[task_key]['format']]
        res = []
        num_pages = len(pages)
        if self._output_flag:
            get_path = self.get_output_path
        else:
            get_path = self.get_log_path
        if silent:
            for i in range(num_pages):
                buf = BytesIO()
                pages[i].save(buf, format=image_format)
                buf.seek(0)
                img_page = Image.open(buf)
                res.append(img_page)
        else:
            for i in range(num_pages):
                output_filename = get_path(output_filename_prefix + '_' + str(output_pages[i]) + '.' + image_format)
                buf = BytesIO()
                pages[i].save(buf, format=image_format)
                buf.seek(0)
                img_page = Image.open(buf)
                res.append(img_page)
                self.to_output(task_key, image=img_page, filename=output_filename)
        return res

    def merge(self, input_obj: list = None, silent: bool = False, **kwargs):
        task_key = 'merge'
        self.set_config_by_task_key(task_key, **kwargs)
        if input_obj is None:
            if self.is_default(task_key):
                return None
            else:
                input_filenames = self._config[task_key]['input']
                input_files = []
                for i in range(len(input_filenames)):
                    input_filename = input_filenames[i]
                    input_stream = open(input_filename, 'rb')
                    pdf_file = PdfFileReader(input_stream, strict=False)
                    input_files.append(pdf_file)
        else:
            input_files = input_obj
        output = PdfFileWriter()
        res_output = PdfFileWriter()
        for i in range(len(input_files)):
            pdf_file = input_files[i]
            pdf_pages = pdf_file.getNumPages()
            for page_index in range(pdf_pages):
                output.addPage(pdf_file.getPage(page_index))
                res_output.addPage(pdf_file.getPage(page_index))
        if silent:
            pass
        else:
            self.to_output(task_key, pdf_writer=output)
        if input_obj is None:
            for pdf_file in input_files:
                pdf_file.stream.close()
        buf = BytesIO()
        res_output.write(buf)
        buf.seek(0)
        res = PdfFileReader(buf)
        return res

    def remove(self, input_obj: PdfFileReader = None, silent: bool = False, **kwargs):
        task_key = 'remove'
        self.set_config_by_task_key(task_key, **kwargs)
        if input_obj is None:
            if self.is_default(task_key):
                return None
            else:
                input_filename = self._config[task_key]['input']
                input_stream = open(input_filename, 'rb')
                pdf_file = PdfFileReader(input_stream)
        else:
            input_filename = '<内存对象>'
            pdf_file = input_obj
        pages = self._config[task_key]['pages']
        output = PdfFileWriter()
        res_output = PdfFileWriter()
        pdf_pages_len = pdf_file.getNumPages()
        for page in range(pdf_pages_len):
            if (page + 1) in pages:
                pass
            else:
                output.addPage(pdf_file.getPage(page))
                res_output.addPage(pdf_file.getPage(page))
        if silent:
            pass
        else:
            self.to_output(task_key, pdf_writer=output)
        if input_obj is None:
            pdf_file.stream.close()
        buf = BytesIO()
        res_output.write(buf)
        buf.seek(0)
        res = PdfFileReader(buf)
        return res

    def extract_images(self, input_obj: PdfFileReader = None, silent: bool = False, **kwargs):
        task_key = 'extract_images'
        self.set_config_by_task_key(task_key, **kwargs)
        if input_obj is None:
            if self.is_default(task_key):
                return None
            else:
                input_filename = self._config[task_key]['input']
                input_stream = open(input_filename, 'rb')
                pdf_file = PdfFileReader(input_stream)
        else:
            input_filename = '<内存对象>'
            pdf_file = input_obj
        pages = []
        pdf_pages_len = len(self._config[task_key]['pages'])
        if pdf_pages_len == 0:
            pdf_pages_len = pdf_file.getNumPages()
            for page in range(pdf_pages_len):
                pages.append(pdf_file.getPage(page))
        else:
            for index in range(pdf_pages_len):
                pages.append(pdf_file.getPage(self._config[task_key]['pages'][index] - 1))
        count = 1
        filenames = []
        prefix = self._config[task_key]['output']
        for page in pages:
            # Images are part of a page's `/Resources/XObject`
            r = page['/Resources']
            if '/XObject' not in r:
                continue
            for k, v in r['/XObject'].items():
                vobj = v.getObject()
                if vobj['/Subtype'] != '/Image' or '/Filter' not in vobj:  # pragma: no cover
                    continue
                if vobj['/Filter'] == '/FlateDecode':
                    # 有关mode的说明参见https://pillow.readthedocs.io/en/stable/handbook/concepts.html#concept-modes
                    mode = 'RGB'
                    buf = vobj.getData()
                    size = tuple(map(int, (vobj['/Width'], vobj['/Height'])))
                    if vobj['/ColorSpace'] == '/DeviceRGB':
                        mode = 'RGB'
                    elif vobj['/ColorSpace'] == '/DeviceCMYK':  # pragma: no cover
                        # 以下未经验证
                        mode = 'CMYK'
                    elif vobj['/ColorSpace'] == '/DeviceGray':  # pragma: no cover
                        # 以下未经验证
                        mode = 'L'
                    elif isinstance(vobj['/ColorSpace'], PyPDF2.generic.ArrayObject):
                        if vobj['/ColorSpace'][0] == '/ICCBased':
                            if vobj['/ColorSpace'][1].getObject().getData().find(b'RGB') > 0:
                                mode = 'RGB'
                            elif vobj['/ColorSpace'][1].getObject().getData().find(b'GRAY') > 0:  # pragma: no cover
                                mode = 'L'
                            elif vobj['/ColorSpace'][1].getObject().getData().find(b'CMYK') > 0:  # pragma: no cover
                                # 以下未经验证
                                mode = 'CMYK'
                    img = Image.frombytes(mode, size, buf, decoder_name='raw')
                    filename = self.get_log_path(prefix + HEX_REG.format(count, 6) + '.png')
                    img.save(filename)
                    filenames.append(filename)
                    count = count + 1
                elif vobj['/Filter'] == '/DCTDecode':
                    filename = self.get_log_path(prefix + HEX_REG.format(count, 6) + '.jpg')
                    img = open(filename, 'wb')
                    img.write(vobj._data)
                    img.close()
                    filenames.append(filename)
                    count = count + 1
                elif vobj['/Filter'] == '/JPXDecode':
                    filename = self.get_log_path(prefix + HEX_REG.format(count, 6) + '.jp2')
                    img = open(filename, 'wb')
                    img.write(vobj._data)
                    img.close()
                    filenames.append(filename)
                    count = count + 1
                elif vobj['/Filter'] == '/CCITTFaxDecode':  # pragma: no cover
                    raise NotImplementedError
                    # 以下未经验证，待有需要再支持
                    # filename = self.get_log_path(prefix + HEX_REG.format(count, 6) + '.tiff')
                    # img = open(filename, 'wb')
                    # img.write(vobj.getData())
                    # img.close()
                    # filenames.append(filename)
                    # count = count + 1
                elif vobj['/Filter'] == '/LZWDecode':  # pragma: no cover
                    raise NotImplementedError
                    # 以下未经验证，待有需要再支持
                    # filename = self.get_log_path(prefix + HEX_REG.format(count, 6) + '.tif')
                    # img = open(filename, 'wb')
                    # img.write(vobj.getData())
                    # img.close()
                    # filenames.append(filename)
                    # count = count + 1
        res = []
        if silent or (not self._output_flag):
            for filename in filenames:
                image = Image.open(filename)
                res.append(image)
        else:
            base_log_path = self.get_log_path('')
            for filename in filenames:
                real_filename = self.get_output_path(filename.replace(base_log_path, ''))
                shutil.move(filename, real_filename)
                image = Image.open(real_filename)
                res.append(image)
        return res
