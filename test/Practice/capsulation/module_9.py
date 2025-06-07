import collections

class DataAnalyzer:
    def count_frequencies(self, data_list):
        return collections.Counter(data_list)

    def find_most_common(self, data_list, n=1):
        return collections.Counter(data_list).most_common(n)
