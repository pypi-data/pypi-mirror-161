import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

with open("requirements.txt") as f:
    requires = []
    for line in f:
        req = line.strip()
        if "#egg=" in req:
            req_url, req_name = req.split("#egg=")
            req_str = f"{req_name} @ {req_url}"
        else:
            req_str = req
        requires.append(req_str)

setuptools.setup(
    name="ondewo-csi-client",
    version='2.9.0',
    author="ONDEWO GbmH",
    author_email="info@ondewo.com",
    description="exposes the ondewo-csi endpoints in a user-friendly way",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ondewo/ondewo-csi-client-python",
    packages=[
        np for np in filter(lambda n: n.startswith("ondewo.") or n == "ondewo", setuptools.find_packages())
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Topic :: Software Development :: Libraries",
    ],
    python_requires=">=2.7, !=3.0.1",
    install_requires=requires,
)
