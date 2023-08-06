import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "datadog-cdk-constructs",
    "version": "0.8.2",
    "description": "CDK Construct Library to automatically instrument Python and Node Lambda functions with Datadog",
    "license": "Apache-2.0",
    "url": "https://github.com/DataDog/datadog-cdk-constructs",
    "long_description_content_type": "text/markdown",
    "author": "Datadog",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/DataDog/datadog-cdk-constructs"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "datadog_cdk_constructs",
        "datadog_cdk_constructs._jsii"
    ],
    "package_data": {
        "datadog_cdk_constructs._jsii": [
            "datadog-cdk-constructs@0.8.2.jsii.tgz"
        ],
        "datadog_cdk_constructs": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.aws-apigateway>=1.134.0, <2.0.0",
        "aws-cdk.aws-lambda-nodejs>=1.134.0, <2.0.0",
        "aws-cdk.aws-lambda-python>=1.134.0, <2.0.0",
        "aws-cdk.aws-lambda>=1.134.0, <2.0.0",
        "aws-cdk.aws-logs-destinations>=1.134.0, <2.0.0",
        "aws-cdk.aws-logs>=1.134.0, <2.0.0",
        "aws-cdk.core>=1.134.0, <2.0.0",
        "constructs>=3.2.27, <4.0.0",
        "jsii>=1.46.0, <2.0.0",
        "publication>=0.0.3"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
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
