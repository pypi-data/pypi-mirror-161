import setuptools
import os

# print(os.path.join(os.getcwd(), 'README.md'))
# with open(os.path.join(os.getcwd(), 'README.md'), "r") as fh:
#     long_description = fh.read()
here = os.path.dirname(os.path.abspath(__file__))
setuptools.setup(
    name="vayaAuto",  # Replace with your own username
    version="0.0.10",
    author="System and Application team",
    author_email="Dor.Mesilati@leddartech.com",
    description="",
    # long_description=long_description,
    long_description='',
    long_description_content_type="text/markdown",
    url="",
    data_files=[],
    packages=setuptools.find_packages(),
    package_data={'vayaAuto.configurations': ['vayadrive_params.yaml']},

    include_package_data=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['PyYaml'],
    python_requires='>=3.6',

)