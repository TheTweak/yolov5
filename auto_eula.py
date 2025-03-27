from helper import UICompType
from ocr import OCR
from text_class import TextClassifier

'''
python.exe detect.py --weights C:\\Users\\thetweak\\source\\gui-element-detection-sook\\weights\\300_1\\best.pt --source "C:\\Users\\thetweak\\Pictures\\Screenshots\\benchmark\\eula" --classes 6 10
'''

ocr = OCR()
tc = TextClassifier()

class UIComp:
    def __init__(self, cls, xyxy, image):
        self.cls = cls
        x0, y0, x1, y1 = xyxy
        self.x0, self.y0, self.x1, self.y1 = int(x0), int(y0), int(x1), int(y1)
        self.text = None
        self.image = image[self.y0:self.y1, self.x0:self.x1]
        self.comp_type = UICompType(cls)
        match self.comp_type:
            case UICompType.TextButton | UICompType.Modal:
                ocr_text = ocr.ocr_yc(self.image)
                if len(ocr_text):
                    self.text = ocr_text

    def __str__(self):
        return f"{self.comp_type.name}(text={self.text} bb=[{self.x0} {self.y0} {self.x1} {self.y1}])"

    def click(self):
        print(f"clicked on {self}")


class AutoEULA:
    def __init__(self):
        self.ui_comps = []

    def process(self, detected, image):
        print("---------------------------------------")
        self.ui_comps = [UIComp(int(cls), xyxy, image) for *xyxy, _, cls in detected]
        # sort UI components by type reversed, so that Modal window would be before TextButton
        self.ui_comps = sorted(self.ui_comps, key=lambda x: x.comp_type.value, reverse=True)
        detected = False

        for uic in self.ui_comps:
            print(f"UI comp: {uic}")
            match uic.comp_type:
                case UICompType.Modal if tc.text_is_eula(uic.text):
                    detected = True
                    print("EULA detected")
                case UICompType.TextButton if (detected and tc.text_is_accept(uic.text)):
                    uic.click()
                    break
