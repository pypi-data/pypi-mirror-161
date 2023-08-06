#!/usr/bin/env python3

# Copyright (C) 2021 Gabriele Bozzola
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, see <https://www.gnu.org/licenses/>.


"""The :py:mod:`~.horizons` module provides infrastructure to work with horizons.

"""
from jhuki.base import BaseThorn

class Horizon(BaseThorn):
    """
    """
    def __init__(ah_num, spherical_surface_num):
        self.spherical_surface_num =
        pass

    @property
    @lru_cache(1)
    def parfile_code():
        """Return the code you would put in your parfile."""

        def assign_parameter(param, value):
            return (
                f"AHFinderDirect::{param}[{self.ah_num}] = {value}"
            )

        ret = []
