from setuptools import setup, find_packages
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
# with open("requirements.txt", "r", encoding="utf-8") as fh:
#     requirements = fh.read()
setup(
    name = 'aws-simple-auth',
    version = '0.2.0',
    author = 'Callum Smith',
    author_email = 'callumsmith@me.com',
    license = 'MIT',
    description = 'AWS CLI authentication helper to better manage MFA profiles',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = 'https://gitlab.com/xi0s/aws-simple-auth',
    py_modules = ['aws_simple_auth', 'app'],
    packages = find_packages(),
    install_requires = ['boto3'],
    python_requires='>=3.7',
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ],
    entry_points = '''
        [console_scripts]
        aws-simple-auth=aws_simple_auth:main
    '''
)