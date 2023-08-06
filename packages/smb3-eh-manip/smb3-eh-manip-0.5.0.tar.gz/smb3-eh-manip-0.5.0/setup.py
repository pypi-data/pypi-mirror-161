from setuptools import setup, find_packages


setup(
    name="smb3-eh-manip",
    version="0.5.0",
    description=("Ingest video data to render smb3 eh manip stimuli"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="smb3-eh-manip",
    author="Jon Robison",
    author_email="narfman0@blastedstudios.com",
    license="LICENSE",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    install_requires=["opencv-python", "pyautogui", "python-vlc"],
    test_suite="tests",
)
