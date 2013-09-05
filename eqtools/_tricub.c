#include <math.h>

/*****************************************************************
 
    This file is part of the EqTools package.

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
{0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -4, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, -20, 16, -4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -4, 12, -12, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -4, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -2, 0, 2, 0, 0, 0, 0, 0, -2, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 14, -16, -2, 0, 0, 0, 0, 4, -10, 8, -2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -2, -10, 10, 2, 0, 0, 0, 0, -2, 6, -6, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, -20, 0, 0, 0, 16, 0, 0, 0, -4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, -4, 0, 14, 0, -14, 0, -8, 0, 8, 0, 2, 0, -2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
{0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -8, -28, 32, 4, -28, 46, -32, 14, 16, -40, 32, -8, -4, 10, -8, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
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

int ijk2n(int i, int j, int k) {
  return(i+4*j+16*k);
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
    a[i] = a[i]/8; /* A2 is the combination of A and the proper derivative operator as ints (requires a division by 8)  */
  }
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
  for (i=0;i<4;i++) {
    for (j=0;j<4;j++) {
      for (k=0;k<4;k++) {
        ret+=a[ijk2n(i,j,k)]*pow(x,i)*pow(y,j)*pow(z,k);
      }
    }
  }
  return(ret);
}

void ev(double val[], double dx1[], double dx2[], double dx3[], double f[], int pos[], int indx[], int fx1, int fx2, int fx3, int ix)
{
  int i,j,k,l,iter = -1,gap1,gap2,loc,findx;
  double fin[64],a[64];
  gap1 = fx2 - 4;
  gap2 = fx3*(fx2 - 4);

 
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
      val[loc] = tricubic_eval(a,dx1[loc],dx2[loc],dx3[loc]);

    }
}

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
