# -*- coding: utf-8 -*-
# Copyright (C) Alexander Pace, Duncan Meacher (2021)
#
# This file is part of igwn-alert
#
# igwn-alert is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# It is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with igwn-alert.  If not, see <http://www.gnu.org/licenses/>.
#

from setuptools import (
    setup,
    find_packages,
)

version = "0.2.2"

setup(
    # metadata
    name="igwn-alert",
    version=version,
    maintainer="Alexander Pace, Duncan Meacher",
    maintainer_email=(
        "alexander.pace@ligo.org, "
        "duncan.meacher@ligo.org, "
    ).rstrip(", "),
    description="IGWN Alert Network",
    long_description=(
        "The IGWN Alert System (igwn-alert) is a prototype notification "
        "service built on Apache Kafka, using the publish-subscribe "
        "(pubsub) protocol. It is a higher-level modification of SCIMMA's "
        "hop-client to streamline receiving and responding to alerts from "
        "GraceDB."
    ),
    url="https://lscsoft.docs.ligo.org/igwn-alert/",
    project_urls={
        "Bug Tracker": "https://git.ligo.org/lscsoft/igwn-alert/issues",
        "Documentation": "https://lscsoft.docs.ligo.org/igwn-alert/",
        "Source Code": "https://git.ligo.org/lscsoft/igwn-alert",
    },
    license='GPLv3+',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: "
        "GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Internet",
        "Topic :: Scientific/Engineering :: Astronomy",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    # requirements
    python_requires=">=3.6",
    setup_requires=["setuptools"],
    install_requires=[
        "setuptools",
        "hop-client==0.6.0",
        "confluent-kafka>=1.7.0",
        "safe-netrc",
    ],
    # contents
    entry_points={
        'console_scripts': [
            'igwn-alert=igwn_alert.tool:main',
        ],
    },
    packages=find_packages(),
)
