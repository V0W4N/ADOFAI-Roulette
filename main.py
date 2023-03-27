import json, threading, random, webbrowser, os, sys, requests
import pygame as pg


from math import floor
from tkinter import messagebox

dims = (480, 560)
apiLink = "https://be.t21c.kro.kr/levels"
folder = os.getenv('APPDATA').replace("\\", "/") + "/"
saveFilePath = folder + "save.json"
chartFilePath = folder + "charts.json"
cycleFilePath = folder + "cycle.json"

if hasattr(sys, "_MEIPASS"):
    os.chdir(sys._MEIPASS)

fontSize = 19.7
fps = 60

textPadding = 7
textBoxPadding = 20
bgColor = [0, 0, 0]

maxPossibleDiff = 21.35
minPossibleDiff = 20

maxLinkLength = 26
rounding = 10
opacity = 50

hugeFontSize = int(fontSize * 1.6)
bigFontSize = int(fontSize * 1.4)
smallFontSize = int(fontSize / 1.2)
fontSize = int(fontSize)
fontType = "NotoSansKR-Medium.otf"
theBG = "bg.png"
icon = "icon.png"

pg.init()
screen = pg.display.set_mode(dims, vsync=True)
titleFont = pg.font.Font(fontType, 100)
subtitleFont = pg.font.Font(fontType, 40)
diffFont = pg.font.Font(fontType, int(fontSize / 1.3))
hugeFont = pg.font.Font(fontType, hugeFontSize)
bigFont = pg.font.Font(fontType, bigFontSize)
font = pg.font.Font(fontType, fontSize)
smallFont = pg.font.Font(fontType, smallFontSize)
CENTER = dims[0] / 2, dims[1] / 2
pg.display.set_caption("ADOFAI Roulette")
pg.display.set_icon(pg.image.load(icon))
diffColors = {
    20.0: (67, 18, 16),
    20.05: (65, 24, 31),
    20.1: (62, 29, 44),
    20.15: (58, 33, 58),
    20.2: (54, 38, 77),
    20.25: (50, 39, 90),
    20.3: (47, 40, 101),
    20.35: (44, 41, 111),
    20.4: (40, 41, 124),
    20.45: (36, 40, 134),
    20.5: (33, 40, 142),
    20.55: (32, 39, 149),
    20.6: (30, 38, 157),
    20.65: (29, 36, 161),
    20.7: (31, 35, 162),
    20.75: (35, 31, 156),
    20.8: (40, 19, 143),
    20.85: (43, 14, 129),
    20.9: (44, 10, 117),
    20.95: (46, 8, 108),
    21.0: (47, 5, 101),
    21.05: (48, 4, 90),
    21.1: (50, 3, 85),
    21.15: (57, 15, 88),
    21.2: (69, 31, 101),
    21.25: (83, 51, 122),
    21.3: (85, 55, 125),
    21.35: (40, 0, 0)}


def center(pos, size):
    return pos[0] - size[0] / 2, pos[1] - size[1] / 2


class ForumScraper:
    def __init__(self, link):
        self.chartList = None
        self.link = link
        self.dotAmount = 0
        self.prevTick = -99999
        self.diffList = {}
        self.tickout = 12 * fps
        self.successText = "Loaded!"
        self.badAccess = False

    def getCharts(self, util):

        def getThread():
            savedCharts = False
            if os.path.isfile(chartFilePath):
                with open(chartFilePath, "r") as file:
                    if file.read():
                        file.seek(0)
                        self.chartList = json.load(file)
                        util.addCharts(self.chartList)
                        savedCharts = True
                        self.prevTick = pg.time.get_ticks()
                        self.successText = "Loaded charts from cache."

            try:
                request = requests.get(self.link)
            except Exception:
                self.successText = "Failed to get from API!"
                request = None
                if not savedCharts:
                    raise Exception

            if request:
                self.successText = "Loaded charts from API."
                self.chartList = []
                self.chartList = json.loads(request.content.decode())["results"]
                self.chartValidator()
                self.prevTick = pg.time.get_ticks()
                with open(chartFilePath, "w+") as file:
                    json.dump(self.chartList, file, indent=4)
            elif not savedCharts:
                raise Exception
            util.addCharts(self.chartList)

        def hook(args):
            messagebox.showerror("No charts found!", "You don't have any charts stored in cache "
                                                     "and the api failed to respond, aborting program.")
            self.badAccess = True

        threading.excepthook = hook
        t = threading.Thread(target=getThread)

        t.start()

    def chartValidator(self):
        validCharts = []
        for chart in self.chartList:
            if chart['dlLink'] and chart not in validCharts:
                validCharts.append(chart)
        self.chartList = validCharts

    def displayLoading(self):
        if self.chartList is not None and pg.time.get_ticks() - self.tickout < self.prevTick:
            loadText = font.render(self.successText, True, "white")
            loadText.set_alpha(int(255 * (pow(1 - (pg.time.get_ticks() - self.prevTick) / self.tickout, 1 / 3))))
            screen.blit(loadText, center(CENTER, loadText.get_rect().size))

        if self.chartList is None:
            if pg.time.get_ticks() - 500 > self.prevTick:
                if self.dotAmount == 3:
                    self.dotAmount = 0
                else:
                    self.dotAmount += 1
                self.prevTick = pg.time.get_ticks()
            dots = self.dotAmount * "."
            loadText = font.render(f"Loading charts from The 21 Forum{dots}", True, "white")
            screen.blit(loadText, center(CENTER, loadText.get_rect().size))


class Button:
    def __init__(self, pos, size, label, centerPos=False, fontSize="normal", color=(255,255,255), lineThickness = 3):
        match fontSize:
            case "huge":
                self.labelRect = hugeFont.render(label, True, "white")
            case "big":
                self.labelRect = bigFont.render(label, True, "white")
            case "normal":
                self.labelRect = font.render(label, True, "white")
            case "small":
                self.labelRect = smallFont.render(label, True, "white")
            case _:
                self.labelRect = font.render(label, True, "white")
        self.color = color
        self.lineThickness = lineThickness
        self.rect = pg.Rect(pos, size)
        if centerPos:
            self.rect.center = pos
        self.hover = 0
        self.clicked = False

    def process(self):
        if self.rect.collidepoint(pg.mouse.get_pos()):
            self.hover = 1
            if pg.mouse.get_pressed()[0]:
                self.clicked = True
            else:
                self.clicked = False
        else:
            self.hover = 0
            self.clicked = False

    def render(self):
        clr = int(self.hover * self.color[0]), int(self.hover * self.color[1]), int(self.hover * self.color[2])
        surf = pg.Surface(self.rect.size)
        pg.draw.rect(surf, clr, pg.Rect((0,0), self.rect.size), border_radius=rounding)
        surf.set_alpha(opacity)
        screen.blit(surf, self.rect.topleft)
        screen.blit(self.labelRect, center(self.rect.center, self.labelRect.get_rect().size))
        if self.hover:
            pg.draw.rect(screen, self.color, self.rect, self.lineThickness, border_radius=int(rounding / 2))
        else:
            pg.draw.rect(screen, "white", self.rect, self.lineThickness, border_radius=int(rounding / 2))


class TextBox:
    def __init__(self, pos, size, label, centerPos=False, lineThickness=3, digitOnlyMode=False, allowedChars="", fontSize="normal", color = (255,255,255)):
        match fontSize:
            case "huge":
                self.font = hugeFont
            case "big":
                self.font = bigFont
            case "normal":
                self.font = font
            case "small":
                self.font = smallFont
            case _:
                self.font = font
        self.lineThickness = lineThickness
        self.color = color
        self.text = ""
        self.verifiedValue = 0
        self.labelRect = smallFont.render(label, True, "white")
        self.digitOnly = digitOnlyMode
        self.textRect = font.render(self.text, True, "white")
        self.allowedChars = allowedChars
        self.rect = pg.Rect(pos, size)
        if centerPos:
            self.rect.center = pos
        self.active = 0
        self.holdDown = 0
        self.timer = 0
        self.countdown = 0

    def process(self, events):
        if self.holdDown and self.timer + 500 < pg.time.get_ticks() and self.active:
            if self.countdown <= 0:
                self.countdown = fps / 90
                self.text = self.text[:-1]
            else:
                self.countdown -= 1
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(pg.mouse.get_pos()):
                    self.active = 1
                else:
                    self.active = 0

            if self.active:
                if event.type == pg.KEYUP:
                    if event.key == pg.K_BACKSPACE:
                        self.holdDown = 0

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_BACKSPACE:
                        self.text = self.text[:-1]
                        self.holdDown = 1

                        self.timer = pg.time.get_ticks()
                    else:
                        if (not self.digitOnly
                            or (event.unicode.isdigit() and self.digitOnly)
                            or event.unicode in self.allowedChars) \
                                and event.unicode.isprintable():
                            self.text += event.unicode
        self.textRect = self.font.render(self.text, True, "white")

    def render(self):
        clr = int(self.active * self.color[0]), int(self.active * self.color[1]), int(self.active * self.color[2])
        surf = pg.Surface(self.rect.size)
        pg.draw.rect(surf, clr, pg.Rect((0,0), self.rect.size), border_radius=rounding)
        surf.set_alpha(int(opacity/2))
        screen.blit(surf, self.rect.topleft)

        textpos = self.rect.left + textPadding, \
                  self.rect.centery - self.textRect.get_rect().h / 2
        labelpos = self.rect.centerx - self.labelRect.get_rect().w / 2, \
                   self.rect.top - self.labelRect.get_rect().h - textPadding

        screen.blit(self.textRect, textpos)
        screen.blit(self.labelRect, labelpos)
        pg.draw.rect(screen, self.color, self.rect, self.lineThickness, border_radius=rounding)


class Link:
    def __init__(self, text, link, font=font):
        self.link = link
        self.text = self.shorten(text)
        self.font = font
        self.textRect = self.font.render(self.text, True, "white")
        self.hover = False
        self.clicked = False

    def render(self, pos):
        screen.blit(self.textRect, pos)

    def process(self, pos):
        colliding = self.textRect.get_rect().collidepoint(
            (pg.mouse.get_pos()[0] - pos[0], pg.mouse.get_pos()[1] - pos[1]))
        if not self.hover and colliding:
            self.hover = True
            self.font.set_underline(True)
            self.textRect = self.font.render(self.text, True, (50, 50, 255))

        elif self.hover and not colliding:
            self.hover = False
            self.font.set_underline(False)
            self.textRect = self.font.render(self.text, True, 'white')

        if self.hover and colliding and not self.clicked and pg.mouse.get_pressed()[0]:
            self.clicked = True
            webbrowser.open(self.link)
        elif not pg.mouse.get_pressed()[0]:
            self.clicked = False

    def shorten(self, text):
        if len(text) > maxLinkLength:
            return text[:maxLinkLength] + "..."
        else:
            return text


class Utilities:
    def __init__(self):
        self.minDiff = 0
        self.maxDiff = 0
        self.charts = None
        self.IDlist = []
        self.ChartList = []
        self.chartCycle = []

    def findSuitableCharts(self):
        if self.charts:
            self.ChartList = []
            for chart in self.charts:
                if self.minDiff <= chart["diff"] <= self.maxDiff:
                    self.ChartList.append(chart)
        if not self.ChartList:
            self.ChartList = [{'id': 1,
                               'song': 'a silly cat video',
                               'artist': 'No suitable charts found!',
                               'creator': 'You probably have entered difficulty that does not have any charts set with',
                               'diff': 21,
                               'dlLink': 'https://www.youtube.com/watch?v=L3tsYC5OYhQ'}]

    def setDiffs(self, minDiff, maxDiff):
        self.minDiff, self.maxDiff = minDiff, maxDiff
        if self.minDiff > self.maxDiff:
            self.minDiff, self.maxDiff = self.maxDiff, self.minDiff
        if self.charts:
            self.findSuitableCharts()

    def addCharts(self, chartDict):
        self.charts = chartDict
        if self.minDiff and self.maxDiff:
            self.findSuitableCharts()

    def pickChart(self):
        if os.path.exists(cycleFilePath):
            with open(cycleFilePath, "r") as file:
                if file.read():
                    file.seek(0)
                    self.chartCycle = json.load(file)
        if not self.chartCycle:
            self.chartCycle = self.ChartList.copy()
        choice = self.chartCycle.pop(random.randint(0, len(self.chartCycle)-1))
        with open(cycleFilePath, "w+") as file:
            json.dump(self.chartCycle, file)
        return choice



    def validateInput(self, inp):
        badInput = False
        if inp == "":
            badInput = True
        split = inp.split(".")
        if "" in split:
            badInput = True
        elif len(split) > 2:
            badInput = True
        elif len(split) == 1:
            if split[0][-1] != "+" and split[0].count("+") >= 1:
                badInput = True
            elif not minPossibleDiff <= self.parseInput(inp) <= maxPossibleDiff:
                badInput = True
        elif inp.count("+") == 1 and inp[-1] != "+":
            badInput = True
        elif split[1].count("+") > 1 or split[0].count("+") > 0:
            badInput = True

        elif not minPossibleDiff <= self.parseInput(inp) <= maxPossibleDiff:
            badInput = True
        return badInput

    def parseInput(self, text):
        diffNum = 0
        if text[-1] == "+":
            diffNum += 0.05
            text = text[:-1]
        diffNum += round(float(text), 1)
        return round(diffNum, 2)

    def backParse(self, num: float):
        whole = int(floor(num))
        fract = int(round(num * 100 - whole * 100))
        text = ""
        if fract % 10 == 5:
            text = "+"
            fract -= 5
        if fract > 0:
            text = str(round(whole + fract / 100, 2)) + text
        else:
            text = str(whole) + text
        return text


class UI:
    def __init__(self):
        self.currScreen = "start"
        self.badInpCountdown = [0, 500]
        self.bgColor = bgColor
        self.flashBrightness = 40
        self.flashCountdown = [-500, 500]
        self.reset()

        self.prevScreenHold = False
        self.badInpText = ""
        self.util = Utilities()
        self.winScreen = self.setupWinscreen()
        self.getProgress()

    def reset(self):
        self.startScreen = self.setupStartScreen()
        self.mainScreen = self.setupMainScreen()
        self.currScreen = "start"
        self.currProgress = 0
        self.skippedCharts = 0
        self.chart = {}
        self.mainTextRects = []
        self.winTextRects = []
        self.completedCharts = 0

    def getProgress(self):
        if not os.path.isfile(saveFilePath):
            self.saveProgress()
            return
        with open(saveFilePath, "r") as file:
            if file.read():
                file.seek(0)
                data = json.load(file)
                if data:
                    if data["chart"]:
                        self.currScreen = data["currScreen"]
                        self.currProgress = data["currProgress"]
                        self.skippedCharts = data["skippedCharts"]
                        self.util.setDiffs(data["diff"][0], data["diff"][1])
                        self.chart = data["chart"]
                        self.completedCharts = data["completedCharts"]
                        self.updateInfoList()
                        self.updateWinList()

    def saveProgress(self):
        saveDict = {"currScreen": self.currScreen,
                    "currProgress": self.currProgress,
                    "skippedCharts": self.skippedCharts,
                    "completedCharts": self.completedCharts,
                    "diff": [self.util.minDiff, self.util.maxDiff],
                    "chart": self.chart}
        with open(saveFilePath, "w+") as file:
            json.dump(saveDict, file)

    def clearProgress(self):
        with open(saveFilePath, "w+") as file:
            file.write("")
        with open(cycleFilePath, "w+") as file:
            file.write("")

    def render(self):
        if self.currScreen == "start":
            self.renderStart()
        elif self.currScreen == "main":
            self.renderMain()
        elif self.currScreen == "win":
            self.renderWin()
        self.badInputDisplay()

    def process(self, events):
        if not self.prevScreenHold:
            if self.currScreen == "start":
                self.processStart(events)
            elif self.currScreen == "main":
                self.processMain(events)
            elif self.currScreen == "win":
                self.processWin()
        elif not pg.mouse.get_pressed()[0]:
            self.prevScreenHold = False

    def setupStartScreen(self):
        TBOffset = dims[0] / 4, -100
        infoList = [[titleFont.render("ADOFAI", True, "white"),
                     titleFont.render("ADO", True, "white"),
                     titleFont.render("F", True, (255,100, 50)),
                     titleFont.render("A", True, "white"),
                     titleFont.render("I", True, (50,50, 255)),
                     subtitleFont.render("Roulette", True, "white")],
                    font.render("Based on The 21 Forum API", True, "white"),
                    smallFont.render("Program by V0W4N", True, "white"),
                    smallFont.render("Idea by WillTRM", True, "white")
                    ]

        minTextbox = TextBox(pos=(dims[0] / 2 - TBOffset[0], dims[1] / 2 - TBOffset[1] - textPadding),
                             size=(dims[0] / 2 - textBoxPadding * 2, fontSize + textPadding * 2),
                             label="Min Difficulty",
                             centerPos=True,
                             digitOnlyMode=True,
                             allowedChars="+.",
                             lineThickness=2)

        maxTextbox = TextBox(pos=(dims[0] / 2 + TBOffset[0], dims[1] / 2 - TBOffset[1] - textPadding),
                             size=(dims[0] / 2 - textBoxPadding * 2, fontSize + textPadding * 2),
                             label="Max Difficulty",
                             centerPos=True,
                             digitOnlyMode=True,
                             allowedChars="+.",
                             lineThickness=2)

        confirmButton = Button(pos=(dims[0] / 2, dims[1] - 100),
                               size=(300, 100),
                               label="Begin challenge!",
                               centerPos=True,
                               fontSize="huge",
                               color=(100,255,100),
                               lineThickness=2)

        return {"confirmButton": confirmButton,
                "maxTextbox": maxTextbox,
                "minTextbox": minTextbox,
                "infoList": infoList}

    def setupMainScreen(self):
        submitTextBox = TextBox(pos=(dims[0] / 2, dims[1] - 190),
                                size=(300, 60),
                                label="Input percentage according to goal",
                                centerPos=True,
                                digitOnlyMode=True,
                                fontSize="big",
                                lineThickness=2)

        submitButton = Button(pos=(dims[0] / 2, dims[1] - 105),
                              size=(200, 75),
                              label="Submit!",
                              centerPos=True,
                              fontSize="big",
                              color=(50,255,50),
                              lineThickness=2)

        skipButton = Button(pos=(dims[0] / 2 + 160, dims[1] - 40),
                            size=(140, 30),
                            label="Skip chart (-1%)",
                            centerPos=True,
                            fontSize="small",
                            color=(255,50,50),
                            lineThickness=2)

        giveUpButton = Button(pos=(dims[0] / 2, dims[1] - 40),
                              size=(150, 40),
                              label="Give up",
                              centerPos=True,
                              fontSize="medium",
                              color=(255,0,0),
                              lineThickness=2)

        return {"submitTextBox": submitTextBox,
                "submitButton": submitButton,
                "skipButton": skipButton,
                "giveUpButton": giveUpButton}

    def setupWinscreen(self):
        againButton = Button(pos=(dims[0] / 2, dims[1] / 2 + 150),
                             size=(200, 75),
                             label="Try again?",
                             centerPos=True,
                             fontSize="big")
        return {"againButton": againButton}

    def renderStart(self):
        for item in self.startScreen.keys():
            if type(self.startScreen[item]) is not list:
                self.startScreen[item].render()
        pos = list(center((dims[0]/2, dims[1]/2-150), self.startScreen["infoList"][0][0].get_rect().size))
        for text in self.startScreen["infoList"][0][1:-1]:
            screen.blit(text, pos)
            pos[0] += text.get_rect().w
        pos = list(center((dims[0]/2, dims[1]/2-80), self.startScreen["infoList"][0][-1].get_rect().size))
        screen.blit(self.startScreen["infoList"][0][-1], pos)
        pos = list(center((dims[0]/2, dims[1]/2-45), self.startScreen["infoList"][1].get_rect().size))
        screen.blit(self.startScreen["infoList"][1], pos)
        pos = list(center((dims[0]/2, dims[1]-15), self.startScreen["infoList"][2].get_rect().size))
        screen.blit(self.startScreen["infoList"][2], pos)
        pos = list(center((dims[0]/2, dims[1]-36), self.startScreen["infoList"][-1].get_rect().size))
        screen.blit(self.startScreen["infoList"][-1], pos)



    def renderMain(self):
        if pg.time.get_ticks() - self.flashCountdown[0] < self.flashCountdown[1]:
            self.bgColor = [bgColor[0],
                            (int(self.flashBrightness * (pow(1 - (pg.time.get_ticks() - self.flashCountdown[0])
                                                             /
                                                             self.flashCountdown[1], 1 / 2)))), bgColor[2]]
        elif self.bgColor[1] != 0:
            self.bgColor[1] = 0

        for itemTag in self.mainScreen.keys():
            item = self.mainScreen[itemTag]
            if type(item) is TextBox or type(item) is Button:
                item.render()
        pos = [40, 50]
        for toRender in self.mainTextRects[:-2]:
            if type(toRender) is str:
                match toRender:
                    case "skip big":
                        pos[1] += bigFontSize
                    case "skip":
                        pos[1] += fontSize
                    case "skip small":
                        pos[1] += fontSize / 2
                    case _:
                        pos[1] += fontSize
                continue
            if type(toRender) is Link:
                toRender.process(pos)
                toRender.render(pos)
                pos[1] += toRender.textRect.get_rect().h
                continue
            if self.mainTextRects.index(toRender) == len(self.mainTextRects) - 5:
                diffPos = pos[0] + toRender.get_rect().w + 20, pos[1] + toRender.get_rect().h / 2 + 4
                pg.draw.circle(screen, diffColors[self.chart["diff"]], diffPos, fontSize * 0.9)
                screen.blit(self.mainTextRects[-2],
                            center((diffPos[0] + 1, diffPos[1] - 1), self.mainTextRects[-2].get_rect().size))
            screen.blit(toRender, pos)
            pos[1] += toRender.get_rect().h

        screen.blit(self.mainTextRects[-1], center((dims[0] / 2 + 160, dims[1] - 15),
                                                   self.mainTextRects[-1].get_rect().size))

    def renderWin(self):
        for itemTag in self.winScreen.keys():
            item = self.winScreen[itemTag]
            if type(item) is TextBox or type(item) is Button:
                item.render()

        pos = [dims[0] / 2, dims[1] / 2 - 100]
        for toRender in self.winTextRects:
            if type(toRender) is str:
                match toRender:
                    case "skip big":
                        pos[1] += bigFontSize
                    case "skip":
                        pos[1] += fontSize
                    case "skip small":
                        pos[1] += fontSize / 2
                    case _:
                        pos[1] += fontSize
                continue
            screen.blit(toRender, center(pos, toRender.get_rect().size))
            pos[1] += toRender.get_rect().h

    def processStart(self, events):
        for item in self.startScreen.keys():
            if type(self.startScreen[item]) is not list:
                if type(self.startScreen[item]) is TextBox:
                    self.startScreen[item].process(events)
                else:
                    self.startScreen[item].process()
        if self.startScreen["confirmButton"].clicked:
            self.buttonClickedStart()

    def processMain(self, events):
        for item in self.mainScreen.keys():
            if type(self.mainScreen[item]) is TextBox:
                self.mainScreen[item].process(events)
            elif type(self.mainScreen[item]) is Button:
                self.mainScreen[item].process()
        if self.mainScreen["submitButton"].clicked:
            self.buttonClickedNext()
        if self.mainScreen["skipButton"].clicked:
            self.buttonClickedSkip()
        if self.mainScreen["giveUpButton"].clicked:
            self.buttonClickedGiveUp()

    def processWin(self):
        for item in self.winScreen.keys():
            if type(self.winScreen[item]) is TextBox:
                self.winScreen[item].process(events)
            elif type(self.winScreen[item]) is Button:
                self.winScreen[item].process()
        if self.winScreen["againButton"].clicked:
            self.reset()
            self.prevScreenHold = True
            self.clearProgress()

    def updateInfoList(self):
        self.saveProgress()
        self.mainTextRects = [
            smallFont.render(f"Your next song:     (ID:{self.chart['id']})", True, "white"),
            Link(text=self.chart['song'],
                 link=self.chart['dlLink'],
                 font=hugeFont),
            font.render(f"       by {self.chart['artist']}", True, "white"),
            "skip",
            smallFont.render("chart by " + str(self.chart['creator']), True, "white"),
            font.render(f"Difficulty: ", True, "white"),
            "skip small",
            bigFont.render(f"Your goal: {self.currProgress + 1}%", True, "white"),
            diffFont.render(str(self.util.backParse(self.chart["diff"])), True, "white"),
            smallFont.render(f"Skipped: {self.skippedCharts}", True, "white")
        ]

    def updateWinList(self):
        self.saveProgress()
        self.winTextRects = [
            hugeFont.render("CONGRATULATIONS!!!", True, (50, 255, 50)),
            bigFont.render("You have completed the roulette!", True, "white"),
            "skip",
            font.render(
                f"Chosen difficulties: {self.util.backParse(self.util.minDiff)} ~ {self.util.backParse(self.util.maxDiff)}",
                True, "white"),
            font.render(f"You completed {self.completedCharts} charts and skipped {self.skippedCharts}", True, "white")
        ]

    def buttonClickedStart(self):
        if not self.startScreen["minTextbox"].verifiedValue and not self.startScreen["maxTextbox"].verifiedValue:

            if self.validateInput(self.startScreen["minTextbox"].text) and \
                    self.validateInput(self.startScreen["maxTextbox"].text):
                self.startScreen["minTextbox"].verifiedValue = self.util.parseInput(self.startScreen["minTextbox"].text)
                self.startScreen["maxTextbox"].verifiedValue = self.util.parseInput(self.startScreen["maxTextbox"].text)
                self.util.setDiffs(self.startScreen["minTextbox"].verifiedValue,
                                   self.startScreen["maxTextbox"].verifiedValue)
                self.chart = self.util.pickChart()

                self.currScreen = "main"
                self.updateInfoList()
                self.saveProgress()

                self.prevScreenHold = True

    def buttonClickedNext(self):
        if self.mainScreen["submitTextBox"].text:
            if int(self.mainScreen["submitTextBox"].text) > 100:
                self.badInpText = "Percentage is too high!"
                self.badInpCountdown[0] = pg.time.get_ticks()
            elif int(self.mainScreen["submitTextBox"].text) <= self.currProgress:
                self.badInpText = "Percentage is too low!"
                self.badInpCountdown[0] = pg.time.get_ticks()
            elif int(self.mainScreen["submitTextBox"].text) == 100:
                self.completedCharts += 1
                self.currScreen = "win"
                self.updateWinList()
                self.prevScreenHold = True


            else:
                self.flashCountdown[0] = pg.time.get_ticks()
                self.completedCharts += 1
                self.chart = self.util.pickChart()
                self.currProgress = int(self.mainScreen["submitTextBox"].text)
                self.mainScreen["submitTextBox"].text = ""
                self.mainScreen["submitTextBox"].process([])
                self.updateInfoList()
                self.prevScreenHold = True

    def buttonClickedSkip(self):
        if (
                messagebox.askokcancel("Skip chart?",
                                       "Are you sure you want to skip this chart? You will loose one percent of your progress and add one skipped chart to the count.")
        ):
            if self.currProgress > 1:
                self.currProgress -= 1
            self.chart = self.util.pickChart()
            self.skippedCharts += 1
            self.updateInfoList()
            self.prevScreenHold = True
            self.saveProgress()

    def buttonClickedGiveUp(self):
        if (
                messagebox.askokcancel("Give up?",
                                       "Are you sure you want to give up? You will loose ALL your progress "
                                       "and will be brought back to difficulty selection screen.")
        ):
            self.reset()
            self.clearProgress()

    def validateInput(self, inp):
        badInput = self.util.validateInput(inp)
        if badInput:
            self.badInpText = "Bad input!!!"
            self.badInpCountdown[0] = pg.time.get_ticks()
        return not badInput

    def badInputDisplay(self):
        if pg.time.get_ticks() - self.badInpCountdown[0] < self.badInpCountdown[1]:
            loadText = font.render(self.badInpText, True, "red")
            loadText.set_alpha(int(255 * (pow(1 - (pg.time.get_ticks() - self.badInpCountdown[0])
                                              /
                                              self.badInpCountdown[1], 1 / 2))))
            screen.blit(loadText, center(CENTER, loadText.get_rect().size))


forum = ForumScraper(apiLink)
ui = UI()
print("starting")
forum.getCharts(ui.util)

clock = pg.time.Clock()
bg = pg.transform.scale_by(pg.image.load(theBG), 3.5)
bg.set_alpha(100)

if __name__ == "__main__":
    while 1:
        if forum.badAccess:
            sys.exit()
        screen.fill(ui.bgColor)
        screen.blit(bg, (0,-450))
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
        forum.displayLoading()
        if forum.chartList is not None:
            ui.render()
            ui.process(events)

        pg.display.flip()
        clock.tick(fps)
