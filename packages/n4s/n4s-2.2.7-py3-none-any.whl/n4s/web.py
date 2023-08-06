import os, shutil, re, base64, warnings, webbrowser, requests
import http.client as httplib
from n4s import fs, strgs
from bs4 import BeautifulSoup
from pathlib import Path
##### Dismiss the 'XML' warning
warnings.filterwarnings("ignore", 
category=UserWarning, module='bs4')
#############################


## CREATE WEB FILES
def build_html(Design: str='default', onefile: bool=False, Directory: Path=fs.root('desktop'), debug: bool=False):
        
        ## DIRECTORIES
        index_dir = f"{Directory}/index"
        assets_dir = f"{index_dir}/assets"
        css_dir = f"{assets_dir}/css"
        js_dir = f"{assets_dir}/js"

        ## FILES
        html_file = f"{index_dir}/index.html"
        css_file = f"{css_dir}/style.css"
        js_file = f"{js_dir}/script.js"
        
        Design = Design.lower()
        ###### TEMPLATES #############
        ## DEFAULT                   #
        if Design == 'default':      
            ## HTML - DEFAULT TEMPALTE
            html_string = '''
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <title>Document</title>
        <link rel="stylesheet" type="text/css" href="assets/css/style.css"/>
    </head>
    <body>

    </body>
    <script src="assets/js/script.js"></script>
</html>
'''

            ## CSS - DEFAULT TEMPLATE
            css_string = '''
/*! normalize.css v8.0.1 | MIT License | github.com/necolas/normalize.css */

/* Document
   ========================================================================== */

/**
 * 1. Correct the line height in all browsers.
 * 2. Prevent adjustments of font size after orientation changes in iOS.
 */

html {
  line-height: 1.15; /* 1 */
  font-size: 62.5%;
  -webkit-text-size-adjust: 100%; /* 2 */
}

/* Sections
   ========================================================================== */

/**
 * Remove the margin in all browsers.
 */

body {
  margin: 0;
  font-size: 1.6rem;
}

/**
 * Render the `main` element consistently in IE.
 */

main {
  display: block;
}

/**
 * Correct the font size and margin on `h1` elements within `section` and
 * `article` contexts in Chrome, Firefox, and Safari.
 */

h1 {
  font-size: 2em;
  margin: 0.67em 0;
}

/* Grouping content
   ========================================================================== */

/**
 * 1. Add the correct box sizing in Firefox.
 * 2. Show the overflow in Edge and IE.
 */

hr {
  box-sizing: content-box; /* 1 */
  height: 0; /* 1 */
  overflow: visible; /* 2 */
}

/**
 * 1. Correct the inheritance and scaling of font size in all browsers.
 * 2. Correct the odd `em` font sizing in all browsers.
 */

pre {
  font-family: monospace, monospace; /* 1 */
  font-size: 1em; /* 2 */
}

/* Text-level semantics
   ========================================================================== */

/**
 * Remove the gray background on active links in IE 10.
 */

a {
  background-color: transparent;
}

/**
 * 1. Remove the bottom border in Chrome 57-
 * 2. Add the correct text decoration in Chrome, Edge, IE, Opera, and Safari.
 */

abbr[title] {
  border-bottom: none; /* 1 */
  text-decoration: underline; /* 2 */
  text-decoration: underline dotted; /* 2 */
}

/**
 * Add the correct font weight in Chrome, Edge, and Safari.
 */

b,
strong {
  font-weight: bolder;
}

/**
 * 1. Correct the inheritance and scaling of font size in all browsers.
 * 2. Correct the odd `em` font sizing in all browsers.
 */

code,
kbd,
samp {
  font-family: monospace, monospace; /* 1 */
  font-size: 1em; /* 2 */
}

/**
 * Add the correct font size in all browsers.
 */

small {
  font-size: 80%;
}

/**
 * Prevent `sub` and `sup` elements from affecting the line height in
 * all browsers.
 */

sub,
sup {
  font-size: 75%;
  line-height: 0;
  position: relative;
  vertical-align: baseline;
}

sub {
  bottom: -0.25em;
}

sup {
  top: -0.5em;
}

/* Embedded content
   ========================================================================== */

/**
 * Remove the border on images inside links in IE 10.
 */

img {
  border-style: none;
}

/* Forms
   ========================================================================== */

/**
 * 1. Change the font styles in all browsers.
 * 2. Remove the margin in Firefox and Safari.
 */

button,
input,
optgroup,
select,
textarea {
  font-family: inherit; /* 1 */
  font-size: 100%; /* 1 */
  line-height: 1.15; /* 1 */
  margin: 0; /* 2 */
}

/**
 * Show the overflow in IE.
 * 1. Show the overflow in Edge.
 */

button,
input { /* 1 */
  overflow: visible;
}

/**
 * Remove the inheritance of text transform in Edge, Firefox, and IE.
 * 1. Remove the inheritance of text transform in Firefox.
 */

button,
select { /* 1 */
  text-transform: none;
}

/**
 * Correct the inability to style clickable types in iOS and Safari.
 */

button,
[type="button"],
[type="reset"],
[type="submit"] {
  -webkit-appearance: button;
}

/**
 * Remove the inner border and padding in Firefox.
 */

button::-moz-focus-inner,
[type="button"]::-moz-focus-inner,
[type="reset"]::-moz-focus-inner,
[type="submit"]::-moz-focus-inner {
  border-style: none;
  padding: 0;
}

/**
 * Restore the focus styles unset by the previous rule.
 */

button:-moz-focusring,
[type="button"]:-moz-focusring,
[type="reset"]:-moz-focusring,
[type="submit"]:-moz-focusring {
  outline: 1px dotted ButtonText;
}

/**
 * Correct the padding in Firefox.
 */

fieldset {
  padding: 0.35em 0.75em 0.625em;
}

/**
 * 1. Correct the text wrapping in Edge and IE.
 * 2. Correct the color inheritance from `fieldset` elements in IE.
 * 3. Remove the padding so developers are not caught out when they zero out
 *    `fieldset` elements in all browsers.
 */

legend {
  box-sizing: border-box; /* 1 */
  color: inherit; /* 2 */
  display: table; /* 1 */
  max-width: 100%; /* 1 */
  padding: 0; /* 3 */
  white-space: normal; /* 1 */
}

/**
 * Add the correct vertical alignment in Chrome, Firefox, and Opera.
 */

progress {
  vertical-align: baseline;
}

/**
 * Remove the default vertical scrollbar in IE 10+.
 */

textarea {
  overflow: auto;
}

/**
 * 1. Add the correct box sizing in IE 10.
 * 2. Remove the padding in IE 10.
 */

[type="checkbox"],
[type="radio"] {
  box-sizing: border-box; /* 1 */
  padding: 0; /* 2 */
}

/**
 * Correct the cursor style of increment and decrement buttons in Chrome.
 */

[type="number"]::-webkit-inner-spin-button,
[type="number"]::-webkit-outer-spin-button {
  height: auto;
}

/**
 * 1. Correct the odd appearance in Chrome and Safari.
 * 2. Correct the outline style in Safari.
 */

[type="search"] {
  -webkit-appearance: textfield; /* 1 */
  outline-offset: -2px; /* 2 */
}

/**
 * Remove the inner padding in Chrome and Safari on macOS.
 */

[type="search"]::-webkit-search-decoration {
  -webkit-appearance: none;
}

/**
 * 1. Correct the inability to style clickable types in iOS and Safari.
 * 2. Change font properties to `inherit` in Safari.
 */

::-webkit-file-upload-button {
  -webkit-appearance: button; /* 1 */
  font: inherit; /* 2 */
}

/* Interactive
   ========================================================================== */

/*
 * Add the correct display in Edge, IE 10+, and Firefox.
 */

details {
  display: block;
}

/*
 * Add the correct display in all browsers.
 */

summary {
  display: list-item;
}

/* Misc
   ========================================================================== */

/**
 * Add the correct display in IE 10+.
 */

template {
  display: none;
}

/**
 * Add the correct display in IE 10.
 */

[hidden] {
  display: none;
}

'''

            ## JS - DEFAULT TEMPLATE
            js_string = '''
console.log(`%cCreated using n4s, by: \nhttps://www.mafshari.work`, 'color:lightgreen;');
'''
        ## IFRAME                    #
        if Design == 'iframe':    
          ## HTML - IFRAME
          html_string = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" type="text/css" href="assets/css/style.css"/>
    <title>Document</title>
</head>
<body>
    <iframe src="https://www.mafshari.work/websites/simplicity" frameborder="0" 
    marginheight="0" 
    marginwidth="0" 
    width="100%" 
    height="100%" 
    scrolling="auto"></iframe>
</body>
</html>
'''
          
          ## CSS - IFRAME
          css_string = '''
html 
{
 overflow: auto;
}
 
html, body, div, iframe 
{
 margin: 0px; 
 padding: 0px; 
 height: 100%; 
 border: none;
}
iframe 
{
 display: block; 
 width: 100%; 
 border: none; 
 overflow-y: auto; 
 overflow-x: hidden;
}
'''
          
          ## JS - IFRAME
          js_string = '''
console.log(`%cCreated using n4s, by: \nhttps://www.mafshari.work`, 'color:lightgreen;');
'''
        ## APPLE - PODCAST REPORT    #
        if Design == 'applepodcastreport' or Design == 'apr':
          print('\nDownloading Apple Podcast Report...')
          return webbrowser.get().open("https://drive.google.com/u/1/uc?id=1j94f4z5vnqBTEc9S-yOOPjIiIkowOPqH&export=download", new=1, autoraise=True)
        ## BARCODE GENERATOR
        if Design == 'barcodegenerator' or Design == 'barcode':
        ## HTML - IFRAME
          html_string = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" type="text/css" href="assets/css/style.css"/>
    <title>N4S - Barcode Generator</title>
</head>
<body>
    <iframe src="https://barcode-maker.netlify.app/generator/" frameborder="0" 
    marginheight="0" 
    marginwidth="0" 
    width="100%" 
    height="100%" 
    scrolling="auto"></iframe>
</body>
</html>
'''
          
          ## CSS - IFRAME
          css_string = '''
html 
{
 overflow: auto;
}
 
html, body, div, iframe 
{
 margin: 0px; 
 padding: 0px; 
 height: 100%; 
 border: none;
}
iframe 
{
 display: block; 
 width: 100%; 
 border: none; 
 overflow-y: auto; 
 overflow-x: hidden;
}
'''
          
          ## JS - IFRAME
          js_string = '''
console.log(`%cCreated using n4s, by: \nhttps://www.mafshari.work`, 'color:lightgreen;');
'''
        ## BARCODE GENERATOR - DOWNLOAD
        if Design == 'barcodegenerator-dl' or Design == 'barcode-dl':
          print('\nDownloading Barcode Generator...')
          url = "https://drive.google.com/uc?export=download&id=1QQqCM0OdD1GhuIKv7lsxVa7ItBsj3VE8"
          r = requests.get(url, allow_redirects=True)
          open(f"{Directory}/barcode_generator.zip", 'wb').write(r.content)
          return print(f'Done: {Directory}/barcode_generator.zip')
        ##############################

        ## CREATE DIRECTORIES AND FILES
        fs.path_exists([index_dir, assets_dir,
            css_dir,
            js_dir,
            html_file,
            css_file,
            js_file
        ], True)

        ## OUTPUT HTML FILE
        with open(html_file, 'w') as htmlFile:
            htmlFile.write(html_string)
        
        ## OUTPUT CSS FILE
        with open(css_file, 'w') as cssFile:
            cssFile.write(css_string)
        
        ## OUTPUT JAVASCRIPT FILE
        with open(js_file, 'w') as jsFile:
            jsFile.write(js_string)

        ## MERGE THE FILES INTO ONE
        if onefile:
            merge_html(html_file, css_file, js_file, True, False)
        return

## DOWNLOAD FILES
def download(URL: str, Filename: str='', Save_Directory: Path=fs.root('downloads'), Detect_Format: bool=True, debug: bool=False):
  '''
  URL: (str) to file or (list) of strings to files
  Filename: Save As... (leave blank to inherit original filename)
  Save_Directory: Save To... (default = User/Downloads)
  debug: Print downloads to console
  '''
  
  ## DOWNLOAD A LIST OF FILES
  if type(URL) == list:

    ## ARRAY OF FILENAMES
    filenames = []

    ## INITIAL FILENAME
    Filname_init = Filename

    ## ITERATE THROUGH LIST
    for link in range(len(URL)):

      ## INITIALIZE FILENAME
      Filename = Filname_init

      ## READ FILE FORMAT
      file_format = f".{URL[link].split('.')[-1]}"

      ## DEBUG: PRINT DL MESSAGE
      if debug:
        print(f"\nDownloading from {URL[link]}")
      
      ## DOWNLOAD FILE
      r = requests.get(URL[link], allow_redirects=True)

      ## IF NO FILENAME ENTERED, USE ORIGINAL FILENAME FROM WEB
      if Filename == '':
        Filename = str(URL[link]).split('/')[-1]

      ## IF FILENAME ENTERED, ADD NUMBERS TO EACH FILE TO DIFFERENTIATE THEM
      else:
        Filename = f"{Filename.split(file_format)[0]}({link+1}){file_format}"

      ## APPEND FILENAMES ARRAY
      filenames.append(Filename)

      ## SAVE FILE TO CHOSEN DIRECTORY
      open(f"{Save_Directory}/{Filename}", 'wb').write(r.content)

      ## DEBUG: PRINT COMPLETION MESSAGE
      if debug:
        print(f'Done: {Save_Directory}/{Filename}')
  
  ## DOWNLOAD SINGLE FILE
  if type(URL) == str:
    
    ## READ FILE FORMAT
    file_format = f".{str(URL).split('.')[-1]}"

    ## DEBUG: PRINT DL MESSAGE
    if debug:
      print(f'\nDownloading from [{URL}]')
    
    ## DOWNLOAD FILE
    r = requests.get(URL, allow_redirects=True)
    
    ## IF NO FILENAME ENTERED, USE ORIGINAL FILENAME FROM WEB
    if Filename == '':
      Filename = str(URL).split("/")[-1]
    
    ## IF FILENAME ENTERED, BUT NO EXTENSION SPECIFIED - GET EXTENSION FROM ORIGINAL FILE
    if not '.' in Filename and Detect_Format:
      Filename = f"{Filename}{file_format}"

    ## SAVE FILE TO CHOSEN DIRECTORY
    open(f"{Save_Directory}/{Filename}", 'wb').write(r.content)

    ## DEBUG: PRINT COMPLETION MESSAGE
    if debug:
      print(f'Done: {Save_Directory}/{Filename}')

## MERGE HTML/CSS/JS INTO ONE HTML FILE
def merge_html(HTML: Path, CSS: Path, JS: Path, onefile: bool=False, debug: bool=False, filename: str='index', remove_webfiles: bool=False):
        '''
        ARGUMENTS

        HTML: Path to HTML file
        CSS: Path to CSS file
        JS: Path to JS file
        onefile: Only keep output file (bool)
        debug: (bool)
        filename: output html filename (str)
        remove_webfiles: delete 'webfiles' dir

        DESCRIPTION

        - Merges HTML, CSS and JS files into one HTML file with inline code
        '''

        ## READ THE BUILT HTML FILE
        try:
            html_file = Path(f'{HTML}').read_text(encoding="utf-8")
            soup = BeautifulSoup(html_file, features='lxml')
        except FileNotFoundError:
            if debug:
                return print('\nn4s.web.merge_html():\nHTML File Not Found - Files Not Merged\n')
            else:
                return

        ## GET FILE DIRECTORY
        index = HTML.rfind("/")
        directory = f"{HTML[0:index]}"

        ## FIND LINK TAGS : <link rel="stylesheet" href="css/somestyle.css">
        for tag in soup.find_all('link', href=True):
            if tag.has_attr('href'):
                try:
                    css_file = Path(f'{CSS}').read_text(encoding="utf-8")
                except FileNotFoundError:
                    if debug:
                        return print('\nn4s.web.merge_html():\nCSS File Not Found - Files Not Merged\n')
                    else:
                        return

                # remove the tag from soup
                tag.extract()
        
                # insert style element
                new_style = soup.new_tag('style')
                new_style.string = css_file
                soup.html.head.append(new_style)
                break
        
        ## FIND SCRIPT TAGS : <script src="js/script.js"></script>
        for tag in soup.find_all('script', src=True):
            if tag.has_attr('src'):
                try:
                    js_file = Path(f'{JS}').read_text(encoding="utf-8")
                except FileNotFoundError:
                    if debug:
                        return print('\nn4s.web.merge_html():\nJS File Not Found - Files Not Merged\n')
                    else:
                        return

                # remove the tag from soup
                tag.extract()
        
                # insert script element
                new_script = soup.new_tag('script')
                new_script.string = js_file
                soup.html.body.append(new_script)
        
        ## FIND IMAGE TAGS : <img src="" alt="">
        for tag in soup.find_all('img', src=True):
            if tag.has_attr('src'):
                file_content = Path(tag['src']).read_bytes()
        
                # replace filename with base64 of the content of the file
                base64_file_content = base64.b64encode(file_content)
                tag['src'] = "data:image/png;base64, {}".format(base64_file_content.decode('ascii'))

        ## CREATE WEBFILES DIR FOR PREVIOUS FILES
        fs.path_exists(f"{directory}/webfiles", True)

        ## COPY PREVIOUS FILES TO WEBFILES IF ONEFILE == FALSE
        if not onefile:
            shutil.copy(HTML, f"{directory}/webfiles/index.html")
            shutil.copytree(f"{directory}/assets", f"{directory}/webfiles/assets")

        ## MERGE HTML/CSS/JS INTO HTML
        try:
            with open(f"{directory}/{filename}.html", "w", encoding="utf-8") as outfile:
                outfile.write(str(soup))
        except Exception:
            if debug:
                return print('\nn4s.web.merge_html():\nHTML/CSS/JS Files Were Found\nBut Failed to Merge')
            else:
                return

        ## REMOVE PREVIOUS FILES
        if os.path.isdir(f"{directory}/assets"):
                shutil.rmtree(f"{directory}/assets")
        if not filename == 'index':
            try:
                os.remove(f"{directory}/index.html")
            except FileNotFoundError:
                pass

        ## REMOVE PREVIOUS HTML IF ONEFILE == TRUE
        if onefile:
          p = Path(directory).absolute()
          parent_dir = p.parents[0]
          shutil.move(f"{directory}/index.html", parent_dir)
          if os.path.isdir(directory):
            if not directory == fs.root():
              shutil.rmtree(directory)

        ## REMOVE WEBFILES DIR IF REMOVE_WEBFILES == ENABLED
        if remove_webfiles:
          if fs.path_exists(f"{directory}/webfiles"):
            shutil.rmtree(f"{directory}/webfiles")

        ## DEBUG: PRINT COMPLETION MESSAGE
        if debug:
            return print(f"\n{HTML}\n"
                            f"{CSS}\n"
                            f"{JS}\n"
                            f"---\n"
                            f"{directory}/{filename}.html")
        return

## CHECK FOR WORKING NETWORK CONNECTION
def network_test():
        network_connectivity_test = httplib.HTTPSConnection("8.8.8.8", timeout=5)
        try:
            network_connectivity_test.request("HEAD", "/")
            return True
        except Exception:
            return False
        finally:
            network_connectivity_test.close()

## READS FILE EXTENSIONS
def read_format(Input: str, Include_Period: bool=False, Print: bool=False, Uppercase: bool=False):
    
    ## INCLUDE PERIOD IN FORMAT
    if Include_Period:
        file_format = f".{Input.split('.')[-1]}"
    
    ## RETURN FORMAT WITHOUT PERIOD
    else:
        file_format = Input.split('.')[-1]

    ## CLEAR SPECIAL CHARACTERS
    if '?' in file_format:
        file_format = file_format.split('?')[0]
    if '/' in file_format:
        file_format = file_format.split('/')[0]
    
    ## IF UPPERCASE == ENABLED
    if Uppercase:
        file_format = file_format.upper()

    ## PRINT FORMAT TO TERMINAL
    if Print:
        print(file_format)

    ## RETURN FORMAT
    return file_format

## STRIP HTML TAGS FROM STRING
def strip_tags(Input: str):
        '''
        ARGUMENTS

        - Input: str
        - Removes HTML tags from string

        DESCRIPTION

        - Remove HTML tags from an input string
        '''
        ## PREVENT CDATA CONTENT FROM BEING STRIPPED
        Input = strgs.filter_text(Input, ['<![CDATA[', ']]>'])

        ## STRIP HTML TAGS
        clean = re.compile('<.*?>')

        ## RETURN (REMOVE WHITESPACE)
        return re.sub(clean, '', Input).strip()


## TESTS