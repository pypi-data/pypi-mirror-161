#!/usr/bin/env python
# BayesianROC.py
# by André Carrington and Franz Mayr

from deeproc.DeepROC import DeepROC

class BayesianROC(DeepROC):

    def __init__(self, predicted_scores=None, labels=None, poslabel=None, BayesianPriorPoint=None,
                 costs=None, quiet=False):
        '''BayesianROC constructor. If predicted_scores and labels are
           empty then it returns an empty object.'''

        super().__init__(predicted_scores=predicted_scores, labels=labels, poslabel=poslabel, quiet=quiet)

        #   Bayesian ROC...
        self.BayesianPriorPoint  = BayesianPriorPoint
        self.costs               = costs
    #enddef

    def analyzeGroupFoldsVsChance(self, groupIndex, prevalence, costs):
        BayesianPriorPoint = (0.5, 0.5)
        forFolds           = True
        return self.analyzeGroupVs(groupIndex, prevalence, costs, prior, forFolds)
    #enddef

    def analyzeGroupVsChance(self, groupIndex, prevalence, costs):
        BayesianPriorPoint = (0.5, 0.5)
        forFolds           = False
        return self.analyzeGroupVs(groupIndex, prevalence, costs, BayesianPriorPoint, forFolds)
    #enddef

    def analyzeGroupFoldsVsPrior(self, groupIndex, prevalence, costs, BayesianPriorPoint):
        if 'BayesianPriorPoint' not in locals():
            BayesianPriorPoint = self.BayesianPriorPoint
        forFolds = True
        return self.analyzeGroupVs(groupIndex, prevalence, costs, BayesianPriorPoint, forFolds)
    # enddef

    def analyzeGroupVsPrior(self, groupIndex, prevalence, costs, BayesianPriorPoint):
        if 'BayesianPriorPoint' not in locals():
            BayesianPriorPoint = self.BayesianPriorPoint
        forFolds = False
        return self.analyzeGroupVs(groupIndex, prevalence, costs, BayesianPriorPoint, forFolds)
    #enddef

    def getMeanROC_A_pi(self, prevalence, costs, BayesianPriorPoint):
        from bayesianroc.Helpers.BayesianROCFunctions import getA_pi
        if 'BayesianPriorPoint' not in locals():
            BayesianPriorPoint = self.BayesianPriorPoint
        return getA_pi(self.mean_fpr, self.mean_tpr, prevalence, costs, BayesianPriorPoint)
    #enddef

    def getA_pi(self, prevalence, costs, BayesianPriorPoint):
        from bayesianroc.Helpers.BayesianROCFunctions import getA_pi
        if 'BayesianPriorPoint' not in locals():
            BayesianPriorPoint = self.BayesianPriorPoint
        return getA_pi(self.full_fpr, self.full_tpr, prevalence, costs, BayesianPriorPoint)
    #enddef

    def setBayesianPriorPoint(self, BayesianPriorPoint):
        self.BayesianPriorPoint = BayesianPriorPoint
    #enddef

    def analyzeGroupVs(self, groupIndex, prevalence, costs, BayesianPriorPoint, forFolds):
        from bayesianroc.Helpers.BayesianROCFunctions import BayesianAUC

        returnValues     = self.getGroupForAUCi(groupIndex, forFolds)
        groupByOtherAxis = returnValues[3]
        if self.groupAxis == 'FPR':
            group = dict(x1=self.groups[groupIndex][0],
                         x2=self.groups[groupIndex][1],
                         y1=groupByOtherAxis[0],
                         y2=groupByOtherAxis[1])
        elif self.groupAxis == 'TPR':
            group = dict(y1=self.groups[groupIndex][0],
                         y2=self.groups[groupIndex][1],
                         x1=groupByOtherAxis[0],
                         x2=groupByOtherAxis[1])
        else:
            SystemError(f'This function has not been implemented yet for groupAxis=={self.groupAxis}.')
            group = None
        #endif

        if forFolds:
            measures_dict = BayesianAUC(self.mean_fpr, self.mean_tpr, group, prevalence, costs, BayesianPriorPoint)
        else:
            measures_dict = BayesianAUC(self.full_fpr, self.full_tpr, group, prevalence, costs, BayesianPriorPoint)
        #endif

        # # to compute Bhattacharyya Dissimilarity (1 - Bhattacharyya Coefficient) we need to
        # # put the posScores and negScores into bins, and then into dictionaries
        # #    first determine if the distributions are linearly separable, because badly chosen bins
        # #    could hide that. So, we need to choose bins wisely, if they are separable.
        # #
        # # first sort elements, high to low, by score, and within equal scores, by label (in descending order)
        # self.predicted_scores, self.newlabels, self.labels, self.sorted_full_slope_factors = \
        #     sortScoresAndLabels4(self.predicted_scores, self.newlabels, self.labels, self.full_slope_factor)
        # # second, determine seperability
        # # third, get the posScores and negScores so that we can make two binned distributions
        # bDissimilar   = BhattacharyyaDissimilarity()

        return measures_dict
    #enddef

    # modified slightly:
    def plotBayesianIsoLine(self, BayesianPriorPoint, neg, pos, costs):
        from   bayesianroc.Helpers.BayesianROCFunctions  import bayesian_iso_lines
        import numpy               as     np
        import matplotlib.pyplot   as     plt

        # plot iso_line that passes through the (bayesian) prior point
        bayes_iso_line_y, bayes_iso_line_x = bayesian_iso_lines(pos/(pos+neg), costs, BayesianPriorPoint)
        x = np.linspace(0, 1, 1000)
        plt.plot(x, bayes_iso_line_y(x), linestyle='-', color='black')
        plt.plot([BayesianPriorPoint[0]], [BayesianPriorPoint[1]], 'ko')
    # enddef

    def plotGroup(self, plotTitle, groupIndex, showError=False, showThresholds=True, showOptimalROCpoints=True,
                  costs=None, saveFileName=None, numShowThresh=20, showPlot=True, labelThresh=True,
                  full_fpr_tpr=True):
        fig, ax = super().plotGroup(plotTitle, groupIndex, showError, showThresholds, showOptimalROCpoints,
                                    costs, saveFileName, numShowThresh, showPlot, labelThresh, full_fpr_tpr)
        pos = 1 / (self.NPclassRatio + 1)
        neg = 1 - pos
        self.plotBayesianIsoLine(self.BayesianPriorPoint, neg, pos, costs)
        return fig, ax
    #enddef

    def plotGroupForFolds(self, plotTitle, groupIndex, foldsNPclassRatio, showError=False, showThresholds=True,
                          showOptimalROCpoints=True, costs=None, saveFileName=None, numShowThresh=20,
                          showPlot=True, labelThresh=True, full_fpr_tpr=True):
        fig, ax = super().plotGroupForFolds(plotTitle, groupIndex, foldsNPclassRatio, showError,
                                            showThresholds, showOptimalROCpoints, costs, saveFileName,
                                            numShowThresh, showPlot, labelThresh, full_fpr_tpr)
        pos = 1/(foldsNPclassRatio + 1)
        neg = 1 - pos
        self.plotBayesianIsoLine(self.BayesianPriorPoint, neg, pos, costs)
        return fig, ax
    #enddef

    def __str__(self):
        '''This method prints the object as a string of its content re 
           predicted scores, labels, full fpr, full tpr, full thresholds.'''
        super().__str__()

        rocdata = f'BayesianPriorPoint = {self.BayesianPriorPoint}\n'
        return rocdata
    #enddef 
