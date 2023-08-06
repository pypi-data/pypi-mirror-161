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
        
    def convert_to_prediction(self, url):
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
        
    def image_to_string(self, url, formatting = 'none', space_size = 11, line_height = 60, line_threshold = 'low'):
        if formatting == 'none':
            return json.loads(self.convert_to_prediction(url))['results'][0]['page_data'][0]['raw_text']
        if formatting == 'lines':
            if line_threshold == 'high':
                line_height_threshold = 5
            if line_threshold == 'low':
                line_height_threshold = line_height
            lines = []
            line = ''
            for x in json.loads(self.convert_to_prediction(url))['results'][0]['page_data'][0]['words']:

                if line == '':
                    line = x['text']
                    y = x['ymax']

                else:
                    if abs(x['ymax'] - y) <= line_height_threshold:
                        line = line + ' ' + x['text']
                        y = x['ymax']

                    else:
                        lines.append(line)
                        line = x['text']
                        y = x['ymax']


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
            if line_threshold == 'low':
                line_height_threshold = line_height
            lines = []
            spaces = []
            line = ''
            space = 0
            for x in json.loads(self.convert_to_prediction(url))['results'][0]['page_data'][0]['words']:

                if line == '':
                    line = x['text']
                    y = x['ymax']
                    y2 = x['ymin']
                    space = x['xmin']
                    spaces.append(space)
                    prev = x['xmax']

                else:
                    if abs(x['ymax'] - y) <= line_height_threshold:
                        line = line + ' '*round((x['xmin']-prev)/space_size) + x['text']
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

    def image_to_boxes(self, url):
        return json.loads(self.convert_to_prediction(url))['results'][0]['page_data'][0]['words']
        
    def image_to_searchablepdf(self, url, filename = 'did not give a filename', formatting = 'lines and spaces',space_size = 11, line_height = 60, line_threshold = 'low'):
        text = self.image_to_string(url, formatting = formatting, space_size = space_size, line_height = line_height, line_threshold = line_threshold)
        if filename == 'did not give a filename':
            filename = url + '.pdf'
        a4_width_mm = 600
        pt_to_mm = 0.35
        fontsize_pt = 10
        fontsize_mm = fontsize_pt * pt_to_mm
        margin_bottom_mm = 10
        character_width_mm = 7 * pt_to_mm
        width_text = a4_width_mm / character_width_mm

        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.set_auto_page_break(True, margin=margin_bottom_mm)
        pdf.add_page()
        pdf.set_font(family='Courier', size=fontsize_pt)
        splitted = text.split('\n')

        for line in splitted:
            lines = textwrap.wrap(line, width_text)

            if len(lines) == 0:
                pdf.ln()

            for wrap in lines:
                pdf.multi_cell(0, fontsize_mm, wrap)

        pdf.output(filename, 'F')
        print(filename + ' created in current directory')
        
    def image_to_csv(self, url, filename = 'did not give a filename', cell_width = 250, cell_height = 50, is_table=True):
        if is_table == False :
            lines = []
            spaces = []
            line = ''
            space = 0
            if filename == 'did not give a filename':
                filename = url + '.csv'
            for x in json.loads(self.convert_to_prediction(url))['results'][0]['page_data'][0]['words']:

                if line == '':
                    line = x['text']
                    y = x['ymax']
                    y2 = x['ymin']
                    space = x['xmin']
                    spaces.append(space)
                    cell = (x['xmin'] + x['xmax']) / cell_width

                else:
                    if abs(x['ymax'] - y) <=5:
                        if round(((x['xmin'] + x['xmax']) / cell_width) - cell) == 0 :
                            line = line + ' ' + x['text']
                        else :
                            line = line + ','*round(((x['xmin'] + x['xmax']) / cell_width) - cell) + x['text']
                        y = x['ymax']
                        y2 = x['ymin']
                        cell = (x['xmin'] + x['xmax']) / cell_width

                    else:
                        lines.append(line)
                        while x['ymax'] - y2 > cell_height:
                            lines.append(",")
                            y2 = y2 + cell_height

                        line = x['text']
                        y = x['ymax']
                        y2 = x['ymin']
                        cell = (x['xmin'] + x['xmax']) / cell_width
                        space = x['xmin']
                        spaces.append(space)

            lines.append(line)

            with open(filename, "w", newline="") as f:
                writer = csv.writer(f)
                for row in lines:
                    writer.writerow(row.split(','))

            print(filename + ' created in current directory')
        
        if is_table == True:
            if filename == 'did not give a filename':
                filename = url + '.csv'
            
            data = {'file': open(url, 'rb')}
            
            url = 'https://app.nanonets.com/api/v2/OCR/Model/6aace346-9b80-4c02-8fd4-138c7575382c/LabelFile/'
            
            response = requests.post(url, auth=requests.auth.HTTPBasicAuth('5_no1N0KdX4Eac_e8BnxDzdsY6ycz_rk', ''), files=data)
            
            i = 1
            
            if not(len(response.json()["result"]) == 1 and len(response.json()["result"][0]["prediction"]) ==1):
                with open(filename, "w") as my_empty_csv:
                    pass
                
                for page in response.json()["result"]:
                    for table in page["prediction"]:

                        maxrow = 0
                        maxcol = 0

                        for el in table['cells']:
                            maxrow = max(el['row'],maxrow)
                            maxcol = max(el['col'], maxcol)

                        df = pd.DataFrame(np.zeros([maxrow, maxcol])*np.nan)

                        for el in table['cells']:
                            row = el['row'] - 1
                            col = el['col'] - 1
                            df.iloc[row,col] = el['text']

                        number = i
                        i = i + 1
                        tablelist = ['',''],["Table "+str(number), '']
                        tablenumber = pd.DataFrame(data = tablelist)
                        tablenumber.to_csv(filename,index=False, header=False, mode='a')
                        df.to_csv(filename,index=False, header=False, mode='a')
                print(filename + ' created in current directory')
                
            else:
                
                table = response.json()["result"][0]["prediction"][0]
                maxrow = 0
                maxcol = 0

                for el in table['cells']:
                    maxrow = max(el['row'],maxrow)
                    maxcol = max(el['col'], maxcol)

                df = pd.DataFrame(np.zeros([maxrow, maxcol])*np.nan)

                for el in table['cells']:
                    row = el['row'] - 1
                    col = el['col'] - 1
                    df.iloc[row,col] = el['text']

                df.to_csv(filename,index=False, header=False)
                print(filename + ' created in current directory')
            
    def pdf_to_string(self, url, formatting = 'none', space_size = 11, line_height = 50, line_threshold = 'low'):
        if formatting == 'none':
            result = ''
            for el in json.loads(self.convert_to_prediction(url))['results'][0]['page_data']:
                if result == '':
                    result = el['raw_text']
                else:
                    result = result + ' ' + el['raw_text']
            return result
        
        if formatting == 'pages':
            result = []
            for el in json.loads(self.convert_to_prediction(url))['results'][0]['page_data']:
                result.append(el['raw_text'])
            return result
        
        if formatting == 'lines':
            if line_threshold == 'high':
                line_height_threshold = 5
            if line_threshold == 'low':
                line_height_threshold = line_height
            pages = []
            for el in json.loads(self.convert_to_prediction(url))['results'][0]['page_data']:    
                lines = []
                line = ''
                for x in el['words']:

                    if line == '':
                        line = x['text']
                        y = x['ymax']

                    else:
                        if abs(x['ymax'] - y) <= line_height_threshold:
                            line = line + ' ' + x['text']
                            y = x['ymax']

                        else:
                            lines.append(line)
                            line = x['text']
                            y = x['ymax']


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
            if line_threshold == 'high':
                line_height_threshold = 5
            if line_threshold == 'low':
                line_height_threshold = line_height
            pages = []
            for el in json.loads(self.convert_to_prediction(url))['results'][0]['page_data']:    
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
                        if abs(x['ymax'] - y) <= line_height_threshold:
                            line = line + ' '*round((x['xmin']-prev)/space_size) + x['text']
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
    
    def pdf_to_boxes(self, url):
        pages = []
        for el in json.loads(self.convert_to_prediction(url))['results'][0]['page_data']:
            result = el['words']
            pages.append(result)
        return pages
    
    def pdf_to_searchablepdf(self, url, filename = 'did not give a filename', formatting = 'lines and spaces',space_size = 11, line_height = 50, line_threshold = 'low'):
        texts = self.pdf_to_string(url, formatting = formatting, space_size = space_size, line_height = line_height, line_threshold = line_threshold)
        if filename == 'did not give a filename':
            filename = url + '.pdf'
        a4_width_mm = 600
        pt_to_mm = 0.35
        fontsize_pt = 10
        fontsize_mm = fontsize_pt * pt_to_mm
        margin_bottom_mm = 10
        character_width_mm = 7 * pt_to_mm
        width_text = a4_width_mm / character_width_mm

        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.set_auto_page_break(False, margin=margin_bottom_mm)
        pdf.set_font(family='Courier', size=fontsize_pt)
        
        text = 'this is starting point'
        for text in texts:
            
            pdf.add_page()
            splitted = text.split('\n')

            for line in splitted:
                lines = textwrap.wrap(line, width_text)

                if len(lines) == 0:
                    pdf.ln()

                for wrap in lines:
                    pdf.multi_cell(0, fontsize_mm, wrap)

        pdf.output(filename, 'F')
        print(filename + ' created in current directory')
                
    def pdf_to_csv(self, url, filename = 'did not give a filename', cell_width = 750, cell_height = 150, is_table = True):
        if is_table==False:
            pages = []
            if filename == 'did not give a filename':
                filename = url + '.csv'
            for el in json.loads(self.convert_to_prediction(url))['results'][0]['page_data']:    

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
                        cell = (x['xmin'] + x['xmax']) / cell_width

                    else:
                        if abs(x['ymax'] - y) <=5:
                            if round(((x['xmin'] + x['xmax']) / cell_width) - cell) == 0 :
                                line = line + ' ' + x['text']
                            else :
                                line = line + ','*round(((x['xmin'] + x['xmax']) / cell_width) - cell) + x['text']
                            y = x['ymax']
                            y2 = x['ymin']
                            cell = (x['xmin'] + x['xmax']) / cell_width

                        else:
                            lines.append(line)
                            while x['ymax'] - y2 > cell_height:
                                lines.append(",")
                                y2 = y2 + cell_height

                            line = x['text']
                            y = x['ymax']
                            y2 = x['ymin']
                            cell = (x['xmin'] + x['xmax']) / cell_width
                            space = x['xmin']
                            spaces.append(space)

                lines.append(line)
                pages.append(lines)

            with open(filename, "w", newline="") as f:
                writer = csv.writer(f)
                for page in pages:
                    for row in page:
                        writer.writerow(row.split(','))
                    writer.writerow([""])

            print(filename + ' created in current directory')
        
        if is_table == True:
            
            if filename == 'did not give a filename':
                filename = url + '.csv'
            
            data = {'file': open(url, 'rb')}
            
            url = 'https://app.nanonets.com/api/v2/OCR/Model/6aace346-9b80-4c02-8fd4-138c7575382c/LabelFile/'
            
            response = requests.post(url, auth=requests.auth.HTTPBasicAuth('5_no1N0KdX4Eac_e8BnxDzdsY6ycz_rk', ''), files=data)
            
            i = 1
            
            if not(len(response.json()["result"]) == 1 and len(response.json()["result"][0]["prediction"]) ==1):
                with open(filename, "w") as my_empty_csv:
                    pass
                
                for page in response.json()["result"]:
                    for table in page["prediction"]:

                        maxrow = 0
                        maxcol = 0

                        for el in table['cells']:
                            maxrow = max(el['row'],maxrow)
                            maxcol = max(el['col'], maxcol)

                        df = pd.DataFrame(np.zeros([maxrow, maxcol])*np.nan)

                        for el in table['cells']:
                            row = el['row'] - 1
                            col = el['col'] - 1
                            df.iloc[row,col] = el['text']

                        number = i
                        i = i + 1
                        tablelist = ['',''],["Table "+str(number), '']
                        tablenumber = pd.DataFrame(data = tablelist)
                        tablenumber.to_csv(filename,index=False, header=False, mode='a')
                        df.to_csv(filename,index=False, header=False, mode='a')
                print(filename + ' created in current directory')
                
            else:
                
                table = response.json()["result"][0]["prediction"][0]
                maxrow = 0
                maxcol = 0

                for el in table['cells']:
                    maxrow = max(el['row'],maxrow)
                    maxcol = max(el['col'], maxcol)

                df = pd.DataFrame(np.zeros([maxrow, maxcol])*np.nan)

                for el in table['cells']:
                    row = el['row'] - 1
                    col = el['col'] - 1
                    df.iloc[row,col] = el['text']

                df.to_csv(filename,index=False, header=False)
                print(filename + ' created in current directory')
    
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
            
    def searchable_pdf(self, file_path, output_file_name = 'did not give a filename'):
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

    def convert_to_string(self, file_path, formatting = 'none', line_threshold = 'low'):
        if '.pdf' in file_path:
            self.pdf_to_string(file_path, formatting = formatting, line_threshold = line_threshold)
        else :
            self.image_to_string(file_path, formatting = formatting, line_threshold = line_threshold)