import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

f = open("requirements.txt","w")
f.write('instaloader\nuser_agent\nmechanize\nrequests\nrandom\nsecrets\ntime\n\nuuid\njson\nos\nre')

fr = open("requirements.txt",'r')
requires = fr.read().split('\n')
    
setuptools.setup(
    name="zerlib",
    version="0.1.1",
    author="ZER TOOLS",
    author_email="",
    description="• Script Very Nice To Helping Programmer .",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    project_urls={
        "Bug Tracker": "https://github.com/pypa/sampleproject/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.9",
    install_requires=requires,
)
