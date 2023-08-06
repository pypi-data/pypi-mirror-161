import setuptools

setuptools.setup(name="streamsage_python_logger",
                 version="0.0.12",
                 author="streamsage",
                 description="python logger",
                 author_email="dev@streamsage.io",
                 packages=["streamsage_python_logger"],
                 package_dir={"": "src"},
                 install_requires=["fluent-logger==0.10.0",
                                   "pydantic~=1.8.0",
                                   "python-dotenv==0.19.1"],
                 license="MIT")