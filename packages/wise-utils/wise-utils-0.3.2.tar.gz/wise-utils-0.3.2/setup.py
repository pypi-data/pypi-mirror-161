import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

VERSION = "0.3.2"

setuptools.setup(
    name="wise-utils",
    version=VERSION,
    author="wise-python",
    author_email="duke.du@uifox.com.cn",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/duquan1995/wise-utils.git",
    project_urls={
        "Bug Tracker": "https://github.com/pypa/sampleproject/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    include_package_data=True,
    python_requires=">3",
    install_requires=[
        "yagmail>=0.15.277",
        "orderedset>=2.0.3",
        "requests>=2.25.1",
        "urllib3>=1.26.7",
        "selenium>=4.1.0",
        "pyppeteer~=1.0.2",
        "redis",
        "PyMySQL>=1.0.2",
        "nacos-sdk-python>=0.1.6",
        "better-exceptions>=0.3.3",
        "loguru>=0.6.0",
        "PyVirtualDisplay>=2.2",
        "undetected_chromedriver~=3.1.5",
        "webdriver_manager~=3.5.4"
    ]
)
