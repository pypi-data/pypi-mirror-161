import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bex",
    version="0.13",
    author="Anonymous",
    author_email="",
    description="Benchmark for explainability methods in computer vision",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://anonymous.4open.science/r/Bex-15A3/",
    # url="https://github.com/dvd42/Bex/tree/benchmark",
    # project_urls={
    #     "Bug Tracker": "https://github.com/dvd42/WhyY/tree/benchmark/issues",
    # },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: Unix",
    ],
    # package_data={"": ["benchmark/data/dataset-generated-font-char.h5py", "benchmark/pretrained_models/classifier/classifier_font_char.pth",
    #                    "benchmark/pretrained_models/model/generator.pth", "benchmark/pretrained_models/models/encoder.pth"]
    #               },
    packages=setuptools.find_packages(),
    install_requires=["torch", "h5py", "pandas", "scipy", "torchvision", "haven-ai", "requests"],
    python_requires=">=3.6",
)
