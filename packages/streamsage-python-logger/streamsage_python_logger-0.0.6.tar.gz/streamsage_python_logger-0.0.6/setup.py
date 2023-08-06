import setuptools

setuptools.setup(name="streamsage_python_logger",
                 version="0.0.6",
                 author="streamsage",
                 description="python logger",
                 author_email="dev@streamsage.io",
                 packages=["streamsage_python_logger"],
                 install_requires=["fluent-logger==0.10.0",],
                 license="MIT")