import setuptools

# pylint: disable=all
"""
python -m pip install --upgrade setuptools wheel twine
python setup.py sdist bdist_wheel

python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
python -m twine upload dist/*
export CURL_CA_BUNDLE="" && python -m twine upload --repository-url https://nexus-ci.corp.dev.vtb/repository/puos-pypi-lib/ dist/*
"""
setuptools.setup(
    name="vtb_secret_utils",
    version="0.0.2",
    author="VTB python team",
    author_email="python.team@vtb.ru",
    description="Secret utils",
    long_description="Утилитарный пакет, содержащий в себе интеграционный модуль с Vault.",
    keywords='python, microservices, utils, http',
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(exclude=['tests']),
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "hvac"
    ],
    extras_require={
        'test': [
            'pytest',
            'pytest-cov',
            'pytest-aiohttp',
            'pytest-mock',
            'pylint',
            'pytest-dotenv',
            'envparse',
            'asynctest',
        ]
    },
    python_requires='>=3.8',
)
