
import hashlib
import os
import string
import setuptools

from pathlib import Path
from setuptools.command.build_py import build_py
from urllib.error import HTTPError
from urllib.request import urlopen

from hachoir.parser.program import ExeFile
from hachoir.parser.archive import CabFile
from hachoir.stream import FileInputStream


__all__ = ['setup']


DOWNLOAD_URL = "https://github.com/brechtm/corefonts/raw/master/{}"


def setup(name, version, archive, sha256sum, setup_file):
    entry_point_name = name.lower()
    identifier = ''.join(char for char in entry_point_name
                         if char in string.ascii_lowercase + string.digits)
    package_name = 'rinoh-typeface-{}'.format(identifier)
    package_dir = package_name.replace('-', '_')
    setup_path = os.path.dirname(os.path.abspath(setup_file))

    class BuildPy(build_py):
        """Download the MS Core fonts distribution archives and unpack them"""

        def get_package_dir(self, package):
            assert package == package_dir
            if not os.path.exists(package_dir):
                os.mkdir(package_dir)
            init_py = Path(package_dir) / '__init__.py'
            init_py.write_text(INIT_PY.format(name=name))
            return super().get_package_dir(package)

        def build_package_data(self):
            self.download_and_extract_fonts()
            super().build_package_data()

        def download_and_extract_fonts(self):
            (_, _, build_dir, _), = self.data_files
            assert download_file(archive) == sha256sum
            extract_fonts(archive, build_dir)

    setuptools.setup(
        cmdclass={'build_py': BuildPy},
        name=package_name,
        version=version,
        packages=[package_dir],
        package_data={package_dir: ['*.ttf']},
        install_requires=['rinohtype>=0.5.3'],
        entry_points={
            'rinoh.typefaces':
                ['{} = {}:typeface'.format(entry_point_name, package_dir)]
        },

        author='Brecht Machiels',
        author_email='brecht@mos6581.org',
        description=f'{name} typeface',
        long_description=open(os.path.join(setup_path, 'README.rst')).read(),
        url=f'https://github.com/brechtm/{package_name}',
        keywords='opentype font',
        license='Microsoft Core fonts for the Web – End-user license agreement',
        classifiers = [
            'Intended Audience :: Developers',
            'Intended Audience :: End Users/Desktop',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'Topic :: Text Processing :: Fonts',
        ]
    )


def download_file(filename):
    url = DOWNLOAD_URL.format(filename)
    print("Downloading", url)
    h = hashlib.sha256()
    try:
        with urlopen(url) as response:
            with open(filename, "wb") as f:
                while True:
                    buffer = response.read(8192)
                    h.update(buffer)
                    if not buffer:
                        break
                    f.write(buffer)
    except HTTPError as e:
        if e.code == 404:
            return None     # not found
        raise
    return h.hexdigest()


# based on https://github.com/vstinner/hachoir/issues/65#issuecomment-866965090
def extract_fonts(filename, dest_dir):
    print("Extracting fonts from", filename)
    f = FileInputStream(filename)
    exe = ExeFile(f)
    rsrc = exe["section_rsrc"]
    for content in rsrc.array("raw_res"):
        directory = content.entry.inode.parent
        name_field = directory.name.replace("directory", "name")
        if name_field in rsrc and rsrc[name_field].value == "CABINET":
            break
    else:
        raise Exception("No CABINET raw_res found")

    cab = CabFile(content.getSubIStream())
    cab["folder_data[0]"].getSubIStream()   # generate uncompressed_data
    folder_data = cab["folder_data[0]"].uncompressed_data
    for file in cab.array("file"):
        filename = file["filename"].value
        if not filename.lower().endswith(".ttf"):
            continue
        offset = file["folder_offset"].value
        size = file["filesize"].value
        file_path = Path(dest_dir) / filename
        file_content = folder_data[offset:offset+size]

        # temp workaround for https://github.com/vstinner/hachoir/issues/76
        if filename == 'Verdanab.TTF':
            file_content[0x56] = 0x0B
            file_content[0x57] = 0x50
        elif filename == 'Verdanai.TTF':
            file_content[0x56] = 0x0B

        with file_path.open("wb") as out:
            out.write(file_content)


INIT_PY = """
from pathlib import Path

from rinoh.font import Typeface
from rinoh.font.opentype import OpenTypeFont


__all__ = ['typeface']


DIR = Path(__file__).parent
FONTS = [OpenTypeFont(ttf) for ttf in [*DIR.glob('*.TTF'), *DIR.glob('*.ttf')]]

typeface = Typeface('{name}', *FONTS)
"""
