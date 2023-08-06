import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "pepperize.cdk-dynamodb-backup",
    "version": "0.0.66",
    "description": "Backup and restore AWS DynamoDB Table to AWS S3 Bucket with AWS Data Pipeline.",
    "license": "MIT",
    "url": "https://github.com/patrick.florek/cdk-dynamodb-backup.git",
    "long_description_content_type": "text/markdown",
    "author": "Patrick Florek<patrick.florek@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/patrick.florek/cdk-dynamodb-backup.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "pepperize_cdk_dynamodb_backup",
        "pepperize_cdk_dynamodb_backup._jsii"
    ],
    "package_data": {
        "pepperize_cdk_dynamodb_backup._jsii": [
            "cdk-dynamodb-backup@0.0.66.jsii.tgz"
        ],
        "pepperize_cdk_dynamodb_backup": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.7",
    "install_requires": [
        "aws-cdk-lib>=2.8.0, <3.0.0",
        "constructs>=10.0.5, <11.0.0",
        "jsii>=1.63.2, <2.0.0",
        "pepperize.cdk-private-bucket>=0.0.141, <0.0.142",
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
