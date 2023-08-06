import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "config-preprocessor",
    version = "0.0.4",
    author= "Techer",
    author_email= "carlos.escalona@techer.com.br",
    description= "",
    long_description= long_description,
    # url= "",
    classifiers= [],
    package_dir= {"": "src"},
    # project_urls = {
    #     "Bug Tracker": "package issues URL",
    # },
    packages= setuptools.find_packages(where="src"),
    install_requires=['boto3', 'Jinja2'],
    python_requires=">=3.6"
)