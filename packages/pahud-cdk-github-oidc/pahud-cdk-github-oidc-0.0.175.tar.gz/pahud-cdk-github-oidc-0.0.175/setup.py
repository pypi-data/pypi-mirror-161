import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "pahud-cdk-github-oidc",
    "version": "0.0.175",
    "description": "CDK construct library for Github OpenID Connect Identity Provider",
    "license": "Apache-2.0",
    "url": "https://github.com/pahud/cdk-github-oidc.git",
    "long_description_content_type": "text/markdown",
    "author": "Pahud Hsieh<pahudnet@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/pahud/cdk-github-oidc.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "pahud_cdk_github_oidc",
        "pahud_cdk_github_oidc._jsii"
    ],
    "package_data": {
        "pahud_cdk_github_oidc._jsii": [
            "cdk-github-oidc@0.0.175.jsii.tgz"
        ],
        "pahud_cdk_github_oidc": [
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
