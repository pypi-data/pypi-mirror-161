from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='get_block',
      version='0.0.3',
      description='Get details about a block provided in hex',
      long_description=readme(),
      long_description_content_type="text/markdown",
      classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9',
        'Topic :: Utilities',
      ],
      keywords='ethereum validator',
      author='Hawk94',
      author_email='tom@miller.mx',
      license='MIT',
      packages=['get_block'],
      install_requires=[
          'markdown',
      ],
      entry_points={
          'console_scripts': ['getBlock=get_block.cli:main'],
      },
      include_package_data=True,
      zip_safe=False)
