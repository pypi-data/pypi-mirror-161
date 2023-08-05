from scipy.stats import chi2_contingency, fisher_exact, hypergeom, ks_2samp, norm, shapiro
import numpy as np
import pingouin as pg
from scipy.signal import find_peaks
from scipy import stats, integrate
from toolbiox.lib.common.fileIO import read_list_file
from fitter import Fitter
import math
import random
from scipy.special import factorial


def n50_stats(len_list, index_list=[10, 20, 30, 40, 50, 60, 70, 80, 90, 100]):
    """
    give me a seq length list or a generator
    """
    length_array = np.array(list(len_list))
    length_array.sort(axis=0, kind='mergesort')
    sorted_length_array = length_array[::-1]
    sum_len = sorted_length_array.sum()
    min_len = sorted_length_array.min()
    max_len = sorted_length_array.max()
    count_sum = len(sorted_length_array)
    percent_stats = np.percentile(sorted_length_array, index_list)

    adder_now = 0
    index_stats_dict = {}
    adder_count = 0
    for i in sorted_length_array:
        adder_now = adder_now + i
        adder_count = adder_count + 1
        for j in index_list:
            if adder_now / sum_len >= j / 100 and j not in index_stats_dict:
                # if index_list.index(j) - 1 >= 0:
                #     used_index.append(index_list[index_list.index(j) - 1])
                index_stats_dict[j] = {'count': adder_count, 'base': adder_now, 'length': i}

    return percent_stats, index_stats_dict, count_sum, sum_len, min_len, max_len

# https://en.wikipedia.org/wiki/False_discovery_rate#Benjamini%E2%80%93Hochberg_procedure
# Benjamini–Hochberg procedure
def get_qvalue(pvalue_dir):
    """

    pvalue_dir = {
        "ID_1":0.001,
        "ID_2":0.02,
        "ID_3":0.002,
        "ID_4":0.8,
        "ID_5":0.05,
        "ID_6":0.1,
    }
    :return:
    """

    sorted_id_list = sorted(pvalue_dir, key=lambda x: pvalue_dir[x])
    total_record = len(sorted_id_list)
    num = 1
    qvalue_dir = {}
    for i in sorted_id_list:
        qvalue = pvalue_dir[i] * total_record / num
        qvalue_dir[i] = qvalue
        num = num + 1
    return qvalue_dir


# we use https://github.com/raphaelvallat/pingouin

# t test
def t_test(list1, list2):
    """
    based on pingouin
    see: https://pingouin-stats.org/generated/pingouin.ttest.html#pingouin.ttest
    :return:
    pandas.DataFrame

    'T' : T-value
    'p-val' : p-value
    'dof' : degrees of freedom
    'cohen-d' : Cohen d effect size
    'CI95%' : 95% confidence intervals of the difference in means
    'power' : achieved power of the test ( = 1 - type II error)
    'BF10' : Bayes Factor of the alternative hypothesis

    example:
        output = t_test([1,2,3,4,5,6,7],[7,6,1,4,3,5,6,4])

    p_value = float(output['p-val'])
    """
    list1 = np.array(list1)
    list2 = np.array(list2)
    return pg.ttest(list1, list2)


# chi2 test
def two_categories_chi2(Contingency_table):
    """
    ref:
    https://codingdisciple.com/chi-squared-python.html
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chi2_contingency.html
    https://en.wikipedia.org/wiki/Contingency_table

    :param Contingency_table: https://en.wikipedia.org/wiki/Contingency_table

        if we have:

            A1          A2
        B1  num1        num2        num1+num2
        B2  num3        num4        num3+num4
            num1+num3   num2+num4   num1+num2+num3+num4

        then input Contingency_table will be:

        Contingency_table = [[num1,num2],[num3,num4]]

    :return:
    """

    obs = np.array(Contingency_table)

    chi2_value, p_value, freedom = chi2_contingency(obs)[0:3]

    return chi2_value, p_value, freedom


def fisher_enrichment(Contingency_table):
    """
    ref:
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.fisher_exact.html
    https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4743627/
    http://mengnote.blogspot.com/2012/12/calculate-correct-hypergeometric-p.html

    :param Contingency_table: https://en.wikipedia.org/wiki/Contingency_table

        if we have:

            A1          A2
        B1  num1        num2        num1+num2
        B2  num3        num4        num3+num4
            num1+num3   num2+num4   num1+num2+num3+num4

        then input Contingency_table will be:

        Contingency_table = [[num1,num2],[num3,num4]]

    :return:
    """

    oddsratio, pvalue = fisher_exact(Contingency_table)

    return oddsratio, pvalue


def hypergeom_enrichment(Contingency_table):
    """
    ref:
    https://stackoverflow.com/questions/6594840/what-are-equivalents-to-rs-phyper-function-in-python
    http://mengnote.blogspot.com/2012/12/calculate-correct-hypergeometric-p.html
    https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.stats.hypergeom.html
    Zhou, P., et al. (2019). "Dynamic Patterns of Gene Expression Additivity and Regulatory Variation throughout Maize Development." Mol Plant 12(3): 410-425.

    Models drawing objects from a bin. M is total number of objects, n is total number of Type I objects. RV counts number of Type I objects in N drawn without replacement from population.

    :param Contingency_table: https://en.wikipedia.org/wiki/Contingency_table

        if we have:

            A1          A2
        B1  num1        num2        num1+num2
        B2  num3        num4        num3+num4
            num1+num3   num2+num4   num1+num2+num3+num4

        then input Contingency_table will be:

        Contingency_table = [[num1,num2],[num3,num4]]
    :return:
    """

    # Contingency_table = [[45, 1284], [47, 6234]]

    [[num1, num2], [num3, num4]] = Contingency_table
    x = num1
    M = num1 + num2 + num3 + num4
    n = num1 + num3
    N = num1 + num2

    p_value = hypergeom.sf(x, M, n, N)

    rv = hypergeom(M, n, N)

    # probability mass function
    pmf_tmp = rv.pmf(np.arange(0, n + 1))

    expected_num = list(pmf_tmp).index(max(pmf_tmp)) + 1

    observed_num = x

    return observed_num, expected_num, p_value


# Kolmogorov-Smirnov test
"""
how it wort
http://www.physics.csbsju.edu/stats/KS-test.html

one sample vs hypothesis distribution
https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.stats.kstest.html

two sample (two distribution) compare
https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.stats.ks_2samp.html
"""


def two_distribution_test(data1, data2):
    """

    :param data1: list for all data from set 1
    :param data2: list for all data from set 2
    :return: KS statistic (D statistic) and p-value

    If the K-S statistic is small or the p-value is high, then we cannot reject the hypothesis that the distributions of the two samples are the same.


    https://stats.idre.ucla.edu/stata/faq/how-can-i-test-for-equality-of-distribution/
    HOW CAN I TEST FOR EQUALITY OF DISTRIBUTION?
    An alternative test to the classic t-test is the Kolmogorov-Smirnov test for equality of distribution functions.
    In a simple example, we’ll see if the distribution of writing test scores across gender are equal using the High-School
    and Beyond 2000 data set. We’ll first do a kernel density plot of writing scores by gender.

    https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.stats.ks_2samp.html

    file_list = [
    '/lustre/home/xuyuxing/Liu/A_D_Arabidopsis_F.txt',
    '/lustre/home/xuyuxing/Liu/A_D_Arabidopsis_O.txt',
    '/lustre/home/xuyuxing/Liu/A_D_Dodder_F.txt',
    '/lustre/home/xuyuxing/Liu/A_D_Dodder_O.txt',
    '/lustre/home/xuyuxing/Liu/S_D_Dodder_F.txt',
    '/lustre/home/xuyuxing/Liu/S_D_Dodder_O.txt',
    '/lustre/home/xuyuxing/Liu/S_D_Soybean_F.txt',
    '/lustre/home/xuyuxing/Liu/S_D_Soybean_O.txt',
    ]

    from toolbiox.lib.common.fileIO import read_list_file

    data_list = []
    for i in file_list:
        data_list.append([float(j) for j in read_list_file(i) if j != ''])

    for i in [0,2,4,6]:
        print(two_distribution_test(data_list[i],data_list[i+1]))

    """

    data1 = np.array(data1)
    data2 = np.array(data2)

    return tuple(ks_2samp(data1, data2))


# anova
# https://www.analyticsvidhya.com/blog/2018/01/anova-analysis-of-variance/
# https://pingouin-stats.org/generated/pingouin.anova.html#pingouin.anova

def anova(input_dataframe, dv, between, ss_type=2, detailed=True):
    """
    see https://pingouin-stats.org/generated/pingouin.anova.html#pingouin.anova for detail

    aov = pg.anova(dv='len', between=['supp', 'dose'], data=input_dataframe, detailed=True)

    input_dataframe should be pandas dataframe, each column is a variable, first row is name of variable for the column
    if in a csv file, it should like 'https://vincentarelbundock.github.io/Rdatasets/csv/datasets/ToothGrowth.csv'
    make df as:
    data = 'https://vincentarelbundock.github.io/Rdatasets/csv/datasets/ToothGrowth.csv'
    df = pd.read_csv(data, index_col=0)

    dv is one of the variable name which as y

    between is list of variable name

    :return
    'Source' : Factor names
    'SS' : Sums of squares
    'DF' : Degrees of freedom
    'MS' : Mean squares
    'F' : F-values
    'p-unc' : uncorrected p-values
    'np2' : Partial eta-square effect sizes

    """
    aov = pg.anova(dv=dv, between=between, data=input_dataframe, detailed=detailed, ss_type=ss_type)
    return aov


def norm_test(data_list):
    if len(data_list) > 3000:
        data_list_random = random.sample(data_list, 3000)
        statistic, pvalue = stats.shapiro(data_list_random)
    else:
        statistic, pvalue = stats.shapiro(data_list)
    
    return statistic, pvalue


def get_threshold(data_list, plot_flag=False, p_value=0.05):
    x, bins = np.histogram(data_list, bins='auto')
    peaks, properties = find_peaks(x, prominence=1, width=1)

    peak_dict = {}
    for i in range(len(peaks)):
        peak_dict[i] = (peaks[i], properties['widths'][i], properties['prominences'][i])

    top_peak = sorted(peak_dict, key=lambda x:peak_dict[x][2], reverse=True)[0]

    # if plot_flag:
    #     plt.plot(x)
    #     plt.plot(peaks[top_peak], x[peaks[top_peak]], "x")
    #     plt.vlines(x=peaks[top_peak], ymin=x[peaks[top_peak]] - properties["prominences"][top_peak],
    #             ymax = x[peaks[top_peak]], color = "C1")
    #     plt.hlines(y=properties["width_heights"][top_peak], xmin=properties["left_ips"][top_peak],
    #             xmax=properties["right_ips"][top_peak], color = "C1")
    #     plt.show()

    peak_site = peak_dict[top_peak][0]
    peak_width = peak_dict[top_peak][1]
    top_peak_range_index = int(peak_site-peak_width), math.ceil(peak_site+peak_width)
    top_peak_range = [bins[i] for i in top_peak_range_index]

    peak_data_list = [i for i in data_list if i >= top_peak_range[0] and i <= top_peak_range[1]]

    statistic, pvalue = norm_test(peak_data_list)

    f = Fitter(peak_data_list, distributions=['norm'])
    f.fit()

    # if plot_flag:
    #     f.summary()

    mu, sigma = f.fitted_param['norm']

    threshold = norm.ppf(p_value, loc=mu, scale = sigma)

    return threshold, mu, sigma, statistic, pvalue

# curve fit by gaussian distribution
def gaussian_funtion(x, *params):
    """
    y = $a * exp\biggl(-\frac{(x-b)^2}{c^2}\biggr)$
    """
    num_func = int(len(params)/3)

    y_list = []
    for i in range(num_func):
        y = np.zeros_like(x)
        param_range = list(range(3*i,3*(i+1),1))
        amp = params[int(param_range[0])]
        ctr = params[int(param_range[1])]
        wid = params[int(param_range[2])]
        y = y + amp * np.exp( -((x - ctr)/wid)**2)
        y_list.append(y)

    y_sum = np.zeros_like(x)
    for i in y_list:
        y_sum = y_sum + i

    y_sum = y_sum + params[-1]

    return y_sum    

def fit_plot(x, *params):
    num_func = int(len(params)/3)
    y_list = []
    for i in range(num_func):
        y = np.zeros_like(x)
        param_range = list(range(3*i,3*(i+1),1))
        amp = params[int(param_range[0])]
        ctr = params[int(param_range[1])]
        wid = params[int(param_range[2])]
        y = y + amp * np.exp( -((x - ctr)/wid)**2) + params[-1]
        y_list.append(y)
    return y_list

    
def get_peak_area(*params):
    # params = (1273,65,20,0)
    ctr = params[1]
    wid = params[2]
    area = integrate.quad(lambda x:gaussian_funtion(x, *params), ctr-6*wid, ctr+6*wid)
    return area[0]

"""
from scipy.optimize import curve_fit

How to use curve fit by gaussian distribution

有三个要优化的参数：a(amp, 峰高)，b(ctr, 位置)和c(wid, 峰宽)。

假设有两个峰重叠进去了
guess = []
guess.append([300, 0.8, 0.5])
guess.append([300, 1.2, 0.5])

background = 5

guess_total = []
for i in guess:
    guess_total.extend(i)
guess_total.append(background)

popt, pcov = curve_fit(func, x, y, p0=guess_total)

fit = func(x, *popt)
plt.scatter(x, y, s=20)
plt.plot(x, fit , ls='-', c='black', lw=1)

y_list = fit_plot(x, *popt)
baseline = np.zeros_like(x) + popt[-1]
for n,i in enumerate(y_list):
    plt.fill_between(x, i, baseline, facecolor=cm.rainbow(n/len(y_list)), alpha=0.6)
"""

def poisson(k, lamb):
  return (lamb**k/factorial(k)) * np.exp(-lamb)