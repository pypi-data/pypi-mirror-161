import setuptools
import subprocess

remote_version = (
    subprocess.run(["git", "describe", "--tags"], stdout=subprocess.PIPE)
    .stdout.decode("utf-8")
    .strip()
)
assert "." in remote_version

setuptools.setup(
    name="muvisdk",
    version=remote_version,
    author="muvinai",
    description="SDK for muvinai developers",
    long_description="SDK Muvinai Python package",
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(where="src"),
    package_data={"muvisdk": ["VERSION"]},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    python_requires=">=3.6",
    install_requires=[
        'mercadopago'
    ],
)
