from setuptools import setup, find_packages

setup(
    name="ansible-yandex-cloud-inventory",
    version="1.0.0",
    description="Ansible dynamic inventory plugin for Yandex Cloud",
    author="Maksim Zatolokin",
    author_email="max.zatol@gmail.com",
    license="MIT",
    packages=find_packages(include=["inventory_plugins*"]),
    package_data={"inventory_plugins": ["*.py"]},
    install_requires=[
        "ansible>=2.18.6",
        "yandexcloud>=0.99.0"
    ],
    entry_points={
        "ansible.plugins.inventory": [
            "yandex_cloud_inventory = inventory_plugins.yandex_cloud_inventory"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
