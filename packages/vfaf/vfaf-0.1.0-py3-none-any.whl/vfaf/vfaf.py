
import warnings
warnings.filterwarnings('ignore')
import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def make_confusion_matrix(cf,
                          group_names=None,
                          categories='auto',
                          count=True,
                          percent=True,
                          cbar=True,
                          xyticks=True,
                          xyplotlabels=True,
                          sum_stats=True,
                          figsize=None,
                          cmap='Blues',
                          title=None):
    '''
    This function will make a pretty plot of an sklearn Confusion Matrix cm using a Seaborn heatmap visualization.
    Arguments
    ---------
    cf:            confusion matrix to be passed in
    group_names:   List of strings that represent the labels row by row to be shown in each square.
    categories:    List of strings containing the categories to be displayed on the x,y axis. Default is 'auto'
    count:         If True, show the raw number in the confusion matrix. Default is True.
    normalize:     If True, show the proportions for each category. Default is True.
    cbar:          If True, show the color bar. The cbar values are based off the values in the confusion matrix.
                   Default is True.
    xyticks:       If True, show x and y ticks. Default is True.
    xyplotlabels:  If True, show 'True Label' and 'Predicted Label' on the figure. Default is True.
    sum_stats:     If True, display summary statistics below the figure. Default is True.
    figsize:       Tuple representing the figure size. Default will be the matplotlib rcParams value.
    cmap:          Colormap of the values displayed from matplotlib.pyplot.cm. Default is 'Blues'
                   See http://matplotlib.org/examples/color/colormaps_reference.html
                   
    title:         Title for the heatmap. Default is None.
    '''


    # CODE TO GENERATE TEXT INSIDE EACH SQUARE
    blanks = ['' for i in range(cf.size)]

    if group_names and len(group_names)==cf.size:
        group_labels = ["{}\n".format(value) for value in group_names]
    else:
        group_labels = blanks

    if count:
        group_counts = ["{0:0.0f}\n".format(value) for value in cf.flatten()]
    else:
        group_counts = blanks

    if percent:
        group_percentages = ["{0:.2%}".format(value) for value in cf.flatten()/np.sum(cf)]
    else:
        group_percentages = blanks

    box_labels = [f"{v1}{v2}{v3}".strip() for v1, v2, v3 in zip(group_labels,group_counts,group_percentages)]
    box_labels = np.asarray(box_labels).reshape(cf.shape[0],cf.shape[1])


    # CODE TO GENERATE SUMMARY STATISTICS & TEXT FOR SUMMARY STATS
    if sum_stats:
        #Accuracy is sum of diagonal divided by total observations
        accuracy  = np.trace(cf) / float(np.sum(cf))

        #if it is a binary confusion matrix, show some more stats
        if len(cf)==2:
            #Metrics for Binary Confusion Matrices
            precision = cf[1,1] / sum(cf[:,1])
            recall    = cf[1,1] / sum(cf[1,:])
            f1_score  = 2*precision*recall / (precision + recall)
            stats_text = "\n\nAccuracy={:0.3f} | Precision={:0.3f} | Recall={:0.3f} | F1 Score={:0.3f}".format(
                accuracy,precision,recall,f1_score)
        else:
            stats_text = "\n\nAccuracy={:0.3f}".format(accuracy)
    else:
        stats_text = ""


    # SET FIGURE PARAMETERS ACCORDING TO OTHER ARGUMENTS
    if figsize==None:
        #Get default figure size if not set
        figsize = plt.rcParams.get('figure.figsize')

    if xyticks==False:
        #Do not show categories if xyticks is False
        categories=False


    # MAKE THE HEATMAP VISUALIZATION
    plt.figure(figsize=figsize)
    sns.heatmap(cf,annot=box_labels,fmt="",cmap=cmap,cbar=cbar,xticklabels=categories,yticklabels=categories)

    if xyplotlabels:
        plt.ylabel('True label')
        plt.xlabel('Predicted label' + stats_text)
    else:
        plt.xlabel(stats_text)
    
    if title:
        plt.title(title)

        
def plt_hist_with_hue(target_one:pd.DataFrame, target_cero: pd.DataFrame, feature:str)->plt:
    """Plot 2 histograms in 1 plot, with alpha 

    Args:
        target_one (pd.DataFrame): dataframe with target value = 1
        target_cero (pd.DataFrame): dataframe with target value = 0
        feature (str): feature name 

    Returns:
        plt: matplot lib chart
    """
    red_blue = ['#EF4836','#19B5FE']
    palette = sns.color_palette(red_blue)
    sns.set_palette(palette)
    sns.set_style("white")

    fig,ax = plt.subplots(figsize=(20, 7))

    #   {feature}
    plt.title(f'{feature}\nDistribution', fontsize=16)
    target_one[f'{feature}'].hist( alpha=0.7, bins=30, label = 'Fraud')
    target_cero[f'{feature}'].hist( alpha=0.7, bins=30, label = 'Not Fraud')
    plt.legend(loc = 'upper right', fontsize=14)
    plt.xlabel(f'{feature}', fontsize=14)
    plt.ylabel('Count', fontsize=14)
    # fig.tight_layout()
    plt.show()

def plot_bar_according_to_target(target_one: pd.DataFrame,target_cero:pd.DataFrame,feature:str, show_n_values:int, vertical_var = True,normalize:bool = False, size = 'small')->plt:
    """Bar plot with 2 target values

    Args:
        target_one (pd.DataFrame): dataframe with target value = 1
        target_cero (pd.DataFrame): dataframe with target value = 0
        feature (str): feature name
        show_n_values (int): number of values to show in the plot
        vertical_var (bool, optional): Vertical bar or horizontal bar. Defaults to True.
        normalize (bool, optional): proportions instead of count. Defaults to False.
        size (str, optional): size of the plot. Defaults to 'small'.

    Returns:
        plt: matplot lib chart
    """

    kind_ = 'bar' if vertical_var == True else 'barh'
    
    if size == 'small':
        size_ = (12,5)
    elif size == 'medium':
        size_ =  (20,7)
    elif size == 'large':
        size_ =  (30,11)
    
    
    if show_n_values == '':
        fig, axs = plt.subplots(1,2,figsize = size_)
        left_plot_target_true = target_one[feature].value_counts(normalize = normalize).plot(kind = kind_ , title = f'Fraud vs {feature}',ax=axs[0], color = '#EF4836',label = 'Fraud', alpha = 0.5, legend = True)
        right_plot_target_false = target_cero[feature].value_counts(normalize = normalize).plot(kind = kind_, title = f'Not Fraud vs {feature}',ax=axs[1], color = '#19B5FE',label = 'Not Fraud', alpha = 0.5, legend = True)
        axs[0].legend(loc = 'upper right', fontsize=14)
        axs[1].legend(loc = 'upper right', fontsize=14)
    else:
        fig, axs = plt.subplots(1,2,figsize = size_)
        left_plot_target_true = target_one[feature].value_counts(normalize = normalize).head(show_n_values).plot(kind = kind_ , title = f'Fraud vs {feature}',ax=axs[0], color = '#EF4836',label = 'Fraud', alpha = 0.5, legend = True)
        right_plot_target_false = target_cero[feature].value_counts(normalize = normalize).head(show_n_values).plot(kind = kind_, title = f'Not Fraud vs {feature}',ax=axs[1], color = '#19B5FE',label = 'Not Fraud', alpha = 0.5, legend = True)
        axs[0].legend(loc = 'upper right', fontsize=14)
        axs[1].legend(loc = 'upper right', fontsize=14)

def plt_hist_without_hue(target_one: pd.DataFrame,target_cero:pd.DataFrame,feature:str, size = 'small')->plt:
    """Hist plot with 2 target values without hue

    Args:
        target_one (pd.DataFrame): dataframe with target value = 1
        target_cero (pd.DataFrame): dataframe with target value = 0
        feature (str): feature name
        size (str, optional): size of the plot. Defaults to 'small'.

    Returns:
        plt: matplot lib chart
    """

    
    if size == 'small':
        size_ = (12,5)
    elif size == 'medium':
        size_ =  (20,7)
    elif size == 'large':
        size_ =  (30,11)
    
    
    sns.set_style("white")
    fig, axs = plt.subplots(1,2,figsize = size_)
    plt.title(f'{feature}\nDistribution', fontsize=16)
    left_plot_target_true = target_one[f'{feature}'].hist( alpha=0.7, bins=30, label = 'Fraud',ax=axs[0], color = '#EF4836')
    plt.title(f'{feature}\nDistribution', fontsize=16)
    right_plot_target_false = target_cero[f'{feature}'].hist( alpha=0.7, bins=30, label = 'Not Fraud',ax=axs[1], color = '#19B5FE')

    axs[0].legend(loc = 'upper right', fontsize=14)
    axs[0].set_title(f'{feature}\nDistribution', fontsize=16)
    axs[0].set_xlabel(f'{feature}', fontsize=14)
    axs[0].set_ylabel('Count', fontsize=14)
    
    axs[1].legend(loc = 'upper right', fontsize=14)
    axs[1].set_title(f'Not {feature}\nDistribution', fontsize=16)
    axs[1].set_xlabel(f'{feature}', fontsize=14)
    axs[1].set_ylabel('Count', fontsize=14)

def plot_single_bar(dataframe: pd.DataFrame,feature:str, show_n_values:int, vertical_var = True,normalize:bool = False, size = 'small')->plt:
    """Sngle bar plot

    Args:
        dataframe (pd.DataFrame): dataframe 
        feature (str): feature name
        show_n_values (int): number of values to show in the plot
        vertical_var (bool, optional): Vertical bar or horizontal bar. Defaults to True.
        normalize (bool, optional): proportions instead of count. Defaults to False.
        size (str, optional): size of the plot. Defaults to 'small'.

    Returns:
        plt: matplot lib chart
    """

    kind_ = 'bar' if vertical_var == True else 'barh'
    
    if size == 'small':
        size_ = (12,5)
    elif size == 'medium':
        size_ =  (20,7)
    elif size == 'large':
        size_ =  (30,11)
    
    
    if show_n_values == '':
        fig, axs = plt.subplots(figsize = size_)
        single_bar_plot = dataframe[feature].value_counts(normalize = normalize).plot(kind = kind_, color = '#19B5FE', alpha = 0.5, legend = True)
    else:
        fig, axs = plt.subplots(figsize = size_)
        single_bar_plot = dataframe[feature].value_counts(normalize = normalize).head(show_n_values).plot(kind = kind_, color = '#19B5FE', alpha = 0.5, legend = True)

    plt.title(f'{feature}\nProportion', fontsize = 14)
    plt.legend(loc = 'upper right', fontsize=14)
