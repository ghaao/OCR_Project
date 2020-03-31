class CharacterSeperator():
    def __init__(self):
        # self.string = string
        # self.result = []
        self.string_result = ""
        self.choseong_list = [char for char in "ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ"]
        self.jungseong_list = [char for char in "ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ"]
        self.jongseong_list = [char for char in " ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ"]

    
    def run(self):
        for char in self.string:
            
            character_code = ord(char)
            # Do not process unless it is in Hangul syllables range.
            if 0xD7A3 < character_code or character_code < 0xAC00:                
                continue

            choseong_index = (character_code - 0xAC00) // 21 // 28
            jungseong_index = (character_code - 0xAC00 - (choseong_index * 21 * 28)) // 28
            jongseong_index = character_code - 0xAC00 - (choseong_index * 21 * 28) - (jungseong_index * 28)
           
            self.string_result = self.string_result + self.choseong_list[choseong_index] + self.jungseong_list[jungseong_index] + self.jongseong_list[jongseong_index]
            
    def set(self, string):
        self.string = string
        self.string_result = ""
        
    def get(self):
        return self.string_result.replace(" ", "")

def number_strip(text):
    chars = text
    rev = chars[::-1]
    cnt = 0
    for char in rev:
        if char.isalpha():
            break 
        else:       
            cnt += 1

    result = chars[0:len(chars)-cnt]
    cnt = 0
    for char in result:
        if char.isalpha():
            break 
        else:       
            cnt += 1
    result = result[cnt:]
    return result

from fuzzywuzzy import fuzz
from fuzzywuzzy import process

def fuzzy_string_matcher(string, word):
    start = 0
    end = len(word)
    character_seperator = CharacterSeperator()
    character_seperator.set(word)
    character_seperator.run()
    word1 = character_seperator.get()
    result = []
    output = []
    while end <= len(string):
        temp = string[start:end]
        character_seperator.set(temp)
        character_seperator.run()
        temp1 = character_seperator.get()

        start+=1        
        end+=1
        ratio = fuzz.ratio(temp1, word1)
        result.append([ratio, temp, word])
    if len(result) > 0 :
        output = max(result)
    return output

import re
 
def clean_text(read_data): 
    #텍스트에 포함되어 있는 숫자 문자만 추출
    text = re.sub('[^0-9a-zA-Zㄱ-힗]', '', read_data)
    return text

def get_acc_clss_cd(acc_list):
    result = []
    pattern = re.compile(r'[A-Z]\d{2,4}')
    for string in acc_list:
        string = string.replace('.', '')
        if string[0] == '0':
            string = 'O' + string[1:]
       
        match = re.search(pattern, string).group()        
        if match is not None:
            result.append(match)
    return result
