"""Notelist Setup script."""

import setuptools as st


if __name__ == "__main__":
    # Long description
    with open("README.md") as f:
        long_desc = f.read()

    # Setup
    st.setup(
        name="notelist",
        version="0.10.0",
        description="Tag based note taking REST API",
        author="Jose A. Jimenez",
        author_email="jajimenezcarm@gmail.com",
        license="MIT",
        long_description=long_desc,
        long_description_content_type="text/markdown",
        url="https://github.com/jajimenez/notelist",
        classifiers=[
            "Programming Language :: Python :: 3",
            "Operating System :: OS Independent",
            "License :: OSI Approved :: MIT License"
        ],
        python_requires=">=3.9.0",
        install_requires=[
            "Flask==2.2.0",
            "Flask-JWT-Extended==4.4.3",
            "marshmallow==3.17.0",
            "pymongo==4.2.0",
            "redis==4.3.4"
        ],
        packages=[
            "notelist",
            "notelist.schemas",
            "notelist.db",
            "notelist.db.main",
            "notelist.db.temp",
            "notelist.views",
            "notelist.config"
        ],
        package_dir={
            "notelist": "src/notelist",
            "notelist.schemas": "src/notelist/schemas",
            "notelist.db": "src/notelist/db",
            "notelist.db.main": "src/notelist/db/main",
            "notelist.db.temp": "src/notelist/db/temp",
            "notelist.views": "src/notelist/views",
            "notelist.config": "src/notelist/config"
        },
        package_data={
            "notelist": ["templates/*.html", "static/*.css"],
            "notelist.config": ["*.json"]
        },
        entry_points={
            "console_scripts": [
                "notelist=notelist.cli:cli"
            ]
        }
    )
