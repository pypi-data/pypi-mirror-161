##################################################################
#                                                                #
# #####...#####...##..##..##..##...####...##......######...####..#
# ##..##..##..##...####...###.##..##......##......##......##.....#
# #####...#####.....##....##.###..##.###..##......####.....####..#
# ##......##..##....##....##..##..##..##..##......##..........##.#
# ##......##..##....##....##..##...####...######..######...####..#
# ...............................................................#
#                                                                #
# PlanetaRY spanGLES                                             #
# The bright-side of the light-curve of (ringed) exoplanets      #
#                                                                #
##################################################################
# Jorge I. Zuluaga, Mario Sucerquia, Jaime A. Alvarado (C) 2022  #
##################################################################
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    # ######################################################################
    # BASIC DESCRIPTION
    # ######################################################################
    name='pryngles',
    author="Jorge I. Zuluaga, Mario Sucerquia, Jaime A. Alvarado",
    author_email="jorge.zuluaga@udea.edu.co",
    description="PlanetaRY spanGLES: the bright-side of the light-curve of (ringed) exoplanets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/pryngles",
    keywords='astronomy exoplanets planetary-rings',
    license='MIT',

    # ######################################################################
    # CLASSIFIER
    # ######################################################################
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        ],
    version='0.7.1',

    # ######################################################################
    # FILES
    # ######################################################################
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),

    # ######################################################################
    # ENTRY POINTS
    # ######################################################################
    entry_points={
        'console_scripts': ['install=pryngles.install:main'],
    },

    # ######################################################################
    # TESTS
    # ######################################################################
    test_suite='nose.collector',
    tests_require=['nose'],

    # ######################################################################
    # DEPENDENCIES
    # ######################################################################
    install_requires=[
        'rebound', 'scipy', 'ipython', 'matplotlib', 'tqdm', 'dill', 'spiceypy', 'cmasher',
    ],

    # ######################################################################
    # OPTIONS
    # ######################################################################
    include_package_data=True,
    package_data={"": ["data/*.*", "tests/*.*"]},
)
