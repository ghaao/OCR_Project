#-*-coding:utf8;-*-
'''
OCR for indemnity insurance receipt
Kim Namkil (2019.11.26)
Add CERTIFICATE MODE, RECEIPT MODE
Kim Namkil (2020.02.18)
'''
from ocr_app.spoiler.document_analyzer import DocumentAnalyzer
from ocr_app.spoiler.mapper import WordMapper
from ocr_app.spoiler.utils.stringutil import fuzzy_string_matcher, clean_text, get_acc_clss_cd
from ocr_app.static.properties.enumeration import RM, DTC, ITC, MTM


class Spoiler:

    def __init__(self, run_mode = RM.LOCAL_TEST):
        self._run_mode = run_mode
        self._document_type_code = None
        self._image_type_code = None
        self._file_path = None
        self._height = None
        self._width = None
        self._table_coords = None
        self._text_coords = None
        self._item_list = None
        # print('### <Init>', str(RM(self._run_mode)))

    def publish(self, document_type_code, image_type_code, file_path, item_list): 
        ''' document_type_code
            1:DTC.MEDICAL_CERTIFICATE
            2:DTC.MEDICAL_RECEIPT
            image_type_code
            1:ITC.SCAN
            2:ITC.PHOTO
        '''   
        self._document_type_code = document_type_code
        self._image_type_code = image_type_code
        self._file_path = file_path
        self._item_list = item_list
        

        # 글자 및 테이블 인식 모듈
        document_analyzer = DocumentAnalyzer(self._file_path)
        # 이미지 파일 셋팅
        self._width, self._height = document_analyzer.set_image_file(self._file_path, image_type=self._image_type_code.value)
        # print('### <Publish> Request specification')
        # print('### File Path     :', self._file_path)
        # print('### Document Type :', DTC(self._document_type_code).name)
        # print('### Image Type    :', ITC(self._image_type_code).name)
        # print('### Image Size    :', 'WIDTH:'+ str(self._width) +', HEIGHT:' + str(self._height))

        # dpi = 200
        # if self._width > 3000 and self._height > 4000:
        #     dpi = 400

        # 사진이미지 crop & warp 확인
        if self._run_mode == RM.LOCAL_TEST:
            # print('### <Debug> Verify perspective transform image.')
            document_analyzer.show_image()

        # 이미지/문서 종류 별 resize 값 셋팅
        # 진단서 
        if self._document_type_code == DTC.MEDICAL_CERTIFICATE:
            font_size = 25
            # 사진 진단서 테이블 인식 시 너무 크면 인식이 어려워 1/4로 사이즈 변경 후 인식 후 좌표를 4배로 계산

            if self._image_type_code == ITC.PHOTO:                     
                self._text_coords = document_analyzer.detect_character()
                # self._table_coords = document_analyzer.detect_table(x=x, y=y, multi=m)
            elif self._image_type_code == ITC.SCAN:                                
                # self._table_coords = document_analyzer.detect_table(x=x, y=y, multi=m) 
                self._text_coords = document_analyzer.detect_character()
                self._table_coords = document_analyzer.detect_table_by_tess()

            # 테이블 인식 없이 문자열 구성만으로 추출로 변경
            self._table_coords = []

            # 진단서 데이터 추출 처리 - 번호 형식의 데이터 추출 (연번호, 등록번호, 주민등록번호 등)
            document_analyzer.cut_row()
            document_analyzer.cut_letter_number()
            # for word in document_analyzer.get_row():
            # print(''.join([word[0] for word in word]))
            #     print(word)
            letter_number = document_analyzer.get_letter_number()

            number_word = []
            table_word = []
            for num in self._item_list.copy():               
                if num[0] == "번호":
                    number_word.append(num[1:])
                elif num[0] == "테이블":
                    table_word.append(num[1:])

            up_letter_number = letter_number[0:round(len(letter_number)/2)]
            up_number_word = [num for num in number_word if num[2] == "0"]

            # 번호체계 값 맵핑 윗부분
            number_word_mapper = WordMapper(up_number_word, up_letter_number, self._table_coords, dtc=DTC.MEDICAL_CERTIFICATE, mtm=MTM.NUMERIC)
            number_word_mapper.word_mapping()

            # recog_word = [정확도, source, target, source_대분류, target_value]
            recog_word = number_word_mapper.get_mapping_results()

            # 번호체계 값 맵핑 아래부분
            down_letter_number = letter_number[round(len(letter_number)/2):]
            down_number_word = [num for num in number_word if num[2] == "5"]
            number_word_mapper = WordMapper(down_number_word, down_letter_number, self._table_coords, dtc=DTC.MEDICAL_CERTIFICATE, mtm=MTM.NUMERIC)
            number_word_mapper.word_mapping()
            recog_word2 = number_word_mapper.get_mapping_results()            
            recog_word.extend(recog_word2)


            # print("### Number type value :", recog_word)

            # 인식한 글자의 좌표와 인식한 테이블의 좌표를 맵핑하여 글자 뭉치 생성
            table_contents = document_analyzer.combine_coordinates()
           
            if len(table_contents) > 0:
                table_word_mapper = WordMapper(table_word, table_contents, self._table_coords, dtc=DTC.MEDICAL_CERTIFICATE, mtm=MTM.SINGLE_WORD)            
                table_word_mapper.word_mapping()           
                recog_word3 = table_word_mapper.get_mapping_results()            
                for column in recog_word3:
                    for idx, val in enumerate(table_contents):                   
                        if column[2] == val[0]: 
                            if column[3] == "질병분류기호":
                                pass
                            else:                          
                                column[4] = clean_text(table_contents[idx+1][0])
                # print("### table type value :", recog_word3)               
                recog_word.extend(recog_word3)

            # 질병분류기호 값 추출
            acc_item_word = [word for word in table_word if word[0] == '질병분류기호']
            acc_word_list = []
            result = []
            acc_word = []
            for row in document_analyzer.get_row():
                row_text = ''.join([word[0] for word in row])                                  
                for item in acc_item_word:                        
                    result.append(fuzzy_string_matcher(row_text, item[1]))

            if len(result) > 0 :                
                result = max(result)
                if result[0] > 7:
                    for row in document_analyzer.get_row():
                        row_text = ''.join([word[0] for word in row])                 
                        idx = row_text.find(result[1])
                        if idx > -1:                            
                            acc_word_list = row[idx:idx+len(result[1])]                        
                            break
                    
                    if len(acc_word_list) > 0:
                        last_idx = len(acc_word_list) - 1
                        text_height = acc_word_list[0][4] - acc_word_list[0][2]
                        char_width = acc_word_list[0][3] - acc_word_list[0][1]
                        text_width = acc_word_list[last_idx][1]-acc_word_list[0][1]+ acc_word_list[0][3] - acc_word_list[0][1]           
                        rectangle = [acc_word_list[0][1] - char_width , acc_word_list[0][2]+text_height, text_width + char_width, text_height*10]
                        acc_word = document_analyzer.rectangle_character(rectangle, lang='eng', psm=6)                        
            
            acc_words = get_acc_clss_cd(list(filter(None, acc_word.split('\n'))))

            final_result = []
            for word in acc_words:
                if word != '':
                    final_result.append(['질병분류기호', word])
            for word in recog_word:
                if word[4] != '':
                    final_result.append([word[3], word[4]])

            return final_result

        # 실손영수증
        elif self._document_type_code == DTC.MEDICAL_RECEIPT:            
            if self._image_type_code == ITC.PHOTO:
                x, y, m, font_size =  0.5, 0.5, 2, 15   
                # x, y, m, font_size =  1,1,1,20        
                self._text_coords =document_analyzer.detect_character(fx=x, fy=y, multi=m)                
                self._table_coords = document_analyzer.detect_table()      
            # 회사 복합기 200dpi 크기 기준
            elif self._image_type_code == ITC.SCAN:
                x, y, m, font_size = 1, 1, 1, 15               
                self._text_coords = document_analyzer.detect_character(fx=x, fy=y, multi=m)                
                self._table_coords = document_analyzer.detect_table(x=x, y=y, multi=m)

            


        # 테이블 & 글자 확인
        if self._run_mode == RM.LOCAL_TEST:
            # print('### <Debug> Verify extract table and text image.')
            # 신규 이미지 오브젝트에 인식한 글자를 그린다.
            document_analyzer.visualize_character(font_size= font_size) 
            # 신규 이미지 오브젝트를 만들고 인식한 테이블을 그린다.
            document_analyzer.visualize_table()            
            # 신규 이미지 오브젝트 시각화
            document_analyzer.show_recognized()
