class colors:
    BLACK = '\33[30m'
    LIGHTRED = '\33[31m'
    RED = '\33[91m'
    LIGHTGREEN = '\33[32m'
    GREEN = '\33[92m'
    LIGHTYELLOW = '\33[33m'
    YELLOW = '\33[93m'
    LIGHTBLUE = '\33[34m'
    BLUE = '\33[94m'
    LIGHTCYAN = '\33[36m'
    CYAN = '\33[96m'
    WHITE = '\33[97m'
    CONSOLEWHITE = '\33[57m'
    UNDERLINE = '\33[4m'
    ITALIC = '\33[3m'
    RESET = '\33[0m'
    BLACKBG = '\33[40m'
    REDBG = '\33[41m'
    GREENBG = '\33[42m'
    YELLOWBG = '\33[43m'
    BLUEBG = '\33[44m'
    VIOLETBG = '\33[45m'
    BEIGEBG = '\33[46m'
    WHITEBG = '\33[47m'
    SELECTED = '\33[7m'
    BOLD = '\33[1m'
    LIGHTVIOLET = '\33[35m'
    VIOLET = '\33[95m'
    BEIGE = '\33[36m'
    GREYBG = '\33[100m'


class Style:
    def __init__(self):
        self.colors = colors
        self.UNDERLINE = colors.UNDERLINE
        self.BOLD = colors.BOLD
        self.ITALIC = colors.ITALIC
        self.RESET = colors.RESET

    def GREEN(self, text):
        return self.colors.GREEN + text + self.RESET

    def GREENBOLD(self, text, underline=False):
        if underline is True:
            return self.colors.GREEN + self.UNDERLINE + self.BOLD + text + self.RESET
        else:
            return self.colors.GREEN + self.BOLD + text + self.RESET

    def GREENITALIC(self, text, underline=False):
        if underline is True:
            return self.colors.GREEN + self.colors.ITALIC + self.UNDERLINE + text + self.RESET
        else:
            return self.colors.GREEN + self.colors.ITALIC + text + self.RESET

    def GREENITALICBOLD(self, text, underline=False):
        if underline is True:
            return self.colors.GREEN + self.colors.ITALIC + self.BOLD + \
                   self.UNDERLINE + text + self.RESET
        else:
            return self.colors.GREEN + self.colors.ITALIC + self.BOLD + text + self.RESET

    def GREENUNDERLINE(self, text, bold=False):
        if bold is True:
            return self.colors.GREEN + self.UNDERLINE + self.BOLD + text + self.RESET
        else:
            return self.colors.GREEN + self.UNDERLINE + text + self.RESET

    def LIGHTGREEN(self, text):
        return self.colors.LIGHTGREEN + text + self.RESET

    def LIGHTGREENBOLD(self, text, underline=False):
        if underline is True:
            return self.colors.LIGHTGREEN + self.UNDERLINE + self.BOLD + text + self.RESET
        else:
            return self.colors.LIGHTGREEN + self.BOLD + text + self.RESET

    def LIGHTGREENITALIC(self, text, underline=False):
        if underline is True:
            return self.colors.LIGHTGREEN + self.colors.ITALIC + self.UNDERLINE + text + self.RESET
        else:
            return self.colors.LIGHTGREEN + self.colors.ITALIC + text + self.RESET

    def LIGHTGREENITALICBOLD(self, text, underline=False):
        if underline is True:
            return self.colors.LIGHTGREEN + self.colors.ITALIC + self.BOLD + \
                   self.UNDERLINE + text + self.RESET
        else:
            return self.colors.LIGHTGREEN + self.colors.ITALIC + self.BOLD + text + self.RESET

    def LIGHTGREENUNDERLINE(self, text, bold=False):
        if bold is True:
            return self.colors.LIGHTGREEN + self.UNDERLINE + self.BOLD + text + self.RESET
        else:
            return self.colors.LIGHTGREEN + self.UNDERLINE + text + self.RESET

    def SELECTED(self, text):
        return self.colors.SELECTED + text + self.RESET

    def SELECTEDBOLD(self, text, underline=False):
        if underline is True:
            return self.colors.SELECTED + self.BOLD + self.UNDERLINE + text + self.RESET
        else:
            return self.colors.SELECTED + self.BOLD + text + self.RESET

    def SELECTEDITALIC(self, text, underline=False):
        if underline is True:
            return self.colors.SELECTED + self.ITALIC + self.UNDERLINE + text + self.RESET
        else:
            return self.colors.SELECTED + self.ITALIC + text + self.RESET

    def SELECTEDITALICBOLD(self, text, underline=False):
        if underline is True:
            return self.colors.SELECTED + self.BOLD + self.ITALIC + self.UNDERLINE + text + self.RESET
        else:
            return self.colors.SELECTED + self.BOLD + self.ITALIC + text + self.RESET

    def SELECTEDUNDERLINE(self, text, bold=False):
        if bold is True:
            return self.colors.SELECTED + self.BOLD + self.UNDERLINE + text + self.RESET
        else:
            return self.colors.SELECTED + self.UNDERLINE + text + self.RESET

    def BEIGE(self, text):
        return self.colors.BEIGE + text + self.RESET

    def BEIGEBOLD(self, text, underline=False):
        if underline is True:
            return self.colors.BEIGE + self.UNDERLINE + self.BOLD + text + self.RESET
        else:
            return self.colors.BEIGE + self.BOLD + text + self.RESET

    def BEIGEITALIC(self, text, underline=False):
        if underline is True:
            return self.colors.BEIGE + self.colors.ITALIC + self.UNDERLINE + text + self.RESET
        else:
            return self.colors.BEIGE + self.colors.ITALIC + text + self.RESET

    def BEIGEITALICBOLD(self, text, underline=False):
        if underline is True:
            return self.colors.BEIGE + self.colors.ITALIC + self.BOLD + self.UNDERLINE + \
                   text + self.RESET
        else:
            return self.colors.BEIGE + self.colors.ITALIC + self.BOLD + text + self.RESET

    def BEIGEUNDERLINE(self, text, bold=False):
        if bold is True:
            return self.colors.BEIGE + self.UNDERLINE + self.BOLD + text + self.RESET
        else:
            return self.colors.BEIGE + self.UNDERLINE + text + self.RESET

    def BLACK(self, text):
        return self.colors.BLACK + text + self.RESET

    def BLACKBOLD(self, text, underline=False):
        if underline is True:
            return self.colors.BLACK + self.UNDERLINE + self.BOLD + text + self.RESET
        else:
            return self.colors.BLACK + self.BOLD + text + self.RESET

    def BLACKITALIC(self, text, underline=False):
        if underline is True:
            return self.colors.BLACK + self.colors.ITALIC + self.UNDERLINE + text + self.RESET
        else:
            return self.colors.BLACK + self.colors.ITALIC + text + self.RESET

    def BLACKITALICBOLD(self, text, underline=False):
        if underline is True:
            return self.colors.BLACK + self.colors.ITALIC + self.BOLD + self.UNDERLINE \
                   + text + self.RESET
        else:
            return self.colors.BLACK + self.colors.ITALIC + self.BOLD + text + self.RESET

    def BLACKUNDERLINE(self, text, bold=False):
        if bold is True:
            return self.colors.BLACK + self.UNDERLINE + self.BOLD + text + self.RESET
        else:
            return self.colors.BLACK + self.UNDERLINE + text + self.RESET

    def BLUE(self, text):
        return self.colors.BLUE + text + self.RESET

    def BLUEBOLD(self, text, underline=False):
        if underline is True:
            return self.colors.BLUE + self.UNDERLINE + self.BOLD + text + self.RESET
        else:
            return self.colors.BLUE + self.BOLD + text + self.RESET

    def BLUEITALIC(self, text, underline=False):
        if underline is True:
            return self.colors.BLUE + self.colors.ITALIC + self.UNDERLINE + text + self.RESET
        else:
            return self.colors.BLUE + self.colors.ITALIC + text + self.RESET

    def BLUEITALICBOLD(self, text, underline=False):
        if underline is True:
            return self.colors.BLUE + self.colors.ITALIC + self.BOLD + self.UNDERLINE + text \
                   + self.RESET
        else:
            return self.colors.BLUE + self.colors.ITALIC + self.BOLD + text + self.RESET

    def BLUEUNDERLINE(self, text, bold=False):
        if bold is True:
            return self.colors.BLUE + self.UNDERLINE + self.BOLD + text + self.RESET
        else:
            return self.colors.BLUE + self.UNDERLINE + text + self.RESET

    def LIGHTBLUE(self, text):
        return self.colors.LIGHTBLUE + text + self.RESET

    def LIGHTBLUEBOLD(self, text, underline=False):
        if underline is True:
            return self.colors.LIGHTBLUE + self.UNDERLINE + self.BOLD + text + self.RESET
        else:
            return self.colors.LIGHTBLUE + self.BOLD + text + self.RESET

    def LIGHTBLUEITALIC(self, text, underline=False):
        if underline is True:
            return self.colors.LIGHTBLUE + self.colors.ITALIC + self.UNDERLINE + text \
                   + self.RESET
        else:
            return self.colors.LIGHTBLUE + self.colors.ITALIC + text + self.RESET

    def LIGHTBLUEITALICBOLD(self, text, underline=False):
        if underline is True:
            return self.colors.LIGHTBLUE + self.colors.ITALIC + self.BOLD + self.UNDERLINE + text \
                   + self.RESET
        else:
            return self.colors.LIGHTBLUE + self.colors.ITALIC + self.BOLD + text + self.RESET

    def LIGHTBLUEUNDERLINE(self, text, bold=False):
        if bold is True:
            return self.colors.BEIGE + self.UNDERLINE + self.BOLD + text + self.RESET
        else:
            return self.colors.BEIGE + self.UNDERLINE + text + self.RESET

    def CYAN(self, text):
        return self.colors.CYAN + text + self.RESET

    def CYANBOLD(self, text, underline=False):
        if underline is True:
            return self.colors.CYAN + self.UNDERLINE + self.BOLD + text + self.RESET
        else:
            return self.colors.CYAN + self.BOLD + text + self.RESET

    def CYANITALIC(self, text, underline=False):
        if underline is True:
            return self.colors.CYAN + self.colors.ITALIC + self.UNDERLINE + text + self.RESET
        else:
            return self.colors.CYAN + self.colors.ITALIC + text + self.RESET

    def CYANITALICBOLD(self, text, underline=False):
        if underline is True:
            return self.colors.CYAN + self.colors.ITALIC + self.BOLD + self.UNDERLINE + text \
                   + self.RESET
        else:
            return self.colors.CYAN + self.colors.ITALIC + self.BOLD + text + self.RESET

    def CYANUNDERLINE(self, text, bold=False):
        if bold is True:
            return self.colors.CYAN + self.UNDERLINE + self.BOLD + text + self.RESET
        else:
            return self.colors.CYAN + self.UNDERLINE + text + self.RESET

    def LIGHTCYAN(self, text):
        return self.colors.LIGHTCYAN + text + self.RESET

    def LIGHTCYANBOLD(self, text, underline=False):
        if underline is True:
            return self.colors.LIGHTCYAN + self.UNDERLINE + self.BOLD + text + self.RESET
        else:
            return self.colors.LIGHTCYAN + self.BOLD + text + self.RESET

    def LIGHTCYANITALIC(self, text, underline=False):
        if underline is True:
            return self.colors.LIGHTCYAN + self.colors.ITALIC + self.UNDERLINE + text + self.RESET
        else:
            return self.colors.LIGHTCYAN + self.colors.ITALIC + text + self.RESET

    def LIGHTCYANITALICBOLD(self, text, underline=False):
        if underline is True:
            return self.colors.LIGHTCYAN + self.colors.ITALIC + self.BOLD + self.UNDERLINE \
                   + text + self.RESET
        else:
            return self.colors.LIGHTCYAN + self.colors.ITALIC + self.BOLD + text + self.RESET

    def LIGHTCYANUNDERLINE(self, text, bold=False):
        if bold is True:
            return self.colors.LIGHTCYAN + self.UNDERLINE + self.BOLD + text + self.RESET
        else:
            return self.colors.LIGHTCYAN + self.UNDERLINE + text + self.RESET

    def VIOLET(self, text):
        return self.colors.VIOLET + text + self.RESET

    def VIOLETBOLD(self, text, underline=False):
        if underline is True:
            return self.colors.VIOLET + self.UNDERLINE + self.BOLD + text + self.RESET
        else:
            return self.colors.VIOLET + self.BOLD + text + self.RESET

    def VIOLETITALIC(self, text, underline=False):
        if underline is True:
            return self.colors.VIOLET + self.colors.ITALIC + self.UNDERLINE + text + self.RESET
        else:
            return self.colors.VIOLET + self.colors.ITALIC + text + self.RESET

    def VIOLETITALICBOLD(self, text, underline=False):
        if underline is True:
            return self.colors.VIOLET + self.colors.ITALIC + self.BOLD + self.UNDERLINE + text \
                   + self.RESET
        else:
            return self.colors.VIOLET + self.colors.ITALIC + self.BOLD + text + self.RESET

    def VIOLETUNDERLINE(self, text, bold=False):
        if bold is True:
            return self.colors.VIOLET + self.UNDERLINE + self.BOLD + text + self.RESET
        else:
            return self.colors.VIOLET + self.UNDERLINE + text + self.RESET

    def LIGHTVIOLET(self, text):
        return self.colors.LIGHTVIOLET + text + self.RESET

    def LIGHTVIOLETBOLD(self, text, underline=False):
        if underline is True:
            return self.colors.LIGHTVIOLET + self.UNDERLINE + self.BOLD + text + self.RESET
        else:
            return self.colors.LIGHTVIOLET + self.BOLD + text + self.RESET

    def LIGHTVIOLETITALIC(self, text, underline=False):
        if underline is True:
            return self.colors.LIGHTVIOLET + self.colors.ITALIC + self.UNDERLINE + text + self.RESET
        else:
            return self.colors.LIGHTVIOLET + self.colors.ITALIC + text + self.RESET

    def LIGHTVIOLETITALICBOLD(self, text, underline=False):
        if underline is True:
            return self.colors.LIGHTVIOLET + self.colors.ITALIC + self.BOLD + self.UNDERLINE \
                   + text + self.RESET
        else:
            return self.colors.LIGHTVIOLET + self.colors.ITALIC + self.BOLD + text + self.RESET

    def LIGHTVIOLETUNDERLINE(self, text, bold=False):
        if bold is True:
            return self.colors.LIGHTVIOLET + self.UNDERLINE + self.BOLD + text + self.RESET
        else:
            return self.colors.LIGHTVIOLET + self.UNDERLINE + text + self.RESET

    def RED(self, text):
        return self.colors.RED + text + self.RESET

    def REDBOLD(self, text, underline=False):
        if underline is True:
            return self.colors.RED + self.UNDERLINE + self.BOLD + text + self.RESET
        else:
            return self.colors.RED + self.BOLD + text + self.RESET

    def REDITALIC(self, text, underline=False):
        if underline is True:
            return self.colors.RED + self.ITALIC + self.UNDERLINE + text + self.RESET
        else:
            return self.colors.RED + self.ITALIC + text + self.RESET

    def REDITALICBOLD(self, text, underline=False):
        if underline is True:
            return self.colors.RED + self.ITALIC + self.BOLD + self.UNDERLINE + text + self.RESET
        else:
            return self.colors.RED + self.ITALIC + self.BOLD + text + self.RESET

    def REDUNDERLINE(self, text, bold=False):
        if bold is True:
            return self.colors.RED + self.UNDERLINE + self.BOLD + text + self.RESET
        else:
            return self.colors.RED + self.UNDERLINE + text + self.RESET

    def LIGHTRED(self, text):
        return self.colors.LIGHTRED + text + self.RESET

    def LIGHTREDBOLD(self, text, underline=False):
        if underline is True:
            return self.colors.LIGHTRED + self.UNDERLINE + self.BOLD + text + self.RESET
        else:
            return self.colors.LIGHTRED + self.BOLD + text + self.RESET

    def LIGHTREDITALIC(self, text, underline=False):
        if underline is True:
            return self.colors.LIGHTRED + self.ITALIC + self.UNDERLINE + text + self.RESET
        else:
            return self.colors.LIGHTRED + self.ITALIC + text + self.RESET

    def LIGHTREDITALICBOLD(self, text, underline=False):
        if underline is True:
            return self.colors.LIGHTRED + self.ITALIC + self.BOLD + self.UNDERLINE + text + self.RESET
        else:
            return self.colors.LIGHTRED + self.ITALIC + self.BOLD + text + self.RESET

    def LIGHTREDUNDERLINE(self, text, bold=False):
        if bold is True:
            return self.colors.LIGHTRED + self.UNDERLINE + self.BOLD + text + self.RESET
        else:
            return self.colors.LIGHTRED + self.UNDERLINE + text + self.RESET

    def WHITE(self, text):
        return self.colors.WHITE + text + self.RESET

    def WHITEBOLD(self, text, underline=False):
        if underline is True:
            return self.colors.WHITE + self.UNDERLINE + self.BOLD + text + self.RESET
        else:
            return self.colors.WHITE + self.BOLD + text + self.RESET

    def WHITEITALIC(self, text, underline=False):
        if underline is True:
            return self.colors.WHITE + self.ITALIC + self.UNDERLINE + text + self.RESET
        else:
            return self.colors.WHITE + self.ITALIC + text + self.RESET

    def WHITEITALICBOLD(self, text, underline=False):
        if underline is True:
            return self.colors.WHITE + self.ITALIC + self.BOLD + self.UNDERLINE + text + self.RESET
        else:
            return self.colors.WHITE + self.ITALIC + self.BOLD + text + self.RESET

    def WHITEUNDERLINE(self, text, bold=False):
        if bold is True:
            return self.colors.WHITE + self.UNDERLINE + self.BOLD + text + self.RESET
        else:
            return self.colors.WHITE + self.UNDERLINE + text + self.RESET

    def CONSOLEWHITE(self, text):
        return self.colors.CONSOLEWHITE + text + self.RESET

    def YELLOW(self, text):
        return self.colors.YELLOW + text + self.RESET

    def YELLOWBOLD(self, text, underline=False):
        if underline is True:
            return self.colors.YELLOW + self.UNDERLINE + self.BOLD + text + self.RESET
        else:
            return self.colors.YELLOW + self.BOLD + text + self.RESET

    def YELLOWITALIC(self, text, underline=False):
        if underline is True:
            return self.colors.YELLOW + self.ITALIC + self.UNDERLINE + text + self.RESET
        else:
            return self.colors.YELLOW + self.ITALIC + text + self.RESET

    def YELLOWITALICBOLD(self, text, underline=False):
        if underline is True:
            return self.colors.YELLOW + self.ITALIC + self.BOLD + self.UNDERLINE + text + self.RESET
        else:
            return self.colors.YELLOW + self.ITALIC + self.BOLD + text + self.RESET

    def YELLOWUNDERLINE(self, text, bold=False):
        if bold is True:
            return self.colors.YELLOW + self.UNDERLINE + self.BOLD + text + self.RESET
        else:
            return self.colors.YELLOW + self.UNDERLINE + text + self.RESET

    def LIGHTYELLOW(self, text):
        return self.colors.LIGHTYELLOW + text + self.RESET

    def LIGHTYELLOWBOLD(self, text, underline=False):
        if underline is True:
            return self.colors.LIGHTYELLOW + self.UNDERLINE + self.BOLD + text + self.RESET
        else:
            return self.colors.LIGHTYELLOW + self.BOLD + text + self.RESET

    def LIGHTYELLOWITALIC(self, text, underline=False):
        if underline is True:
            return self.colors.LIGHTYELLOW + self.ITALIC + self.UNDERLINE + text + self.RESET
        else:
            return self.colors.LIGHTYELLOW + self.ITALIC + text + self.RESET

    def LIGHTYELLOWITALICBOLD(self, text, underline=False):
        if underline is True:
            return self.colors.LIGHTYELLOW + self.ITALIC + self.BOLD + self.UNDERLINE + text + self.RESET
        else:
            return self.colors.LIGHTYELLOW + self.ITALIC + self.BOLD + text + self.RESET

    def LIGHTYELLOWUNDERLINE(self, text, bold=False):
        if bold is True:
            return self.colors.LIGHTYELLOW + self.UNDERLINE + self.BOLD + text + self.RESET
        else:
            return self.colors.LIGHTYELLOW + self.UNDERLINE + text + self.RESET

    def BGBLACK(self, text):
        return self.colors.BLACKBG + text + self.RESET

    def BGBLACKBOLD(self, text):
        return self.colors.BLACKBG + self.BOLD + text + self.RESET

    def BGBLACKITALIC(self, text):
        return self.colors.BLACKBG + self.ITALIC + text + self.RESET

    def BGBLACKITALICBOLD(self, text):
        return self.colors.BLACKBG + self.BOLD + self.ITALIC + text + self.RESET

    def BGBLACKUNDERLINE(self, text):
        return self.colors.BLACKBG + self.UNDERLINE + text + self.RESET

    def BGBLUE(self, text):
        return self.colors.BLUEBG + text + self.RESET

    def BGBLUEBOLD(self, text):
        return self.colors.BLUEBG + self.BOLD + text + self.RESET

    def BGBLUEITALIC(self, text):
        return self.colors.BLUEBG + self.ITALIC + text + self.RESET

    def BGBLUEITALICBOLD(self, text):
        return self.colors.BLUEBG + self.BOLD + self.ITALIC + text + self.RESET

    def BGBLUEUNDERLINE(self, text):
        return self.colors.BLUEBG + self.UNDERLINE + text + self.RESET

    def BGRED(self, text):
        return self.colors.REDBG + text + self.RESET

    def BGREDBOLD(self, text):
        return self.colors.REDBG + self.BOLD + text + self.RESET

    def BGREDITALIC(self, text):
        return self.colors.REDBG + self.ITALIC + text + self.RESET

    def BGREDITALICBOLD(self, text):
        return self.colors.REDBG + self.BOLD + self.ITALIC + text + self.RESET

    def BGREDUNDERLINE(self, text):
        return self.colors.REDBG + self.UNDERLINE + text + self.RESET

    def BGGREEN(self, text):
        return self.colors.GREENBG + text + self.RESET

    def BGGREENBOLD(self, text):
        return self.colors.GREENBG + self.BOLD + text + self.RESET

    def BGGREENITALIC(self, text):
        return self.colors.GREENBG + self.ITALIC + text + self.RESET

    def BGGREENITALICBOLD(self, text):
        return self.colors.GREENBG + self.BOLD + self.ITALIC + text + self.RESET

    def BGGREENUNDERLINE(self, text):
        return self.colors.GREENBG + self.UNDERLINE + text + self.RESET

    def BGGREY(self, text):
        return self.colors.GREYBG + text + self.RESET

    def BGGREYBOLD(self, text):
        return self.colors.GREYBG + self.BOLD + text + self.RESET

    def BGGREYITALIC(self, text):
        return self.colors.GREYBG + self.ITALIC + text + self.RESET

    def BGGREYITALICBOLD(self, text):
        return self.colors.GREYBG + self.BOLD + self.ITALIC + text + self.RESET

    def BGGREYUNDERLINE(self, text):
        return self.colors.GREYBG + self.UNDERLINE + text + self.RESET

    def BGVIOLET(self, text):
        return self.colors.VIOLETBG + text + self.RESET

    def BGVIOLETBOLD(self, text):
        return self.colors.VIOLETBG + self.BOLD + text + self.RESET

    def BGVIOLETITALIC(self, text):
        return self.colors.VIOLETBG + self.ITALIC + text + self.RESET

    def BGVIOLETITALICBOLD(self, text):
        return self.colors.VIOLETBG + self.BOLD + self.ITALIC + text + self.RESET

    def BGVIOLETEUNDERLINE(self, text):
        return self.colors.BLUEBG + self.UNDERLINE + text + self.RESET

    def BGYELLOW(self, text):
        return self.colors.YELLOWBG + text + self.RESET

    def BGYELLOWBOLD(self, text):
        return self.colors.YELLOWBG + self.BOLD + text + self.RESET

    def BGYELLOWITALIC(self, text):
        return self.colors.YELLOWBG + self.ITALIC + text + self.RESET

    def BGYELLOWITALICBOLD(self, text):
        return self.colors.YELLOWBG + self.BOLD + self.ITALIC + text + self.RESET

    def BGYELLOWUNDERLINE(self, text):
        return self.colors.YELLOWBG + self.UNDERLINE + text + self.RESET
