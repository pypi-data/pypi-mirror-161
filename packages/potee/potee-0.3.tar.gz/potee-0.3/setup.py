from distutils.core import setup

setup(
    name="potee",
    packages=["potee"],
    version="0.3",
    license="MIT",
    description="A package to simplify the process of writing checkers for the Poteet platform",
    author="Ivan Hahanov",
    author_email="ivanhahanov13@gmail.com",
    url="https://github.com/PoteeDev/",
    keywords=[
        "checkers",
        "security",
        "paltform",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",  # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        "Intended Audience :: Developers",  # Define that your audience are developers
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",  # Specify which pyhton versions that you want to support
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
