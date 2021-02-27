#%%
#a bidirectional dictionary. call dictname.inverse to make the values the keys
class bidict(dict):
    def __init__(self, *args, **kwargs):
        super(bidict, self).__init__(*args, **kwargs)
        self.inverse = {}
        for key, value in self.items():
            if hasattr(value, '__iter__'):
                for v in value:
                    self.inverse.setdefault(v,[]).append(key)        
            else: self.inverse.setdefault(value,[]).append(key) 

    def __setitem__(self, key, value):
        if key in self:
            self.inverse[self[key]].remove(key) 
        super(bidict, self).__setitem__(key, value)
        if hasattr(value, '__iter__'):
            for v in value:
                self.inverse.setdefault(v,[]).append(key)  
        self.inverse.setdefault(value,[]).append(key)        

    def __delitem__(self, key):
        self.inverse.setdefault(self[key],[]).remove(key)
        if self[key] in self.inverse and not self.inverse[self[key]]: 
            del self.inverse[self[key]]
        super(bidict, self).__delitem__(key)

#will cut val (a string) to length or pad it with padchars to output a fixed length string of length length
#cutfrom: 'right' or 'left'. will remove characters from the side stated here if string is longer than length
#padfrom: 'right' or 'left'. will pad string with padchar from the side stated here to output a string of defined length length
def cutOrPad(val, length, cutfrom='right', padfrom='right', padchar=' '):
    if len(val)>length: 
        if cutfrom=='right': return val[:length]
        else: return val[-length:]
    elif len(val)<length:
        if padfrom=='left': return val.rjust(length, padchar)
        else: return val.ljust(length, padchar)
    return val
