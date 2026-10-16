from setuptools import setup, find_packages

setup(
    name="CTkFileDialog",
    version="0.4.6",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "opencv-python",
        "customtkinter",
        "Pillow",
        "CTkMessagebox",
        "CTkToolTip",
        "typeguard",
    ],
    package_data={
        "CTkFileDialog": ["icons/**/*"],
    },
)
