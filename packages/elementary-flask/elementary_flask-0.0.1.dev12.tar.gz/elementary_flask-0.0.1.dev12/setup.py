import os

import setuptools

VERSION = "0.0.1.dev12"
install_requires = ['Flask==2.1.1', 'Flask-WTF~=1.0.0', 'Jinja2==3.1.1', 'MarkupSafe~=2.1.1', 'croniter==1.3.4', 'redis~=4.2.2', 'pottery', 'PyYAML~=6.0', 'WTForms~=3.0.1', 'Werkzeug==2.1.1', 'setuptools~=62.0.0', 'Flask-Caching']

if __name__ == '__main__':
    with open("README.md") as fin:
        long_description = fin.read()

    # with open('requirements.txt') as fin:
    #     install_requires = [l.strip() for l in fin.readlines() if l and l.strip()]

    data_files = []
    for dn in ('templates', 'static'):
        for root, dirs, files in os.walk(os.path.join('src/elementary_flask', dn)):
            for fn in files:
                data_files.append(os.path.join(root, fn))

    setuptools.setup(
        name="elementary_flask",
        version=VERSION,
        author="Khalid Grandi",
        author_email="kh.grandi@gmail.com",
        description="Component based framework for Flask/Python",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/xaled/elementary_flask",
        project_urls={
            "Bug Tracker": "https://github.com/xaled/elementary_flask/issues",
        },
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
        package_dir={"": "src"},
        packages=setuptools.find_packages(where="src"),
        python_requires=">=3.6",
        install_requires=install_requires,
        include_package_data=True,
        license='MIT',
        platforms=['any']
    )
