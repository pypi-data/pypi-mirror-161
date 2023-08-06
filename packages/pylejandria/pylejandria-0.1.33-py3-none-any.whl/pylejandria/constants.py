Number = int | float
Coordinate = tuple[int, int]
Array = list[int | float]

SETUP = f"""[metadata]
    name = module_name
    version = 0.0.1
    author = _____
    author_email = _____
    description = _____
    long_description = _____
    long_description_content_type = text/markdown
    url = _____
    project_urls =
        Bug Tracker = _____
    classifiers =
        Programming Language :: Python :: 3
        License :: OSI Approved :: MIT License
        Operating System :: OS Independent

    [options]
    package_dir =
        = src
    packages = find:
    python_requires = >= _____

    [options.packages.find]
    where = src"""

PYPROJECT = f"""[build-system]
    requires = [
        "setuptools>=42",
        "wheel"
    ]
    build-backend = "setuptools.build_meta"""

LICENSE = f"""MIT License
    Copyright (c) [_____] [_____]

    Permission is hereby granted, free of charge, to any person obtaining a
    copy of this software and associated documentation files (the "Software"),
    to deal in the Software without restriction, including without limitation
    the rights to use, copy, modify, merge, publish, distribute, sublicense,
    and/or sell copies of the Software, and to permit persons to whom the
    Software is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
    DEALINGS IN THE SOFTWARE."""

PHONE_EXTENSIONS = (
    "+1", "+7", "+20", "+27", "+30", "+31", "+32", "+33", "+34", "+36", "+39",
    "+40", "+41", "+43", "+44", "+45", "+46", "+47", "+48", "+49", "+51",
    "+52", "+53", "+54", "+55", "+56", "+57", "+58", "+60", "+61", "+62",
    "+63", "+64", "+65", "+66", "+81", "+82", "+84", "+86", "+90", "+91",
    "+92", "+93", "+94", "+95", "+98", "+211", "+212", "+213", "+216", "+218",
    "+220", "+221", "+222", "+223", "+224", "+225", "+226", "+227", "+228",
    "+229", "+230", "+231", "+232", "+233", "+234", "+235", "+236", "+237",
    "+238", "+239", "+240", "+241", "+242", "+243", "+244", "+245", "+246",
    "+247", "+248", "+249", "+250", "+251", "+252", "+253", "+254", "+255",
    "+256", "+257", "+258", "+260", "+261", "+262", "+263", "+264", "+265",
    "+266", "+267", "+268", "+269", "+290", "+291", "+297", "+298", "+299",
    "+350", "+351", "+352", "+353", "+354", "+355", "+356", "+357", "+358",
    "+359", "+370", "+371", "+372", "+373", "+374", "+375", "+376", "+377",
    "+378", "+380", "+381", "+382", "+383", "+385", "+386", "+387", "+389",
    "+420", "+421", "+423", "+500", "+501", "+502", "+503", "+504", "+505",
    "+506", "+507", "+508", "+509", "+590", "+591", "+592", "+593", "+594",
    "+595", "+596", "+597", "+598", "+599", "+670", "+672", "+673", "+674",
    "+675", "+676", "+677", "+678", "+679", "+680", "+681", "+682", "+683",
    "+685", "+686", "+687", "+688", "+689", "+690", "+691", "+692", "+850",
    "+852", "+853", "+855", "+856", "+880", "+886", "+960", "+961", "+962",
    "+963", "+964", "+965", "+966", "+967", "+968", "+970", "+971", "+972",
    "+973", "+974", "+975", "+976", "+977", "+992", "+993", "+994", "+995",
    "+996", "+998"
)

FILETYPES = {
    'PDF': ('.pdf',),
    'JPEG': ('.jpg', '.jpeg', '.jpe', '.jfif'),
    'PNG': ('.png',),
    'TIFF': ('.tiff', '.tif'),
    'ICO': ('.ico',),
    'WORD': ('.docx', '.docm', '.dotx', '.dotm'),
    'EXCEL': ('.csv', '.xlsx', '.xlsm', '.xltx', '.xltm', '.xlsb', '.xlam'),
    'PYTHON': ('.py', '.pyw', '.pyc', '.pyi', '.pyo', '.pyd'),
    'POWERPOINT': (
        '.pptx', '.pptm', '.potx', '.potm', '.ppam', '.ppsx', '.ppsm',
        '.sldx', '.sldm', '.thmx'
    ),
    'VIDEO': (
        '.asf', '.lsf', '.asx', '.bik', '.smk', '.div', '.divx', '.dvd',
        '.wob', '.ivf', '.m1v', '.mp2v', '.mp4', '.mpa', '.mpe', '.mpeg',
        '.mpg', '.mpv2', '.mov', '.qt', '.qtl', '.rpm', '.wm', '.wmv', '.avi'
    ),
    'AUDIO': (
        '.mp3', '.mid', '.midi', '.wav', '.wma', '.cda', '.ogg', '.ogm',
        '.aac', '.adt', '.adts', '.ac3', '.flac', '.mp4', '.aym'
    ),
    'IMAGE': (
        '.bmp', '.gif', '.jpeg', '.jpg', '.png', '.psd', '.ai', '.cdr',
        '.svg', '.raw', '.nef', '.jpe', '.jfif', '.ico', '.tiff', '.tif'
    )
}