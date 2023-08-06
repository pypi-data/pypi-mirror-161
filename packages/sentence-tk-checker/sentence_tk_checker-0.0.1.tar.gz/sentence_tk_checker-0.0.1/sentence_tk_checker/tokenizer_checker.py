'''
Copyright 2022 Rairye
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    https://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import warnings
import string

def norm_spaces(line):
    result = ""

    i = 0
    j = 0

    last_type = None

    while j < len(line):
        current_char = line[j]

        if not current_char.isspace():
            last_type = "NOTSPACE"
            j+=1
        else:
            if last_type == "SPACE":
                ss = line[i:j]
                if not ss.isspace():
                    result +=(ss + " ")
                
            else:
                result += (line[i:j] + " ")

            last_type = "SPACE"

            i= j+1
            j = i+1

    result += line[i:j]

    return result


class checker():

    def __init__(self):
        self.__caller = None
        self.detect_novel_abbr = True
        self.__abbre_set = set(["co.", "ltd.", "inc.", "oo.", "jan.", "feb.", "mar.", "apr.", "jun.", "jul.", "aug", "sept.", "oct", "nov.", "dec.", "mt.", "st.", 
                 "etc.", "e.g.", "a.m.", "p.m.", "jr.", "i.e.", "misc.", "i.e.", "fig.", "illus.", "no.", "sr.", "assoc.", "bros.", "corp.", "mtg."])
        self.__title_set = set(["mr.", "ms.", "mrs.", "dir." "dr.", "ald.", "atty.", "gen.", "insp.", "prof.", "gov.", "pres.", "supt.", "sr.", "fr.", "messrs.", "lt.", "capt.", "col.", "cdr.",
                 "sgt.", "maj."])
        self.__abc_set = set(list(string.ascii_lowercase))
        self.__vowel_set = set(["a", "e", "i", "o", "u"])
        self.__punctuation_set = set(list(string.punctuation))
        self.__end_punctuation_set = set([".", "?", "!"])

    def reset_abc_set(self):
        self.__abc_set = set(list(string.ascii_lowercase))

    def reset_vowel_set(self):
        self.__vowel_set = set(["a", "e", "i", "o", "u"])

    def reset_punctuation_set(self):
        self.__punctuation_set = set(list(string.punctuation))

    def reset_end_punctuation_set(self):
        self.__end_punctuation_set = set([".", "?", "!"])

    def add_to_abc_set(self, char):
        if type(char) is str and len(char) == 1:
            self.__abc_set.add(char.lower())
            return True

        return False

    def add_to_vowel_set(self, char):
        if type(char) is str and len(char) == 1:
            self.__vowel_set.add(char.lower())
            return True

        return False

    def add_to_punctuation_set(self, char):
        if type(char) is str and len(char) == 1:
            self.__punctuation_set.add(char)
            return True

        return False

    def add_to_end_punctuation_set(self, char):
        if type(char) is str and len(char) == 1:
            self.__end_punctuation_set.add(char)
            return True

        return False
    

    def set_function(self, function):
        
        if callable(function):
            self.__caller = function
        else:
            warnings.warn("Invalid argument. The argument should be a function", Warning)

    def set_detect_novel_abbr(self, value):
        
        if type(value) is bool:
            self.detect_novel_abbr = value
            return True

        return False
            

    def is_novel_abbreviation(self, word):

        if self.detect_novel_abb == False:
            return False
                    
        if word[0].isnumeric():
            return False

        if not word.isalpha():
            return False

        for char in word:
            lowered = char.lower()
            if not (lowered in self.__abc_set or lowered in self.__vowel_set):
                return False            
                
        length = len(word) -1
        periods = 0
        vowels = 0
        i = 0
        
        for i in range(length):
            current_char = word[i].lower()
            if current_char == "." and i > length:
                periods+=1
            if current_char in vowel_set:
                vowels +=1

        if vowels == 0:
            return True
        if periods == len(word):
            return True
        if periods == vowels:
            return True
        
        return False

    def add_abbre(self, word):
        if type(word) is str:
            word = word.lower()

            if not word.endswith("."):
                word = word + "."
            
            self.__abbre_set.add(word)
            return True

        return False

    def add_title(self, word):
        if type(word) is str:
            word = word.lower()

            if not word.endswith("."):
                word = word + "."

            self.__title_set.add(word)
            return True

        return False

    def delete_abbre(self, word):
        word = word.lower()

        if not word.endswith("."):
            word = word + "."
        
        if type(word) is str and word in self.__abbre_set:
            self.__abbre_set.remove(word)
            return True

        return False

    def delete_title(self, word):
        word = word.lower()

        if not word.endswith("."):
            word = word + "."
        
        if type(word) is str and word in self.__title_set:
            self.__title_set.remove(word)
            return True

        return False

    def get_abbre_set(self):
        return self.__abbre_set

    def get_title_set(self):
        return self.__title_set

    def get_abc_set(self):
        return self.__abc_set

    def get_vowel_set(self):
        return self.__vowel_set

    def get_punctuation_set(self):
        return self.__punctuation_set

    def get_end_punctuation_set(self):
        return self.__end_punctuation_set

    def is_valid_start(self, char):
        return (char.isalpha() or char in self.__punctuation_set)
            
    def is_single_word_sentence(self, sentence):
        if len(sentence) == 0:
            return True

        if sentence[0] in self.__punctuation_set and sentence[-1] in self.__punctuation_set:
            return False
        
        i = 0
        current_char = sentence[i]
        if current_char.islower() or current_char.isalpha():
            return False
        else:
            i+=1
            while i <= len(sentence) -1:
                current_char = sentence[i]
                if current_char not in self.__end_punctuation_set and current_char.isalpha():
                    if current_char.isupper():
                        return False
                i+=1

            return True

    def join_sentences(self, sentences, normalize_spaces = True):

        if type(sentences) != list:
            warnings.warn("Invalid argument. Must be passed as a list.", Warning)
            return []
        
        if len(sentences) == 1:
            return sentences
        
        results = []
        intermediate_result = ""
        last_word = ""
        i = 0
        length = len(sentences)
        last_length = 0
        
        while i <= length - 1:
            if i == length -1:
                if intermediate_result != "":
                    results.append(intermediate_result)
                    intermediate_result = ""
                results.append(sentences[-1])
                break

            first_strip = sentences[i].strip()
            second_strip = sentences[i+1].strip()
            first = norm_spaces(first_strip) if normalize_spaces == True else first_strip
            second = norm_spaces(second_strip) if normalize_spaces == True else second_strip

            if len(first) == 0:
                i+=1
                continue
                
            first_len_one = True if (first.find(" ") == -1 and len(first) > 0) else False
            second_len_one = True if (second.find(" ") == -1 and len(second) > 0 ) else False
            first_single_word_sentence = False if first_len_one == False else self.is_single_word_sentence(first)
            second_single_word_sentence = False if second_len_one == False else self.is_single_word_sentence(second)
        
            if first_single_word_sentence == True and second_single_word_sentence == True:
                if intermediate_result != "":
                    results.append(intermediate_result)
                    intermediate_result == ""
                if i == (length - 2):
                    results.append(first + " " + second)
                else:
                    results.append(first)
                    results.append(second)
                i+=2
                continue

            if first_single_word_sentence == True:
                
                if not (last_word.lower() in self.__abbre_set or (second[i].islower() and self.is_novel_abbreviation(last_word)) or (last_word.lower() in self.__title_set and second[i].isupper())):
      
                    if intermediate_result == "":
                        results.append(first + " " + second)
                        i+=2
                    else:
                        intermediate_result += (" " + first)
                        i+=1
                    continue

            if second_single_word_sentence == True:
                if intermediate_result == "":
                    results.append(first)
                else:
                    results.append(intermediate_result)
                    intermediate_result == ""
                i+=1
                continue

            if second_len_one == True and second_single_word_sentence == False:
                if intermediate_result != "":
                    results.append(intermediate_result)
                    results.append(first)
                    intermediate_result = ""
                    
                else:
                    results.append(first)
            
                i+=1
                continue


            if len(second) == 0:
                if intermediate_result != "":
                    results.append(intermediate_result)
                                
                results.append(first)
                intermediate_result = "" 
            
                i+=2
                continue
                
            if (not self.is_valid_start(second[0].lower()) and intermediate_result == "") or second[0].islower():
                intermediate_result = first + " " + second
                i+=2

            elif (first[0].islower() or not self.is_valid_start(first[0].lower())) and intermediate_result != "":
                intermediate_result += (" " + first)
                i+=1
            else:
                if intermediate_result != "" and second_len_one == False:
                    start_index = intermediate_result.rfind(" ", 0, len(intermediate_result) - 1)
                    last_word = intermediate_result[start_index if start_index != -1 else 0:]
                    if (last_word.lower() in self.__abbre_set or (second[0].islower() and self.is_novel_abbreviation(last_word)) or (last_word.lower() in self.__title_set and second[0].isupper())):
                        intermediate_result += (" " + first)
                        i+=1
                        continue
                
                start_index = first.rfind(" ", 0, len(first) - 1)
                last_word = first[start_index if start_index != -1 else 0:]
                if (last_word.lower() in self.__abbre_set or (second[0].islower() and self.is_novel_abbreviation(last_word)) or (last_word.lower() in self.__title_set and second[0].isupper())) :
                    intermediate_result += (" " + first + " " + second)
                    i+=2
                    continue

                if intermediate_result != "":
                    results.append(intermediate_result)
                results.append(first)
                intermediate_result = ""
                i+=1
                
        if intermediate_result != "":
            results.append(intermediate_result)
        results = [result.strip() for result in results if len(result) > 0 and not result.isspace()]
        
        return results


    def tokenize(self, line):

        if type(line) != str:
            warnings.warn("Invalid argument. Should be a str.", Warning)
            return []

        if self.__caller == None:
            warnings.warn("The function has not been defined. Please define it using set_function(). Or, try passing a list of str data to join_sentences() directly.", Warning)
            return []

        line = norm_spaces(line.strip())

        splits = self.__caller(line)
        splits = [split for split in splits if len(split) > 0 and not split.isspace()]
        splits = self.join_sentences(splits, False)

        return splits
    
