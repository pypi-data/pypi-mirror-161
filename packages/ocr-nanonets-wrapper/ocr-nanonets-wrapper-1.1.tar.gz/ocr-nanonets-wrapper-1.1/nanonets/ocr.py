import requests
import json
import textwrap
from fpdf import FPDF
import csv
import sys
import warnings
import numpy as np
import pandas as pd
import urllib.request
warnings.filterwarnings('ignore')
warnings.simplefilter(action='ignore', category=FutureWarning) 

class NANONETSOCR():
    
    def __init__(self):
        self.endpoint = "https://app.nanonets.com/api/v2/OCR/FullText"
        self.authentication = 0
        
    def set_token(self, token):
        
        payload={'urls': 'https://upload.wikimedia.org/wikipedia/commons/5/5a/Povray_hello_world.png'}
        headers = {}    
        response = requests.request("POST", url = self.endpoint, headers=headers, data=payload, auth=requests.auth.HTTPBasicAuth(token, ''))
        if response.status_code == 200:
            self.token = token
            self.authentication = 1
        if response.status_code == 401:
            print("Authentication Not Successful : Wrong API Key!\n\nGet your free API Key - \n1. Go to https://app.nanonets.com/#/signup?&utm_source=wrapper\n2. On your Nanonets account, Go to Account Info -> API Keys. Generate your free API Key and copy it\n3. Use it to authenticate this Nanonets OCR Wrapper.")
            sys.exit()
        
    def raw_prediction(self, url):
        if 'https://' in url or 'http://' in url:
            payload={'urls': url}
            headers = {}
            response = requests.request("POST", url = self.endpoint, headers=headers, data=payload, auth=requests.auth.HTTPBasicAuth(self.token, ''))
            return response.text
        else :
            files=[('file',(str(url),open(url,'rb'),'application/pdf'))]
            headers = {}
            response = requests.request("POST", url = self.endpoint, headers=headers, files=files, auth=requests.auth.HTTPBasicAuth(self.token, ''))
            return response.text
        
    def formatting(self, prediction):

        df = pd.DataFrame(prediction)
        df['vertical'] = df['ymax']
        df = df[['text','vertical']]
        df.reset_index(inplace = True)
        df['on'] = 'on'
        df = pd.merge(left = df, right = df, on = 'on', how = 'inner')
        df = df[df['index_y'] - df['index_x'] == 1]
        df['height'] = abs(df['vertical_y'] - df['vertical_x'])
        df = df[['text_x', 'text_y', 'height']]
        df = df[df['height']>20]
        #line_height = 0.8*df['height'].min()
        line_height = 0.8*df['height'].nsmallest(11).iloc[-1]

        df = pd.DataFrame(prediction)
        df['vertical'] = df['ymax']
        df = df[['text', 'xmin','xmax', 'vertical']]
        df.reset_index(inplace = True)
        df['on'] = 'on'
        df = pd.merge(left = df, right = df, on = 'on', how = 'inner')
        df = df[df['index_y'] - df['index_x'] == 1]
        df = df[df['vertical_y'] - df['vertical_x'] <= line_height]
        df['space'] = df['xmin_y'] - df['xmax_x']
        df = df[df['space'] > 10]
        #space_size = 0.8*df['space'].min()
        space_size = 0.8*df['space'].nsmallest(3).iloc[-1]

        return line_height, space_size
    
    def image_to_string(self, url, formatting = 'none', line_threshold = 'low'):
        line_height = 60
        space_size = 11
        try:
            line_height, space_size = self.formatting(json.loads(self.raw_prediction(url))['results'][0]['page_data'][0]['words'])
        except:
            pass
        
        if formatting == 'none':
            return json.loads(self.raw_prediction(url))['results'][0]['page_data'][0]['raw_text']
            
        if formatting == 'lines':
            if line_threshold == 'high':
                line_height_threshold = 5
            if line_threshold == 'low':
                line_height_threshold = line_height
            lines = []
            line = ''
            for x in json.loads(self.raw_prediction(url))['results'][0]['page_data'][0]['words']:

                if line == '':
                    line = x['text']
                    y = x['ymax']
                    prev = x['xmax']

                else:
                    if abs(x['ymax'] - y) <= line_height_threshold and x['xmax'] - prev > 0 :
                        line = line + ' ' + x['text']
                        y = x['ymax']
                        prev = x['xmax']

                    else:
                        lines.append(line)
                        line = x['text']
                        y = x['ymax']
                        prev = x['xmax']


            lines.append(line)

            result = ''
            for newline in lines : 
                if result == '':
                    result = newline
                else:
                    result = result + '\n' + newline
                    
            return result
        
        if formatting == 'lines and spaces':
            if line_threshold == 'high':
                line_height_threshold = 5
                line_height = 60
                space_size = 11
            if line_threshold == 'low':
                line_height_threshold = line_height
            lines = []
            spaces = []
            line = ''
            space = 0
            for x in json.loads(self.raw_prediction(url))['results'][0]['page_data'][0]['words']:

                if line == '':
                    line = x['text']
                    y = x['ymax']
                    y2 = x['ymin']
                    space = x['xmin']
                    spaces.append(space)
                    prev = x['xmax']

                else:
                    if abs(x['ymax'] - y) <= line_height_threshold and x['xmax'] - prev > 0 :
                        numspace = round((x['xmin']-prev)/space_size)
                        if numspace <=2:
                            numspace = 1
                        line = line + ' '*numspace + x['text']
                        y = x['ymax']
                        y2 = x['ymin']
                        prev = x['xmax']

                    else:
                        lines.append(line)
                        while x['ymax'] - y > line_height*2:
                            lines.append("")
                            spaces.append(0)
                            y = y + line_height
                        
                        line = x['text']
                        y = x['ymax']
                        y2 = x['ymin']
                        space = x['xmin']
                        spaces.append(space)
                        prev = x['xmax']


            lines.append(line)
            minspace = min(spaces)
            minspaces = []
            for el in spaces:
                el = el - minspace
                el = round(el / space_size)
                minspaces.append(el)

            result = ''
            i = 0
            for newline in lines : 
                if result == '':
                    result = ' '*minspaces[i] + newline
                    i = i + 1
                else:
                    result = result + '\n' + ' '*minspaces[i] + newline
                    i = i + 1
            
            return result

    def pdf_to_string(self, url, formatting = 'none', line_threshold = 'low'):
        if formatting == 'none':
            result = ''
            for el in json.loads(self.raw_prediction(url))['results'][0]['page_data']:
                if result == '':
                    result = el['raw_text']
                else:
                    result = result + ' ' + el['raw_text']
            return result
        
        if formatting == 'pages':
            result = []
            for el in json.loads(self.raw_prediction(url))['results'][0]['page_data']:
                result.append(el['raw_text'])
            return result
        
        if formatting == 'lines':
            pages = []
            for el in json.loads(self.raw_prediction(url))['results'][0]['page_data']:

                line_height = 60
                space_size = 11
                try:
                    line_height, space_size = self.formatting(el['words'])
                except:
                    pass
                
                if line_threshold == 'high':
                    line_height_threshold = 5
                if line_threshold == 'low':
                    line_height_threshold = line_height

                lines = []
                line = ''
                for x in el['words']:

                    if line == '':
                        line = x['text']
                        y = x['ymax']
                        prev = x['xmax']

                    else:
                        if abs(x['ymax'] - y) <= line_height_threshold and x['xmax'] - prev > 0 :
                            line = line + ' ' + x['text']
                            y = x['ymax']
                            prev = x['xmax']

                        else:
                            lines.append(line)
                            line = x['text']
                            y = x['ymax']
                            prev = x['xmax']


                lines.append(line)

                result = ''
                for newline in lines : 
                    if result == '':
                        result = newline
                    else:
                        result = result + '\n' + newline

                pages.append(result)
            return pages
        
        if formatting == 'lines and spaces' :
            pages = []
            for el in json.loads(self.raw_prediction(url))['results'][0]['page_data']:    

                line_height = 60
                space_size = 11
                try:
                    line_height, space_size = self.formatting(el['words'])
                except:
                    pass
                
                if line_threshold == 'high':
                    line_height_threshold = 5
                    line_height = 60
                    space_size = 11
                if line_threshold == 'low':
                    line_height_threshold = line_height

                lines = []
                spaces = []
                line = ''
                space = 0
                for x in el['words']:

                    if line == '':
                        line = x['text']
                        y = x['ymax']
                        y2 = x['ymin']
                        space = x['xmin']
                        spaces.append(space)
                        prev = x['xmax']
                        
                    else:
                        if abs(x['ymax'] - y) <= line_height_threshold and x['xmax'] - prev > 0 :
                            numspace = round((x['xmin']-prev)/space_size)
                            if numspace <=2:
                                numspace = 1
                            line = line + ' '*numspace + x['text']
                            y = x['ymax']
                            y2 = x['ymin']
                            prev = x['xmax']
                        else:
                            lines.append(line)
                            while x['ymax'] - y > line_height*2:
                                lines.append("")
                                spaces.append(0)
                                y = y + line_height
                            
                            line = x['text']
                            y = x['ymax']
                            y2 = x['ymin']
                            space = x['xmin']
                            spaces.append(space)
                            prev = x['xmax']

                lines.append(line)
                minspace = min(spaces)
                minspaces = []
                for el in spaces:
                    el = el - minspace
                    el = round(el / space_size)
                    minspaces.append(el)

                result = ''
                i = 0
                for newline in lines : 
                    if result == '':
                        result = ' '*minspaces[i] + newline
                        i = i + 1
                    else:
                        result = result + '\n' + ' '*minspaces[i] + newline
                        i = i + 1

                pages.append(result)
            return pages  
    
    def image_to_boxes(self, url):
        return json.loads(self.raw_prediction(url))['results'][0]['page_data'][0]['words']
    
    def pdf_to_boxes(self, url):
        pages = []
        for el in json.loads(self.raw_prediction(url))['results'][0]['page_data']:
            result = el['words']
            pages.append(result)
        return pages
    
    def extract_tables(self, file_path, download = False, output_file_name = 'did not give a filename'):
        if self.authentication==1:
            if download == False:
                url = 'https://app.nanonets.com/api/v2/OCR/Model/6aace346-9b80-4c02-8fd4-138c7575382c/LabelFile/'
                data = {'file': open(file_path, 'rb')}
                response = requests.post(url, auth=requests.auth.HTTPBasicAuth('5_no1N0KdX4Eac_e8BnxDzdsY6ycz_rk', ''), files=data)
                return response.json()['result']
            elif download == True:
                if output_file_name == 'did not give a filename':
                    output_file_name = str(file_path) + '_tables.csv'
                url = "https://customerstaging.nanonets.com/textract/csvconvert"
                payload={'conversion_type': 'table'}
                files=[('image_file',(str(file_path),open(file_path,'rb'),'application/pdf'))]
                headers = {'Authorization': 'dummy_api_key_frontend'}
                response = requests.request("POST", url, headers=headers, data=payload, files=files)
                a = response.json()
                urllib.request.urlretrieve(a['result']['url'], output_file_name)
        else :
            print("Authentication Not Successful : Wrong API Key!\n\nGet your free API Key - \n1. Go to https://app.nanonets.com/#/signup?&utm_source=wrapper\n2. On your Nanonets account, Go to Account Info -> API Keys. Generate your free API Key and copy it\n3. Use it to authenticate this Nanonets OCR Wrapper.")
            sys.exit()
            
    def convert_to_searchable_pdf(self, file_path, output_file_name = 'did not give a filename'):
        if self.authentication==1:
            if output_file_name == 'did not give a filename':
                output_file_name = str(file_path) + '_searchable.pdf'
            url = "https://customerstaging.nanonets.com/textract/csvconvert"
            payload={'conversion_type': 'searchablepdf'}
            files=[('image_file',(str(file_path),open(file_path,'rb'),'application/pdf'))]
            headers = {'Authorization': 'dummy_api_key_frontend'}
            response = requests.request("POST", url, headers=headers, data=payload, files=files)
            a = response.json()
            urllib.request.urlretrieve(a['result']['url'], output_file_name)
        else :
            print("Authentication Not Successful : Wrong API Key!\n\nGet your free API Key - \n1. Go to https://app.nanonets.com/#/signup?&utm_source=wrapper\n2. On your Nanonets account, Go to Account Info -> API Keys. Generate your free API Key and copy it\n3. Use it to authenticate this Nanonets OCR Wrapper.")
            sys.exit()

    def convert_to_prediction(self, file_path):
        return json.loads(self.raw_prediction(file_path))
    
    def convert_to_boxes(self, file_path):
        if '.pdf' in file_path:
            return self.pdf_to_boxes(file_path)
        else :
            return self.image_to_boxes(file_path)
    
    def convert_to_string(self, file_path, formatting = 'lines and spaces', line_threshold = 'low'):
        if '.pdf' in file_path:
            result = self.pdf_to_string(file_path, formatting = formatting, line_threshold = line_threshold)
            if formatting == 'none':
                return result
            else:
                string = ''
                i = 1
                for page in result:
                    string = string + "PAGE " + str(i) + '\n\n' + page + '\n\n'
                    i = i + 1
                return string
        else :
            return self.image_to_string(file_path, formatting = formatting, line_threshold = line_threshold)

    def convert_to_csv(self, file_path, output_file_name = 'did not give a filename'):
        self.extract_tables(file_path = file_path, download = True, output_file_name = output_file_name)

    def convert_to_tables(self, file_path):
        result = self.extract_tables(file_path = file_path)
        return result
    
    def convert_to_txt(self, file_path, formatting = 'lines and spaces', line_threshold = 'low', output_file_name = 'did not give a filename'):
        string = self.convert_to_string(file_path = file_path, formatting = formatting, line_threshold = line_threshold)
        if output_file_name == 'did not give a filename':
            output_file_name = str(file_path) + '_text.txt'
        textfile = open(output_file_name, 'w')
        textfile.write(string)
        textfile.close()
        