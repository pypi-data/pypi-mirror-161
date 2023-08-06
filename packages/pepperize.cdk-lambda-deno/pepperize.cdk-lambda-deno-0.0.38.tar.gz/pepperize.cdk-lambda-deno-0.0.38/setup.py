import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "pepperize.cdk-lambda-deno",
    "version": "0.0.38",
    "description": "AWS CDK custom AWS Lambda runtime with Deno",
    "license": "MIT",
    "url": "https://github.com/pepperize/cdk-lambda-deno.git",
    "long_description_content_type": "text/markdown",
    "author": "Patrick Florek<patrick.florek@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/pepperize/cdk-lambda-deno.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "pepperize_cdk_lambda_deno",
        "pepperize_cdk_lambda_deno._jsii"
    ],
    "package_data": {
        "pepperize_cdk_lambda_deno._jsii": [
            "cdk-lambda-deno@0.0.38.jsii.tgz"
        ],
        "pepperize_cdk_lambda_deno": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.7",
    "install_requires": [
        "aws-cdk-lib>=2.29.1, <3.0.0",
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
