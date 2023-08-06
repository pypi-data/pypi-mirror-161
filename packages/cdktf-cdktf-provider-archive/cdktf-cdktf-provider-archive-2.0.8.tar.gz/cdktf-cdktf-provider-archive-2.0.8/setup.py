import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdktf-cdktf-provider-archive",
    "version": "2.0.8",
    "description": "Prebuilt archive Provider for Terraform CDK (cdktf)",
    "license": "MPL-2.0",
    "url": "https://github.com/hashicorp/cdktf-provider-archive.git",
    "long_description_content_type": "text/markdown",
    "author": "HashiCorp",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/hashicorp/cdktf-provider-archive.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdktf_cdktf_provider_archive",
        "cdktf_cdktf_provider_archive._jsii"
    ],
    "package_data": {
        "cdktf_cdktf_provider_archive._jsii": [
            "provider-archive@2.0.8.jsii.tgz"
        ],
        "cdktf_cdktf_provider_archive": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.7",
    "install_requires": [
        "cdktf>=0.12.0, <0.13.0",
        "constructs>=10.0.0, <11.0.0",
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
