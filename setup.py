from setuptools import setup


def get_readme() -> str:
    with open("README.md") as f:
        return f.read()


setup(
    name="gdscript_docs_maker",
    version="1.2.0",
    description="Create documentation and class references from your Godot GDScript code.",
    long_description=get_readme(),
    long_description_content_type="text/markdown",
    keywords=["godot", "gdscript", "documentation", "reference", "godotengine"],
    url="https://github.com/GDQuest/gdscript-docs-maker",
    author="Nathan Lovato",
    author_email="nathan@gdquest.com",
    license="MIT",
    packages=["gdscript_docs_maker", "gdscript_docs_maker.modules"],
    package_data={"gdscript_docs_maker.modules": ["data/*"]},
    entry_points={
        "console_scripts": ["gdscript_docs_maker=gdscript_docs_maker.__main__:main"]
    },
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
