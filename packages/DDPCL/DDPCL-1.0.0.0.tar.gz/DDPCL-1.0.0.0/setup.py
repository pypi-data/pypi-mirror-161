from setuptools import setup, find_packages

setup(
    name='DDPCL',
    version='1.0.0.0',
    license='MIT',
    author="Anthony SIAMPIRINGUE",
    author_email='anthony.siampiringue@epita.fr',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='http://pypi.python.org/pypi/DDPCL/',
    keywords='drift detection CV bayesian recognition autolabeling',
    install_requires=[
          'opencv-python',
          'pandas',
          'numpy',
          'scipy',
          'scikit-learn',
          'shutils',
          'uuid',
          'pillow',
          'face_recognition',
          'matplotlib'
      ],

)