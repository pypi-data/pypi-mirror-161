# NiuLab-crawl-YouTube-screenshots


NiuLab-crawl-YouTube-screenshots is a Python library that extracts clips from youtube videos with help of their ID.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install NiuLab-crawl-YouTube-screenshots.

```bash
pip install NiuLab-crawl-YouTube-screenshots
```

## Usage

```python
import importlib

imported_package=importlib.import_module("NiuLab-crawl-YouTube-screenshots.NiuLab-crawl-YouTube-screenshots")

imported_package.process_video(SOURCE FILE XLSX, DESTINATION FOLDER)

```
## Example Usage

```python
import importlib

imported_package=importlib.import_module("NiuLab-crawl-YouTube-screenshots.NiuLab-crawl-YouTube-screenshots")

imported_package.process_video(r'C:\Users\testUser\PycharmProjects\python_package_test\test_file.xlsx',
               r'C:\Users\testUser\PycharmProjects\outputFolder')

```

### Dependencies

To use **NiuLab-crawl-YouTube-screenshots** in your application developments, you must have installed the following dependencies to successfully use **NiuLab-crawl-YouTube-screenshots** : 
 
 - Pandas
 - OpenCV 
 - Youtube-Dl 
 - OpenPyXl


You can install all the dependencies by running the commands below 

**Pandas**
```bash
pip install pandas
```

**OpenCV**
```bash
pip install opencv-python
```
**Youtube-Dl**
```bash
pip install youtube-dl
```

**OpenPyXL**
```bash
 pip install openpyxl
```
## License
[MIT](https://choosealicense.com/licenses/mit/)

# NOTE : This package is under process of development.

## Some things to remember:

1. It supports "XLSX" filetype as input
2. Provide raw full pathname for input file and output destination folder
3. First column of excel file should contain all id for videos and it should have title as "video_id"

