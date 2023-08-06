import setuptools

# Reads the content of your README.md into a variable to be used in the setup below
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='latent_ideology',                           # should match the package folder
    packages=['latent_ideology'],                     # should match the package folder
    version='0.0.5',                                # important for updates
    license='MIT',                                  # should match your chosen license
    description='Latent ideology method',
    long_description=long_description,              # loads your README.md
    long_description_content_type="text/markdown",  # README.md is of type 'markdown'
    author='Fede Moss',
    author_email='fedemoss@gmail.com',
    url='https://github.com/fedemoss', 
    project_urls = {                                # Optional
        "Bug Tracker": "https://https://github.com/fedemoss/latent_ideology"
    },
    install_requires=['pandas','numpy','scipy'],                  # list all packages that your package uses
    keywords=["correspondence analysis", "latent ideology"], #descriptive meta-data
    classifiers=[                                   # https://pypi.org/classifiers
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Documentation',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    
    #download_url="https://github.com/fedemoss/latent_ideology/archive/refs/tags/0.0.3.tar.gz",
    download_url="https://github.com/fedemoss/-source-code-latent-method/archive/refs/tags/0.0.5.tar.gz",
)

