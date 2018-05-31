# coding=utf-8
from typing import List, Dict, Text
from collections import OrderedDict

class Metric(object):

    def __init__(self, label, n, plural=None):
        self.label=label
        self.n=n
        self.plural=plural

    def add(self, n):
        self.n += n
        return self

    @property
    def _pair(self):
        if self.n==0:
            return ('no', self.label)
        elif self.n==1:
            return ('1', self.label)
        else:
            return (
                str(self.n),
                self.plural if self.plural is not None
                            else self.label+'s')

    def __str__(self):
        return '%s %s' % self._pair

    def __repr__(self):
        return '<"%s",%i>' % (self.label, self.n)


class Metrics(object):

    def __init__(self):
        self.metricNamed = OrderedDict()
        #type: Dict[Text, Metric]

    @property
    def all(self):
        _=self.metricNamed.values()
        return _

    def add(self, metric):
        #type: (Metric)->Metrics
        if metric.label not in self.metricNamed:
            self.metricNamed[metric.label]=\
                Metric(metric.label,0)
        self.metricNamed[metric.label].add(metric.n)
        return self

    def addList(self, labelsAndValues):
        for (l,v) in labelsAndValues:
            self.add(Metric(label=l, n=v))
        return self

    def addMetrics(self, metrics):
        #type: (Metrics)->Metrics
        for metric in metrics.all:
            self.add(metric)
        return self

    def addMetricsList(self, metricsList):
        #type: (List[Metrics])->Metrics
        """
        Increment all metric with the values in the given
        metrics. Add metric entry in case of new metric.
        """
        for metrics in metricsList:
            self.addMetrics(metrics)
        return self
            # for metric in metrics.all:
            #     if metric.label in self.metricNamed:
            #         # the metric exists, add the new value
            #         self.metricNamed[metric.label]+=\
            #             metric.n
            #     else:
            #         self.metricNamed[metric.label]=metric.n

    def __len__(self):
        return len(self.metricNamed)

    def __str__(self):
        return ''.join(
            [str(m)+'\n' for m in self.all])

    def __repr__(self):
        return 'Metrics(%s)' % \
               ','.join(m.__repr__() for m in self.all)
