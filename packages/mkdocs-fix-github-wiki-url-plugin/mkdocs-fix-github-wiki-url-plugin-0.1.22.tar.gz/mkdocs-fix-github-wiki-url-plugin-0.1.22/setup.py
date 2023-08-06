from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as f:
    readme = f.read()

setup(
    name="mkdocs-fix-github-wiki-url-plugin",
    version="0.1.22",
    author="Quentin Escarbajal",
    author_email="xiaoxiao921@hotmail.fr",
    url="https://github.com/xiaoxiao921/mkdocs-fix-github-wiki-url-plugin",
    description="",
    long_description=readme,
    long_description_content_type="text/markdown",
    license='MIT',
    packages=find_packages(),
    install_requires=[
        "mkdocs>=1.1.0,<2"
    ],
    include_package_data=True,
    python_requires='>=3.6',
    entry_points={
        'mkdocs.plugins': [
            'mkdocs-fix-github-wiki-url-plugin = mkdocs_fix_github_wiki_url_plugin.plugin:Plugin',
        ]
    }

)