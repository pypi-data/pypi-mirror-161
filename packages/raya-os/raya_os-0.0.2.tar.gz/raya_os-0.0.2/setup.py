from setuptools import setup, find_packages


with open('README.md', 'r', encoding='utf-8') as f:
    readme = f.read()

setup(
    name='raya_os',
    packages=find_packages(),
    version='0.0.2',
    license='MIT',
    description='Raya OS skelaton',
    long_description=readme,
    author='Ofir Ozeri',
    author_email='ofiro@unlimited-robotics.com',
    url='', 
    python_requires=">=3.8",
    install_requires=[
        'rayasdk'
    ]  
)
