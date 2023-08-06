from setuptools import setup, find_packages

with open("README", "r", encoding="utf-8") as fh:
    long_description = fh.read()

#def download_data(url='http://...'):
    # Download; extract data to disk.
    # Raise an exception if the link is bad, or we can't connect, etc.

#def load_data():
#    if not os.path.exists(DATA_DIR):
#        download_data()
#    data = read_data_from_disk(DATA_DIR)
#    return data

setup(
    name="madys",
    version="0.4.1",
    author='Vito Squicciarini',
    author_email='vito.squicciarini@inaf.it',
    description='Manifold Age Determination for Young Stars',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/vsquicciarini/madys',
    project_urls={
        "Bug Tracker": "https://github.com/vsquicciarini/madys/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=['numpy','scipy','astropy','pandas','matplotlib','astroquery','h5py','tabulate','lxml'],
    packages=['madys'],
    package_data={
    'madys': [r'utils/filters.pkl',
              r'utils/models.pkl'],},
    include_package_data=True,
    zip_safe=False
)
