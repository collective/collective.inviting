from setuptools import setup, find_packages
import os

version = '0.1.1'

setup(name='collective.inviting',
      version=version,
      description="Plone add-on for event invitations, confirmation.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("doc", "HISTORY.txt")).read(),
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Plone",
        ],
      keywords='',
      author='Sean Upton',
      author_email='sean.upton@hsc.utah.edu',
      url='https://github.com/collective/collective.inviting',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.subscribe',
          'Products.CMFPlone',
          'icalendar', # http://codespeak.net/icalendar/
          # -*- Extra requirements: -*-
      ],
      extras_require = {
          'test': [ 'plone.app.testing', ],
      },
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )

