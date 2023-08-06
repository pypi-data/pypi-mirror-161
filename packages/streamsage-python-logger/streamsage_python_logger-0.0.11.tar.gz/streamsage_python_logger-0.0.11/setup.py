import setuptools

setuptools.setup(name="streamsage_python_logger",
                 version="0.0.11",
                 author="streamsage",
                 description="python logger",
                 author_email="dev@streamsage.io",
                 install_requires=["fluent-logger==0.10.0",
                                   "pydantic~=1.8.0",
                                   "python-dotenv==0.19.1"],
                 packages=setuptools.find_packages(where="streamsage_python_logger"),
                 license="MIT")