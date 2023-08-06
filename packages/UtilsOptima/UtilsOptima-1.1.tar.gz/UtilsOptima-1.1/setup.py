import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="UtilsOptima", # Replace with your own username
    version="1.1",
    author="Cesar Corbacho",
    author_email="cesar.corbacho@tecnoglass.com",
    description="Usado para los metodos y mensajes comunmente usados en nuestros proyectos.",
    url="https://github.com/tecnoglass-optima/utils_optima",
    download_url = 'https://github.com/tecnoglass-optima/utils_optima/tarball/1.0',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)