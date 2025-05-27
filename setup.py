from setuptools import setup, find_packages

setup(
    install_requires=[
        'numpy>=1.18.0',
        'opencv-python-headless>=4.5.0',
        'mavsdk>=3.0.1',
        'picamera2>=0.3.25'
        'shapely>=2.1.1'
        ],
    include_package_data=True,
    packages=find_packages(exclude=[
        'image_tools', 
        'test'
        ]),
)

