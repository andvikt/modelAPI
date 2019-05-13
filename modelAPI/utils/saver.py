import dill as pickle


class _SelfSaving(object):
    """
    Self saving object, provide save_list in order for special save (for example if some attribute will be ovverridden)
    """
    def __init__(self, save_list: set = set()):
        """

        :param save_list: name of object attributes, that will be serialised individually, need in case of saving
            hackable methods
        """
        assert isinstance(save_list, set)
        self._save_list = save_list
        self.ser = None

    def save(self, addr: str):
        """
        Save object to file
        :param addr: addr of file
        :return:
        """
        def dump():
            for name in self._save_list:
                value = self.__getattribute__(name)
                yield name, pickle.dumps(value)

        if self._save_list:
            self.ser = dict(dump())

        with open(addr, 'wb') as f:
            pickle.dump(self, f)

        self.ser = None

    @classmethod
    def load(cls, addr: str):
        """
        Load object from file
        :param addr: addr of file to open for loading
        :return: cls
        """
        def _open()->cls:
            """
            Wrap open so that ide knows what is loading
            :return: cls
            """
            with open(addr, 'rb') as f:
                obj = pickle.load(f)
            return obj

        obj = _open()

        def unpack():
            for name, value in obj.ser.items():
                yield name, pickle.loads(value)

        if obj._save_list:
            for name, value in unpack():
                obj.__setattr__(name, value)

        obj.ser = None
        return obj
