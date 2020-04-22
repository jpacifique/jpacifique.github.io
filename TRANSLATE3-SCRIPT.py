#!/usr/bin/env python
# coding: utf-8

# ## "journal pacifique" web bot
# parses sources for new articles, translates them into target languages ["es","pt","pl","zh-CN"]. Wraps it up in a simple html document and writes it out to the appropriate directory.
# 
# #### TO DO TECHNICAL:
# 
# *   save the articles dictionary as a json or something (__done__)
# *   *   (dic backup for later design changes) important
# *   implement an automatic parser (__done(sd)__)
# *   detect and highlight keywords
# *   automatic git push (__done__ but pass cache time should be increased)
# *   run the script on an aws server
# *   maybe an open source grammar rating mechanism?
# *   don't send a separate request to the website for every translation (__done__)
# *   same pages shouldn't be crawled twice. Even if they are crawled they shouldn't be overwritten. (__done__)
# *   implement waiting if requests exhaust limit
# *   also implement a timeout. maybe take articles into a queue.
# *   re-read SD's [terms](https://www.sciencedaily.com/terms.htm) on reproduction. (especially on images)
# *   take the bot 1 directory up so it won't be pushed into the public repo. (__done__)
# 
# #### TO DO GRAPHICAL
# *   responsive text, currently changes size by page??
# *   resizable design (__done__)
# *   mobile-friendly design
# *   *   [media queries for different device widths](https://stackoverflow.com/questions/16387400/getting-the-right-font-size-on-every-mobile-device)
# *   subscribe and social media block
# 
# 
# #### POSSIBLE SOURCES
# *   [the conversation](https://theconversation.com/uk/republishing-guidelines)
# *   *   approval needed for translation
# *   
# 
# NOTE: google transalte tokens refresh every hour (?)
# 
# 
# 
# 
# 
# 
# ---
# 
# 

# In[55]:


#for colab
#!pip install googletrans
#!pip install mechanize

## Character limit: 15K


# In[56]:


#import os
#cmd = "cd cemreefe.github.io; git pull; cd .."
#os.system(cmd)


# In[57]:


from googletrans import Translator
import re

translator = Translator()


# In[58]:


def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""


# In[59]:


def string_strip(s):
    return re.sub(r"[^A-Za-z0-9]", "-", s)


# In[60]:


from urllib.request import Request, urlopen
from random import randrange

def sciencedaily_parse_article(url):
  
    site = url
    html_string = ""
    tagged_w_ps = ""

    # parse html

    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()

    html_string = webpage.decode("utf-8") 
  
    # get info
  
    # get the headline

    headline = find_between(html_string, '<h1 id="headline" class="headline">','</h1>')
  
    # get the meta
  
    meta     = find_between(html_string, '<dd id="abstract">','</dd>')
  
    # get the img address
  
    imgaddr  = find_between(html_string, 'center-block" src="','"')
    
    # set imgaddr image from sciencedaily if it exists. Else use one of the dummy imgs.
    
    if(imgaddr!=""):
        imgaddr  = 'https://www.sciencedaily.com'+imgaddr
    else:
        imgaddr  = '../../../img/dummy'+repr(randrange(20))+'.jpeg'
    
    # get random image from dummies since sciencedaily images get dead links later on.
    #imgaddr  = '../../../img/dummy'+repr(randrange(20))+'.jpeg'
  
    # get the img alt
  
    imgalt   = find_between(html_string, '<div class="photo-caption">','</div>')
    cred     = '\t'+find_between(html_string, '<div class="photo-credit"><em>','</div>')
  
    # get the citation
  
    citation = find_between(html_string, '<div role="tabpanel" class="tab-pane active" id="citation_mla">','</div>')
  
    
    # get the article itself

    article  = find_between(html_string, '<div id="text">','</div>')
    article  = re.sub(r"<p>" ,     "", article)
    article  = re.sub(r"</p>", "\n", article)
  
    # get the href at the end if it exists
    href_tab = ""
    href_tab = href_tab + find_between(article, '<a href','</a>')
  
    # delete the href and useless tags from the article
  
    article  = re.sub(r"<a href.*?</a>", "", article)
    article  = re.sub(r"<.*?>", "",          article)
    article  = re.sub(r" -- ", ", ",         article)
  
    # special characters, this list will expand.
  
    #article  = re.sub(r"&uuml;", "ü",         article)
    #article  = re.sub(r"&ouml;", "ö",         article)
    #article  = re.sub(r"&eacute;", "e",         article)
    # new sltn:
    import html
    article   = html.unescape(article)
      
            #y                    #y                                #y                                                       #y                  
    return {"headline": headline, "meta": meta, "imgaddr": imgaddr, "imgalt": imgalt, "imgcredit":cred,"citation": citation, "article": article, "href": href_tab}
  


# In[61]:


def get_translation(article_dictionary,target_language):
    big_string= ""
    translations = {}
    token_in = "(#@)"
    if (target_language=="zh-CN"):
        token_out = "（＃@）"
    else: token_out="(# @)"
      
    
    #sırası karışmasın!! keylerden array oluştur, arrayi itere et.
    keys = ["headline","meta","article","imgalt"]
    
    for key in keys:
        print(key)
        if big_string != "":
            big_string = big_string + token_in + article_dictionary[key]
        else:
            big_string = article_dictionary[key]
            
    big_translated_string = translator.translate(big_string,dest=target_language).text
    
    translations_array    = big_translated_string.split(token_out)
   
    #print(big_translated_string)
    #print(len(translations_array),translations_array)
    
    for i in range (4):
        translations[keys[i]]=translations_array[i]
    translations["imgaddr"]=article_dictionary["imgaddr"]
    translations["citation"]=article_dictionary["citation"]
    translations["imgcredit"]=article_dictionary["imgcredit"]
    translations["href"]=article_dictionary["href"]
    translations["org-headline"]=article_dictionary["headline"]
    translations["lang"]=target_language
    

    return translations


# In[62]:


("# deprecated")
def get_language_dictionary(target_language):
    ld = {}
    words = ["journal pacifique", "homepage", "archive", "about us", "source:"]
    for word in words:
        print(word)
        ld[word] = translator.translate(word, dest=target_language).text
    return ld


# In[63]:


def html_from_dictionary(translated_dictionary, target_language, language_dictionary): # translated & language could be just one dictionary this was stupid.
  
    from datetime import date
    hoy  = date.today()
    d1   = hoy.strftime("%d/%m/%Y")
  
    html = open(SUBFOLDER + "jp.temp").read()

    html_article = re.sub(r"\n\n", "</p>\n\n<p>",   translated_dictionary["article"])
    html_article = "<p>" + html_article + "</p>"

    print(translated_dictionary["headline"])
  
    html = re.sub(r"\$\$article-title%%",  translated_dictionary["headline"],         html)
    html = re.sub(r"\$\$img-alt%%",        translated_dictionary["imgalt"],           html)
    html = re.sub(r"\$\$article-meta%%",   translated_dictionary["meta"],             html)
    html = re.sub(r"\$\$source%%",         translated_dictionary["citation"],            html)
    html = re.sub(r"\$\$img.jpg%%",        translated_dictionary["imgaddr"],             html)
    html = re.sub(r"\$\$article-text%%",   html_article                  ,            html)
  
    html = re.sub(r"\$\$home%%",           language_dictionary["homepage-"+target_language],           html)
    html = re.sub(r"\$\$archive%%",        language_dictionary["archive-"+target_language],            html)
    html = re.sub(r"\$\$about%%",          language_dictionary["about us-"+target_language],           html)
    html = re.sub(r"\$\$jp-translation%%", language_dictionary["journal pacifique-"+target_language],  html)
    html = re.sub(r"\$\$taken-from%%",     language_dictionary["source:-"+target_language],            html)
    html = re.sub(r"\$\$target-languages%%",     target_language,            html)
  
    html = re.sub(r"\$\$imgcredit%%",       translated_dictionary["imgcredit"],          html)
  
    html = re.sub(r"\$\$href%%",           translated_dictionary["href"],            html)
  
    html = re.sub(r"-- ", ",",  html)
 
    html = re.sub(r"\$\$date%%", d1, html)
  
    #html = re.sub(r'</head>', '<style> p { text-indent: 30px;} </style>\n\t</head>', html)
  
    return html
  


# In[64]:


def getnewpath(translated_dict):
  
    from datetime import date
    hoy  = date.today()
    date = hoy.strftime("%Y-%m-%d")
    
    translated_dict["date"]=date
  
    urlheadline = string_strip(translated_dict["org-headline"])+"-"+translated_dict["lang"]
    postsfolder = "/posts/"+date+"/"
    newpathaddr = translated_dict["lang"]+postsfolder
    newheadline = newpathaddr+urlheadline+".html"
    newheadlang = postsfolder+urlheadline+".html"
    
    translated_dict["pathfromhome"]=newheadline
    translated_dict["pathfromlang"]=newheadlang
    
    # this was implemented for short headlines (~10char)
    #if newheadline in headlinessofar:
    #    c=2
    #    while (newheadline[:-5]+repr(c)+newheadline[-5:] in headlinessofar):
    #        c+=1
    #    newheadline = newheadline[:-5]+repr(c)+newheadline[-5:]
    
    headlinessofar.append(newheadline)
    return [newheadline,newpathaddr,urlheadline]


# In[65]:


SUBFOLDER = ""


# In[66]:


import pickle

def save_obj(obj, name ):
    with open(SUBFOLDER+'obj/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name ):
    with open(SUBFOLDER+'obj/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)


# In[67]:


def dic_to_dirfile(dic,target_language, elements_dictionary):
    
    #we used to translate all elements at every step, now it is automated due to
    #google translate's quota restrictions.
    
    #zh_ld = get_language_dictionary(target_language)

    tr_di = get_translation(dic,target_language)
    htmlx = html_from_dictionary(tr_di, target_language, elements_dictionary)
  
    newdirs = getnewpath(tr_di)
  
    import os
    cmd = "mkdir -p "+SUBFOLDER+newdirs[1]
    os.system(cmd)
  
    f= open(SUBFOLDER+newdirs[0],"w+")
    f.write(htmlx)

    return [htmlx,tr_di,newdirs[2],newdirs[0]]


# In[68]:


def targdic_to_dirfile(tr_di,target_language, elements_dictionary):
    
    htmlx = html_from_dictionary(tr_di, target_language, elements_dictionary)
  
    newdirs = getnewpath(tr_di)
  
    import os
    cmd = "mkdir -p "+SUBFOLDER+newdirs[1]
    os.system(cmd)
  
    f= open(SUBFOLDER+newdirs[0],"w+")
    f.write(htmlx)
    
    print(SUBFOLDER+newdirs[0])
  
    return [htmlx,tr_di,newdirs[2],newdirs[0]]


# In[129]:


elements_dictionary = {
    "journal pacifique-es":"periódico pacífico", 
    "homepage-es":"página principal", 
    "archive-es":"archivo",
    "about us-es":"sobre nosotros",
    "source:-es":"fuente:",
    "journal pacifique-pt":"jornal pacífico", 
    "homepage-pt":"pagina inicial", 
    "archive-pt":"arquivo",
    "about us-pt":"sobre nós",
    "source:-pt":"fonte:",
    "journal pacifique-tr":"barışçıl gazete", 
    "homepage-tr":"anasayfa", 
    "archive-tr":"arşiv",
    "about us-tr":"hakkında",
    "source:-tr":"kaynakça:",
    "journal pacifique-zh-CN":"和平的报纸", 
    "homepage-zh-CN":"主页", 
    "archive-zh-CN":"档案",
    "about us-zh-CN":"关于我们",
    "source:-zh-CN":"资源",
    "journal pacifique-pl":"spokojna gazeta", 
    "homepage-pl":"strona główna", 
    "archive-pl":"archiwum",
    "about us-pl":"o nas",
    "source:-pl":"źródło",
    "latest-articles-es":"Últimos artículos",
    "latest-articles-pt":"Artigos Mais Recentes",
    "latest-articles-pl":"Ostatnie artykuły",
    "latest-articles-zh-CN":"最新的文章",
    "latest_articles-tr":"En yeni makaleler",
    "hometext-es":"Bienvenido a Journal Pacifique. Le proporcionamos los últimos artículos sobre ciencia y tecnología. Journal Pacifique se dedica a la distribución de investigaciones científicas populares en otros idiomas además del inglés.",
    "hometext-pt":"Bem-vindo ao Journal Pacifique. Fornecemos os artigos mais recentes sobre ciência e tecnologia. O Journal Pacifique é dedicado à distribuição de pesquisas científicas populares em outros idiomas que não o inglês.",
    "hometext-pl":"Witamy w Journal Pacifique. Zapewniamy najnowsze artykuły na temat nauki i technologii. Czasopismo Pacifique poświęcone jest rozpowszechnianiu popularnych badań naukowych w językach innych niż angielski.",
    "hometext-zh-CN":"欢迎来到Journal Pacifique。 我们为您提供有关科学和技术的最新文章。 Journal Pacifique致力于以英语以外的语言分发流行的科学研究。",
    "hometext-tr":"Journal Pacifique'e hoş geldiniz. Bilim ve teknoloji ile ilgili en son makaleleri size sunuyoruz. Journal Pacifique, popüler bilimsel araştırmaların İngilizce dışındaki dillerde dağıtımına adanmıştır.",
    "abouttext-es":"Journal Pacifique se estableció para evitar que la barrera del idioma obstruya la accesibilidad de los artículos científicos. En Journal Pacifique pensamos que todos los artículos científicos deberían ser fácilmente accesibles para las personas en su propio idioma. Por lo tanto, hemos asumido la responsabilidad de encontrar artículos en Internet de valor decente y traducirlos a tantos idiomas como sea posible, haciéndolos accesibles a muchas más personas de lo que era posible en su idioma original.",
    "abouttext-pt":"O Journal Pacifique foi criado para impedir que a barreira do idioma obstrua a acessibilidade de artigos científicos. No Journal Pacifique, pensamos que todos os artigos científicos devem ser facilmente acessíveis às pessoas em seu próprio idioma. Portanto, assumimos a responsabilidade de encontrar artigos na Internet de valor decente e traduzi-los para o maior número possível de idiomas, tornando-os acessíveis a muito mais pessoas do que era possível em seu idioma original.",
    "abouttext-pl":"Journal Pacifique został utworzony, aby bariera językowa nie utrudniała dostępu do artykułów naukowych. W Journal Pacifique uważamy, że wszystkie artykuły naukowe powinny być łatwo dostępne dla ludzi w ich własnym języku. Dlatego podjęliśmy się odpowiedzialności za znalezienie artykułów w Internecie o przyzwoitej wartości i przetłumaczenie ich na jak najwięcej języków, dzięki czemu będą dostępne dla większej liczby osób niż było to możliwe w ich oryginalnym języku.",
    "abouttext-zh-CN":"Journal Pacifique的建立是为了防止语言障碍阻碍科学文章的可访问性。 Journal Pacifique认为我们所有的科学文章都应该易于人们以自己的语言阅读。 因此，我们承担了在互联网上查找具有体面价值的文章并将其翻译成尽可能多的语言的责任，从而使更多的人可以使用原始语言。",
    "abouttext-tr":"",
    "see-more-es":"Ver más",
    "see-more-pt":"Ver mais",
    "see-more-pl":"Zobacz więcej",
    "see-more-zh-CN":"看更多",
    "see-more-tr":"Daha fazla",
}


# In[130]:


def url_to_dirfile(url,target_language):

    ar_di = sciencedaily_parse_article(url)

    htmlx = dic_to_dirfile(ar_di,target_language, elements_dictionary)
  
    return [htmlx,ar_di]


# In[131]:


def get_article_urls_sd():

    main = "https://www.sciencedaily.com/news/top/technology/"
    req = Request(main, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    main_html = webpage.decode("utf-8") 
    
    links = []
    
    headline  = find_between(main_html, '<h5 class="clearfix"><a href="','">')
    
    for i in range(12):
        main_html = main_html[main_html.index(headline)+len(headline):]
        links.append("https://www.sciencedaily.com"+headline)
        headline  = find_between(main_html, '<h5 class="clearfix"><a href="','">')

    return links


# In[132]:


articles = get_article_urls_sd()
            
languages = ["es","pt","pl","zh-CN"]


# In[133]:


articles


# In[134]:


#headlinessofar = []
#articlessofar  = {}
#articleurlssofar = []


# In[135]:


headlinessofar = load_obj("headlinessofar")
articlessofar = load_obj("articlessofar")
articleurlssofar =load_obj("articleurlssofar")


# In[136]:


#refresh already saved articles' html
#for when a design change is implemented.
import time

for article in articlessofar:
    tmp = targdic_to_dirfile(articlessofar[article], articlessofar[article]["lang"], elements_dictionary)


# In[137]:


import time
test_enable = False

for article in articles:
    if (article not in articleurlssofar) or test_enable:
        dic = sciencedaily_parse_article(article)
        for target_language in languages:
                tmp = dic_to_dirfile(dic,target_language, elements_dictionary)
                articlessofar[tmp[2]]=tmp[1]
        articleurlssofar.append(article)


# In[138]:


save_obj(headlinessofar,     "headlinessofar")
save_obj(articlessofar,       "articlessofar")
save_obj(articleurlssofar, "articleurlssofar")


# In[139]:


#get most recent 9 articles and get their "keys"

def form_index(target_language):
  
    homepage_text="welcome my friend we have carpets."
 
    html = open(SUBFOLDER + "jp-index.temp").read()
    
    from datetime import date
    hoy  = date.today()
    d1   = hoy.strftime("%d/%m/%Y")
    
    html = re.sub(r"\$\$date%%", d1, html)

    html = re.sub(r"\$\$home%%",           elements_dictionary["homepage-"+target_language],           html)
    html = re.sub(r"\$\$archive%%",        elements_dictionary["archive-"+target_language],            html)
    html = re.sub(r"\$\$about%%",          elements_dictionary["about us-"+target_language],           html)
    html = re.sub(r"\$\$jp-translation%%", elements_dictionary["journal pacifique-"+target_language],  html)
    html = re.sub(r"\$\$latest-articles%%",elements_dictionary["latest-articles-"+target_language],    html)
    
    #save these to elements dictionary
    html = re.sub(r"\$\$homepage-text%%",  elements_dictionary["hometext-"+target_language],    html)
    
    html = re.sub(r"\$\$see-more%%",  elements_dictionary["see-more-"+target_language],    html)
    
    html = re.sub(r"\$\$target-language%%",target_language,  html)

    asfl = []
    for key in articlessofar:
        if(articlessofar[key]["lang"]==target_language):
            asfl.append(key)
            
    writenum = min(len(asfl),9)
    
    for i in range (writenum):
        j = writenum-i
        
        key = asfl[i]
    
        html = re.sub(r"\$\$article-link"+repr(j)+"%%",   articlessofar[key]["pathfromlang"][1:],           html)
        print(articlessofar[key]["pathfromlang"])
        html = re.sub(r"\$\$headline"+repr(j)+"%%",           articlessofar[key]["headline"],           html)
        #html = re.sub(r"\$\$headlinemeta"+repr(j)+"%%",           articlessofar[key]["meta"],           html)
        if(articlessofar[key]["imgaddr"][:2]!=".."):
            html = re.sub(r"\$\$headline-img"+repr(j)+"%%",      articlessofar[key]["imgaddr"],         html)
        else:
            html = re.sub(r"\$\$headline-img"+repr(j)+"%%",      articlessofar[key]["imgaddr"][6:],              html)
    
    return html


def refresh_indices():
    for language in languages:

        htmlx = form_index(language)
        path  = language +"/index.html"
        
        import os
        cmd = "mkdir -p "+SUBFOLDER+language
        os.system(cmd)
        cmd = "touch "+SUBFOLDER+path
        os.system(cmd)
        
        f= open(SUBFOLDER+path,"w+")
        f.write(htmlx)


# In[140]:


#get most recent 9 articles and get their "keys"

def form_archive(target_language):
 
    html = open(SUBFOLDER + "jp-archive.temp").read()
    
    from datetime import date
    hoy  = date.today()
    d1   = hoy.strftime("%d/%m/%Y")
    
    html = re.sub(r"\$\$date%%", d1, html)

    html = re.sub(r"\$\$home%%",           elements_dictionary["homepage-"+target_language],           html)
    html = re.sub(r"\$\$archive%%",        elements_dictionary["archive-"+target_language],            html)
    html = re.sub(r"\$\$about%%",          elements_dictionary["about us-"+target_language],           html)
    html = re.sub(r"\$\$jp-translation%%", elements_dictionary["journal pacifique-"+target_language],  html)
    html = re.sub(r"\$\$latest-articles%%",elements_dictionary["latest-articles-"+target_language],    html)
    
    html = re.sub(r"\$\$target-language%%",target_language,  html)

    asfl = []
    for key in articlessofar:
        if(articlessofar[key]["lang"]==target_language):
            asfl.append(key)
            
    writenum = len(asfl)
    
    archive_text = ""
    
    for i in range (writenum):
        j = writenum-i
        
        key = asfl[i]
        
        link = articlessofar[key]["pathfromlang"][1:]
        titl = articlessofar[key]["headline"]
        date = articlessofar[key]["date"]
        
        article_text = f"<p>{date} <a href=\"{link}\" style=\"font-weight:900;\">{titl}</a></p>\n"
    
        print(article_text)
        archive_text += article_text
        
    html = re.sub(r"\$\$archive-text%%",archive_text,  html)
    
    return html


def refresh_archives():
    for language in languages:

        htmlx = form_archive(language)
        path  = language +"/archive.html"
        
        import os
        cmd = "mkdir -p "+SUBFOLDER+language
        os.system(cmd)
        cmd = "touch "+SUBFOLDER+path
        os.system(cmd)
        
        f= open(SUBFOLDER+path,"w+")
        f.write(htmlx)


# In[141]:


#get most recent 9 articles and get their "keys"

def form_about(target_language):
 
    html = open(SUBFOLDER + "jp-about.temp").read()

    html = re.sub(r"\$\$home%%",           elements_dictionary["homepage-"+target_language],           html)
    html = re.sub(r"\$\$archive%%",        elements_dictionary["archive-"+target_language],            html)
    html = re.sub(r"\$\$about%%",          elements_dictionary["about us-"+target_language],           html)
    html = re.sub(r"\$\$jp-translation%%", elements_dictionary["journal pacifique-"+target_language],  html)
    
    #save these to elements dictionary
    html = re.sub(r"\$\$about-text%%",  elements_dictionary["abouttext-"+target_language],    html)
    
    html = re.sub(r"\$\$target-language%%",target_language,  html)
    
    return html


def refresh_abouts():
    for language in languages:

        htmlx = form_about(language)
        path  = language +"/about.html"
        
        import os
        cmd = "mkdir -p "+SUBFOLDER+language
        os.system(cmd)
        cmd = "touch "+SUBFOLDER+path
        os.system(cmd)
        
        f= open(SUBFOLDER+path,"w+")
        f.write(htmlx)


# In[ ]:





# In[146]:


refresh_archives()


# In[143]:


refresh_abouts()


# In[147]:


refresh_indices()


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




