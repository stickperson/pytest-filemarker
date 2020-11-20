from setuptools import setup


with open('README.md', 'r') as f:
    readme = f.read()


setup(
    name="pytest-filemarker",
    version='0.1.0.dev2',
    description='A pytest plugin that runs marked tests when files change.',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Joe Meissler',
    author_email='meissler.dev@gmail.com',
    url='https://github.com/stickperson/pytest-filemarker',
    license='MIT',
    python_requires='>=3.6',
    packages=["pytest_filemarker"],
    package_data={'': ['LICENSE']},
    package_dir={'pytest_filemarker': 'pytest_filemarker'},
    entry_points={"pytest11": ["filemarker = pytest_filemarker.plugin"]},
    classifiers=["Framework :: Pytest"],
    install_requires=[
        'pytest'
    ]
)
