from setuptools import setup


setup(name='XCTimage',
      version='0.0.0.1',
      description='package for XCT image analysis',
      url='http://engineering.case.edu/centers/sdle/',
      author='Pawan K. Tripathi, Tommy Ciardi, Roger H. French',
      author_email='pkt19@case.edu, roger.french@case.edu',
      license='MIT',
      packages=[''],
      package_dir={'XCTimage': './XCTimage'},
   #   package_data={'pvimage': ['files/data/Minimodules/*','files/data/FullSizeModules/*','files/tutorials/*','files/data/out','README.rst']},
      python_requires='>=3.6.5',
      install_requires=['markdown','opencv-python','scipy','scikit-image'],
   #   include_package_data=True,
      project_urls={"Documentation":"https://xctimage-doc.readthedocs.io/en/latest/#","Bugtracker": "https://bitbucket.org/cwrusdle/xctimage/src/main/"},
      )

