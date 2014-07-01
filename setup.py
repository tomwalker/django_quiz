import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-quiz-app',
    version='0.3.1',
    packages=['quiz', 'multichoice', 'true_false'],
    include_package_data=True,
    license='MIT License',
    description='A configurable quiz app for Django.',
    long_description=README,
    url='https://github.com/tomwalker/django_quiz',
    author='Tom Walker',
    author_email='tomwalker0472@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
      'django-model-utils == 2.0.3',
      'Django >= 1.5.1',
    ],
)
