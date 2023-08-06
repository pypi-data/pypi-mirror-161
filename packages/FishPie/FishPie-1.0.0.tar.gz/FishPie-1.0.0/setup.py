import os

import setuptools

here = os.path.abspath(os.path.dirname(__file__))
long_description = open(os.path.join(here, "README.md")).read()

setuptools.setup(
    name="FishPie",
    version="1.0.0",
    
    description="File sharing web application",
    long_description=long_description,
    long_description_content_type="text/markdown",
    
    url="https://github.com/lamyj/fishpie",
    
    author="Julien Lamy",
    author_email="julien@seasofcheese.net",
    
    license="GPL-3.0-or-later",
    
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        
        "Environment :: Web Environment",
        
        "Framework :: Flask",
        
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        
        "Programming Language :: Python :: 3",
        
        "Topic :: Internet :: WWW/HTTP",
    ],
    
    keywords = ["File sharing", "Web application", "Flask"],
    
    packages=["fishpie"],
    package_data = {
        "fishpie": ["static/*", "templates/*", "translations/*/*/*mo"]},
    
    setup_requires=["setuptools_scm"],
    use_scm_version=True,
    
    install_requires=["flask", "flask-babel"],
    extras_require={ "wordpress-auth": ["mysqlclient"] },
)
