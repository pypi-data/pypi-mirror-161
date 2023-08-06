import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "aws-solutions-constructs.aws-lambda-ssmstringparameter",
    "version": "1.159.0",
    "description": "CDK constructs for defining an interaction between an AWS Lambda function and AWS Systems Manager Parameter Store String parameter",
    "license": "Apache-2.0",
    "url": "https://github.com/awslabs/aws-solutions-constructs.git",
    "long_description_content_type": "text/markdown",
    "author": "Amazon Web Services",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/awslabs/aws-solutions-constructs.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "aws_solutions_constructs.aws_lambda_ssmstringparameter",
        "aws_solutions_constructs.aws_lambda_ssmstringparameter._jsii"
    ],
    "package_data": {
        "aws_solutions_constructs.aws_lambda_ssmstringparameter._jsii": [
            "aws-lambda-ssmstringparameter@1.159.0.jsii.tgz"
        ],
        "aws_solutions_constructs.aws_lambda_ssmstringparameter": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.7",
    "install_requires": [
        "aws-cdk.aws-ec2==1.159.0",
        "aws-cdk.aws-lambda==1.159.0",
        "aws-cdk.aws-ssm==1.159.0",
        "aws-cdk.core==1.159.0",
        "aws-solutions-constructs.core==1.159.0",
        "constructs>=3.2.0, <4.0.0",
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
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
