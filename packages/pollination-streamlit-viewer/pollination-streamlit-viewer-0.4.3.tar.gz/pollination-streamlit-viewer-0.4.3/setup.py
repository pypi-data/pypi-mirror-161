import setuptools

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

def _clean_version():
    """
    This function was required because scm was generating developer versions on
    GitHub Action.
    """
    def get_version(version):
        return str(version.tag)
    def empty(version):
        return ''

    return {'local_scheme': get_version, 'version_scheme': empty}

setuptools.setup(
    name="pollination-streamlit-viewer",
    use_scm_version=_clean_version,
    setup_requires=['setuptools_scm'],
    author="Pollination",
    author_email="nicolas@ladybug.tools",
    description="vtkjs component for streamlit",
    long_description="vtkjs component for streamlit",
    long_description_content_type="text/plain",
    url="https://github.com/pollination/pollination-streamlit-viewer",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[],
    python_requires=">=3.7",
    install_requires=requirements
)
