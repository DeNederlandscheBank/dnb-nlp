from html.parser import HTMLParser
import pandas as pd
from os import listdir, walk
from os.path import isfile, join
import sklearn
import sklearn.ensemble
import numpy
import ast
import regex as re
 
def doc2dataframe(file, data, df=None):
    """
    Convert pdf document to dataframe (each sentence separately)
    """
    codec = 'utf-8'
    print(file)
    if file[-3:].lower()=='pdf':
        try:
            with open(file, 'rb') as in_file:
                parser = PDFParser(in_file)
                doc = PDFDocument(parser)
 
                pages_txt = []
                for page_idx, page in enumerate(PDFPage.create_pages(doc)):
                    output_string = StringIO()
                    rsrcmgr = PDFResourceManager()
                    device = TextConverter(rsrcmgr, output_string, codec = codec, laparams = LAParams())
                    interpreter = PDFPageInterpreter(rsrcmgr, device)
                    interpreter.process_page(page)
                    text = output_string.getvalue()
                    device.close()
                    output_string.close()
                    pages_txt.append(text)
 
                html_pages = []
                pagenos = set()
                for page in PDFPage.get_pages(in_file, pagenos, maxpages=0, caching=True, check_extractable=True):
                    rsrcmgr = PDFResourceManager()
                    output_string = BytesIO()
                    device = HTMLConverter(rsrcmgr, output_string, codec = codec, laparams = LAParams(), showpageno=False)
                    interpreter = PDFPageInterpreter(rsrcmgr, device)
                    interpreter.process_page(page)
                    html = output_string.getvalue()
                    html_pages.append(html)
 
                html_pages = [pdfparser.html2lines(page) for page in html_pages]
                html_pages = pdfparser.tag_page_headers(html_pages)
                html_pages = pdfparser.tag_page_footers(html_pages)

                annotations = [[line[0] for line in page] for page in html_pages]
                html_text = [[line[1] for line in page] for page in html_pages]
                html_tags = [[line[2] for line in page] for page in html_pages]
 
                if len(pages_txt)==len(html_pages):
                    for idx, page in enumerate(pages_txt):
                        df = df.append(pd.DataFrame(columns = ['dc:source', 'dc:format', 'dc:language', 'dc:type', 'dc:coverage', 'dc:publisher', 'page', 'text', 'html_text', 'html_tags', 'annotations'],
                                                    data = [data + [idx, pages_txt[idx], html_text[idx], html_tags[idx], annotations[idx]]]), ignore_index=True)
                else:
                    print("unequal number of pages in txt and html")
        except:
            print("Error parsing: " + str(file))
            df = df.append(pd.DataFrame(columns = ['dc:source', 'dc:format', 'dc:language', 'dc:type', 'dc:coverage', 'dc:publisher', 'page', 'text', 'html_text', 'html_tags', 'annotations'],
                                        data = [data + [0, 'no text', 'no text', '', '']]), ignore_index=True)
    return df

class PDF2HTMLParser(HTMLParser):
    '''
    Simple parser PDF to HTML
    '''
   
    def __init__(self, *args, **kwargs):
        HTMLParser.__init__(self)
        self.text = list()
        self.current_attributes = ''
        self.current_tags = []
    
    def handle_starttag(self, tag, attrs):
        # attributes
        if attrs!=[]: # if empty then keep last attributes
            self.current_attributes = attrs[0]
        # tags (not used yet)
        if tag!='br': # ignore br tags
            self.current_tags.append(tag)
 
    def handle_endtag(self, tag):
        # tags (not used yet)
        self.current_tags.remove(tag)
 
    def handle_data(self, data):
        self.text.append((data, self.current_attributes))
       
def html2lines(html_page):
    '''
    Convert html (one page) to text and tags
    '''
   
    parser = PDF2HTMLParser()
    parser.feed(html_page.decode('utf-8'))
   
    # construct lines from html with attributes
    html_line = ''
    html_attr = set()
 
    html_lines = []
   
    for text_block in parser.text:
        html_line += text_block[0]
        html_attr.add(text_block[1])
        if "\n" in text_block[0]:
            # the initial category is None
            html_lines.append((None, html_line, html_attr))
            html_line = ''
            html_attr = set()
   
    return html_lines
 
def remove_digits(s):
    return ''.join([i for i in s if not i.isdigit()])
 
def remove_block(previous_page, page, reverse):
    cleaned = []
    block = True
    block_text_lines = 0
   
    previous_text = [remove_digits(line[1]) for line in previous_page]
 
    if reverse:
        lines = page[::-1]
    else:
        lines = page
       
    for idx, line in enumerate(lines):
        if len(lines[idx][1].strip())!=0: # line contains text
            p1 = remove_digits(lines[idx][1])
            # we have a header/footer text if text in previous page and not a table content
            if (p1 in previous_text) and ("position:absolute" not in str(lines[idx][2])):
                block_text_lines += 1
                if not reverse:
                    block_type = 2 # header text
                else:
                    block_type = 3 # footer text
            else:
                block = False
        else:
            if not reverse:
                block_type = 0 # header spaces
            else:
                block_type = 1 # footer spaces
        if block==True:
            cleaned.append([block_type, line[1], line[2]])
        else:
            cleaned.append(line)
 
    if reverse:
        cleaned = cleaned[::-1]
   
    return cleaned
 
def tag_page_headers(pages):
 
    pages = [remove_block(pages[idx-1] if idx > 0 else [],
                     page, True) for idx, page in enumerate(pages)]
    pages = [remove_block(pages[idx-1] if idx > 0 else [],
                     page, False) for idx, page in enumerate(pages)]
    return pages
 
def tag_page_footers(pages):
    return tag_page_headers(pages[::-1])[::-1]
 
def get_feature_vector(line_to_process, prefix):
    '''
    Create feature list from line_to_process (a tuple (text, attributes))
    '''
 
    line = line_to_process[0]
    attr = line_to_process[1]
 
    feature_vector = {}
 
    # general features
    feature_vector[prefix+"line_len"] = len(line)
    feature_vector[prefix+"line_len_strip"] = len(line.strip())
    feature_vector[prefix+"line_len_lowercase"] = len([char for char in line if char==char.lower()])
    feature_vector[prefix+"line_len_uppercase"] = len([char for char in line if char==char.upper()])
 
    feature_vector[prefix+"#alfa"] = len(re.findall("[A-Za-z]", line))
    feature_vector[prefix+"#alfa_upper"] = len(re.findall("[A-Z]", line))
    feature_vector[prefix+"#alfa_lower"] = len(re.findall("[a-z]", line))
    feature_vector[prefix+"#number"] = len(re.findall("[0-9]", line))
    feature_vector[prefix+"#whitespace"] = len([char for char in line if char in [' ']])
    feature_vector[prefix+"#punct"] = len([char for char in line if char in ['()[],.<>']])
    feature_vector[prefix+"#tab"] = len([char for char in line if char=='\t'])
    feature_vector[prefix+"#endline"] = len([char for char in line if char=='\n'])
 
    # sentence characteristics
    if len(line)>0:
        feature_vector[prefix+"starts_with_uppercase"] = line[0]==line[0].upper()
        feature_vector[prefix+"ends_with_point"] = line[-1]=='.'
    else:
        feature_vector[prefix+"starts_with_uppercase"] = False
        feature_vector[prefix+"ends_with_point"] = False
    feature_vector[prefix+"len_points"] = len([char for char in line if char=='.'])
 
    # header characteristics
    feature_vector[prefix+"#par refs"] = len(re.findall("[\\d.\\d?]+", line))
    feature_vector[prefix+"#par refs with start in uppercase"] = len(re.findall("[\\d.\\d?]+\\s*[A-Z]", line))
 
    # features from html attributes
    feature_vector[prefix+'position_absolute'] = 'position:absolute' in str(attr).lower()
    feature_vector[prefix+'bold'] = 'bold' in str(attr).lower()
    feature_vector[prefix+'italic'] = 'italic' in str(attr).lower()
    font_size = re.search('font-size:(\\d*)px', str(attr))
    if font_size:
        feature_vector[prefix+'font_size'] = int(font_size[1])
    else:
        feature_vector[prefix+'font_size'] = 0
 
    return feature_vector
 
def build_line_features(previous_line, current_line, next_line):
    """
    Build a feature vector for previous_line, current_line and next_line
 
    """
    features_previous_line = get_feature_vector(previous_line, "previous_line_")
    features_current_line = get_feature_vector(current_line, "current_line_")
    features_next_line = get_feature_vector(next_line, "next_line_")
 
    feature_vector =  {**features_previous_line, **features_current_line, **features_next_line}
   
    return feature_vector
 
def generate_line_features(page, df_features):
    """
    Build a feature vector for a given page.
 
    """
    for idx, line in enumerate(page):
        previous_line = page[idx-1] if idx==0 else ('', '') 
        next_line = page[idx] if idx==len(page) else ('', '')
        current_line = page[idx]
        features = build_line_features(previous_line, current_line, next_line)
        df_features = df_features.append([features], ignore_index = True)
   
    return df_features
 

