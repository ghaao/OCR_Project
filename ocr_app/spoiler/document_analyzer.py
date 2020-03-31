#-*-coding:utf8;-*-
'''
Optical Character and Table Recogniton (OCTR) 
Kim Namkil (2019.11.26) : First scripting
Kim Namkil (2020.02.10) : add pre-processing logic for mobile photo image (document_scanner)
'''

from PIL import Image, ImageDraw, ImageFont
from tesserocr import PyTessBaseAPI, RIL, PSM, OEM
from operator import itemgetter
from ocr_app.spoiler.utils.rectangle import Rectangle
from ocr_app.spoiler.utils import geometry as geo

from ocr_app.spoiler.imageProcessingFunction.document_scanner import DocScanner
import numpy as np
import ocr_app.spoiler.table_recognition
import cv2
import os


class DocumentAnalyzer:

    FONT_FILE = "/usr/share/fonts/truetype/nanum/NanumGothicCoding.ttf"
    FONT_SIZE = 42
    # 직선을 연장하여 교차점을 만들기 위하여 길이를 연장
    LINE_EXTENTION = 10

    def __init__(self, image_file):
        self._image_file = image_file
        if image_file:
            self._load_image_file()
        self._pil_img = None
        self._cv2_img = None
        # for Visualize
        self._draw_img = None
        # self._oem_mode = oem
        # self._tess_api = PyTessBaseAPI(lang=language, psm = self._psm_mode)        
        self._table_coords = [] 
        self._text_coords = [] 
        self._table_contents = []
        self._row_text_coords = []
        # document size
        self._width = None   
        self._height = None
        # detect table by tess
        self._horizontal_lines = []
        self._vertical_lines = []

    def _load_image_file(self):
        """
        Load the image file self._image_file to self._pil_img, self._cv2_img. Additionally set the image width and height (self.image_width
        and self.image_height)
        """
        self._cv2_img = cv2.imread(self._image_file, flags=cv2.IMREAD_COLOR)
        self._cv2_img = cv2.cvtColor(self._cv2_img, cv2.COLOR_BGR2GRAY)
        self._pil_img = Image.fromarray(cv2.cvtColor(self._cv2_img, cv2.COLOR_BGR2RGB)) 
        # self._pil_img = Image.open(self._image_file)
        # self._tess_api.SetImage(self._pil_img)
        # self._tess_api.SetImageFile(self._image_file)
        self._width, self._height = self._pil_img.size
        
    
    def _scan_image_file(self):
        """
        pre processing : convert RGB to gray and crop paper area
        """
        doc_scanner = DocScanner()
        img = cv2.imread(self._image_file, flags=cv2.IMREAD_COLOR)
        self._image_file = self._image_file
        self._cv2_img = doc_scanner.scan(img)
        new_path = os.path.splitext(self._image_file)
        self._image_file = new_path[0] + "_copy" + new_path[1]
        cv2.imwrite(self._image_file, self._cv2_img)      
        self._pil_img = Image.fromarray(cv2.cvtColor(self._cv2_img, cv2.COLOR_BGR2RGB))        
        # self._tess_api.SetImage(self._pil_img)        
        self._width, self._height = self._pil_img.size
        

    def set_image_file(self, image_file, image_type):
        """
        Load the image file self._image_file to self._pil_img, self._cv2_img. Additionally set the image width and height (self.image_width
        and self.image_height)
        scan type image = 1
        photo type image = 2        
        """
        if image_file is None:
            raise IOError("could not load file '%s'" % image_file)
        
        self._image_file = image_file
        if image_type == 1:
            self._load_image_file()
        elif image_type == 2:
            self._scan_image_file()
       
        width = self._width
        height = self._height
        return width, height

    
    def show_image(self):
        self._pil_img.show()

    def detect_lines(self, line_extention = LINE_EXTENTION):
        """
        Detect lines in input image using tesseractOCR
        Return detected lines as list with tuples:
        """       
        # self._tess_api.SetImage(self._pil_img)
        tess_api = PyTessBaseAPI(lang='eng', psm = PSM.AUTO_ONLY)
        tess_api.SetImageFile(self._image_file)    
        self._horizontal_lines = []
        self._vertical_lines = []
        vertical_lines = []
        horizontal_lines = []        
        # SYMBOL로 하는 이유는 속도가 가장 빠르고 라인으로 찾으로 TEXT의 박스를 선으로 오인함.        
        
        boxes = tess_api.GetComponentImages(RIL.SYMBOL, False)
        
        for i, (im, box, _, _) in enumerate(boxes):
            # im is a PIL image object
            # box is a dict with x, y, w and h keys
            
            # 세로라인 (높이가 폭의 10배가 넘는 박스 필터)
            if box['w'] * 10 < box['h']:
                start_point = (int(box['x'] + box['w'] / 2), int(box['y']) - line_extention)
                end_point = (int(box['x'] + box['w'] / 2), int(box['y'] + box['h']) + line_extention)
                vertical_lines.append(start_point + end_point)                

            # 가로라인 (폭이 높이의 10배가 넘는 박스 필터)
            if box['h'] * 10 < box['w']:
                start_point = (int(box['x']) - line_extention, int(box['y'] + box['h'] / 2))
                end_point = (int(box['x'] + box['w']) + line_extention, int(box['y'] + box['h'] / 2))
                horizontal_lines.append(start_point + end_point)                

        self._horizontal_lines, self._vertical_lines = horizontal_lines.copy(), vertical_lines.copy()        
        return horizontal_lines, vertical_lines

    def detect_table_by_tess(self):
        """
        Extract grid in lines
        Return rectangle list:
        """
        horizontal_lines, vertical_lines = self.detect_lines()  
        # debug
        img = Image.new("RGB", (3312, 4677), color='white')
        draw = ImageDraw.Draw(img)
        for h_line in self._horizontal_lines:
            draw.line((h_line[0],h_line[1],h_line[2],h_line[3]), fill='blue', width=3)
        for v_line in self._vertical_lines:            
            draw.line((v_line[0], v_line[1], v_line[2], v_line[3]), fill='red', width=3)        

        grid_cells = geo.get_grid_cell(horizontal_lines, vertical_lines)
        
        self._table_coords = grid_cells.copy()
        return grid_cells


    def detect_table(self, x=1, y=1, multi=1):
        """
        Refer to the Algotithm.pdf for details on how it works
        a raster-based method to recognize tables using openCV        
        return list[x,y(Vertext of the rectangle),x1,y1(Vertext of the rectangle opposite to x,y) ]
         """
        img = cv2.resize(self._cv2_img, dsize=(0, 0), fx=x, fy=y, interpolation=cv2.INTER_AREA)

        if img is None:
            raise ValueError("File {0} does not exist".format(self._image_file))
        
        imgThresh = cv2.threshold(img, 150, 255, cv2.THRESH_BINARY_INV)[1]
        imgThreshInv = cv2.threshold(img, 150, 255, cv2.THRESH_BINARY)[1]

        imgDil = cv2.dilate(imgThresh, np.ones((5, 5), np.uint8))
        imgEro = cv2.erode(imgDil, np.ones((4, 4), np.uint8))
        
        contour_analyzer = table_recognition.ContourAnalyzer(imgDil)
        # 1st pass (black in algorithm diagram)
        contour_analyzer.filter_contours(min_area=400)        
        contour_analyzer.build_graph()
        contour_analyzer.remove_non_table_nodes()
        contour_analyzer.compute_contour_bounding_boxes()
        contour_analyzer.separate_supernode()
        contour_analyzer.find_empty_cells(imgThreshInv)

        contour_analyzer.find_corner_clusters()
        contour_analyzer.compute_cell_hulls()
        contour_analyzer.find_fine_table_corners()

        # Add missing contours to contour list
        missing_contours = contour_analyzer.compute_filtered_missing_cell_contours()
        contour_analyzer.contours += missing_contours

        # 2nd pass (red in algorithm diagram)
        contour_analyzer.compute_contour_bounding_boxes()
        contour_analyzer.find_empty_cells(imgThreshInv)

        contour_analyzer.find_corner_clusters()
        contour_analyzer.compute_cell_hulls()
        contour_analyzer.find_fine_table_corners()

        # End of 2nd pass. Continue regularly
        contour_analyzer.compute_table_coordinates(5.)
        # contour_analyzer.draw_table_coord_cell_hulls(img, xscale=.8, yscale=.8)
        coord_list = contour_analyzer.getNodePoints()

        # Remove none-square and sorting
        for coord in coord_list:           
            temp = { sum(coord[0]) : 0 , sum(coord[1]) : 1 , sum(coord[2]) : 2, sum(coord[3]) : 3}        
            temp = sorted(temp.items(), key=itemgetter(0))        
            if len(temp) == 4:
                # x, y, x1, y1 = coord[temp[0][1]][0]*2, coord[temp[0][1]][1]*2, coord[temp[3][1]][0]*2, coord[temp[3][1]][1]*2               
                x, y, x1, y1 = coord[temp[0][1]][0]*multi, coord[temp[0][1]][1]*multi, coord[temp[3][1]][0]*multi, coord[temp[3][1]][1]*multi            
                self._table_coords.append([ x, y, x1, y1]) 
        table_coordinates = self._table_coords.copy()
        
        return table_coordinates

    def visualize_table(self):
        """
        Draw table on empty image by pillow(OpenCV does not support uft-8)
        return list[symbol, x,y(Vertext of the rectangle), x1,y1(Vertext of the rectangle opposite to x,y) ]
        """
        if self._table_coords is None:
            raise ValueError("could not find table coordinates. Run [def detect_table] first.")
        if self._draw_img is None:
            self._draw_img = Image.new("RGB", (self._width, self._height), color='white')        
        draw = ImageDraw.Draw(self._draw_img)
        for table_coord in self._table_coords.copy():
            draw.rectangle((table_coord[0], table_coord[1], table_coord[2], (table_coord[3])), outline='black', width=2)

    def detect_character(self, lang = 'kor', psm = PSM.SINGLE_COLUMN, fx=1, fy=1, multi=1):
        """ 
        Extract text and text bounding box coordinates
        """
        # _img = cv2.resize(self._cv2_img, dsize=(0, 0), fx=fx, fy=fy, interpolation=cv2.INTER_AREA)
        # _pil_img = Image.fromarray(cv2.cvtColor(_img, cv2.COLOR_BGR2RGB))

        tess_api = PyTessBaseAPI(lang=lang, psm=psm)
        tess_api.SetImageFile(self._image_file)
        box_text_coords = tess_api.GetBoxText(1).split('\n')

        for box_text_coord in box_text_coords:
            if box_text_coord != '':
                box_text_coord = box_text_coord.split(' ')                
                # The coordinate system of tesseact and OpenCV are different
                x1, y1, x2, y2 = int(box_text_coord[1]), self._height * fy- int(box_text_coord[2]), int(box_text_coord[3]), self._height * fy - int(box_text_coord[4])
                x = sorted([x1, x2])
                y = sorted([y1, y2])
                symbol, x1, y1, x2, y2, w, h = box_text_coord[0], x[0]*multi, y[0]*multi, x[1]*multi, y[1]*multi, (x[1]-x[0])*multi, y[1]-y[0]*multi
                # remove lines 
                if (symbol == '~' and ((w * 5 < h or h * 5 < w) or h == 0 or w == 0 ) or h == 0 or w == 0 ) is not True:
                    self._text_coords.append([symbol, x1, y1, x2, y2])

        text_coordinates = self._text_coords.copy()

        return text_coordinates

    def rectangle_character(self, rectangle, lang = 'kor', psm = PSM.SINGLE_COLUMN ):  
        tess_api = PyTessBaseAPI(lang=lang, psm = psm)        
        tess_api.SetImageFile(self._image_file)
        tess_api.SetRectangle(rectangle[0], rectangle[1], rectangle[2], rectangle[3])

        return tess_api.GetUTF8Text()

    def visualize_character(self, font_file = FONT_FILE, font_size = FONT_SIZE):
        """
        Draw text on empty image by pillow 

        """        
        if self._text_coords is None:
            raise ValueError("could not find text coordinates. Run [def detect_character] first.")
        if self._draw_img is None:
            self._draw_img = Image.new("RGB", (self._width, self._height), color='white')
        font = ImageFont.truetype(font_file, font_size)
        draw = ImageDraw.Draw(self._draw_img)
        for text_coord in self._text_coords.copy():            
            draw.text((text_coord[1], text_coord[2]), text_coord[0], fill='black', font=font)
    
    def show_recognized(self):
        self._draw_img.show()

    def combine_coordinates(self):
        """ 
        Extract the contents of the table by mapping the coordinates of the table with the coordinates of the text.
        """        
        for table_coord in self._table_coords.copy():
            self._table_contents.append(["", table_coord[0], table_coord[1], table_coord[2], table_coord[3]])

        for table in self._table_contents.copy():                 
            for text in self._text_coords.copy():
                
                a = Rectangle(table[1], table[2], table[3], table[4])
                b = Rectangle(text[1], text[2], text[3], text[4])
                # Check if intersection of two rectangles is over 70%
                c = a&b
                if c is not None:                                     
                    if b/c > 0.7 and b/c <= 1.3:                           
                        table[0] = table[0] + text[0]
                    
        self._table_contents = sorted(self._table_contents, key=lambda table: table[2])
        table_contents = self._table_contents.copy()

        return table_contents

    def cut_row(self):
        """
        cut text_coords into row
        """         
        forechar = None
        row = []
        rowlist = []
        # text_coords = sorted(self._text_coords, key=itemgetter(2, 1+2))
        text_coords = self._text_coords.copy()
        for text in text_coords:
            if forechar is None:
                row.append(text)
                forechar = text
                half_height = (forechar[4] - forechar[2]) / 2
                baseline = forechar[2] + half_height
                base_top = forechar[2] - half_height
                base_bottom = forechar[4] + half_height
            else:                
                if (text[2] < baseline and text[4] > baseline) or (text[2] > base_top and text[4] < base_bottom):
                    row.append(text)                    
                else:
                    rowlist.append(row)
                    forechar = None
                    row = []
                    row.append(text)
        self._row_text_coords = rowlist.copy()

    def get_row(self):
        return self._row_text_coords

    def cut_letter_number(self):
        """
        cut row into letters and numbers
        """        
        self._letter_number = []
        row_text_coords = self._row_text_coords.copy()   
        for row in row_text_coords:
            # 문자 숫자 자르기               
            number_type = self._get_number_type(row)              
            for source in number_type:                   
                self._letter_number.append(source)
    
    def get_letter_number(self):
        return self._letter_number.copy()

    def _add_coords(self, target, source):
        if len(target) > 0 :
            target[0] = target[0] + source[0]
            target[1] = min(target[1], source[1])
            target[2] = min(target[2], source[2])
            target[3] = max(target[3], source[3])
            target[4] = max(target[4], source[4])
        else:
            target = source[:]
        return target
    
    def _get_number_type(self, row):        
        pair_list = []
        key = []
        value = []        
        for i in range(0, len(row)):                            
            if (i > 0 and (row[i-1][0].isnumeric() and row[i][0].isalpha())):                
                pair_list.append([key, value]) 
                key = []
                value = []              

            if row[i][0].isalpha():
                key = self._add_coords(key, row[i])
            elif row[i][0].isnumeric():
                value = self._add_coords(value, row[i])
            elif row[i][0] == "-" or row[i][0] == "*" :
                value = self._add_coords(value, row[i])            
            if i == len(row)-1 :
                pair_list.append([key, value])

        return pair_list
