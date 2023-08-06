#try block for termux
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import *
    from selenium.webdriver.firefox.service import *
    from webdriver_manager.firefox import *

except:
    pass

from bs4 import BeautifulSoup
from collections import *
from os import name

import codecs
import numpy as np
import os
import re
import requests
import socket
import time
import urllib3

#create html sessions object
web_session = requests.Session()

#fake user agent
user_agent = {"User-Agent" : "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36", "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", "Accept-Language" : "en-US,en"}

#increased security
requests.packages.urllib3.disable_warnings()
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ":HIGH:!DH:!aNULL"

#increased security
try:
    requests.packages.urllib3.contrib.pyopenssl.util.ssl_.DEFAULT_CIPHERS += ":HIGH:!DH:!aNULL"

except AttributeError:
    pass

#machine learning antivirus detect engine
def av_detect(virus, learn):
    clear()
    ml_virus = av_learn(learn)
    
    list_files = []
    ml_list = []
    possible = []

    progress = 0
    progress_count = 0
    total_progress = 0

    print("preparing")

    for root, dirs, files in os.walk(virus, topdown = True):
        if len(dirs) > 0:
            for directory in dirs:
                for file in files:
                    progress_count += 1
                    list_files.append(root + directory + "/" + file)

        else:
            for file in files:
                progress_count += 1
                list_files.append(root + "/" + file)

    list_files.sort()

    counter = 0

    clear()
    
    print("progress: " + str(total_progress) + "%")

    for file in list_files:
        progress += 1

        if progress == int(progress_count / 100):
            progress = 0
            total_progress += 1
            print("progress: " + str(total_progress) + "%")
        
        try:
            if os.path.isfile(file) and os.path.getsize(file) > 0:
                with open(file, "rb") as f:
                    
                    for chunk in iter(lambda: f.read(128), b""):
                        try:
                            ascii_convert = codecs.decode(chunk, "utf8")
                        
                            clean = str(ascii_convert).replace("b", "")
                            clean = clean.replace("'", "")
                            clean = clean.replace("\x00", "")
                            clean = clean.replace("\x11", "")

                            if clean != "":
                                ml_list.append(clean)
                                
                        except:
                            pass

                ml_list = list(dict.fromkeys(ml_list))

                for string in ml_list:
                    for i in ml_virus:
                        if string == i:
                            counter += 10

                if counter > 0:
                    possible.append(file + ": " + str(counter) + "%")
                    
                counter = 0
                ml_list = []

        except:
            pass

    clear()
    possible.sort()
    
    for i in possible:
        print(i)

#machine learning antivirus learn engine
def av_learn(virus_folder):
    clear()
    list_files = []
    counter_array = np.array([])
    ml_array = np.array([])
    ml_list = []

    print("preparing")

    for root, dirs, files in os.walk(virus_folder, topdown = True):
       for name in files:
          list_files.append(name)

    list_files.sort()

    for file in list_files:
        try:
            if os.path.isfile(virus_folder + "/" + file) and os.path.getsize(virus_folder + "/" + file) > 0:
                with open(virus_folder + "/" + file, "rb") as f:
                    print("learning from: " + file)
                    
                    for chunk in iter(lambda: f.read(128), b""):
                        try:
                            ascii_convert = codecs.decode(chunk, "utf8")
                        
                            clean = str(ascii_convert).replace("b", "")
                            clean = clean.replace("'", "")
                            clean = clean.replace("\x00", "")
                            clean = clean.replace("\x11", "")

                            if clean != "":
                                ml_list.append(clean)
                                
                        except:
                            pass

        except FileNotFoundError:
            pass

    ml_array = np.array(ml_list)
    counter = str(Counter(ml_array).most_common(10))

    super_clean = counter.replace("[", "")
    super_clean = super_clean.replace("]", "")
    super_clean = super_clean.replace("('", "~")
    super_clean = super_clean.replace(")", "")
    super_clean = super_clean.replace("',", "`")
    counter_list = list(super_clean)

    counter_boolean = False
    my_string = ""
    super_counter = []

    for i in counter_list:
        if i == "`":
            my_string = my_string.replace("~", "")
            super_counter.append(my_string)
            my_string = ""
            counter_boolean = False

        if i == "~":
            counter_boolean = True

        if counter_boolean == True:
            my_string += i

    clear()

    return super_counter

#clear console (platform independent)
def clear():
    if name == "nt":
        os.system("cls")

    else:
        os.system("clear")
        
#extract metadata
def extract_metadata(image):
    image = Image.open(image)
    exifdata = image.getexif()

    for tagid in exifdata:
        tagname = TAGS.get(tagid, tagid)
        value = exifdata.get(tagid)
        clear()
        print(f"{tagname:25}: {value}")

def hex_viewer(file):
    clear()

    count = 0

    my_string = ""
    
    with open(file, "rb") as f:
        for chunk in iter(lambda: f.read(2), b""):
            try:
                hex_code = codecs.decode(chunk, "hex")
                clean = str(hex_code).replace("b", "")
                clean = clean.replace("'", "")
                clean = clean.replace("\\", "")
                clean = clean.replace("x", "")

                my_string += clean

                count += 1

                if count == 64:
                    print(my_string)
                    
                    count = 0
                    my_string = ""
                    
            except:
                pass

    print("\ndone")

#scans for hyperlinks using selenium
def link_scanner_selenium(url):
    result = "http://" + url
    
    driver = webdriver.Firefox(service = Service(GeckoDriverManager().install()))

    i = -1
    total_web_list = []
    total_web_list.append(result)
    web_list = []

    while True:
        i = i + 1
        
        try:
            print(total_web_list[i])
            driver.get(total_web_list[i])

        except IndexError:
            break

        except:
            continue
        
        try:
            for ii in driver.find_elements(by = By.XPATH, value = ".//a"):
                web_list.append(ii.get_attribute("href"))

        except:
            pass

        web_list = list(dict.fromkeys(web_list))

        for iii in web_list:
            try:
                domain_name = result in iii

                parse = iii.index(result, 0, len(result))
                
                if domain_name == True and parse == 0:
                    total_web_list.append(iii)
                    total_web_list = list(dict.fromkeys(total_web_list))

            except:
                continue

    total_web_list = list(dict.fromkeys(total_web_list))
    total_web_list.sort()

    clear()

    return total_web_list

def port_scanner(url):
    clear()
    my_list = []

    for port in range(1,65535):
        print("checking port: " + str(port))
        sock = socket.socket()
        sock.settimeout(0.5)
        result = sock.connect_ex((url, port))
        sock.close()

        if result == 0:
            print(True)
            my_list.append(port)

        else:
            print(False)

    clear()
    return my_list

def search_engine_email(url, secure = True):
    if secure == True:
        my_secure = "https://"

    if secure == False:
        my_secure = "http://"

    clear()
    user_input = input("1 = scan all | 2 = scan domain\n")
    clear()
    
    counter = 0
    email_list = []
    web_list = []

    web_list.append(my_secure + url)

    clear()

    if user_input == "1":
        while True:
            try:
                print(web_list[counter])

            except IndexError:
                break
            
            try:
                my_request = web_session.get(web_list[counter], headers = user_agent, timeout = (5,30)).text

            except:
                pass

            counter += 1
            
            if len(my_request) <= 1000000:
                website = re.findall("[^\"\'=]https://|http://|www\S+[$;\"\']", my_request)
                website = list(dict.fromkeys(website))
                email = re.findall("[a-z0-9]+@[a-z0-9]+[.][a-z]+", my_request)
                email = list(dict.fromkeys(email))

                for i in website:
                    clean = i.replace('"', " ")
                    clean = clean.replace("'", " ")
                    clean = clean.replace(";", " ")
                    clean = clean.replace("\\", "")
                    clean = clean.replace("%", " ")
                    clean = clean.split()

                    try:
                        if "http" not in i:
                            web_list.append(my_secure + clean[0])

                        else:
                            web_list.append(clean[0])

                    except:
                        pass

                for i in email:
                    email_list.append(i)
                    email_list = list(dict.fromkeys(email_list))

                web_list = list(dict.fromkeys(web_list))

    if user_input == "2":
         while True:
            try:
                print(web_list[counter])

            except IndexError:
                break
            
            try:
                my_request = web_session.get(web_list[counter], headers = user_agent, timeout = (5,30)).text

            except:
                pass

            counter += 1

            if len(my_request) <= 1000000:
                website = re.findall("[^\"\'=]https://|http://|www\S+[$;\"\']", my_request)
                website = list(dict.fromkeys(website))
                email = re.findall("[a-z0-9]+@[a-z0-9]+[.][a-z]+", my_request)
                email = list(dict.fromkeys(email))

                for i in website:
                    if url in i:
                        clean = i.replace('"', " ")
                        clean = clean.replace("'", " ")
                        clean = clean.replace(";", " ")
                        clean = clean.replace("\\", "")
                        clean = clean.replace("%", " ")
                        clean = clean.split()
                        
                        try:
                            if "http" not in i:
                                web_list.append(my_secure + clean[0])

                            else:
                                web_list.append(clean[0])

                        except:
                            pass

                href = re.findall("href=\S+", my_request)
                href = list(dict.fromkeys(href))

                for i in href:
                    clean = i.replace('"', "")
                    clean = clean.replace("'", "")
                    clean = clean.replace(";", " ")
                    clean = clean.replace("\\", "")
                    clean = clean.replace(">", " ")
                    clean = clean.replace("href=", "")
                    clean = clean.replace("%", " ")
                    clean = clean.split()

                    try:
                        if "http" not in i:
                            web_list.append(my_secure + url + "/" + clean[0])

                        else:
                            if url in i:
                                web_list.append(clean[0])

                    except:
                        pass

                for i in email:
                    if url in i:
                        email_list.append(i)
                        email_list = list(dict.fromkeys(email_list))

                web_list = list(dict.fromkeys(web_list))

    clear()

    return email_list

def search_engine_string(url, string, secure = True):
    if secure == True:
        my_secure = "https://"

    if secure == False:
        my_secure = "http://"

    clear()
    user_input = input("1 = scan all | 2 = scan domain\n")
    clear()

    counter = 0

    string_list = []
    web_list = []

    web_list.append(my_secure + url)

    if user_input == "1":
        while True:
            try:
                done = web_list[counter]

            except IndexError:
                break
            
            try:
                my_request = web_session.get(web_list[counter], headers = user_agent, timeout = (5,30)).text

                if string in my_request:
                    print(web_list[counter])
                    string_list.append(web_list[counter])

            except:
                pass

            counter += 1

            if len(my_request) <= 1000000:
                website = re.findall("[^\"\'=]https://|http://|www\S+[$;\"\']", my_request)
                website = list(dict.fromkeys(website))

                for i in website:
                    clean = i.replace('"', " ")
                    clean = clean.replace("'", " ")
                    clean = clean.replace(";", " ")
                    clean = clean.replace("\\", "")
                    clean = clean.replace("%", " ")
                    clean = clean.split()

                    
                    try:
                        if "http" not in i:
                            web_list.append(my_secure + clean[0])

                        else:
                            web_list.append(clean[0])

                    except:
                        pass

                web_list = list(dict.fromkeys(web_list))

    if user_input == "2":
        while True:
            try:
                done = web_list[counter]

            except IndexError:
                break
            
            try:
                my_request = web_session.get(web_list[counter], headers = user_agent, timeout = (5,30)).text

                if string in my_request:
                    print(web_list[counter])
                    string_list.append(web_list[counter])

            except:
                pass

            counter += 1

            if len(my_request) <= 1000000:
                website = re.findall("[^\"\'=]https://|http://|www\S+[$;\"\']", my_request)
                website = list(dict.fromkeys(website))

                for i in website:
                    if i in url:
                        clean = i.replace('"', " ")
                        clean = clean.replace("'", " ")
                        clean = clean.replace(";", " ")
                        clean = clean.replace("\\", "")
                        clean = clean.replace("%", " ")
                        clean = clean.split()

                        try:
                            if "http" not in i:
                                web_list.append(my_secure + clean[0])

                            else:
                                web_list.append(clean[0])

                        except:
                            pass

                href = re.findall("href=\S+", my_request)
                href = list(dict.fromkeys(href))

            for i in href:
                    clean = i.replace('"', "")
                    clean = clean.replace("'", "")
                    clean = clean.replace(";", " ")
                    clean = clean.replace("\\", "")
                    clean = clean.replace(">", " ")
                    clean = clean.replace("href=", "")
                    clean = clean.replace("%", " ")
                    clean = clean.split()

                    try:
                        if "http" not in i:
                            web_list.append(my_secure + url + "/" + clean[0])

                        else:
                            if url in i:
                                web_list.append(clean[0])

                    except:
                        pass

            web_list = list(dict.fromkeys(web_list))

    clear()

    return web_list

def search_engine_website(url, secure = True):
    if secure == True:
        my_secure = "https://"

    if secure == False:
        my_secure = "http://"

    clear()
    user_input = input("1 = scan all | 2 = scan domain\n")
    clear()
    
    counter = 0
    web_list = []

    web_list.append(my_secure + url)

    if user_input == "1":
        while True:
            try:
                print(web_list[counter])

            except IndexError:
                break
            
            try:
                my_request = web_session.get(web_list[counter], headers = user_agent, timeout = (5,30)).text

            except:
                print("ERROR!")

            counter += 1

            if len(my_request) <= 1000000:
                website = re.findall("[^\"\'=]https://|http://|www\S+[$;\"\']", my_request)
                website = list(dict.fromkeys(website))

                for i in website:
                    clean = i.replace('"', " ")
                    clean = clean.replace("'", " ")
                    clean = clean.replace(";", " ")
                    clean = clean.replace("\\", "")
                    clean = clean.replace("%", " ")
                    clean = clean.split()

                    try:
                        if "http" not in i:
                            web_list.append(my_secure + clean[0])

                        else:
                            web_list.append(clean[0])

                    except:
                        pass

                web_list = list(dict.fromkeys(web_list))

    if user_input == "2":
        while True:
            try:
                print(web_list[counter])

            except IndexError:
                break
            
            try:
                my_request = web_session.get(web_list[counter], headers = user_agent, timeout = (5,30)).text

            except:
                print("ERROR!")

            counter += 1

            if len(my_request) <= 1000000:
                website = re.findall("[^\"\'=]https://|http://|www\S+[$;\"\']", my_request)
                website = list(dict.fromkeys(website))

                for i in website:
                    if url in i:
                        clean = i.replace('"', " ")
                        clean = clean.replace("'", " ")
                        clean = clean.replace(";", " ")
                        clean = clean.replace("\\", "")
                        clean = clean.replace("%", " ")
                        clean = clean.split()

                        try:
                            if "http" not in i:
                                web_list.append(my_secure + clean[0])

                            else:
                                web_list.append(clean[0])

                        except:
                            pass

                href = re.findall("href=\S+", my_request)
                href = list(dict.fromkeys(href))

                for i in href:
                    clean = i.replace('"', "")
                    clean = clean.replace("'", "")
                    clean = clean.replace(";", " ")
                    clean = clean.replace("\\", "")
                    clean = clean.replace(">", " ")
                    clean = clean.replace("href=", "")
                    clean = clean.replace("%", " ")
                    clean = clean.split()

                    try:
                        if "http" not in i:
                            web_list.append(my_secure + url + "/" + clean[0])

                        else:
                            if url in i:
                                web_list.append(clean[0])

                    except:
                        pass

                web_list = list(dict.fromkeys(web_list))
        

    clear()

    return web_list

def source_code_viewer(file, keyword = ""):
    clear()

    count = 0
    
    with open(file, "rb") as f:
        for chunk in iter(lambda: f.read(128), b""):
            try:
                ascii_convert = codecs.decode(chunk, "utf8")

                if keyword in ascii_convert:
                    print(ascii_convert)

                    count += 1

                    if count == 128:
                        count = 0
                        pause = input()
                    
            except UnicodeDecodeError:
                continue

    print("\ndone")

def sql_injection_scanner(url, secure = True):
    if secure == True:
        my_secure = "https://"

    if secure == False:
        my_secure = "http://"
    
    my_url = my_secure + url

    #sql errors
    error_mesage = {"SQL syntax.*?MySQL", "Warning.*?\Wmysqli?_", "MySQLSyntaxErrorException", "valid MySQL result", "check the manual that (corresponds to|fits) your MySQL server version", "check the manual that (corresponds to|fits) your MariaDB server version", "check the manual that (corresponds to|fits) your Drizzle server version", "Unknown column '[^ ]+' in 'field list'", "MySqlClient\.", "com\.mysql\.jdbc", "Zend_Db_(Adapter|Statement)_Mysqli_Exception", "Pdo\[./_\\]Mysql", "MySqlException", "SQLSTATE\[\d+\]: Syntax error or access violation", "MemSQL does not support this type of query", "is not supported by MemSQL", "unsupported nested scalar subselect", "PostgreSQL.*?ERROR", "Warning.*?\Wpg_", "valid PostgreSQL result", "Npgsql\.", "PG::SyntaxError:", "org\.postgresql\.util\.PSQLException", "ERROR:\s\ssyntax error at or near", "ERROR: parser: parse error at or near", "PostgreSQL query failed", "org\.postgresql\.jdbc", "Pdo\[./_\\]Pgsql", "PSQLException", "OLE DB.*? SQL Server", "\bSQL Server[^&lt;&quot;]+Driver", "Warning.*?\W(mssql|sqlsrv)_", "\bSQL Server[^&lt;&quot;]+[0-9a-fA-F]{8}", "System\.Data\.SqlClient\.(SqlException|SqlConnection\.OnError)", "(?s)Exception.*?\bRoadhouse\.Cms\.", "Microsoft SQL Native Client error '[0-9a-fA-F]{8}", "\[SQL Server\]", "ODBC SQL Server Driver", "ODBC Driver \d+ for SQL Server", "SQLServer JDBC Driver", "com\.jnetdirect\.jsql", "macromedia\.jdbc\.sqlserver", "Zend_Db_(Adapter|Statement)_Sqlsrv_Exception", "com\.microsoft\.sqlserver\.jdbc", "Pdo\[./_\\](Mssql|SqlSrv)", "SQL(Srv|Server)Exception", "Unclosed quotation mark after the character string", "Microsoft Access (\d+ )?Driver", "JET Database Engine", "Access Database Engine", "ODBC Microsoft Access", "Syntax error \(missing operator\) in query expression", "\bORA-\d{5}", "Oracle error", "Oracle.*?Driver", "Warning.*?\W(oci|ora)_", "quoted string not properly terminated", "SQL command not properly ended", "macromedia\.jdbc\.oracle", "oracle\.jdbc", "Zend_Db_(Adapter|Statement)_Oracle_Exception", "Pdo\[./_\\](Oracle|OCI)", "OracleException", "CLI Driver.*?DB2", "DB2 SQL error", "\bdb2_\w+\(", "SQLCODE[=:\d, -]+SQLSTATE", "com\.ibm\.db2\.jcc", "Zend_Db_(Adapter|Statement)_Db2_Exception", "Pdo\[./_\\]Ibm", "DB2Exception", "ibm_db_dbi\.ProgrammingError", "Warning.*?\Wifx_", "Exception.*?Informix", "Informix ODBC Driver", "ODBC Informix driver", "com\.informix\.jdbc", "weblogic\.jdbc\.informix", "Pdo\[./_\\]Informix", "IfxException", "Dynamic SQL Error", "Warning.*?\Wibase_", "org\.firebirdsql\.jdbc", "Pdo\[./_\\]Firebird", "SQLite/JDBCDriver", "SQLite\.Exception", "(Microsoft|System)\.Data\.SQLite\.SQLiteException", "Warning.*?\W(sqlite_|SQLite3::)", "\[SQLITE_ERROR\]", "SQLite error \d+:", "sqlite3.OperationalError:", "SQLite3::SQLException", "org\.sqlite\.JDBC", "Pdo\[./_\\]Sqlite", "SQLiteException", "SQL error.*?POS([0-9]+)", "Warning.*?\Wmaxdb_", "DriverSapDB", "-3014.*?Invalid end of SQL statement", "com\.sap\.dbtech\.jdbc", "\[-3008\].*?: Invalid keyword or missing delimiter", "Warning.*?\Wsybase_", "Sybase message", "Sybase.*?Server message", "SybSQLException", "Sybase\.Data\.AseClient", "com\.sybase\.jdbc", "Warning.*?\Wingres_", "Ingres SQLSTATE", "Ingres\W.*?Driver", "com\.ingres\.gcf\.jdbc", "Exception (condition )?\d+\. Transaction rollback", "com\.frontbase\.jdbc", "Syntax error 1. Missing", "(Semantic|Syntax) error [1-4]\d{2}\.", "Unexpected end of command in statement \[", "Unexpected token.*?in statement \[", "org\.hsqldb\.jdbc", "org\.h2\.jdbc", "\[42000-192\]", "![0-9]{5}![^\n]+(failed|unexpected|error|syntax|expected|violation|exception)", "\[MonetDB\]\[ODBC Driver", "nl\.cwi\.monetdb\.jdbc", "Syntax error: Encountered", "org\.apache\.derby", "ERROR 42X01", ", Sqlstate: (3F|42).{3}, (Routine|Hint|Position):", "/vertica/Parser/scan", "com\.vertica\.jdbc", "org\.jkiss\.dbeaver\.ext\.vertica", "com\.vertica\.dsi\.dataengine", "com\.mckoi\.JDBCDriver", "com\.mckoi\.database\.jdbc", "&lt;REGEX_LITERAL&gt;", "com\.facebook\.presto\.jdbc", "io\.prestosql\.jdbc", "com\.simba\.presto\.jdbc", "UNION query has different number of fields: \d+, \d+", "Altibase\.jdbc\.driver", "com\.mimer\.jdbc", "Syntax error,[^\n]+assumed to mean", "io\.crate\.client\.jdbc", "encountered after end of query", "A comparison operator is required here", "-10048: Syntax error", "rdmStmtPrepare\(.+?\) returned", "SQ074: Line \d+:", "SR185: Undefined procedure", "SQ200: No table ", "Virtuoso S0002 Error", "\[(Virtuoso Driver|Virtuoso iODBC Driver)\]\[Virtuoso Server\]"}
    
    #malicious sql code
    mal_sql = ["\"", "\'", ";"]

    my_list = []

    clear()

    user_input = input("1 = scan url | 2 = scan url and hyperlinks (requests) | 3 = scan url and hyperlinks (selenium)\n")

    clear()
    
    if user_input == "1":
        for c in mal_sql:
            new_url = f"{my_url}{c}"
            print("checking: " + new_url)
            
            try:
                result = web_session.get(new_url, verify = True, headers = user_agent, timeout = (5, 30))

                for i in error_mesage:
                    my_regex = re.search(i, result.text)
                    my_boolean = False

                    try:
                        if my_regex:
                            my_boolean = True
                            break

                    except UnicodeDecodeError:
                        break

                if my_boolean == True:
                    print("true: " + new_url)
                    my_list.append(new_url)

            except requests.exceptions.SSLError:
                print("ERROR: invalid certificate!")
                continue

            except urllib3.exceptions.LocationParseError:
                print("ERROR: location parse error!")
                continue

            except requests.exceptions.ConnectionError:
                print("ERROR: connection error!")
                continue

            except requests.exceptions.ConnectTimeout:
                print("ERROR: connect timeout!")
                continue

            except requests.exceptions.InvalidSchema:
                print("ERROR: invalid schema!")
                continue

            except requests.exceptions.InvalidURL:
                print("ERROR: invalid url!")
                continue

            except requests.exceptions.MissingSchema:
                print("ERROR: missing schema!")
                continue

            except requests.exceptions.TooManyRedirects:
                print("ERROR: too many redirects!")
                continue

            except requests.exceptions.ReadTimeout:
                print("ERROR: read timeout!")
                continue

        try:
            print("checking for forms on: " + my_url)

            result = web_session.get(my_url, verify = True, headers = user_agent, timeout = (5, 30))

            try:
                soup = BeautifulSoup(result.text, "html.parser")
                get_input = soup.find_all("input")

            except:
                pass

            form_list = []

            for i in get_input:
                if "email" in str(i):
                    form_name = ""

                    try:
                        parse_name_start = str(i).index("name=\"")
                        parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))

                        for ii in range(parse_name_start + 6, parse_name_end):
                            form_name = form_name + str(i)[ii]

                        form_list.append(form_name)

                    except:
                        pass

                if "hidden" in str(i):
                    form_name = ""

                    try:
                        parse_name_start = str(i).index("name=\"")
                        parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))

                        for ii in range(parse_name_start + 6, parse_name_end):
                            form_name = form_name + str(i)[ii]

                        form_list.append(form_name)

                    except:
                        pass
                    
                if "number" in str(i):
                    form_name = ""

                    try:
                        parse_name_start = str(i).index("name=\"")
                        parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))

                        for ii in range(parse_name_start + 6, parse_name_end):
                            form_name = form_name + str(i)[ii]

                        form_list.append(form_name)

                    except:
                        pass

                if "password" in str(i):
                    form_name = ""

                    try:
                        parse_name_start = str(i).index("name=\"")
                        parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))

                        for ii in range(parse_name_start + 6, parse_name_end):
                            form_name = form_name + str(i)[ii]

                        form_list.append(form_name)

                    except:
                        pass

                if "query" in str(i):
                    form_name = ""

                    try:
                        parse_name_start = str(i).index("name=\"")
                        parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))

                        for ii in range(parse_name_start + 6, parse_name_end):
                            form_name = form_name + str(i)[ii]

                        form_list.append(form_name)

                    except:
                        pass

                if "search" in str(i):
                    form_name = ""

                    try:
                        parse_name_start = str(i).index("name=\"")
                        parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))
                        
                        for ii in range(parse_name_start + 6, parse_name_end):
                            form_name = form_name + str(i)[ii]

                        form_list.append(form_name)

                    except:
                        pass

                if "tel" in str(i):
                    form_name = ""

                    try:
                        parse_name_start = str(i).index("name=\"")
                        parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))

                        for ii in range(parse_name_start + 6, parse_name_end):
                            form_name = form_name + str(i)[ii]

                        form_list.append(form_name)

                    except:
                        pass

                if "text" in str(i):
                    form_name = ""

                    try:
                        parse_name_start = str(i).index("name=\"")
                        parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))

                        for ii in range(parse_name_start + 6, parse_name_end):
                            form_name = form_name + str(i)[ii]

                        form_list.append(form_name)

                    except:
                        pass

                if "url" in str(i):
                    form_name = ""

                    try:
                        parse_name_start = str(i).index("name=\"")
                        parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))

                        for ii in range(parse_name_start + 6, parse_name_end):
                            form_name = form_name + str(i)[ii]

                        form_list.append(form_name)

                    except:
                        pass

            form_list = list(dict.fromkeys(form_list))
            form_list.sort()

            for forms in form_list:
                for mal in mal_sql:
                    form_dict = {forms: mal}

                    print("checking form (" + mal + "): " + forms)

                    send_data = web_session.post(my_url, data = form_dict, verify = True, headers = user_agent, timeout = (5, 30))

                    for i in error_mesage:
                        my_regex = re.search(i, send_data.text)
                        my_boolean = False

                        try:
                            if my_regex:
                                    my_boolean = True
                                    break

                        except UnicodeDecodeError:
                            continue

                    if my_boolean == True:
                        print("true: " + url + " form: " + forms)
                        my_list.append(url + " form: " + forms)

                    get_data = web_session.get(my_url, params = form_dict, verify = True, headers = user_agent, timeout = (5, 30))

                    for i in error_mesage:
                        my_regex = re.search(i, get_data.text)
                        my_boolean = False

                        try:
                            if my_regex:
                                    my_boolean = True
                                    break

                        except UnicodeDecodeError:
                            continue

                    if my_boolean == True:
                        print("true: " + url + " form: " + forms)
                        my_list.append(url + " form: " + forms)

        except requests.exceptions.SSLError:
            print("ERROR: invalid certificate!")
            pass

        except urllib3.exceptions.LocationParseError:
            print("ERROR: location parse error!")
            pass

        except requests.exceptions.ConnectionError:
            print("ERROR: connection error!")
            pass

        except requests.exceptions.ConnectTimeout:
            print("ERROR: connect timeout!")
            pass

        except requests.exceptions.InvalidSchema:
            print("ERROR: invalid schema!")
            pass

        except requests.exceptions.InvalidURL:
            print("ERROR: invalid url!")
            pass

        except requests.exceptions.MissingSchema:
            print("ERROR: missing schema!")
            pass

        except requests.exceptions.TooManyRedirects:
            print("ERROR: too many redirects!")
            pass

        except requests.exceptions.ReadTimeout:
            print("ERROR: read timeout!")
            pass

    if user_input == "2":
        my_result = search_engine_website(url, secure = secure)

        for j in my_result:
            for c in mal_sql:
                new_url = f"{j}{c}"

                print("checking: " + new_url)

                try:
                    result = web_session.get(new_url, verify = True, headers = user_agent, timeout = (5, 30))

                    for i in error_mesage:
                        my_regex = re.search(i, result.text)
                        my_boolean = False

                        try:
                            if my_regex:
                                my_boolean = True
                                break

                        except UnicodeDecodeError:
                            continue

                    if my_boolean == True:
                        print("true: " + new_url)
                        my_list.append(new_url)

                except requests.exceptions.SSLError:
                    print("ERROR: invalid certificate!")
                    pass

                except urllib3.exceptions.LocationParseError:
                    print("ERROR: location parse error!")
                    pass

                except requests.exceptions.ConnectionError:
                    print("ERROR: connection error!")
                    pass

                except requests.exceptions.ConnectTimeout:
                    print("ERROR: connect timeout!")
                    pass

                except requests.exceptions.InvalidSchema:
                    print("ERROR: invalid schema!")
                    pass

                except requests.exceptions.InvalidURL:
                    print("ERROR: invalid url!")
                    pass

                except requests.exceptions.MissingSchema:
                    print("ERROR: missing schema!")
                    pass

                except requests.exceptions.TooManyRedirects:
                    print("ERROR: too many redirects!")
                    pass

                except requests.exceptions.ReadTimeout:
                    print("ERROR: read timeout!")
                    pass
                
            try:
                print("checking for forms on: " + j)

                result = web_session.get(j, verify = True, headers = user_agent, timeout = (5, 30))

                try:
                    soup = BeautifulSoup(result.text, "html.parser")
                    get_input = soup.find_all("input")

                except:
                    pass

                form_list = []

                for i in get_input:
                    if "email" in str(i):
                        form_name = ""

                        try:
                            parse_name_start = str(i).index("name=\"")
                            parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))

                            for ii in range(parse_name_start + 6, parse_name_end):
                                form_name = form_name + str(i)[ii]

                            form_list.append(form_name)

                        except:
                            pass

                    if "hidden" in str(i):
                        form_name = ""

                        try:
                            parse_name_start = str(i).index("name=\"")
                            parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))

                            for ii in range(parse_name_start + 6, parse_name_end):
                                form_name = form_name + str(i)[ii]

                            form_list.append(form_name)

                        except:
                            pass
                        
                    if "number" in str(i):
                        form_name = ""

                        try:
                            parse_name_start = str(i).index("name=\"")
                            parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))

                            for ii in range(parse_name_start + 6, parse_name_end):
                                form_name = form_name + str(i)[ii]

                            form_list.append(form_name)

                        except:
                            pass

                    if "password" in str(i):
                        form_name = ""

                        try:
                            parse_name_start = str(i).index("name=\"")
                            parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))
                            
                            for ii in range(parse_name_start + 6, parse_name_end):
                                form_name = form_name + str(i)[ii]

                            form_list.append(form_name)

                        except:
                            pass

                    if "query" in str(i):
                        form_name = ""

                        try:
                            parse_name_start = str(i).index("name=\"")
                            parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))
                            
                            for ii in range(parse_name_start + 6, parse_name_end):
                                form_name = form_name + str(i)[ii]

                            form_list.append(form_name)

                        except:
                            pass

                    if "search" in str(i):
                        form_name = ""

                        try:
                            parse_name_start = str(i).index("name=\"")
                            parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))

                            for ii in range(parse_name_start + 6, parse_name_end):
                                form_name = form_name + str(i)[ii]

                            form_list.append(form_name)

                        except:
                            pass

                    if "tel" in str(i):
                        form_name = ""

                        try:
                            parse_name_start = str(i).index("name=\"")
                            parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))

                            for ii in range(parse_name_start + 6, parse_name_end):
                                form_name = form_name + str(i)[ii]

                            form_list.append(form_name)

                        except:
                            pass

                    if "text" in str(i):
                        form_name = ""

                        try:
                            parse_name_start = str(i).index("name=\"")
                            parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))

                            for ii in range(parse_name_start + 6, parse_name_end):
                                form_name = form_name + str(i)[ii]

                            form_list.append(form_name)

                        except:
                            pass

                    if "url" in str(i):
                        form_name = ""

                        try:
                            parse_name_start = str(i).index("name=\"")
                            parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))

                            for ii in range(parse_name_start + 6, parse_name_end):
                                form_name = form_name + str(i)[ii]

                            form_list.append(form_name)

                        except:
                            pass

                form_list = list(dict.fromkeys(form_list))
                form_list.sort()

                for forms in form_list:
                    for mal in mal_sql:
                        form_dict = {forms: mal}

                        print("checking form (" + mal + "): " + forms)

                        send_data = web_session.post(j, data = form_dict, verify = True, headers = user_agent, timeout = (5, 30))

                        for i in error_mesage:
                            my_regex = re.search(i, send_data.text)
                            my_boolean = False

                            try:
                                if my_regex:
                                        my_boolean = True
                                        break

                            except UnicodeDecodeError:
                                continue

                        if my_boolean == True:
                            print("true: " + url + " form: " + forms)
                            my_list.append(url + " form: " + forms)

                        get_data = web_session.get(j, params = form_dict, verify = True, headers = user_agent, timeout = (5, 30))

                        for i in error_mesage:
                            my_regex = re.search(i, get_data.text)
                            my_boolean = False

                            try:
                                if my_regex:
                                        my_boolean = True
                                        break

                            except UnicodeDecodeError:
                                continue

                        if my_boolean == True:
                            print("true: " + url + " form: " + forms)
                            my_list.append(url + " form: " + forms)

            except requests.exceptions.SSLError:
                print("ERROR: invalid certificate!")
                continue

            except urllib3.exceptions.LocationParseError:
                print("ERROR: location parse error!")
                continue

            except requests.exceptions.ConnectionError:
                print("ERROR: connection error!")
                continue

            except requests.exceptions.ConnectTimeout:
                print("ERROR: connect timeout!")
                continue

            except requests.exceptions.InvalidSchema:
                print("ERROR: invalid schema!")
                continue

            except requests.exceptions.InvalidURL:
                print("ERROR: invalid url!")
                continue

            except requests.exceptions.MissingSchema:
                print("ERROR: missing schema!")
                continue

            except requests.exceptions.TooManyRedirects:
                print("ERROR: too many redirects!")
                continue

            except requests.exceptions.ReadTimeout:
                print("ERROR: read timeout!")
                continue

    if user_input == "3":
        my_result = link_scanner_selenium(url)

        for j in my_result:
            for c in mal_sql:
                new_url = f"{j}{c}"

                print("checking: " + new_url)

                try:
                    result = web_session.get(new_url, verify = True, headers = user_agent, timeout = (5, 30))

                    for i in error_mesage:
                        my_regex = re.search(i, result.text)
                        my_boolean = False

                        try:
                            if my_regex:
                                my_boolean = True
                                break

                        except UnicodeDecodeError:
                            continue

                    if my_boolean == True:
                        print("true: " + new_url)
                        my_list.append(new_url)

                except requests.exceptions.SSLError:
                    print("ERROR: invalid certificate!")
                    pass

                except urllib3.exceptions.LocationParseError:
                    print("ERROR: location parse error!")
                    pass

                except requests.exceptions.ConnectionError:
                    print("ERROR: connection error!")
                    pass

                except requests.exceptions.ConnectTimeout:
                    print("ERROR: connect timeout!")
                    pass

                except requests.exceptions.InvalidSchema:
                    print("ERROR: invalid schema!")
                    pass

                except requests.exceptions.InvalidURL:
                    print("ERROR: invalid url!")
                    pass

                except requests.exceptions.MissingSchema:
                    print("ERROR: missing schema!")
                    pass

                except requests.exceptions.TooManyRedirects:
                    print("ERROR: too many redirects!")
                    pass

                except requests.exceptions.ReadTimeout:
                    print("ERROR: read timeout!")
                    pass
                
            try:
                print("checking for forms on: " + j)

                result = web_session.get(j, verify = True, headers = user_agent, timeout = (5, 30))

                try:
                    soup = BeautifulSoup(result.text, "html.parser")
                    get_input = soup.find_all("input")

                except:
                    pass

                form_list = []

                for i in get_input:
                    if "email" in str(i):
                        form_name = ""

                        try:
                            parse_name_start = str(i).index("name=\"")
                            parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))

                            for ii in range(parse_name_start + 6, parse_name_end):
                                form_name = form_name + str(i)[ii]

                            form_list.append(form_name)

                        except:
                            pass

                    if "hidden" in str(i):
                        form_name = ""

                        try:
                            parse_name_start = str(i).index("name=\"")
                            parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))

                            for ii in range(parse_name_start + 6, parse_name_end):
                                form_name = form_name + str(i)[ii]

                            form_list.append(form_name)

                        except:
                            pass
                        
                    if "number" in str(i):
                        form_name = ""

                        try:
                            parse_name_start = str(i).index("name=\"")
                            parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))

                            for ii in range(parse_name_start + 6, parse_name_end):
                                form_name = form_name + str(i)[ii]

                            form_list.append(form_name)

                        except:
                            pass

                    if "password" in str(i):
                        form_name = ""

                        try:
                            parse_name_start = str(i).index("name=\"")
                            parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))
                            
                            for ii in range(parse_name_start + 6, parse_name_end):
                                form_name = form_name + str(i)[ii]

                            form_list.append(form_name)

                        except:
                            pass

                    if "query" in str(i):
                        form_name = ""

                        try:
                            parse_name_start = str(i).index("name=\"")
                            parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))
                            
                            for ii in range(parse_name_start + 6, parse_name_end):
                                form_name = form_name + str(i)[ii]

                            form_list.append(form_name)

                        except:
                            pass

                    if "search" in str(i):
                        form_name = ""

                        try:
                            parse_name_start = str(i).index("name=\"")
                            parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))

                            for ii in range(parse_name_start + 6, parse_name_end):
                                form_name = form_name + str(i)[ii]

                            form_list.append(form_name)

                        except:
                            pass

                    if "tel" in str(i):
                        form_name = ""

                        try:
                            parse_name_start = str(i).index("name=\"")
                            parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))

                            for ii in range(parse_name_start + 6, parse_name_end):
                                form_name = form_name + str(i)[ii]

                            form_list.append(form_name)

                        except:
                            pass

                    if "text" in str(i):
                        form_name = ""

                        try:
                            parse_name_start = str(i).index("name=\"")
                            parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))

                            for ii in range(parse_name_start + 6, parse_name_end):
                                form_name = form_name + str(i)[ii]

                            form_list.append(form_name)

                        except:
                            pass

                    if "url" in str(i):
                        form_name = ""

                        try:
                            parse_name_start = str(i).index("name=\"")
                            parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))

                            for ii in range(parse_name_start + 6, parse_name_end):
                                form_name = form_name + str(i)[ii]

                            form_list.append(form_name)

                        except:
                            pass

                form_list = list(dict.fromkeys(form_list))
                form_list.sort()

                for forms in form_list:
                    for mal in mal_sql:
                        form_dict = {forms: mal}

                        print("checking form (" + mal + "): " + forms)

                        send_data = web_session.post(j, data = form_dict, verify = True, headers = user_agent, timeout = (5, 30))

                        for i in error_mesage:
                            my_regex = re.search(i, send_data.text)
                            my_boolean = False

                            try:
                                if my_regex:
                                        my_boolean = True
                                        break

                            except UnicodeDecodeError:
                                continue

                        if my_boolean == True:
                            print("true: " + url + " form: " + forms)
                            my_list.append(url + " form: " + forms)

                        if termux_tor_boolean == True or tor_boolean == True:
                            get_data = web_session.get(j, params = form_dict, verify = valid_certificate, headers = user_agent, proxies = tor_proxy, timeout = (5, 30))

                        if tor_boolean == False and termux_tor_boolean == False and tor_boolean == False:
                            get_data = web_session.get(j, params = form_dict, verify = valid_certificate, headers = user_agent, timeout = (5, 30))

                        for i in error_mesage:
                            my_regex = re.search(i, get_data.text)
                            my_boolean = False

                            try:
                                if my_regex:
                                        my_boolean = True
                                        break

                            except UnicodeDecodeError:
                                continue

                        if my_boolean == True:
                            print("true: " + url + " form: " + forms)
                            my_list.append(url + " form: " + forms)

            except requests.exceptions.SSLError:
                print("ERROR: invalid certificate!")
                continue

            except urllib3.exceptions.LocationParseError:
                print("ERROR: location parse error!")
                continue

            except requests.exceptions.ConnectionError:
                print("ERROR: connection error!")
                continue

            except requests.exceptions.ConnectTimeout:
                print("ERROR: connect timeout!")
                continue

            except requests.exceptions.InvalidSchema:
                print("ERROR: invalid schema!")
                continue

            except requests.exceptions.InvalidURL:
                print("ERROR: invalid url!")
                continue

            except requests.exceptions.MissingSchema:
                print("ERROR: missing schema!")
                continue

            except requests.exceptions.TooManyRedirects:
                print("ERROR: too many redirects!")
                continue

            except requests.exceptions.ReadTimeout:
                print("ERROR: read timeout!")
                continue

    clear()
    
    return my_list

def upgrade():
    clear()

    #upgrade
    os.system("pip install bs4 --upgrade")
    os.system("pip install numpy --upgrade")
    os.system("pip install requests --upgrade")
    os.system("pip install selenium --upgrade")
    os.system("pip install urllib3 --upgrade")
    os.system("pip install webdriver-manager --upgrade")

def xss_scanner(url, secure = True):
    if secure == True:
        my_secure = "https://"

    if secure == False:
        my_secure = "http://"
        
    my_list = []
    my_url = my_secure + url
    
    #malicious script
    mal_script = "<script>alert('The Silent')</script>"

    clear()

    user_input = input("1 = scan url | 2 = scan url and hyperlinks (requests) | 3 = scan url and hyperlinks (selenium)\n")

    clear()

    if user_input == "1":
        try:
            super_result = my_url.split("=")
            print("checking: " + super_result[0] + "=" + mal_script)
            result = web_session.get(super_result[0] + "=" + mal_script, verify = True, headers = user_agent, timeout = (5, 30))

            if mal_script in result.text:
                print("True: " + super_result[0] + "=" + mal_script + " (script in url)")
                my_list.append(super_result[0] + "=" + mal_script + " (script in url)")

        except requests.exceptions.SSLError:
            print("ERROR: invalid certificate!")
            pass

        except urllib3.exceptions.LocationParseError:
            print("ERROR: location parse error!")
            pass

        except requests.exceptions.ConnectionError:
            print("ERROR: connection error!")
            pass

        except requests.exceptions.ConnectTimeout:
            print("ERROR: connect timeout!")
            pass

        except requests.exceptions.InvalidSchema:
            print("ERROR: invalid schema!")
            pass

        except requests.exceptions.InvalidURL:
            print("ERROR: invalid url!")
            pass

        except requests.exceptions.MissingSchema:
            print("ERROR: missing schema!")
            pass

        except requests.exceptions.TooManyRedirects:
            print("ERROR: too many redirects!")
            pass

        except requests.exceptions.ReadTimeout:
            print("ERROR: read timeout!")
            pass

        except UnicodeError:
            pass
        
        try:
            print("checking: " + my_url + mal_script)
            result = web_session.get(my_url + mal_script, verify = True, headers = user_agent, timeout = (5, 30))

            if mal_script in result.text:
                print("True: " + my_url + mal_script + " (script in url)")
                my_list.append(my_url + mal_script + " (script in url)")

        except requests.exceptions.SSLError:
            print("ERROR: invalid certificate!")
            pass

        except urllib3.exceptions.LocationParseError:
            print("ERROR: location parse error!")
            pass

        except requests.exceptions.ConnectionError:
            print("ERROR: connection error!")
            pass

        except requests.exceptions.ConnectTimeout:
            print("ERROR: connect timeout!")
            pass

        except requests.exceptions.InvalidSchema:
            print("ERROR: invalid schema!")
            pass

        except requests.exceptions.InvalidURL:
            print("ERROR: invalid url!")
            pass

        except requests.exceptions.MissingSchema:
            print("ERROR: missing schema!")
            pass

        except requests.exceptions.TooManyRedirects:
            print("ERROR: too many redirects!")
            pass

        except requests.exceptions.ReadTimeout:
            print("ERROR: read timeout!")
            pass

        except UnicodeError:
            pass

        try:
            print("Checking for forms on: " + my_url)
            
            result = web_session.get(my_url, verify = True, headers = user_agent, timeout = (5, 30))

            try:
                soup = BeautifulSoup(result.text, "html.parser")
                get_input = soup.find_all("input")

            except:
                pass

            form_list = []

            for i in get_input:
                if "email" in str(i):
                    form_name = ""

                    try:
                        parse_name_start = str(i).index("name=\"")
                        parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))
                        
                        for ii in range(parse_name_start + 6, parse_name_end):
                            form_name = form_name + str(i)[ii]

                        form_list.append(form_name)

                    except:
                        pass

                if "hidden" in str(i):
                    form_name = ""

                    try:
                        parse_name_start = str(i).index("name=\"")
                        parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))

                        for ii in range(parse_name_start + 6, parse_name_end):
                            form_name = form_name + str(i)[ii]

                        form_list.append(form_name)

                    except:
                        pass
                    
                if "number" in str(i):
                    form_name = ""

                    try:
                        parse_name_start = str(i).index("name=\"")
                        parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))

                        for ii in range(parse_name_start + 6, parse_name_end):
                            form_name = form_name + str(i)[ii]

                        form_list.append(form_name)

                    except:
                        pass

                if "password" in str(i):
                    form_name = ""

                    try:
                        parse_name_start = str(i).index("name=\"")
                        parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))

                        for ii in range(parse_name_start + 6, parse_name_end):
                            form_name = form_name + str(i)[ii]

                        form_list.append(form_name)

                    except:
                        pass

                if "query" in str(i):
                    form_name = ""

                    try:
                        parse_name_start = str(i).index("name=\"")
                        parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))
                        
                        for ii in range(parse_name_start + 6, parse_name_end):
                            form_name = form_name + str(i)[ii]

                        form_list.append(form_name)

                    except:
                        pass

                if "search" in str(i):
                    form_name = ""

                    try:
                        parse_name_start = str(i).index("name=\"")
                        parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))

                        for ii in range(parse_name_start + 6, parse_name_end):
                            form_name = form_name + str(i)[ii]

                        form_list.append(form_name)

                    except:
                        pass

                if "tel" in str(i):
                    form_name = ""

                    try:
                        parse_name_start = str(i).index("name=\"")
                        parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))
                        
                        for ii in range(parse_name_start + 6, parse_name_end):
                            form_name = form_name + str(i)[ii]

                        form_list.append(form_name)

                    except:
                        pass

                if "text" in str(i):
                    form_name = ""

                    try:
                        parse_name_start = str(i).index("name=\"")
                        parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))
                        
                        for ii in range(parse_name_start + 6, parse_name_end):
                            form_name = form_name + str(i)[ii]

                        form_list.append(form_name)

                    except:
                        pass

                if "url" in str(i):
                    form_name = ""

                    try:
                        parse_name_start = str(i).index("name=\"")
                        parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))
                        
                        for ii in range(parse_name_start + 6, parse_name_end):
                            form_name = form_name + str(i)[ii]

                        form_list.append(form_name)

                    except:
                        pass

                form_list = list(dict.fromkeys(form_list))
                form_list.sort()

                for forms in form_list:
                    print("checking form: " + forms)
                    mal_dict = {forms: mal_script}

                    get_data = web_session.get(my_url, params = mal_dict, verify = True, headers = user_agent, timeout = (5, 30))
                    send_data = web_session.post(my_url, data = mal_dict, verify = True, headers = user_agent, timeout = (5, 30))

                    if mal_script in send_data.text or mal_script in get_data.text:
                        print("true: " + url + " form: " + forms)
                        my_list.append(url + " form: " + forms)

        except requests.exceptions.SSLError:
            print("ERROR: invalid certificate!")
            pass

        except urllib3.exceptions.LocationParseError:
            print("ERROR: location parse error!")
            pass

        except requests.exceptions.ConnectionError:
            print("ERROR: connection error!")
            pass

        except requests.exceptions.ConnectTimeout:
            print("ERROR: connect timeout!")
            pass

        except requests.exceptions.InvalidSchema:
            print("ERROR: invalid schema!")
            pass

        except requests.exceptions.InvalidURL:
            print("ERROR: invalid url!")
            pass

        except requests.exceptions.MissingSchema:
            print("ERROR: missing schema!")
            pass

        except requests.exceptions.TooManyRedirects:
            print("ERROR: too many redirects!")
            pass

        except requests.exceptions.ReadTimeout:
            print("ERROR: read timeout!")
            pass

        except UnicodeError:
            pass

    if user_input == "2":
        my_result = search_engine_website(url, secure = secure) 

        for links in my_result:
            try:
                super_result = links.split("=")
                print("checking: " + super_result[0] + "=" + mal_script)
                result = web_session.get(super_result[0] + "=" + mal_script, verify = True, headers = user_agent, timeout = (5, 30))

                if mal_script in result.text:
                    print("True: " + super_result[0] + "=" + mal_script + " (script in url)")
                    my_list.append(super_result[0] + "=" + mal_script + " (script in url)")

            except requests.exceptions.SSLError:
                print("ERROR: invalid certificate!")
                pass

            except urllib3.exceptions.LocationParseError:
                print("ERROR: location parse error!")
                pass

            except requests.exceptions.ConnectionError:
                print("ERROR: connection error!")
                pass

            except requests.exceptions.ConnectTimeout:
                print("ERROR: connect timeout!")
                pass

            except requests.exceptions.InvalidSchema:
                print("ERROR: invalid schema!")
                pass

            except requests.exceptions.InvalidURL:
                print("ERROR: invalid url!")
                pass

            except requests.exceptions.MissingSchema:
                print("ERROR: missing schema!")
                pass

            except requests.exceptions.TooManyRedirects:
                print("ERROR: too many redirects!")
                pass

            except requests.exceptions.ReadTimeout:
                print("ERROR: read timeout!")
                pass

            except UnicodeError:
                pass
                
            try:
                print("checking: " + links + mal_script)
                
                result = web_session.get(links + mal_script, verify = True, headers = user_agent, timeout = (5, 30))

                if mal_script in result.text:
                    print("True: " + links  + mal_script + " (script in url)")
                    my_list.append(links  + mal_script + " (script in url)")

            except requests.exceptions.SSLError:
                print("ERROR: invalid certificate!")
                pass

            except urllib3.exceptions.LocationParseError:
                print("ERROR: location parse error!")
                pass

            except requests.exceptions.ConnectionError:
                print("ERROR: connection error!")
                pass

            except requests.exceptions.ConnectTimeout:
                print("ERROR: connect timeout!")
                pass

            except requests.exceptions.InvalidSchema:
                print("ERROR: invalid schema!")
                pass

            except requests.exceptions.InvalidURL:
                print("ERROR: invalid url!")
                pass

            except requests.exceptions.MissingSchema:
                print("ERROR: missing schema!")
                pass

            except requests.exceptions.TooManyRedirects:
                print("ERROR: too many redirects!")
                pass

            except requests.exceptions.ReadTimeout:
                print("ERROR: read timeout!")
                pass

            except UnicodeError:
                pass

            try:
                print("checking for forms on: " + links)

                result = web_session.get(links, verify = True, headers = user_agent, timeout = (5, 30))

                try:
                    soup = BeautifulSoup(result.text, "html.parser")
                    get_input = soup.find_all("input")

                except:
                    pass

                form_list = []

                for i in get_input:
                    if "email" in str(i):
                        form_name = ""

                        try:
                            parse_name_start = str(i).index("name=\"")
                            parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))
                            
                            for ii in range(parse_name_start + 6, parse_name_end):
                                form_name = form_name + str(i)[ii]

                            form_list.append(form_name)

                        except:
                            pass

                    if "hidden" in str(i):
                        form_name = ""

                        try:
                            parse_name_start = str(i).index("name=\"")
                            parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))

                            for ii in range(parse_name_start + 6, parse_name_end):
                                form_name = form_name + str(i)[ii]

                            form_list.append(form_name)

                        except:
                            pass
                        
                    if "number" in str(i):
                        form_name = ""

                        try:
                            parse_name_start = str(i).index("name=\"")
                            parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))

                            for ii in range(parse_name_start + 6, parse_name_end):
                                form_name = form_name + str(i)[ii]

                            form_list.append(form_name)

                        except:
                            pass

                    if "password" in str(i):
                        form_name = ""

                        try:
                            parse_name_start = str(i).index("name=\"")
                            parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))

                            for ii in range(parse_name_start + 6, parse_name_end):
                                form_name = form_name + str(i)[ii]

                            form_list.append(form_name)

                        except:
                            pass

                    if "query" in str(i):
                        form_name = ""

                        try:
                            parse_name_start = str(i).index("name=\"")
                            parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))
                            
                            for ii in range(parse_name_start + 6, parse_name_end):
                                form_name = form_name + str(i)[ii]

                            form_list.append(form_name)

                        except:
                            pass

                    if "search" in str(i):
                        form_name = ""

                        try:
                            parse_name_start = str(i).index("name=\"")
                            parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))

                            for ii in range(parse_name_start + 6, parse_name_end):
                                form_name = form_name + str(i)[ii]

                            form_list.append(form_name)

                        except:
                            pass

                    if "search" in str(i):
                        form_name = ""

                        try:
                            parse_name_start = str(i).index("name=\"")
                            parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))
                            
                            for ii in range(parse_name_start + 6, parse_name_end):
                                form_name = form_name + str(i)[ii]

                            form_list.append(form_name)

                        except:
                            pass

                    if "tel" in str(i):
                        form_name = ""

                        try:
                            parse_name_start = str(i).index("name=\"")
                            parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))
                            
                            for ii in range(parse_name_start + 6, parse_name_end):
                                form_name = form_name + str(i)[ii]

                            form_list.append(form_name)

                        except:
                            pass

                    if "text" in str(i):
                        form_name = ""

                        try:
                            parse_name_start = str(i).index("name=\"")
                            parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))
                            
                            for ii in range(parse_name_start + 6, parse_name_end):
                                form_name = form_name + str(i)[ii]

                            form_list.append(form_name)

                        except:
                            pass

                    if "url" in str(i):
                        form_name = ""

                        try:
                            parse_name_start = str(i).index("name=\"")
                            parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))
                            
                            for ii in range(parse_name_start + 6, parse_name_end):
                                form_name = form_name + str(i)[ii]

                            form_list.append(form_name)

                        except:
                            pass

                form_list = list(dict.fromkeys(form_list))
                form_list.sort()

                for forms in form_list:
                    print("checking form: " + forms)
                    mal_dict = {forms: mal_script}

                    get_data = web_session.get(links, params = mal_dict, verify = True, headers = user_agent, timeout = (5, 30))
                    send_data = web_session.post(links, data = mal_dict, verify = True, headers = user_agent, timeout = (5, 30))

                    if mal_script in send_data.text or mal_script in get_data.text:
                        print("true: " + links + " form: " + forms)
                        my_list.append(links + " form: " + forms)

            except requests.exceptions.SSLError:
                print("ERROR: invalid certificate!")
                pass

            except urllib3.exceptions.LocationParseError:
                print("ERROR: location parse error!")
                pass

            except requests.exceptions.ConnectionError:
                print("ERROR: connection error!")
                pass

            except requests.exceptions.ConnectTimeout:
                print("ERROR: connect timeout!")
                pass

            except requests.exceptions.InvalidSchema:
                print("ERROR: invalid schema!")
                pass

            except requests.exceptions.InvalidURL:
                print("ERROR: invalid url!")
                pass

            except requests.exceptions.MissingSchema:
                print("ERROR: missing schema!")
                pass

            except requests.exceptions.TooManyRedirects:
                print("ERROR: too many redirects!")
                pass

            except requests.exceptions.ReadTimeout:
                print("ERROR: read timeout!")
                pass

            except UnicodeError:
                pass

    if user_input == "3":
        my_result = link_scanner_selenium(url) 

        for links in my_result:
            try:
                super_result = links.split("=")
                print("checking: " + super_result[0] + "=" + mal_script)
                result = web_session.get(super_result[0] + "=" + mal_script, verify = True, headers = user_agent, timeout = (5, 30))

                if mal_script in result.text:
                    print("True: " + super_result[0] + "=" + mal_script + " (script in url)")
                    my_list.append(super_result[0] + "=" + mal_script + " (script in url)")

            except requests.exceptions.SSLError:
                print("ERROR: invalid certificate!")
                pass

            except urllib3.exceptions.LocationParseError:
                print("ERROR: location parse error!")
                pass

            except requests.exceptions.ConnectionError:
                print("ERROR: connection error!")
                pass

            except requests.exceptions.ConnectTimeout:
                print("ERROR: connect timeout!")
                pass

            except requests.exceptions.InvalidSchema:
                print("ERROR: invalid schema!")
                pass

            except requests.exceptions.InvalidURL:
                print("ERROR: invalid url!")
                pass

            except requests.exceptions.MissingSchema:
                print("ERROR: missing schema!")
                pass

            except requests.exceptions.TooManyRedirects:
                print("ERROR: too many redirects!")
                pass

            except requests.exceptions.ReadTimeout:
                print("ERROR: read timeout!")
                pass

            except UnicodeError:
                pass
                
            try:
                print("checking: " + links + mal_script)
                
                result = web_session.get(links + mal_script, verify = True, headers = user_agent, timeout = (5, 30))

                if mal_script in result.text:
                    print("True: " + links  + mal_script + " (script in url)")
                    my_list.append(links  + mal_script + " (script in url)")

            except requests.exceptions.SSLError:
                print("ERROR: invalid certificate!")
                pass

            except urllib3.exceptions.LocationParseError:
                print("ERROR: location parse error!")
                pass

            except requests.exceptions.ConnectionError:
                print("ERROR: connection error!")
                pass

            except requests.exceptions.ConnectTimeout:
                print("ERROR: connect timeout!")
                pass

            except requests.exceptions.InvalidSchema:
                print("ERROR: invalid schema!")
                pass

            except requests.exceptions.InvalidURL:
                print("ERROR: invalid url!")
                pass

            except requests.exceptions.MissingSchema:
                print("ERROR: missing schema!")
                pass

            except requests.exceptions.TooManyRedirects:
                print("ERROR: too many redirects!")
                pass

            except requests.exceptions.ReadTimeout:
                print("ERROR: read timeout!")
                pass

            except UnicodeError:
                pass

            try:
                print("checking for forms on: " + links)

                result = web_session.get(links, verify = True, headers = user_agent, timeout = (5, 30))

                try:
                    soup = BeautifulSoup(result.text, "html.parser")
                    get_input = soup.find_all("input")

                except:
                    pass

                form_list = []

                for i in get_input:
                    if "email" in str(i):
                        form_name = ""

                        try:
                            parse_name_start = str(i).index("name=\"")
                            parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))
                            
                            for ii in range(parse_name_start + 6, parse_name_end):
                                form_name = form_name + str(i)[ii]

                            form_list.append(form_name)

                        except:
                            pass

                    if "hidden" in str(i):
                        form_name = ""

                        try:
                            parse_name_start = str(i).index("name=\"")
                            parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))

                            for ii in range(parse_name_start + 6, parse_name_end):
                                form_name = form_name + str(i)[ii]

                            form_list.append(form_name)

                        except:
                            pass
                        
                    if "number" in str(i):
                        form_name = ""

                        try:
                            parse_name_start = str(i).index("name=\"")
                            parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))

                            for ii in range(parse_name_start + 6, parse_name_end):
                                form_name = form_name + str(i)[ii]

                            form_list.append(form_name)

                        except:
                            pass

                    if "password" in str(i):
                        form_name = ""

                        try:
                            parse_name_start = str(i).index("name=\"")
                            parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))

                            for ii in range(parse_name_start + 6, parse_name_end):
                                form_name = form_name + str(i)[ii]

                            form_list.append(form_name)

                        except:
                            pass

                    if "query" in str(i):
                        form_name = ""

                        try:
                            parse_name_start = str(i).index("name=\"")
                            parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))
                            
                            for ii in range(parse_name_start + 6, parse_name_end):
                                form_name = form_name + str(i)[ii]

                            form_list.append(form_name)

                        except:
                            pass

                    if "search" in str(i):
                        form_name = ""

                        try:
                            parse_name_start = str(i).index("name=\"")
                            parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))

                            for ii in range(parse_name_start + 6, parse_name_end):
                                form_name = form_name + str(i)[ii]

                            form_list.append(form_name)

                        except:
                            pass

                    if "search" in str(i):
                        form_name = ""

                        try:
                            parse_name_start = str(i).index("name=\"")
                            parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))
                            
                            for ii in range(parse_name_start + 6, parse_name_end):
                                form_name = form_name + str(i)[ii]

                            form_list.append(form_name)

                        except:
                            pass

                    if "tel" in str(i):
                        form_name = ""

                        try:
                            parse_name_start = str(i).index("name=\"")
                            parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))
                            
                            for ii in range(parse_name_start + 6, parse_name_end):
                                form_name = form_name + str(i)[ii]

                            form_list.append(form_name)

                        except:
                            pass

                    if "text" in str(i):
                        form_name = ""

                        try:
                            parse_name_start = str(i).index("name=\"")
                            parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))
                            
                            for ii in range(parse_name_start + 6, parse_name_end):
                                form_name = form_name + str(i)[ii]

                            form_list.append(form_name)

                        except:
                            pass

                    if "url" in str(i):
                        form_name = ""

                        try:
                            parse_name_start = str(i).index("name=\"")
                            parse_name_end = str(i).index("\"", parse_name_start + 6, len(str(i)))
                            
                            for ii in range(parse_name_start + 6, parse_name_end):
                                form_name = form_name + str(i)[ii]

                            form_list.append(form_name)

                        except:
                            pass

                form_list = list(dict.fromkeys(form_list))
                form_list.sort()

                for forms in form_list:
                    print("checking form: " + forms)
                    mal_dict = {forms: mal_script}

                    get_data = web_session.get(links, params = mal_dict, verify = True, headers = user_agent, timeout = (5, 30))
                    send_data = web_session.post(links, data = mal_dict, verify = True, headers = user_agent, timeout = (5, 30))

                    if mal_script in send_data.text or mal_script in get_data.text:
                        print("true: " + links + " form: " + forms)
                        my_list.append(links + " form: " + forms)

            except requests.exceptions.SSLError:
                print("ERROR: invalid certificate!")
                pass

            except urllib3.exceptions.LocationParseError:
                print("ERROR: location parse error!")
                pass

            except requests.exceptions.ConnectionError:
                print("ERROR: connection error!")
                pass

            except requests.exceptions.ConnectTimeout:
                print("ERROR: connect timeout!")
                pass

            except requests.exceptions.InvalidSchema:
                print("ERROR: invalid schema!")
                pass

            except requests.exceptions.InvalidURL:
                print("ERROR: invalid url!")
                pass

            except requests.exceptions.MissingSchema:
                print("ERROR: missing schema!")
                pass

            except requests.exceptions.TooManyRedirects:
                print("ERROR: too many redirects!")
                pass

            except requests.exceptions.ReadTimeout:
                print("ERROR: read timeout!")
                pass

            except UnicodeError:
                pass

    my_list = list(dict.fromkeys(my_list))
    my_list.sort()

    clear()

    return my_list
