# Import Libraries
import numpy as np
import pandas as pd
import yfinance as yf
from math import sqrt
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter


def pythg(pt1, pt2):
    a_sq = (pt2[0] - pt1[0]) ** 2
    b_sq = (pt2[1] - pt1[1]) ** 2
    return sqrt(a_sq + b_sq)


def loc_min_max(points):
    loc_minima = []
    loc_maxima = []
    prev_pts = [(0, points[0]), (1, points[1])]
    for i in range(1, len(points) - 1):
        append_to = ''
        if points[i - 1] > points[i] < points[i + 1]:
            append_to = 'min'
        elif points[i - 1] < points[i] > points[i + 1]:
            append_to = 'max'
        if append_to:
            if loc_minima or loc_maxima:
                prev_distance = pythg(prev_pts[0], prev_pts[1]) * 0.5
                curr_distance = pythg(prev_pts[1], (i, points[i]))
                if curr_distance >= prev_distance:
                    prev_pts[0] = prev_pts[1]
                    prev_pts[1] = (i, points[i])
                    if append_to == 'min':
                        loc_minima.append((i, points[i]))
                    else:
                        loc_maxima.append((i, points[i]))
            else:
                prev_pts[0] = prev_pts[1]
                prev_pts[1] = (i, points[i])
                if append_to == 'min':
                    loc_minima.append((i, points[i]))
                else:
                    loc_maxima.append((i, points[i]))
    return loc_minima, loc_maxima


def line_mse(pt1, pt2, data):

    dist = 0
    dist_sq = 0
    sum_dist_sq = 0
    mean_sq_err = 0
    length = len(data)
    norm = np.linalg.norm

    for pt3 in range(0, length):
            p1 = data[pt1]
            p2 = data[pt2]
            p3 = data[pt3]

            dist = np.abs(norm(np.cross(p2-p1, p1-p3)))/norm(p2-p1)
            dist_sq = dist ** 2
            sum_dist_sq = sum_dist_sq + dist_sq
            mean_sq_err = sum_dist_sq / length
            return mean_sq_err


def s_r_lines(data):
    lines = []
    for pt1 in range(0, len(data) - 1):
        for pt2 in range(0, len(data)):
            if pt1 != pt2:
                mse_val = line_mse(pt1, pt2, data)
                lines.append((data[pt1], data[pt2], mse_val))


# Main entrance
if __name__ == '__main__':

    start = '2018-01-01'
    end = '2021-10-29'
    symbol = 'OKE'

    # Get the data from Yahoo! Finance
    df = yf.download(symbol, start, end)

    # Display the data
    df.tail(10)

    series = df['Close']
    series.index = np.arange(series.shape[0])

    month_diff = series.shape[0] // 30
    if month_diff == 0:
        month_diff = 1

    smooth = int(2 * month_diff + 3)
    points = savgol_filter(series, smooth, 7)

    plt.figure(figsize=(15, 7))
    plt.title(symbol)

    plt.xlabel('Days')
    plt.ylabel('Price')
    plt.plot(series, label=f'{symbol}')
    plt.plot(points, label=f'Smooth {symbol}')

    plt.legend()
    plt.show()
