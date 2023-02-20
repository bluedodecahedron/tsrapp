import setuptools


def get_install_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as f:
        reqs = [x.strip() for x in f.read().splitlines()]
    reqs = [x for x in reqs if not x.startswith("#")]
    return reqs


setuptools.setup(
    name="tsrmodel",
    version="1.0.0",
    author="Richard Binder",
    packages=["tsrmodel.tools"],
    package_dir={"tsrmodel.tools": "tsrmodel/tools"},
    python_requires=">=3.8",
    install_requires=get_install_requirements(),
    setup_requires=["wheel"],  # avoid building error when pip is not updated
    include_package_data=True,  # include files in MANIFEST.in
)
