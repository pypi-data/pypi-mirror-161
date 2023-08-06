import setuptools
  
with open("README.md", "r") as fh:
    description = fh.read()
  
setuptools.setup(
    name="basicModules",
    version="1.0.2",
    author="PandaGamerYT",
    author_email="zachgameryt08@gmail.com",
    packages=["basicModules"],
    description="A python package gives basic modules.",
    long_description=description,
    long_description_content_type="text/markdown",
    license='MIT',
    url="https://github.com/Zach-Tolentino-161/robloxFunctions",
    python_requires='>=3.8',
    install_requires=['requests']
)
