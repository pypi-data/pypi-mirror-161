from setuptools import find_packages, setup


def get_long_description() -> str:
    """
    获取 README
    """
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
    return long_description


if __name__ == "__main__":
    setup(
        name="v2donut",
        version="1.0.0",
        description="自动获取、设置延迟最低的 V2Ray 节点",
        author="drawmoon",
        author_email="1340260725@qq.com",
        url="https://github.com/drawmoon/v2donut",
        long_description=get_long_description(),
        long_description_content_type="text/markdown",
        packages=find_packages(),
        install_requires=["httpx", "pythonping"],
        include_package_data=True,
        python_requires=">=3.7",
        license="MIT License",
        classifiers=[
            "Programming Language :: Python :: 3.10",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
    )
