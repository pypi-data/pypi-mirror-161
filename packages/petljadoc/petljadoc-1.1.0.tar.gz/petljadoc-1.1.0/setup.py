import io
import re
import setuptools

with open("README.md", "rt", encoding='utf8') as fh:
    long_description = fh.read()

install_requires= []
with open('requirements.txt', 'rt', encoding='utf8') as fh:
    for l in fh:
        install_requires.append(l.strip())

with io.open('petljadoc/__init__.py', 'rt', encoding='utf8') as f:
    src = f.read()
m = re.search(r'\_\_version\_\_\s*=\s*\"([^"]*)\"', src)
version = m.group(1)

setuptools.setup(
    python_requires=">=3.7",
    name="petljadoc",
    version=version,
    author="Fondacija Petlja",
    author_email="team@petlja.org",
    description="Petlja's command-line interface for learning content",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Petlja/PetljaDoc",
    install_requires=install_requires,
    include_package_data=True,
    zip_safe=False,
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3.6',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Topic :: Education',
        'Topic :: Text Processing :: Markup'
    ],
    entry_points={
        'console_scripts': [ 'petljadoc = petljadoc.cli:main' ],
        'sphinx.html_themes': [ 'bootstrap_petlja_theme = petljadoc.themes.runestone_theme',
                                'petljadoc_runestone_theme = petljadoc.themes.runestone_theme',
                                'petljadoc_course_theme = petljadoc.themes.course_theme'
                              ]
    }
)
