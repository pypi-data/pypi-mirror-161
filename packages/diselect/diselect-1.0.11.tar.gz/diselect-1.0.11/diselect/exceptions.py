class QueryBase(Exception):
    '''Query Base Exception'''


class InvalidQueryKey(QueryBase):

    def __str__(self):
        return 'Invalid Query Keys {}'.fomrat(self.args)


class InvalidQueryValues(QueryBase):
    '''Invalid Query Key'''
    
    def __str__(self):
        return 'Invalid Query Values {}'.format(self.args)



class QueryMultipleMatched(QueryBase):

    def __str__(self):
        tmp = '''\n{} has multiple matching with paths in {}... Requires more detail query of path'''
        return tmp.format(*self.args)