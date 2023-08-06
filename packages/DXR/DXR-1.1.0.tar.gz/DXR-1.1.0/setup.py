from setuptools import setup

setup(
    name='DXR',
    version='1.1.0',
    packages=['Dxr_mqtt', 'Dxr_log', 'Dxr_bytes', 'Dxr_utils', 'Dxr_video', 'Dxr_serial', 'Dxr_yaml'],
    install_requires=['paho-mqtt', 'pyyaml', 'opencv-python', 'pyserial'],
    author='luzhipeng',
    author_email='402087139@qq.com',
    license='MIT',
    url='http://pycn.me',
    description='DXR is a python library for DXR_mqtt',
)
