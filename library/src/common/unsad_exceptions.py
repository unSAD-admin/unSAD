# Created by Xinyu Zhu on 10/22/2019, 4:11 PM


class UnSADException(Exception):
    """
    For defining exceptions used in the library
    Feel free to add your exception here
    """

    def __init__(self, *args, **kwargs):
        super(UnSADException, self).__init__(*args, **kwargs)
        # TODO consider adding error code

    @staticmethod
    def data_type_exception():
        return UnSADException("Invalid Data Type")

    @staticmethod
    def input_number_exception():
        return UnSADException("Wrong parameter number")

    @staticmethod
    def not_proper_initialize_exception():
        return UnSADException("Detector is not initialized properly")

    @staticmethod
    def data_format_exception():
        return UnSADException("Wrong Data format")
