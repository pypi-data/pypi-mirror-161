import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "state-machine-semaphore",
    "version": "0.0.1",
    "description": "Create distributed semaphores using AWS Step Functions and Amazon DynamoDB to control concurrent invocations of contentious work.",
    "license": "Apache-2.0",
    "url": "https://github.com/dontirun/state-machine-semaphore.git",
    "long_description_content_type": "text/markdown",
    "author": "Arun Donti<dontirun@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/dontirun/state-machine-semaphore.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "state_machine_semaphore",
        "state_machine_semaphore._jsii"
    ],
    "package_data": {
        "state_machine_semaphore._jsii": [
            "state-machine-semaphore@0.0.1.jsii.tgz"
        ],
        "state_machine_semaphore": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.7",
    "install_requires": [
        "aws-cdk-lib>=2.22.0, <3.0.0",
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
