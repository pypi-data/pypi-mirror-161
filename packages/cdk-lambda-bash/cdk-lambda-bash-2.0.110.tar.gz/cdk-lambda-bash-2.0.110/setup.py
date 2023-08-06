import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-lambda-bash",
    "version": "2.0.110",
    "description": "Deploy Bash Lambda Functions with AWS CDK",
    "license": "Apache-2.0",
    "url": "https://github.com/pahud/cdk-lambda-bash.git",
    "long_description_content_type": "text/markdown",
    "author": "Pahud Hsieh",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/pahud/cdk-lambda-bash.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_lambda_bash",
        "cdk_lambda_bash._jsii"
    ],
    "package_data": {
        "cdk_lambda_bash._jsii": [
            "cdk-lambda-bash@2.0.110.jsii.tgz"
        ],
        "cdk_lambda_bash": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.7",
    "install_requires": [
        "aws-cdk-lib>=2.0.0, <3.0.0",
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
