from setuptools import find_packages, setup
from io import open

readme = open('README.rst', encoding='utf-8').read()

setup(
    name='django-quiz-app',
    version='0.5.1',
    packages=find_packages(),
    include_package_data=True,
    license='MIT License',
    description='A configurable quiz app for Django.',
    long_description=readme,
    url='https://github.com/tomwalker/django_quiz',
    author='Tom Walker',
    author_email='tomwalker0472@gmail.com',
    zip_safe=False,
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
        'django-model-utils>=3.1.1',
        'Django>=1.8.19',
        'Pillow>=4.0.0'
    ],
    test_suite='runtests.runtests'
)
