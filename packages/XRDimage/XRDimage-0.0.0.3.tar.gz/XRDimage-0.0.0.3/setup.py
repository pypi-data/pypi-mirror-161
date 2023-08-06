from setuptools import setup


setup(name='XRDimage',
      version='0.0.0.3',
      description='package for image processing on XRD images',
      url='http://engineering.case.edu/centers/sdle/',
      author='Weiqi Yue, Gabriel Ponon, Zhuldyz Ualikhankyzy, Nathaniel K. Tomczak, Pawan K. Tripathi, Roger H. French',
      author_email='wxy215@case.edu, pkt19@case.edu, roger.french@case.edu',
      license='MIT License',
      packages=[''],
      package_dir={'XRDimage': './XRDimage'},
#      package_data={'XRDimage': ['data','files/data/FullSizeModules/*','files/tutorials/*','files/data/out','README.rst']},
      python_requires='>=3.8',
      install_requires=['numpy', 'PIL','scikit-image','scikit-image','os'],
#      include_package_data=True,
      project_urls={"Documentation":"https://xrdimage-doc.readthedocs.io/en/latest/","Bugtracker": "https://bitbucket.org/cwrusdle/xrd-image/src/main/"},
      )

