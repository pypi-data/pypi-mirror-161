from setuptools import setup, find_packages

setup(
    name='hrthy.core',
    version='1.0.81',
    author='Lorenzo Castelli',
    description='Core SDK for Hrthy Project',
    license='MIT',
    url='https://github.com/lorenzocastelli/hrthy-core',
    long_description='Core SDK for Hrthy Project',
    package_dir={"": "src"},
    project_urls={
        'Source': 'https://github.com/lorenzocastelli/hrthy-core',
    },
    packages=find_packages(where="src"),
    python_requires=">=3.8.3",
    install_requires=[
        'fastapi>=0.79.0,<1',
        'kafka-python>=2.0.2<3',
        'python-jose[cryptography]>=3.3.0,<4',
        'SQLAlchemy>=1.4.39,<2',
        'requests>=2.28.1<3'
    ],
)
