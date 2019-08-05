from setuptools import setup

setup(
    name='awsume-key-rotation-plugin',
    version='0.0.0',
    entry_points={
        'awsume': [
            'key_rotation = key_rotation'
        ]
    },
    author='Trek10, Inc',
    author_email='package-management@trek10.com',
    py_modules=['key_rotation'],
)
