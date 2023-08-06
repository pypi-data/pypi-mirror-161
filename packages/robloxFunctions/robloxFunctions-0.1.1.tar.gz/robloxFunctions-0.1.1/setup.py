import setuptools
  
with open("README.md", "r") as fh:
    description = fh.read()
  
setuptools.setup(
    name="robloxFunctions",
    version="0.1.1",
    author="PandaGamerYT",
    author_email="zachgameryt08@gmail.com",
    packages=["robloxFunctions"],
    description="A python package that uses roblox's API.",
    long_description=description,
    long_description_content_type="text/markdown",
    url="https://github.com/Zach-Tolentino-161/robloxFunctions/tree/master",
    license='MIT',
    python_requires='>=3.8',
    install_requires=['requests']
)
