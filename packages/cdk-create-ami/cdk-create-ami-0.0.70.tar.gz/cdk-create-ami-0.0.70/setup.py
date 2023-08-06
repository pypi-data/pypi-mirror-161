import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-create-ami",
    "version": "0.0.70",
    "description": "cdk-create-ami",
    "license": "Apache-2.0",
    "url": "https://github.com/schuettc/cdk-create-ami.git",
    "long_description_content_type": "text/markdown",
    "author": "Court Schuett",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/schuettc/cdk-create-ami.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_create_ami",
        "cdk_create_ami._jsii"
    ],
    "package_data": {
        "cdk_create_ami._jsii": [
            "cdk-create-ami@0.0.70.jsii.tgz"
        ],
        "cdk_create_ami": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.7",
    "install_requires": [
        "aws-cdk-lib>=2.27.0, <3.0.0",
        "constructs>=10.0.5, <11.0.0",
        "jsii>=1.63.2, <2.0.0",
        "publication>=0.0.3",
        "typeguard~=2.13.3"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Typing :: Typed",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
