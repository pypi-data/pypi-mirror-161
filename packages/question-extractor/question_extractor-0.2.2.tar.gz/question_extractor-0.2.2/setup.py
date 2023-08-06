from setuptools import setup, find_packages

setup(
    name='question_extractor',
    version='0.2.2',
    license='MIT',
    author='Maisa',
    packages=find_packages('src'),
    package_dir={'':'src'},
    url='',
    keywords= 'question_extractor',
    install_requires=[
        'cleantext',
        'visualise-spacy-tree',
        'sentence-transformers',
        'spacy',

    ],

)