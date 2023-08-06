from colorama import Fore

class NameSpace(Exception):
    """called as a result of an error in the CopperUI namespace set"""
    error = Fore.RED + "Bad namespace call!" + Fore.RESET
    def __init__(self, message = error):
        super().__init__(message)

    class BackgroundColorError(Exception):
        """called as a result of incorrect usage of the background color namespace"""
        error = Fore.RED + "You used a text color when calling a background color! try back_ before your color name!" + Fore.RESET
        def __init__(self, message = error):
            super().__init__(message)

    class ForegroundColorError(Exception):
        """this is called when a user calls a background color in the case of a foreground usage"""
        error = Fore.RED + "You used a background color when calling a text color! don't use back_ before your color name!" + Fore.RESET
        def __init__(self, message = error):
            super().__init__(message)

class ArgumentError(Exception):
    error = Fore.RED + "Bad argument!" + Fore.RESET
    def __init__(self, message = error):
        super().__init__(message)
