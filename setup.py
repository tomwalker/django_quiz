from io import open

from setuptools import find_packages, setup

readme = open("README.rst", encoding="utf-8").read()

setup(
    name="django-quiz-app",
    version="0.6.0-rc0",
    packages=find_packages(),
    include_package_data=True,
    license="MIT License",
    description="A configurable quiz app for Django.",
    long_description=readme,
    url="https://github.com/tomwalker/django_quiz",
    author="Tom Walker",
    author_email="tomwalker0472@gmail.com",
    zip_safe=False,
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    install_requires=[
        "Django>=2.2",
        "Pillow>=4.0.0",
        "django-parler>=2.2,<2.3",
        "django-polymorphic",
        "django-jsonfield-backport",
    ],
    test_suite="runtests.runtests",
)
