from setuptools import setup, find_packages

with open('README.md') as readme_file:
    README = readme_file.read()

with open('HISTORY.md') as history_file:
    HISTORY = history_file.read()

setup_args = dict(
    name='vendor_color_swatches_py',
    version='0.0.0',
    description='Use color swatches/palettes from popular providers (Material Design, Ant, TailwindCSS)',
    long_description_content_type="text/markdown",
    long_description=README + '\n\n' + HISTORY,
    license='MIT',
    packages=find_packages(),
    author='Muhammad Aufa Rijal',
    author_email='rijalaufa0@gmail.com',
    keywords=['Color', 'MaterialDesign', 'Ant', 'AntDesign', 'MD', 'TailwindCSS', 'Tailwind', 'ColorPalettes', 'ColorSwatches'],
    url='https://github.com/aufarijaal/vendor_color_swaches_py',
    download_url='https://pypi.org/project/vendor_color_swaches_py/'
)


if __name__ == '__main__':
    setup(**setup_args)