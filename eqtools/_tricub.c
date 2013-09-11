#include <math.h>
#include <stdlib.h>

/*****************************************************************
 
    This file is part of the eqtools package.

    EqTools is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    EqTools is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with EqTools.  If not, see <http://www.gnu.org/licenses/>.

    Copyright 2013 Ian C. Faust

******************************************************************/

int A[64][64] = {
{0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-4, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8,-20,16,-4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-4,12,-12, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-4, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-2, 0, 2, 0, 0, 0, 0, 0,-2, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4,14,-16,-2, 0, 0, 0, 0, 4,-10, 8,-2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -2,-10,10, 2, 0, 0, 0, 0, -2, 6,-6, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0,-20, 0, 0, 0,16, 0, 0, 0,-4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, -4, 0,14, 0, -14, 0, -8, 0, 8, 0, 2, 0,-2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-8,-28,32, 4,-28,46,-32,14,16,-40,32,-8,-4,10,-8, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 20, -20, -4, 14, -26, 26, -14, -8, 24, -24, 8, 2, -6, 6, -2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -4, 0, 0, 0, 12, 0, 0, 0, -12, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -2, 0, 2, 0, -10, 0, 10, 0, 6, 0, -6, 0, -2, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 14, -16, -2, 20, -26, 16, -10, -12, 30, -24, 6, 4, -10, 8, -2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -2, -10, 10, 2, -10, 14, -14, 10, 6, -18, 18, -6, -2, 6, -6, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{0, 0, 0, 0, 0, -4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{0, 0, 0, 0, -2, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -2, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{0, 0, 0, 0, 4, 14, -16, -2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, -10, 8, -2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{0, 0, 0, 0, -2, -10, 10, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -2, 6, -6, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{0, -2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{-1, 0, 1, 0, 0, 0, 0, 0, -1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 1, 0, 0, 0, 0, 0, -1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{2, 7, -8, -1, 0, 0, 0, 0, 2, -5, 4, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 7, -8, -1, 0, 0, 0, 0, 2, -5, 4, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{-1, -5, 5, 1, 0, 0, 0, 0, -1, 3, -3, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -5, 5, 1, 0, 0, 0, 0, -1, 3, -3, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{0, 4, 0, 0, 0, 14, 0, 0, 0, -16, 0, 0, 0, -2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, -10, 0, 0, 0, 8, 0, 0, 0, -2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{2, 0, -2, 0, 7, 0, -7, 0, -4, 0, 4, 0, 1, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, -2, 0, 7, 0, -7, 0, -4, 0, 4, 0, 1, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{-4, -14, 16, 2, -14, -49, 56, 7, 8, 52, -56, -4, -2, 5, -4, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -4, -14, 16, 2, -14, 23, -16, 7, 8, -20, 16, -4, -2, 5, -4, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{2, 10, -10, -2, 7, 35, -35, -7, -4, -36, 36, 4, 1, -3, 3, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 10, -10, -2, 7, -13, 13, -7, -4, 12, -12, 4, 1, -3, 3, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{0, -2, 0, 0, 0, -10, 0, 0, 0, 10, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -2, 0, 0, 0, 6, 0, 0, 0, -6, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{-1, 0, 1, 0, -5, 0, 5, 0, 3, 0, -3, 0, -1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 1, 0, -5, 0, 5, 0, 3, 0, -3, 0, -1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{2, 7, -8, -1, 10, 35, -40, -5, -6, -33, 36, 3, 2, -5, 4, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 7, -8, -1, 10, -13, 8, -5, -6, 15, -12, 3, 2, -5, 4, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{-1, -5, 5, 1, -5, -25, 25, 5, 3, 23, -23, -3, -1, 3, -3, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -5, 5, 1, -5, 7, -7, 5, 3, -9, 9, -3, -1, 3, -3, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 16, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{0, 0, 0, 0, 4, 0, -4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 14, 0, -14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -8, 0, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, -2, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{0, 0, 0, 0, -8, -28, 32, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -28, 46, -32, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 16, -40, 32, -8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -4, 10, -8, 2, 0, 0, 0, 0, 0, 0, 0, 0},
{0, 0, 0, 0, 4, 20, -20, -4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 14, -26, 26, -14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -8, 24, -24, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, -6, 6, -2, 0, 0, 0, 0, 0, 0, 0, 0},
{0, 4, 0, 0, 0, 0, 0, 0, 0, -4, 0, 0, 0, 0, 0, 0, 0, 14, 0, 0, 0, 0, 0, 0, 0, -14, 0, 0, 0, 0, 0, 0, 0, -8, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, -2, 0, 0, 0, 0, 0, 0},
{2, 0, -2, 0, 0, 0, 0, 0, 2, 0, -2, 0, 0, 0, 0, 0, 7, 0, -7, 0, 0, 0, 0, 0, 7, 0, -7, 0, 0, 0, 0, 0, -4, 0, 4, 0, 0, 0, 0, 0, -4, 0, 4, 0, 0, 0, 0, 0, 1, 0, -1, 0, 0, 0, 0, 0, 1, 0, -1, 0, 0, 0, 0, 0},
{-4, -14, 16, 2, 0, 0, 0, 0, -4, 10, -8, 2, 0, 0, 0, 0, -14, -49, 56, 7, 0, 0, 0, 0, -14, 35, -28, 7, 0, 0, 0, 0, 8, 28, -32, -4, 0, 0, 0, 0, 8, -20, 16, -4, 0, 0, 0, 0, -2, -7, 8, 1, 0, 0, 0, 0, -2, 5, -4, 1, 0, 0, 0, 0},
{2, 10, -10, -2, 0, 0, 0, 0, 2, -6, 6, -2, 0, 0, 0, 0, 7, 35, -35, -7, 0, 0, 0, 0, 7, -21, 21, -7, 0, 0, 0, 0, -4, -20, 20, 4, 0, 0, 0, 0, -4, 12, -12, 4, 0, 0, 0, 0, 1, 5, -5, -1, 0, 0, 0, 0, 1, -3, 3, -1, 0, 0, 0, 0},
{0, -8, 0, 0, 0, -28, 0, 0, 0, 32, 0, 0, 0, 4, 0, 0, 0, -28, 0, 0, 0, 46, 0, 0, 0, -32, 0, 0, 0, 14, 0, 0, 0, 16, 0, 0, 0, -40, 0, 0, 0, 32, 0, 0, 0, -8, 0, 0, 0, -4, 0, 0, 0, 10, 0, 0, 0, -8, 0, 0, 0, 2, 0, 0},
{-4, 0, 4, 0, -14, 0, 14, 0, 8, 0, -8, 0, -2, 0, 2, 0, -14, 0, 14, 0, -49, 0, 49, 0, 28, 0, -28, 0, -7, 0, 7, 0, 8, 0, -8, 0, 28, 0, -28, 0, -16, 0, 16, 0, 4, 0, -4, 0, -2, 0, 2, 0, -7, 0, 7, 0, 4, 0, -4, 0, -1, 0, 1, 0},
{8, 28, -32, -4, 28, 98, -112, -14, -16, -104, 112, 8, 4, -10, 8, -2, 28, 98, -112, -14, 98, -89, 40, -49, -56, 68, -40, 28, 14, -35, 28, -7, -16, -56, 64, 8, -56, 92, -64, 28, 32, -80, 64, -16, -8, 20, -16, 4, 4, 14, -16, -2, 14, -23, 16, -7, -8, 20, -16, 4, 2, -5, 4, -1},
{-4, -20, 20, 4, -14, -70, 70, 14, 8, 72, -72, -8, -2, 6, -6, 2, -14, -70, 70, 14, -49, 43, -43, 49, 28, -36, 36, -28, -7, 21, -21, 7, 8, 40, -40, -8, 28, -52, 52, -28, -16, 48, -48, 16, 4, -12, 12, -4, -2, -10, 10, 2, -7, 13, -13, 7, 4, -12, 12, -4, -1, 3, -3, 1},
{0, 4, 0, 0, 0, 20, 0, 0, 0, -20, 0, 0, 0, -4, 0, 0, 0, 14, 0, 0, 0, -26, 0, 0, 0, 26, 0, 0, 0, -14, 0, 0, 0, -8, 0, 0, 0, 24, 0, 0, 0, -24, 0, 0, 0, 8, 0, 0, 0, 2, 0, 0, 0, -6, 0, 0, 0, 6, 0, 0, 0, -2, 0, 0},
{2, 0, -2, 0, 10, 0, -10, 0, -6, 0, 6, 0, 2, 0, -2, 0, 7, 0, -7, 0, 35, 0, -35, 0, -21, 0, 21, 0, 7, 0, -7, 0, -4, 0, 4, 0, -20, 0, 20, 0, 12, 0, -12, 0, -4, 0, 4, 0, 1, 0, -1, 0, 5, 0, -5, 0, -3, 0, 3, 0, 1, 0, -1, 0},
{-4, -14, 16, 2, -20, -70, 80, 10, 12, 66, -72, -6, -4, 10, -8, 2, -14, -49, 56, 7, -70, 43, -8, 35, 42, -57, 36, -21, -14, 35, -28, 7, 8, 28, -32, -4, 40, -52, 32, -20, -24, 60, -48, 12, 8, -20, 16, -4, -2, -7, 8, 1, -10, 13, -8, 5, 6, -15, 12, -3, -2, 5, -4, 1},
{2, 10, -10, -2, 10, 50, -50, -10, -6, -46, 46, 6, 2, -6, 6, -2, 7, 35, -35, -7, 35, -17, 17, -35, -21, 31, -31, 21, 7, -21, 21, -7, -4, -20, 20, 4, -20, 28, -28, 20, 12, -36, 36, -12, -4, 12, -12, 4, 1, 5, -5, -1, 5, -7, 7, -5, -3, 9, -9, 3, 1, -3, 3, -1},
{0, 0, 0, 0, 0, -4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 12, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -12, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{0, 0, 0, 0, -2, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -10, 0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 0, -6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -2, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{0, 0, 0, 0, 4, 14, -16, -2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 20, -26, 16, -10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -12, 30, -24, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, -10, 8, -2, 0, 0, 0, 0, 0, 0, 0, 0},
{0, 0, 0, 0, -2, -10, 10, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -10, 14, -14, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, -18, 18, -6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -2, 6, -6, 2, 0, 0, 0, 0, 0, 0, 0, 0},
{0, -2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, -10, 0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, -6, 0, 0, 0, 0, 0, 0, 0, -2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0},
{-1, 0, 1, 0, 0, 0, 0, 0, -1, 0, 1, 0, 0, 0, 0, 0, -5, 0, 5, 0, 0, 0, 0, 0, -5, 0, 5, 0, 0, 0, 0, 0, 3, 0, -3, 0, 0, 0, 0, 0, 3, 0, -3, 0, 0, 0, 0, 0, -1, 0, 1, 0, 0, 0, 0, 0, -1, 0, 1, 0, 0, 0, 0, 0},
{2, 7, -8, -1, 0, 0, 0, 0, 2, -5, 4, -1, 0, 0, 0, 0, 10, 35, -40, -5, 0, 0, 0, 0, 10, -25, 20, -5, 0, 0, 0, 0, -6, -21, 24, 3, 0, 0, 0, 0, -6, 15, -12, 3, 0, 0, 0, 0, 2, 7, -8, -1, 0, 0, 0, 0, 2, -5, 4, -1, 0, 0, 0, 0},
{-1, -5, 5, 1, 0, 0, 0, 0, -1, 3, -3, 1, 0, 0, 0, 0, -5, -25, 25, 5, 0, 0, 0, 0, -5, 15, -15, 5, 0, 0, 0, 0, 3, 15, -15, -3, 0, 0, 0, 0, 3, -9, 9, -3, 0, 0, 0, 0, -1, -5, 5, 1, 0, 0, 0, 0, -1, 3, -3, 1, 0, 0, 0, 0},
{0, 4, 0, 0, 0, 14, 0, 0, 0, -16, 0, 0, 0, -2, 0, 0, 0, 20, 0, 0, 0, -26, 0, 0, 0, 16, 0, 0, 0, -10, 0, 0, 0, -12, 0, 0, 0, 30, 0, 0, 0, -24, 0, 0, 0, 6, 0, 0, 0, 4, 0, 0, 0, -10, 0, 0, 0, 8, 0, 0, 0, -2, 0, 0},
{2, 0, -2, 0, 7, 0, -7, 0, -4, 0, 4, 0, 1, 0, -1, 0, 10, 0, -10, 0, 35, 0, -35, 0, -20, 0, 20, 0, 5, 0, -5, 0, -6, 0, 6, 0, -21, 0, 21, 0, 12, 0, -12, 0, -3, 0, 3, 0, 2, 0, -2, 0, 7, 0, -7, 0, -4, 0, 4, 0, 1, 0, -1, 0},
{-4, -14, 16, 2, -14, -49, 56, 7, 8, 52, -56, -4, -2, 5, -4, 1, -20, -70, 80, 10, -70, 43, -8, 35, 40, -28, 8, -20, -10, 25, -20, 5, 12, 42, -48, -6, 42, -69, 48, -21, -24, 60, -48, 12, 6, -15, 12, -3, -4, -14, 16, 2, -14, 23, -16, 7, 8, -20, 16, -4, -2, 5, -4, 1},
{2, 10, -10, -2, 7, 35, -35, -7, -4, -36, 36, 4, 1, -3, 3, -1, 10, 50, -50, -10, 35, -17, 17, -35, -20, 12, -12, 20, 5, -15, 15, -5, -6, -30, 30, 6, -21, 39, -39, 21, 12, -36, 36, -12, -3, 9, -9, 3, 2, 10, -10, -2, 7, -13, 13, -7, -4, 12, -12, 4, 1, -3, 3, -1},
{0, -2, 0, 0, 0, -10, 0, 0, 0, 10, 0, 0, 0, 2, 0, 0, 0, -10, 0, 0, 0, 14, 0, 0, 0, -14, 0, 0, 0, 10, 0, 0, 0, 6, 0, 0, 0, -18, 0, 0, 0, 18, 0, 0, 0, -6, 0, 0, 0, -2, 0, 0, 0, 6, 0, 0, 0, -6, 0, 0, 0, 2, 0, 0},
{-1, 0, 1, 0, -5, 0, 5, 0, 3, 0, -3, 0, -1, 0, 1, 0, -5, 0, 5, 0, -25, 0, 25, 0, 15, 0, -15, 0, -5, 0, 5, 0, 3, 0, -3, 0, 15, 0, -15, 0, -9, 0, 9, 0, 3, 0, -3, 0, -1, 0, 1, 0, -5, 0, 5, 0, 3, 0, -3, 0, -1, 0, 1, 0},
{2, 7, -8, -1, 10, 35, -40, -5, -6, -33, 36, 3, 2, -5, 4, -1, 10, 35, -40, -5, 50, -17, -8, -25, -30, 27, -12, 15, 10, -25, 20, -5, -6, -21, 24, 3, -30, 39, -24, 15, 18, -45, 36, -9, -6, 15, -12, 3, 2, 7, -8, -1, 10, -13, 8, -5, -6, 15, -12, 3, 2, -5, 4, -1},
{-1, -5, 5, 1, -5, -25, 25, 5, 3, 23, -23, -3, -1, 3, -3, 1, -5, -25, 25, 5, -25, 3, -3, 25, 15, -13, 13, -15, -5, 15, -15, 5, 3, 15, -15, -3, 15, -21, 21, -15, -9, 27, -27, 9, 3, -9, 9, -3, -1, -5, 5, 1, -5, 7, -7, 5, 3, -9, 9, -3, -1, 3, -3, 1}};

int A_v2[64][64] = {
{ 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{ 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{-3, 3, 0, 0, 0, 0, 0, 0,-2,-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{ 2,-2, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-2,-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2,-2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{-3, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-2, 0,-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{ 0, 0, 0, 0, 0, 0, 0, 0,-3, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-2, 0,-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{ 9,-9,-9, 9, 0, 0, 0, 0, 6, 3,-6,-3, 0, 0, 0, 0, 6,-6, 3,-3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 2, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{-6, 6, 6,-6, 0, 0, 0, 0,-3,-3, 3, 3, 0, 0, 0, 0,-4, 4,-2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-2,-2,-1,-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{ 2, 0,-2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{ 0, 0, 0, 0, 0, 0, 0, 0, 2, 0,-2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{-6, 6, 6,-6, 0, 0, 0, 0,-4,-2, 4, 2, 0, 0, 0, 0,-3, 3,-3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-2,-1,-2,-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{ 4,-4,-4, 4, 0, 0, 0, 0, 2, 2,-2,-2, 0, 0, 0, 0, 2,-2, 2,-2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-2,-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2,-2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0},
{ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-3, 3, 0, 0, 0, 0, 0, 0,-2,-1, 0, 0, 0, 0, 0, 0},
{ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2,-2, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0},
{ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-3, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-2, 0,-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-3, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-2, 0,-1, 0, 0, 0, 0, 0},
{ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9,-9,-9, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 3,-6,-3, 0, 0, 0, 0, 6,-6, 3,-3, 0, 0, 0, 0, 4, 2, 2, 1, 0, 0, 0, 0},
{ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-6, 6, 6,-6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-3,-3, 3, 3, 0, 0, 0, 0,-4, 4,-2, 2, 0, 0, 0, 0,-2,-2,-1,-1, 0, 0, 0, 0},
{ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0,-2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0,-2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0},
{ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-6, 6, 6,-6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-4,-2, 4, 2, 0, 0, 0, 0,-3, 3,-3, 3, 0, 0, 0, 0,-2,-1,-2,-1, 0, 0, 0, 0},
{ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4,-4,-4, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2,-2,-2, 0, 0, 0, 0, 2,-2, 2,-2, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0},
{-3, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-2, 0, 0, 0,-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{ 0, 0, 0, 0, 0, 0, 0, 0,-3, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-2, 0, 0, 0,-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{ 9,-9, 0, 0,-9, 9, 0, 0, 6, 3, 0, 0,-6,-3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6,-6, 0, 0, 3,-3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 2, 0, 0, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{-6, 6, 0, 0, 6,-6, 0, 0,-3,-3, 0, 0, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-4, 4, 0, 0,-2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-2,-2, 0, 0,-1,-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-3, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-2, 0, 0, 0,-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-3, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-2, 0, 0, 0,-1, 0, 0, 0},
{ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9,-9, 0, 0,-9, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 3, 0, 0,-6,-3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6,-6, 0, 0, 3,-3, 0, 0, 4, 2, 0, 0, 2, 1, 0, 0},
{ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-6, 6, 0, 0, 6,-6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-3,-3, 0, 0, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-4, 4, 0, 0,-2, 2, 0, 0,-2,-2, 0, 0,-1,-1, 0, 0},
{ 9, 0,-9, 0,-9, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 0, 3, 0,-6, 0,-3, 0, 6, 0,-6, 0, 3, 0,-3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 2, 0, 2, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{ 0, 0, 0, 0, 0, 0, 0, 0, 9, 0,-9, 0,-9, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 0, 3, 0,-6, 0,-3, 0, 6, 0,-6, 0, 3, 0,-3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 2, 0, 2, 0, 1, 0},
{-27,27,27,-27,27,-27,-27,27,-18,-9,18, 9,18, 9,-18,-9,-18,18,-9, 9,18,-18, 9,-9,-18,18,18,-18,-9, 9, 9,-9,-12,-6,-6,-3,12, 6, 6, 3,-12,-6,12, 6,-6,-3, 6, 3,-12,12,-6, 6,-6, 6,-3, 3,-8,-4,-4,-2,-4,-2,-2,-1},
{18,-18,-18,18,-18,18,18,-18, 9, 9,-9,-9,-9,-9, 9, 9,12,-12, 6,-6,-12,12,-6, 6,12,-12,-12,12, 6,-6,-6, 6, 6, 6, 3, 3,-6,-6,-3,-3, 6, 6,-6,-6, 3, 3,-3,-3, 8,-8, 4,-4, 4,-4, 2,-2, 4, 4, 2, 2, 2, 2, 1, 1},
{-6, 0, 6, 0, 6, 0,-6, 0, 0, 0, 0, 0, 0, 0, 0, 0,-3, 0,-3, 0, 3, 0, 3, 0,-4, 0, 4, 0,-2, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-2, 0,-2, 0,-1, 0,-1, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{ 0, 0, 0, 0, 0, 0, 0, 0,-6, 0, 6, 0, 6, 0,-6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-3, 0,-3, 0, 3, 0, 3, 0,-4, 0, 4, 0,-2, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0,-2, 0,-2, 0,-1, 0,-1, 0},
{18,-18,-18,18,-18,18,18,-18,12, 6,-12,-6,-12,-6,12, 6, 9,-9, 9,-9,-9, 9,-9, 9,12,-12,-12,12, 6,-6,-6, 6, 6, 3, 6, 3,-6,-3,-6,-3, 8, 4,-8,-4, 4, 2,-4,-2, 6,-6, 6,-6, 3,-3, 3,-3, 4, 2, 4, 2, 2, 1, 2, 1},
{-12,12,12,-12,12,-12,-12,12,-6,-6, 6, 6, 6, 6,-6,-6,-6, 6,-6, 6, 6,-6, 6,-6,-8, 8, 8,-8,-4, 4, 4,-4,-3,-3,-3,-3, 3, 3, 3, 3,-4,-4, 4, 4,-2,-2, 2, 2,-4, 4,-4, 4,-2, 2,-2, 2,-2,-2,-2,-2,-1,-1,-1,-1},
{ 2, 0, 0, 0,-2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{ 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0,-2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{-6, 6, 0, 0, 6,-6, 0, 0,-4,-2, 0, 0, 4, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-3, 3, 0, 0,-3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-2,-1, 0, 0,-2,-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{ 4,-4, 0, 0,-4, 4, 0, 0, 2, 2, 0, 0,-2,-2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2,-2, 0, 0, 2,-2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0,-2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0,-2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0},
{ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-6, 6, 0, 0, 6,-6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-4,-2, 0, 0, 4, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-3, 3, 0, 0,-3, 3, 0, 0,-2,-1, 0, 0,-2,-1, 0, 0},
{ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4,-4, 0, 0,-4, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0,-2,-2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2,-2, 0, 0, 2,-2, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0},
{-6, 0, 6, 0, 6, 0,-6, 0, 0, 0, 0, 0, 0, 0, 0, 0,-4, 0,-2, 0, 4, 0, 2, 0,-3, 0, 3, 0,-3, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-2, 0,-1, 0,-2, 0,-1, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{ 0, 0, 0, 0, 0, 0, 0, 0,-6, 0, 6, 0, 6, 0,-6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-4, 0,-2, 0, 4, 0, 2, 0,-3, 0, 3, 0,-3, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0,-2, 0,-1, 0,-2, 0,-1, 0},
{18,-18,-18,18,-18,18,18,-18,12, 6,-12,-6,-12,-6,12, 6,12,-12, 6,-6,-12,12,-6, 6, 9,-9,-9, 9, 9,-9,-9, 9, 8, 4, 4, 2,-8,-4,-4,-2, 6, 3,-6,-3, 6, 3,-6,-3, 6,-6, 3,-3, 6,-6, 3,-3, 4, 2, 2, 1, 4, 2, 2, 1},
{-12,12,12,-12,12,-12,-12,12,-6,-6, 6, 6, 6, 6,-6,-6,-8, 8,-4, 4, 8,-8, 4,-4,-6, 6, 6,-6,-6, 6, 6,-6,-4,-4,-2,-2, 4, 4, 2, 2,-3,-3, 3, 3,-3,-3, 3, 3,-4, 4,-2, 2,-4, 4,-2, 2,-2,-2,-1,-1,-2,-2,-1,-1},
{ 4, 0,-4, 0,-4, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 0,-2, 0,-2, 0, 2, 0,-2, 0, 2, 0,-2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{ 0, 0, 0, 0, 0, 0, 0, 0, 4, 0,-4, 0,-4, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 0,-2, 0,-2, 0, 2, 0,-2, 0, 2, 0,-2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0},
{-12,12,12,-12,12,-12,-12,12,-8,-4, 8, 4, 8, 4,-8,-4,-6, 6,-6, 6, 6,-6, 6,-6,-6, 6, 6,-6,-6, 6, 6,-6,-4,-2,-4,-2, 4, 2, 4, 2,-4,-2, 4, 2,-4,-2, 4, 2,-3, 3,-3, 3,-3, 3,-3, 3,-2,-1,-2,-1,-2,-1,-2,-1},
{ 8,-8,-8, 8,-8, 8, 8,-8, 4, 4,-4,-4,-4,-4, 4, 4, 4,-4, 4,-4,-4, 4,-4, 4, 4,-4,-4, 4, 4,-4,-4, 4, 2, 2, 2, 2,-2,-2,-2,-2, 2, 2,-2,-2, 2, 2,-2,-2, 2,-2, 2,-2, 2,-2, 2,-2, 1, 1, 1, 1, 1, 1, 1, 1}};


int ismonotonic(double val[], int ix)
{   /* while loop based check of monotonicity,
       so on very large bases that fail, it 
       stops early. Starts at end.  */
  int counter = ix - 1,output = 1;
  
  while( counter )
    { counter--;  
      if(val[counter] - val[counter + 1] > 0)
	{
	  counter = 0;
	  output = 0;
	}
    }
  return output;
}


int isregular(double val[], int ix)
{   /* while loop based check of monotonicity,
       so on very large bases that fail, it 
       stops early. Starts at end.  */
  int counter = ix - 2,output = 1;
  double temp = val[counter] - val[counter + 1];
  while( counter )
    { counter--;

      if(val[counter] - val[counter + 1] != temp)
	{
	  counter = 0;
	  output = 0;
	}
    }
  return output;
}


int ijk2n(int i, int j, int k)
{
  return(i+4*j+16*k);
}


double tricubic_eval(double a[64], double x, double y, double z)
{
  int i,j,k;
  double ret=(double)(0.0);
  /* TRICUBIC EVAL
     This is the short version of tricubic_eval. It is used to compute
     the value of the function at a given point (x,y,z). To compute
     partial derivatives of f, use the full version with the extra args.
  */
  for (i=0;i<4;i++)
    {
      for (j=0;j<4;j++) 
	{
	  for (k=0;k<4;k++) 
	    {
	      ret+=a[ijk2n(i,j,k)]*pow(x,i)*pow(y,j)*pow(z,k);
	    }
	}
    }
  return(ret);
}


int _compare_fun(const void* a, const void* b)
{
  return (**(int**)a - **(int**)b);
}


int _compare_double(const void* a, const void* b)
{
  return (int)(*(double*)a - *(double*)b);
}


void int_argsort(int outvec[], int invec[], int len)
{ int i;
  int** temp = malloc(len * sizeof(int*));
  /* temp is constructed to reference invec, temp will
     be the modified order. outvec is the difference
     from the start to provide indicies for other matricies*/
  for(i=0; i<len; i++)
    {
      temp[i] = &invec[i];
    }

  qsort(temp,len,sizeof(int*),_compare_fun);
  for(i=0; i<len; i++)
    {
      outvec[i] = (int)(temp[i] - &invec[0]);
    }
  free(temp);
}


void _nonreg_x_construct(double val[], double inmat[], int shape[])
{
  int k,j,i,idx0,idx1,gap0,gap1;
  gap0 = shape[0]-2;
  gap1 = (shape[1]-2)*shape[0];
  idx0 = 0;
  idx1 = 0;
  for(k=0;k<2;k++)
    {
      for(j=0;j<2;j++)
	{
	  for(i=0;i<2;i++)
	    {
	      val[idx1] = inmat[idx0];
	      idx1++;
	      idx0++;
	    }
	  idx0 = idx0 + gap0;
	}
      idx1 = idx1 + gap1;				    
    }

}


void tridiff(double outmat[], double inmat[], double x[4], int shapeout[3], int shapein[3], int dim)
{
  /*outmat is the matrix reduced by 2 (derivatives calculated along same base or centered)
   dimension of derivative is specified by 'dim', the shape of the input array is described by
   'shape'. The arrays are always three dimensional (hence tridiff HARDCODED). Positions along
   derivative axis specified by 'x' and will have length 4 in inmat, and 2 in the outmat.  Other
  dimensions are variable and sized accoriding to the discrepancy as shown by the difference 
  of shapeout and shapein*/

  /*x0,x1,and x2 represent some sort of einstein notation, where the iteration
   follows a similar convention to the levi-civita symbol*/
  int x0,x1,x2,idx,gap,gap0,gap1,ixin,ixout,x0lim,x1lim,x2lim;
  x0lim = shapeout[0];
  x1lim = shapeout[1];
  x2lim = shapeout[2];
  ixout = 0;

  if(dim == 0)
    {
      gap = 1;
    }
  else if(dim == 1)
    {
      gap = shapein[0];
    }
  else
    {
      gap = shapein[0]*shapein[1];
    }

  gap0 = shapein[0] - x0lim;
  gap1 = (shapein[1] - x1lim)*shapein[0];
  ixin = (gap0 + gap1 + (shapein[0]*shapein[1])*(shapein[2] - x2lim))/2;

  
  for(x2=0; x2<x2lim; x2++)
    {
      for(x1=0; x1<x1lim; x1++)
	{
	  for(x0=0; x0<x0lim; x0++)
	    { 
	      idx = ixin/gap;
	      outmat[ixout] = (inmat[ixin + gap] - inmat[ixin - gap])/(x[idx + 1] - x[idx - 1]);
	      ixout++;
	      ixin++;
	    }
	  ixin = ixin + gap0;
	}
      ixin = ixin + gap1;
    }
}


void _gen_nonreg_x(double val[], double f[], double x0[4], double x1[4], double x2[4])
{ /*initialize necessary derivatives */
  double dfdx0[32];//[2][4][4];
  double dfdx1[16];//[2][2][4];
  double dfdx2[8];//[2][2][2];
  double dfdx01[16];//[2][2][4];
  double dfdx12[8];//[2][2][2];
  double dfdx02[8];//[2][2][2];
  double dfdx012[8];//[2][2][2];
  /* i think i need to modify tridiff to intelligently deal with the different sizes  */

  /*int in[3] = {4,4,4};*/
  int in[3];
  in[0] = 4;
  in[1] = 4;
  in[2] = 4;
  _nonreg_x_construct(&val[0],&f[21],in);

  int out[3] = {2,4,4};

  
  /* x0 derivative */
  tridiff(dfdx0, f, x0, out, in, 0);
  _nonreg_x_construct(&val[1], &dfdx0[10], out);

  /* x1 derivative */
  out[1] = 2;

  tridiff(dfdx1, f, x1, out, in, 1);
  _nonreg_x_construct(&val[2], &dfdx1[4], out);
  
  in[0] = 2;
  tridiff(dfdx01, dfdx0, x1, out, in, 1);
  _nonreg_x_construct(&val[4], &dfdx01[4], out);

  /* x2 derivative */
  out[2] = 2;
 
  in[0] = 4;
  tridiff(dfdx2, f, x2, out, in, 2);
  _nonreg_x_construct(&val[3], &dfdx2[0], out);  

  in[0] = 2;
  tridiff(dfdx02, dfdx0, x2, out, in, 2);
  _nonreg_x_construct(&val[5], &dfdx02[0], out);    

  in[1] = 2;
  tridiff(dfdx12, dfdx1, x2, out, in, 2);
  _nonreg_x_construct(&val[6], &dfdx02[0], out);
  
  tridiff(dfdx012, dfdx01, x2, out, in, 2);
  _nonreg_x_construct(&val[7], &dfdx02[0], out);    

}


void tricubic_get_coeff_stacked(double a[64], double x[64])
{
  int i,j;
  for (i=0;i<64;i++) 
    {
      a[i]=(double)(0.0);
      for (j=0;j<64;j++) 
	{
	  a[i]+=A[i][j]*x[j];
	}
      a[i] = a[i]/8; /* A is the combination of A_v2 and the proper derivative operator as ints (requires a division by 8)  */
    }
}


void tricubic_get_coeff_stacked_nonreg(double a[64], double f[64], double x0[], double x1[], double x2[])
{
  int i,j;
  double x[64];
  
  _gen_nonreg_x(x, f, x0, x1, x2);
  for (i=0;i<64;i++) 
    {
      a[i]=(double)(0.0);
      for (j=0;j<64;j++) 
	{
	  a[i]+=A_v2[i][j]*x[j];
	}
    }
}


void reg_ev(double val[], double dx0[], double dx1[], double dx2[], double f[], int pos[], int indx[], int ix0, int ix1, int ix2, int ix)
{
  int i,j,k,l,iter = -1,gap1,gap2,loc,findx;
  double fin[64],a[64];

  /* does this pertain only to the python/c interface ?*/
  gap1 = ix0 - 4;
  gap2 = ix0*(ix1 - 4);

 
  for(i=0;i < ix; i++)
    {
      
      /* generate matrix for input into interp, this
       is the first attempt at trying to speed up the 
      equation by forcing it more onto the C side*/
      loc = indx[i];
      if(iter != pos[loc])
	{ 
	  findx = 0;
	  iter = pos[loc];
	    /* iter provides a unique identifier to the voxel of
		interest, and the code generates the interpolating
		coefficients once per voxel (at max). The evaluated points
		are sorted such that all values of a voxel are calculated
		in direct sequence. */
		
	    /* the padding of f (from python) allows for a lot of
	    	simplifcation, as its starts 1 off on every dimension */
	  for(l = 0;l < 4; l++)
	    {
	      for(k = 0;k < 4; k++)
		{
		  for(j = 0;j < 4; j++)
		    { 
		      fin[findx] = *(f + iter);
		      findx++;
		      iter++;
		    }
		  iter = iter + gap1;
		}	  
	      iter = iter + gap2;
	    }
	  iter = pos[loc];
	  tricubic_get_coeff_stacked(a,fin);


	}
      val[loc] = tricubic_eval(a,dx0[loc],dx1[loc],dx2[loc]);

    }
}

void nonreg_ev(double val[], double x0[], double x1[], double x2[], double f[], double fx0[], double fx1[], double fx2[], int ix0, int ix1, int ix2, int ix)
{
  int i,j,k,l,iter = -1,gap1,gap2,loc,findx;
  double fin[64],a[64];

  double* dx0 = malloc(ix*sizeof(double));
  double* dx1 = malloc(ix*sizeof(double));
  double* dx2 = malloc(ix*sizeof(double));
  int* in0 = malloc(ix*sizeof(int));
  int* in1 = malloc(ix*sizeof(int));
  int* in2 = malloc(ix*sizeof(int));
  int* pos = malloc(ix*sizeof(int));
  int* indx = malloc(ix*sizeof(int));

  gap1 = ix0 - 4;
  gap2 = ix0*(ix1 - 4);


  /* solve for indexes */
  for(k=0;k<ix;k++)
    {
      in0[k] = *(int*) bsearch(&x0[k], fx0, ix0, sizeof(double), _compare_double);
      in1[k] = *(int*) bsearch(&x1[k], fx1, ix1, sizeof(double), _compare_double);
      in2[k] = *(int*) bsearch(&x2[k], fx2, ix2, sizeof(double), _compare_double);
      pos[k] = in0[k] + ix0*(in1[k] + ix1*in2[k]); 
    }
  int_argsort(indx, pos, ix);
  

  /*generate pos and loc */

 
  for(i=0;i < ix; i++)
    {
      
      /* generate matrix for input into interp, this
       is the first attempt at trying to speed up the 
      equation by forcing it more onto the C side*/
      loc = indx[i];
      if(iter != pos[loc])
	{ 
	  findx = 0;
	  iter = pos[loc];
	    /* iter provides a unique identifier to the voxel of
		interest, and the code generates the interpolating
		coefficients once per voxel (at max). The evaluated points
		are sorted such that all values of a voxel are calculated
		in direct sequence. */
		
	    /* the padding of f (from python) allows for a lot of
	    	simplifcation, as its starts 1 off on every dimension */
	  for(l = 0;l < 4; l++)
	    {
	      for(k = 0;k < 4; k++)
		{
		  for(j = 0;j < 4; j++)
		    { 
		      fin[findx] = *(f + iter);
		      findx++;
		      iter++;
		    }
		  iter = iter + gap1;
		}	  
	      iter = iter + gap2;
	    }
	  iter = pos[loc];
	  tricubic_get_coeff_stacked_nonreg(a,fin,&x0[loc],&x1[loc],&x2[loc]);


	}
      val[loc] = tricubic_eval(a,dx0[loc],dx1[loc],dx2[loc]);

    }

  free(dx0);
  free(dx1);
  free(dx2);
  free(in0);
  free(in1);
  free(in2);
  free(pos);
  free(indx);

}


void ev(double val[], double x0[], double x1[], double x2[], double f[], double fx0[], double fx1[], double fx2[], int ix0, int ix1, int ix2, int ix)
{ 
  if(isregular(fx0, ix0) && isregular(fx1, ix1) && isregular(fx2, ix2))
    {
      int idx;
      double dx0gap,dx1gap,dx2gap,tempx0,tempx1,tempx2;
      double* dx0 = malloc(ix*sizeof(double));
      double* dx1 = malloc(ix*sizeof(double));
      double* dx2 = malloc(ix*sizeof(double));    
      int* pos = malloc(ix*sizeof(int));
      int* loc = malloc(ix*sizeof(int));

      dx0gap = fx0[1]-fx0[0];
      dx1gap = fx1[1]-fx1[0];
      dx2gap = fx2[1]-fx2[0];

      /*generate indicies*/
      for(idx=0;idx<ix;idx++)
	{
	  dx0[idx] = modf((x0[idx] - x0[0])/dx0gap,&tempx0);
	  dx1[idx] = modf((x1[idx] - x1[0])/dx1gap,&tempx1);
	  dx2[idx] = modf((x2[idx] - x2[0])/dx2gap,&tempx2);
	  pos[idx] = (int)tempx0 + ix0*((int)tempx1 + ix1*((int)tempx2));
	}
      int_argsort(loc, pos, ix);

      reg_ev(val, dx0, dx1, dx2, f, pos, loc, ix0, ix1, ix2, ix);

      free(dx0);
      free(dx1);
      free(dx2);
      free(pos);
      free(loc);
    }
  else
    {

      nonreg_ev( val, x0, x1, x2, f, fx0, fx1, fx2, ix0, ix1, ix2, ix);

    }

} 
