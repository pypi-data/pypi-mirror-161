import setuptools
import versioneer
import os

readme = os.path.normpath(os.path.join(__file__, "..", "README.md"))
with open(readme, "r", encoding="utf-8") as fh:
    long_description = fh.read()

long_description += "\n\n"

changelog = os.path.normpath(os.path.join(__file__, "..", "CHANGELOG.md"))
with open(changelog, "r", encoding="utf-8") as fh:
    long_description = fh.read()


setuptools.setup(
    cmdclass=versioneer.get_cmdclass(),
    name="libreflow.rouge",
    version=versioneer.get_version(),
    author="Flavio Perez",
    author_email="flavio@lfs.coop",
    description="A rouge flow",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/lfs.coop/libreflow/libreflow.rouge",
    license="LGPLv3+",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Operating System :: OS Independent",
    ],
    keywords="kabaret cgwire kitsu gazu animation pipeline libreflow",
    install_requires=["libreflow>=2.1.5.1"],
    python_requires=">=3.7",
    packages=setuptools.find_packages("src"),
    package_dir={"": "src"},
    package_data={
        "": [
            "*.css",
            "*.png",
            "*.svg",
            "*.gif",
            "*.abc",
            "*.aep",
            "*.ai",
            "*.blend",
            "*.jpg",
            "*.kra",
            "*.mov",
            "*.psd",
            "*.txt",
            "*.usd",
            "*.fbx",
            "*.json",
            "*.obj",
            "*.plas",
            "*.houdoo",
        ],
    },

)