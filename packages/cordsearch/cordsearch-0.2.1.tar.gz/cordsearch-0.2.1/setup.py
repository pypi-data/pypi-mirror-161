import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    reqs = []
    for line in f:
        line = line.strip()
        reqs.append(line.split('==')[0])

setuptools.setup(
     name='cordsearch',
     version='0.2.1',
     description="Utility package for computing and finding similar sentences in passages",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://github.com/IanBluth/cordsearch",
     packages=setuptools.find_packages(),
     install_requires=reqs,
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: Apache Software License",
         "Operating System :: OS Independent",
         "Topic :: Scientific/Engineering :: Artificial Intelligence",
     ],
 )