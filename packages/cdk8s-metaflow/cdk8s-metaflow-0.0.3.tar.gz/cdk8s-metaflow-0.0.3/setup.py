import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk8s-metaflow",
    "version": "0.0.3",
    "description": "cdk8s-metaflow",
    "license": "Apache-2.0",
    "url": "https://github.com/bcgalvin/cdk8s-metaflow.git",
    "long_description_content_type": "text/markdown",
    "author": "Bryan Galvin<bcgalvin@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/bcgalvin/cdk8s-metaflow.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk8s_metaflow",
        "cdk8s_metaflow._jsii",
        "cdk8s_metaflow.k8s",
        "cdk8s_metaflow.minio"
    ],
    "package_data": {
        "cdk8s_metaflow._jsii": [
            "cdk8s-metaflow@0.0.3.jsii.tgz"
        ],
        "cdk8s_metaflow": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.7",
    "install_requires": [
        "cdk8s>=2.3.73, <3.0.0",
        "constructs>=10.1.64, <11.0.0",
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
        "Development Status :: 4 - Beta",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
