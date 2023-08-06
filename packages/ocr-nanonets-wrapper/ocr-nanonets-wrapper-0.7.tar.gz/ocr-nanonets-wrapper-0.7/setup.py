from distutils.core import setup
setup(
  name = 'ocr-nanonets-wrapper',         # How you named your package folder (MyLib)
  packages = ['nanonets'],   # Chose the same as "name"
  version = '0.7',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Intelligent text and table extraction OCR tool which uses Nanonets OCR Engine to read and extract plain text and tables from image or pdf files with great accuracy',   # Give a short description about your library
  author = 'Karan Kalra',                   # Type in your name
  author_email = 'karankalra97w@gmail.com',      # Type in your E-Mail
  url = 'https://app.nanonets.com/#/signup?&utm_source=wrapper',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/karan-nanonets/ocr-nanonets/archive/refs/tags/v7.tar.gz',    # I explain this later on
  keywords = ['OCR', 'Text Extraction', 'Tesseract', 'Image to text', 'PDF to text', 'Image OCR', 'PDF OCR', 'Extract Table from PDF', 'Extract Table from image', 'Extract Table', 'Table Extraction', 'Extract Text from PDF', 'Extract Text from image', 'Extract Text'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'requests',
          'fpdf',
          'numpy',
          'pandas'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)
