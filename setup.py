from setuptools import setup, find_packages

setup(
    name="CTkFileDialog",
    version="0.6.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "opencv-python-headless",
        "customtkinter",
        "Pillow",
        "CTkMessagebox @ git+https://github.com/sirthegamercoder/CTkMessagebox",
        "CTkToolTip",
        "typeguard",
    ],
    package_data={
        "CTkFileDialog": ["icons/*/*"],
    },
)
