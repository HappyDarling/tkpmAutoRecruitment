import os, sys, json
from PIL import Image

# PyQT Module
from PyQt5 import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import uic

# PyQt Design Library
from qt_material import QtStyleTools

# 분리된 Module Import
from module import Capture, ImgProcessing, Util, FindCharacterByTag

# Qt Designer로 만든 UI 불러오기
form_class = uic.loadUiType("tkpm_UI.ui")[0]

# 
global win_list
win_list = None

class WindowClass(QMainWindow, QtStyleTools, form_class):
    # Init
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.set_style()
        self.ScanWindow.clicked.connect(self.ScanWindowItem)
        self.ScanButton.clicked.connect(self.ScanAutoFiltering)
        
    # Style
    def set_style(self):
        extra = {}
        extra['font_family'] = 'Roboto'
        extra['density_scale'] = str(0)
        theme = 'light_pink.xml'
        invert = True
        self.apply_stylesheet(self, theme=theme, extra=extra, invert_secondary=invert)
        
        self.treeWidget.setColumnWidth(0, 180)
        self.treeWidget.setColumnWidth(1, 80)
        
    # 
    def ScanWindowItem(self):
        global win_list
        win_list = Capture.get_win_list()
        self.WindowListBox.clear()
        for win_item in win_list:
            self.WindowListBox.addItem(win_item[0]) # 프로세스 드롭다운 박스에 추가
    
    # 
    def ScanAutoFiltering(self):
        hwnd = win_list[self.WindowListBox.currentIndex()][1]
        x1, y1, x2, y2 = Capture.get_win_size(hwnd)
        Image.fromarray(Capture.get_win_image(x1, y1, x2, y2)).save("screenshot.png", "PNG")
        tag_list = Util.RegexToKor(ImgProcessing.RootImageTrim())
        
        # 태그 오류 수정
        for index, item in enumerate(tag_list):
            if item == "품속성":
                tag_list[index] = "풍속성"
        
        print(tag_list)
        tags_num = FindCharacterByTag.FindTagNumToKor(tag_list)
        tags_num.sort()
        self.ScanAutoButton(tags_num)
        tagSummonCharacterList = FindCharacterByTag.FindCharacter(tags_num)
        self.SetTreeWidget(tagSummonCharacterList)

    def SetTreeWidget(self, tagSummonCharacterList):
        rootDir = os.path.dirname(__file__)
        korInfoDir = os.path.join(rootDir, '.\data\KorInfo.json')
        with open(korInfoDir, 'r', encoding="utf-8") as f:
            korInfoJson = json.load(f)
        
        self.ClearTreeWidget()
        
        # 확정 SR, Tree 작업 완료
        if len(tagSummonCharacterList["DefinitiveSR"]) > 0:
            for tsc in tagSummonCharacterList["DefinitiveSR"]:
                treeOne = self.treeWidget.topLevelItem(1)
                itemOne = QTreeWidgetItem(treeOne)
                itemOne.setText(0, korInfoJson.get('name').get(tsc.get("id")))
                
                if (int(tsc.get("id")) < 200):
                    itemOne.setText(1, "⁂ SSR")
                elif (int(tsc.get("id")) < 300):
                    itemOne.setText(1, "⁑ SR")
                elif (int(tsc.get("id")) < 400):
                    itemOne.setText(1, "⁎ R")
                elif (int(tsc.get("id")) < 500):
                    itemOne.setText(1, "N")
                out = ''
                for tags in tsc.get("tags"):
                    out += "["
                    for tag in tags:
                        print(tag)
                        out += korInfoJson.get('tags')[int(tag)]
                        out += ", "
                    out = out.rstrip(", ")
                    out += "], "
                itemOne.setText(2, out)
                
        # 확정 캐릭터 (SR), Tree 작업 완료
        if len(tagSummonCharacterList["DefinitiveCharacter"]) > 0:
            for tsc in tagSummonCharacterList["DefinitiveCharacter"]:
                treeTwo = self.treeWidget.topLevelItem(2)
                itemTwo = QTreeWidgetItem(treeTwo)
                itemTwo.setText(0, korInfoJson.get('name').get(tsc.get("id")))
                
                if (int(tsc.get("id")) < 200):
                    itemTwo.setText(1, "⁂ SSR")
                elif (int(tsc.get("id")) < 300):
                    itemTwo.setText(1, "⁑ SR")
                elif (int(tsc.get("id")) < 400):
                    itemTwo.setText(1, "⁎ R")
                elif (int(tsc.get("id")) < 500):
                    itemTwo.setText(1, "N")
                out = ''
                for tags in tsc.get("tags"):
                    out += "["
                    for tag in tags:
                        out += korInfoJson.get('tags')[int(tag)] + ", "
                    out = out.rstrip(", ")
                    out += "], "
                itemTwo.setText(2, out)
        
        # 확정 X, Tree 작업 완료
        if len(tagSummonCharacterList["Default"]) > 0:
            for tsc in tagSummonCharacterList["Default"]:
                treeThree = self.treeWidget.topLevelItem(3)
                itemThree = QTreeWidgetItem(treeThree)
                itemThree.setText(0, korInfoJson.get('name').get(tsc.get("id")))
                
                if (int(tsc.get("id")) < 200):
                    itemThree.setText(1, "⁂ SSR")
                elif (int(tsc.get("id")) < 300):
                    itemThree.setText(1, "⁑ SR")
                elif (int(tsc.get("id")) < 400):
                    itemThree.setText(1, "⁎ R")
                elif (int(tsc.get("id")) < 500):
                    itemThree.setText(1, "N")
                out = ''
                for tag in tsc.get("tags"):
                    out += korInfoJson.get('tags')[int(tag)] + ", "
                out = out.rstrip(", ")
                itemThree.setText(2, out)
                
        self.treeWidget.itemClicked.connect(self.SetListWidget)
    
    # TreeWidget의 아이템 클릭시 ListWidget 재설정 (],)를 기준으로 함
    def SetListWidget(self, it, col):
        self.listWidget.clear()
        print("click!")
        tagList = it.text(col).split('],')
        if col == 2:
            for item in tagList:
                self.listWidget.addItem(item.lstrip("["))
            
    # 스캔 후 Tag 변수 리스트화 및 자동 체크
    def ScanAutoButton(self, tags_num):
        tagButtonList = [self.TagBtn00, self.TagBtn01, self.TagBtn02, self.TagBtn03, self.TagBtn04, self.TagBtn05, self.TagBtn06, self.TagBtn07, self.TagBtn08, self.TagBtn09, self.TagBtn10,
                         self.TagBtn11, self.TagBtn12, self.TagBtn13, self.TagBtn14, self.TagBtn15, self.TagBtn16, self.TagBtn17, self.TagBtn18, self.TagBtn19, self.TagBtn20,
                         self.TagBtn21, self.TagBtn22, self.TagBtn23, self.TagBtn24, self.TagBtn25, self.TagBtn26, self.TagBtn27, self.TagBtn28, self.TagBtn29, self.TagBtn30,
                         self.TagBtn31, self.TagBtn32]
        
        # 기존 체크되있는 리스트 제거
        for index in range(0, 33):
            tagButtonList[index].setCheckState(0)
            
        # 현재 태그 정보로 갱신
        for tag in tags_num:
            tagButtonList[tag].setCheckState(2)
    
    # 스캔 후 TreeWidget 재설정
    def ClearTreeWidget(self):
        treeWidgetTextList = ["확정 SSR", "확정 SR", "확정 캐릭터", "조합식"]
        self.treeWidget.clear()
        
        for index in range(0, 4):
            item = QTreeWidgetItem()
            item.setText(0, treeWidgetTextList[index])
            self.treeWidget.invisibleRootItem().addChild(item)
    
    
if __name__ == '__main__':
   app = QApplication(sys.argv)
   myWindow = WindowClass()
   myWindow.show()
   app.exec_()