class Sample():
    def __init__(self, name, title, hists=False):
        self.name = name
        self.title = title
        self.hists = hists

    def __add__(self, other):
        name  = self.name  + '_AND_' + other.name
        title = self.title +  ' + '  + other.title
        return Sample(name, title, hists)

