import math
import numpy as np
from sklearn import decomposition
from sklearn.preprocessing import StandardScaler

def hard_standard(input_matrix):
    """
    standard by average 
    each column standard, use average from sorted row
    """

    rank_matrix = []
    for i in range(input_matrix.shape[1]):
        rank_matrix.append(np.argsort(np.argsort(input_matrix[:,i])))
    rank_matrix = np.array(rank_matrix)
    rank_matrix = rank_matrix.T

    sorted_matrix = []
    for i in range(input_matrix.shape[1]):
        sorted_matrix.append(np.sort(input_matrix[:,i]))
    sorted_matrix = np.array(sorted_matrix)
    sorted_matrix = sorted_matrix.T

    avg_array = []
    for i in range(len(sorted_matrix)):
        avg_array.append(np.average(sorted_matrix[i]))
    avg_array = np.array(avg_array)

    output_matrix = []
    for i in range(rank_matrix.shape[1]):
        output_matrix.append(avg_array[rank_matrix[:,i]])
    output_matrix = np.array(output_matrix)
    output_matrix = output_matrix.T    

    return output_matrix

def euler_distance(point1, point2):
    distance = 0.0
    for a, b in zip(point1, point2):
        distance += math.pow(a - b, 2)
    return math.sqrt(distance)


def pearson_correlation(array1, array2):
    x = np.vstack((array1, array2))
    r = np.corrcoef(x)
    return r[0][1]


def PCA_do(input_list, n_components, correlation=False):
    """
    do the PCA
    input a list of lists: [[a1,a2,a3],[b1,b2,b3],...]
    a or b is sample
    1,2,3 is dimension
    n_components is the nums of PC you want get
    """
    pca = decomposition.PCA(n_components=n_components)

    input_list = np.array(input_list)

    if correlation:
        input_list = StandardScaler().fit_transform(input_list)

    return pca.fit_transform(input_list), pca.explained_variance_ratio_


def PCA_figure(input_dict, ax, correlation=False):
    """
    input_dict = {
        group_1 : [[a1,a2,a3],...],
        group_2 : [[b1,b2,b3],...]
    }
    """
    data_tran = []
    for i in input_dict:
        for j in input_dict[i]:
            data_tran.append((i, j))

    pca_input = [data for type, data in data_tran]

    pca_output, pca_ratio = PCA_do(pca_input, 2, correlation)

    output_tran = []
    for i in range(0, len(pca_output)):
        output_tran.append((data_tran[i][0], pca_output[i]))

    color_style = ['bo', 'go', 'ro', 'co', 'mo', 'yo', 'ko', 'wo']

    num = 0
    for type in input_dict:
        PC1 = [data[0] for type_tmp, data in output_tran if type_tmp == type]
        PC2 = [data[1] for type_tmp, data in output_tran if type_tmp == type]
        ax.plot(PC1, PC2, color_style[num], markersize=3, label=type)
        num = num + 1

    ax.legend(loc='upper left')

    ax.xlabel("PC1  %.1f%%" % (pca_ratio[0] * 100))
    ax.ylabel("PC2  %.1f%%" % (pca_ratio[1] * 100))

    # plt.savefig(figure_file, dpi=1000)

    return ax, output_tran, pca_ratio
