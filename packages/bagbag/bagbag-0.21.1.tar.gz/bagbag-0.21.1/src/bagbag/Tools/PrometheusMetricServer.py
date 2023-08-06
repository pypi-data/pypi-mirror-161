import prometheus_client as pc

class PrometheusCounter():
    def __init__(self, name:str, help:str) -> None:
        self.c = pc.Counter(name, help)
    
    def Add(self, num:int|float=1):
        self.c.inc(num)

class PrometheusCounterVec():
    def __init__(self, name:str, labels:list[str], help:str) -> None:
        self.labels = labels 
        self.c = pc.Counter(name, help, labels)
    
    def Add(self, labels:dict|list, num:int|float=1):
        """
        It adds a new label to the metric.
        
        :param labels: a list of labels, or a dict of labels
        :type labels: dict|list
        :param num: The number to increment the counter by, defaults to 1
        :type num: int|float (optional)
        """
        if type(labels) == dict:
            lb = []
            for k in self.labels:
                if k in labels:
                    lb.append(labels[k])
                else:
                    lb.append("")
        elif type(labels) == list:
            if len(self.labels) == len(labels):
                lb = labels
            else:
                lb = labels[:len(self.labels)] + [""]*(len(self.labels) - len(labels))
        self.c.labels(*lb).inc(num)

class PrometheusGauge:
    def __init__(self, name:str, help:str) -> None:
        self.g = pc.Gauge(name, help)
    
    def Set(self, num:int|float):
        self.g.set(num)

class PrometheusGaugeVec():
    def __init__(self, name:str, labels:list[str], help:str) -> None:
        self.labels = labels 
        self.g = pc.Gauge(name, help, labels)
    
    def Set(self, labels:dict|list, num:int|float):
        """
        It adds a number to the graph.
        
        :param labels: The labels of the histogram
        :type labels: dict|list
        :param num: The number of times the label is added, defaults to 1
        :type num: int|float (optional)
        """
        if type(labels) == dict:
            lb = []
            for k in self.labels:
                if k in labels:
                    lb.append(labels[k])
                else:
                    lb.append("")
        elif type(labels) == list:
            if len(self.labels) == len(labels):
                lb = labels
            else:
                lb = labels[:len(self.labels)] + [0]*(len(self.labels) - len(labels))
        self.g.labels(*lb).set(num)

# It creates a Prometheus server that listens on the specified port and IP address.
class PrometheusMetricServer():
    def __init__(self, listen:str="0.0.0.0", port:int=9105):
        pc.start_http_server(port, listen)
    
    def NewCounter(self, name:str, help:str) -> PrometheusCounter:
        return PrometheusCounter(name, help)
    
    def NewCounterWithLabel(self, name:str, labels:list[str], help:str) -> PrometheusCounterVec:
        return PrometheusCounterVec(name, labels, help)
    
    def NewGauge(self, name:str, help:str) -> PrometheusGauge:
        return PrometheusGauge(name, help)
    
    def NewGaugeWithLabel(self, name:str, labels:list[str], help:str) -> PrometheusGaugeVec:
        return PrometheusGaugeVec(name, labels, help)

if __name__ == "__main__":
    import time
    import random

    p = PrometheusMetricServer(port=8876)
    c = p.NewCounterWithLabel(
        "test_counter", 
        ["label1", "label2"], # Two labels, will display with this order
        "test counter metric"
    )
    g = p.NewGaugeWithLabel(
        "test_gauge", 
        ["label1", "label2"], # Two labels, will display with this order
        "test gauge metric"
    )
    while True:
        c.Add({"label2": "value2", "label1": "value1"}) # Order is not matter
        c.Add(["l3", "l4"])
        c.Add(["l5"]) # Will be "l5" and ""
        c.Add(["l6", "l7", "l8"]) # Will be "l7" and "l8"
        g.Set(["l6", "l7", "l8"], random.randint(0, 100))
        time.sleep(1)