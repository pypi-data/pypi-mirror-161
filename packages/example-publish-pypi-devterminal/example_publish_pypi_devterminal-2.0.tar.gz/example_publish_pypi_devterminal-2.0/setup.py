from setuptools import setup

with open('README.md', 'r') as f:
    long_desc = f.read()

setup(
    name='example_publish_pypi_devterminal',
    version='2.0',
    license='MIT',
    author="Ahmad Almohammad",
    author_email='almohammedahmed23@gmail.com',
    py_modules= ["hello_world"],
    package_dir={'': 'src'},
    url='https://github.com/Eng-Ahmad-Almohammad/pypi-test',
    keywords='example project',
    long_description= long_desc,
    long_description_content_type = 'text/markdown',
    install_requires = [
        "blessings ~= 1.7",
    ]

)