#!/usr/bin/env python
# coding: utf-8

# "scientific turk" web bot
# parses sources for new articles, translates them into target languages ["es","pt","pl","zh-CN" ...]. 
# Wraps it up in a simple html document and writes it out to the appropriate directory.

import pickle
import re
import time
import re
from deep_translator import GoogleTranslator
from datetime import date
from googletrans import Translator
from urllib.request import Request, urlopen
from random import randrange

get_ipython().system('pip install googletrans')
get_ipython().system('pip install mechanize')
get_ipython().system('pip3 install -U deep-translator')


def translate_adaptor(text, source, target):
    translator = GoogleTranslator(source=source, target=target)
    return translator.translate(text, src=source, dest=target)

hoy  = date.today()
d1   = hoy.strftime("%d/%m/%Y")

translator = Translator()

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def string_strip(s):
    return re.sub(r"[^A-Za-z0-9]", "-", s)


def sciencedaily_parse_article(url):
  
    html_string = ""

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
        imgaddr  = '/img/dummy'+repr(randrange(20))+'.jpeg'
  
    # get the img alt
  
    imgalt   = find_between(html_string, '<div class="photo-caption">','</div>')
    cred     = '\t'+find_between(html_string, '<div class="photo-credit"><em>','</div>')
  
    # get the citation
    citation = find_between(html_string, '<div role="tabpanel" class="tab-pane active" id="citation_mla">','</div>')
  
    
    # get the article itself
    html_string = re.sub(r"<!-- BEGIN mobile-middle-rectangle -->.*?<!-- END mobile-middle-rectangle -->", "", html_string, flags=re.S)

    assert "<!-- BEGIN mobile-middle-rectangle -->" not in html_string

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
  
    import html
    article   = html.unescape(article)
      
            #y                    #y                                #y                                                       #y                  
    return {"headline": headline, "meta": meta, "imgaddr": imgaddr, "imgalt": imgalt, "imgcredit":cred,"citation": citation, "article": article, "href": href_tab}
  

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
            
    big_translated_string = translate_adaptor(big_string, source='en', target=target_language)
    
    # a manual fix
    big_translated_string = big_translated_string.replace('(#@)', token_out)
    translations_array    = big_translated_string.split(token_out)
    
    for i in range (4):
        translations[keys[i]]=translations_array[i]
    translations["imgaddr"]=article_dictionary["imgaddr"]
    translations["citation"]=article_dictionary["citation"]
    translations["imgcredit"]=article_dictionary["imgcredit"]
    translations["href"]=article_dictionary["href"]
    translations["org-headline"]=article_dictionary["headline"]
    translations["lang"]=target_language    

    return translations

# deprecated
def get_language_dictionary(target_language):
    ld = {}
    words = ["scientific turk", "homepage", "archive", "about us", "source:"]
    for word in words:
        print(word)
        ld[word] = translate_adaptor(word, source='en', target=target_language)
    return ld

slogans = [
    "Wissenschaft für alle, überall.",
    "科学无处不在，无处不在。",
    "Ciencia para todos, en todas partes.",
]

def html_from_dictionary(translated_dictionary, target_language, language_dictionary): # translated & language could be just one dictionary this was stupid.
  
    from datetime import date
    hoy  = date.today()
    d1   = hoy.strftime("%d/%m/%Y")
  
    html = open(SUBFOLDER + "templates/details.html").read()

    article_text = re.sub(r"\n\n", "</p>\n\n<p>",   translated_dictionary["article"])
    html_article = "<p>" + article_text + "</p>"

    print(translated_dictionary["headline"])
  
    html = re.sub(r"\$\$article-title%%",  translated_dictionary["headline"],         html)
    html = re.sub(r"\$\$img-alt%%",        translated_dictionary["imgalt"],           html)
    html = re.sub(r"\$\$article-meta%%",   translated_dictionary["meta"],             html)
    
    html = re.sub(r"\$\$meta-tag-text%%",  article_text[:150],                        html)
    
    html = re.sub(r"\$\$source%%",         translated_dictionary["citation"],         html)
    html = re.sub(r"\$\$img.jpg%%",        translated_dictionary["imgaddr"],          html)
    html = re.sub(r"\$\$article-text%%",   html_article                  ,            html)
  
    html = re.sub(r"\$\$home%%",           language_dictionary["homepage-"+target_language],           html)
    html = re.sub(r"\$\$archive%%",        language_dictionary["archive-"+target_language],            html)
    html = re.sub(r"\$\$about%%",          language_dictionary["about us-"+target_language],           html)
    html = re.sub(r"\$\$jp-translation%%", language_dictionary["scientific turk-"+target_language],  html)
    html = re.sub(r"\$\$taken-from%%",     language_dictionary["source:-"+target_language],            html)
    
    html = re.sub(r"\$\$author-name%%",    language_dictionary["author-name-"+target_language],          html)
    html = re.sub(r"\$\$author-img-url%%",    language_dictionary["author-img-"+target_language],        html)
    html = re.sub(r"\$\$author-description%%",    language_dictionary["author-desc-"+target_language],   html)
    
    
    html = re.sub(r"\$\$slogan1%%",       slogans[0],    html)
    html = re.sub(r"\$\$slogan2%%",       slogans[1],    html)
    html = re.sub(r"\$\$slogan3%%",       slogans[2],    html)
    
    
    html = re.sub(r"\$\$homepage-text%%",  elements_dictionary["hometext-"+target_language],    html)
    
    html = re.sub(r"\$\$target-language%%",     target_language,            html)
  
    html = re.sub(r"\$\$imgcredit%%",       translated_dictionary["imgcredit"],          html)
  
    html = re.sub(r"\$\$href%%",           translated_dictionary["href"],            html)
  
    html = re.sub(r"-- ", ",",  html)
 
    html = re.sub(r"\$\$date%%", d1, html)
    
    return html
  

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

SUBFOLDER = ""


def save_obj(obj, name ):
    with open(SUBFOLDER+'obj/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name ):
    with open(SUBFOLDER+'obj/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)

def dic_to_dirfile(dic,target_language, elements_dictionary):

    if target_language == 'en':
        print("Skip english")
        return
    
    #we used to translate all elements at every step, now it is automated due to
    #google translate's quota restrictions.
    
    tr_di = get_translation(dic,target_language)

    htmlx = html_from_dictionary(tr_di, target_language, elements_dictionary)
  
    newdirs = getnewpath(tr_di)
  
    import os
    cmd = "mkdir -p "+SUBFOLDER+newdirs[1]
    os.system(cmd)
  
    f= open(SUBFOLDER+newdirs[0],"w+")
    f.write(htmlx)

    return [htmlx,tr_di,newdirs[2],newdirs[0]]

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

elements_dictionary = {
    "scientific turk-es":"ciencia para todxs", 
    "scientific turk-pt":"ciência para todos", 
    "scientific turk-tr":"herkes için bilim", 
    "scientific turk-zh-CN":"科学为每个人", 
    "scientific turk-pl":"spokojna gazeta", 
    "scientific turk-de":"friedliche Zeitung", 
    "scientific turk-af":"vreedsame koerant",
    
    "homepage-es":"página principal", 
    "homepage-pt":"pagina inicial", 
    "homepage-tr":"anasayfa",
    "homepage-pl":"strona główna", 
    "homepage-de":"Startseite", 
    "homepage-zh-CN":"主页", 
    "homepage-af":"tuisblad", 
    
    "archive-es":"archivo",
    "archive-pt":"arquivo",
    "archive-tr":"arşiv",
    "archive-zh-CN":"档案",
    "archive-pl":"archiwum",
    "archive-de":"Archiv",
    "archive-af":"argief",
    
    
    "about us-es":"sobre nosotros",
    "about us-pt":"sobre nós",
    "about us-tr":"hakkında",
    "about us-zh-CN":"关于我们",
    "about us-pl":"o nas",
    "about us-de":"Über uns",
    "about us-af":"oor ons",
    
    "source:-es":"fuente:",
    "source:-pt":"fonte:",
    "source:-tr":"kaynakça:",
    "source:-zh-CN":"资源",
    "source:-pl":"źródło",
    "source:-de":"Quelle:",
    "source:-af":"bron:",
    
    "latest-articles-es":"Últimos artículos",
    "latest-articles-pt":"Artigos Mais Recentes",
    "latest-articles-pl":"Ostatnie artykuły",
    "latest-articles-zh-CN":"最新的文章",
    "latest-articles-tr":"En yeni makaleler",
    "latest-articles-de":"Neueste Artikel",
    "latest-articles-af":"Mees onlangse artikels",
    
    "hometext-es":"Bienvenido a Scientific Turk. Le proporcionamos los últimos artículos sobre ciencia y tecnología. Scientific Turk se dedica a la distribución de investigaciones científicas populares en otros idiomas además del inglés.",
    "hometext-pt":"Bem-vindo ao Scientific Turk. Fornecemos os artigos mais recentes sobre ciência e tecnologia. O Scientific Turk é dedicado à distribuição de pesquisas científicas populares em outros idiomas que não o inglês.",
    "hometext-pl":"Witamy w Scientific Turk. Zapewniamy najnowsze artykuły na temat nauki i technologii. Czasopismo Pacifique poświęcone jest rozpowszechnianiu popularnych badań naukowych w językach innych niż angielski.",
    "hometext-zh-CN":"欢迎来到Scientific Turk。 我们为您提供有关科学和技术的最新文章。 Scientific Turk致力于以英语以外的语言分发流行的科学研究。",
    "hometext-tr":"Scientific Turk'e hoş geldiniz. Bilim ve teknoloji ile ilgili en son makaleleri size sunuyoruz. Scientific Turk, popüler bilimsel araştırmaların İngilizce dışındaki dillerde dağıtımına adanmıştır.",
    "hometext-de":"Willkommen im Scientific Turk. Wir präsentieren Ihnen die neuesten Artikel über Wissenschaft und Technologie. Das Scientific Turk widmet sich der Verbreitung populärwissenschaftlicher Forschung in anderen Sprachen als Englisch.",
    "hometext-af":"Welkom by die Scientific Turk. Ons bied die nuutste artikels oor wetenskap en tegnologie aan. Die Scientific Turk is toegewy aan die verspreiding van populêre wetenskaplike navorsing in ander tale as Engels.",
    
    "abouttext-es":"Scientific Turk se estableció para evitar que la barrera del idioma obstruya la accesibilidad de los artículos científicos. En Scientific Turk pensamos que todos los artículos científicos deberían ser fácilmente accesibles para las personas en su propio idioma. Por lo tanto, hemos asumido la responsabilidad de encontrar artículos en Internet de valor decente y traducirlos a tantos idiomas como sea posible, haciéndolos accesibles a muchas más personas de lo que era posible en su idioma original.",
    "abouttext-pt":"O Scientific Turk foi criado para impedir que a barreira do idioma obstrua a acessibilidade de artigos científicos. No Scientific Turk, pensamos que todos os artigos científicos devem ser facilmente acessíveis às pessoas em seu próprio idioma. Portanto, assumimos a responsabilidade de encontrar artigos na Internet de valor decente e traduzi-los para o maior número possível de idiomas, tornando-os acessíveis a muito mais pessoas do que era possível em seu idioma original.",
    "abouttext-pl":"Scientific Turk został utworzony, aby bariera językowa nie utrudniała dostępu do artykułów naukowych. W Scientific Turk uważamy, że wszystkie artykuły naukowe powinny być łatwo dostępne dla ludzi w ich własnym języku. Dlatego podjęliśmy się odpowiedzialności za znalezienie artykułów w Internecie o przyzwoitej wartości i przetłumaczenie ich na jak najwięcej języków, dzięki czemu będą dostępne dla większej liczby osób niż było to możliwe w ich oryginalnym języku.",
    "abouttext-zh-CN":"Scientific Turk的建立是为了防止语言障碍阻碍科学文章的可访问性。 Scientific Turk认为我们所有的科学文章都应该易于人们以自己的语言阅读。 因此，我们承担了在互联网上查找具有体面价值的文章并将其翻译成尽可能多的语言的责任，从而使更多的人可以使用原始语言。",
    "abouttext-tr":"",
    "abouttext-de":"Das Scientific Turk wurde gegründet, um zu verhindern, dass die Sprachbarriere die Zugänglichkeit wissenschaftlicher Artikel behindert. Wir bei Scientific Turk glauben, dass alle wissenschaftlichen Artikel für Menschen in ihrer eigenen Sprache leicht zugänglich sein sollten. Aus diesem Grund haben wir die Verantwortung dafür übernommen, Artikel mit angemessenem Wert im Internet zu finden und in so viele Sprachen wie möglich zu übersetzen, um sie für viel mehr Menschen zugänglich zu machen, als dies in ihrer Originalsprache möglich war.",
    "abouttext-af":"Tydskrif Pacifique is gestig om te voorkom dat die taalversperring die toeganklikheid van wetenskaplike artikels belemmer. In Scientific Turk glo ons dat alle wetenskaplike artikels maklik toeganklik moet wees vir mense in hul eie taal. Daarom het ons die verantwoordelikheid aanvaar om artikels met 'n ordentlike waarde op die internet te vind en dit in soveel tale as moontlik te vertaal, sodat dit vir baie meer mense toeganklik is as wat in hul oorspronklike taal moontlik was.",
    
    "see-more-es":"Ver más",
    "see-more-pt":"Ver mais",
    "see-more-pl":"Zobacz więcej",
    "see-more-zh-CN":"看更多",
    "see-more-tr":"Daha fazla",
    "see-more-de":"Mehr sehen",
    "see-more-af":"Sien meer",
    
    "author-name-es":"Edgardo Terrazas",
    "author-name-pt":"Dário Aguiar",
    "author-name-pl":"Julia Wojnicz",
    "author-name-zh-CN":"Adrian Ng",
    "author-name-tr":"Aygün İncesu",
    "author-name-de":"Kai Schulte",
    "author-name-af":"Imka Friedrich",
    
    "author-desc-es":"Traductor español - inglés en Scientific Turk",
    "author-desc-pt":"Tradutora de português - inglês no Scientific Turk",
    "author-desc-pl":"Tłumacz polsko - angielski w Scientific Turk",
    "author-desc-zh-CN":"Scientific Turk的中英文翻译",
    "author-desc-tr":"Scientific Turk'te Türkçe - İngilizce çevirmen",
    "author-desc-de":"Deutsch - Englisch Übersetzer bei Scientific Turk",
    "author-desc-af":"Afrikaans - Engelse vertaler by Scientific Turk",
    
    "author-img-es":"https://avataaars.io/?avatarStyle=Circle&topType=LongHairCurly&accessoriesType=Blank&hairColor=SilverGray&facialHairType=BeardLight&facialHairColor=Brown&clotheType=GraphicShirt&clotheColor=PastelGreen&graphicType=Diamond&eyeType=WinkWacky&eyebrowType=FlatNatural&mouthType=Disbelief&skinColor=Light",
    "author-img-pt":"https://avataaars.io/?avatarStyle=Circle&topType=WinterHat4&accessoriesType=Blank&hatColor=Red&facialHairType=BeardMedium&facialHairColor=Brown&clotheType=ShirtCrewNeck&clotheColor=Heather&eyeType=Surprised&eyebrowType=DefaultNatural&mouthType=Disbelief&skinColor=Light",
    "author-img-pl":"https://avataaars.io/?avatarStyle=Circle&topType=LongHairBun&accessoriesType=Blank&hairColor=BlondeGolden&facialHairType=Blank&clotheType=ShirtScoopNeck&clotheColor=Pink&eyeType=Cry&eyebrowType=UpDownNatural&mouthType=Serious&skinColor=Pale",
    "author-img-zh-CN":"https://avataaars.io/?avatarStyle=Circle&topType=LongHairNotTooLong&accessoriesType=Kurt&hairColor=Black&facialHairType=Blank&clotheType=BlazerSweater&eyeType=Cry&eyebrowType=Default&mouthType=Smile&skinColor=Light",
    "author-img-tr":"https://avataaars.io/?avatarStyle=Circle&topType=ShortHairShaggyMullet&accessoriesType=Prescription02&hairColor=BrownDark&facialHairType=Blank&clotheType=ShirtScoopNeck&clotheColor=White&eyeType=Close&eyebrowType=FlatNatural&mouthType=Default&skinColor=Light",
    "author-img-de":"https://avataaars.io/?avatarStyle=Circle&topType=LongHairStraightStrand&accessoriesType=Sunglasses&hairColor=BlondeGolden&facialHairType=MoustacheFancy&facialHairColor=Brown&clotheType=BlazerSweater&eyeType=Happy&eyebrowType=AngryNatural&mouthType=Twinkle&skinColor=Light",
    "author-img-af":"https://avataaars.io/?avatarStyle=Circle&topType=LongHairStraight2&accessoriesType=Round&hairColor=PastelPink&facialHairType=Blank&clotheType=ShirtVNeck&clotheColor=Gray01&eyeType=Default&eyebrowType=UpDownNatural&mouthType=Disbelief&skinColor=Black",
}

def url_to_dirfile(url,target_language):

    ar_di = sciencedaily_parse_article(url)

    print(url, ": Article Parsed")

    htmlx = dic_to_dirfile(ar_di,target_language, elements_dictionary)
  
    return [htmlx,ar_di]


def get_article_urls_sd():

    main = "https://www.sciencedaily.com"#/news/top/technology/"
    req = Request(main, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    main_html = webpage.decode("utf-8") 
    
    links = []
    
    pattern = r'<a href="(/releases/[0-9]+/[0-9]+/[0-9]+.htm)">(.+?)</a>'
    releases = re.findall(pattern, main_html)

    seen = []
    
    for release_url, headline in releases:
        if release_url in seen:
            continue
        links.append("https://www.sciencedaily.com"+release_url)
        seen.append(release_url)

    return links

articles = get_article_urls_sd()
            
languages = ["es", "pt", "pl", "zh-CN", "de", "af", 'tr']
#languages = ["de", "af"]
articles

#headlinessofar = []
#articlessofar  = {}
#articleurlssofar = []
headlinessofar = load_obj("headlinessofar")
articlessofar = load_obj("articlessofar")
articleurlssofar =load_obj("articleurlssofar")

list(articlessofar.keys())

#refresh already saved articles' html
#for when a design change is implemented.

#for article in articlessofar:
#    tmp = targdic_to_dirfile(articlessofar[article], articlessofar[article]["lang"], elements_dictionary)

test_enable = False

for article in articles:
    if (article not in articleurlssofar) or test_enable:
        dic = sciencedaily_parse_article(article)

        print(dic)
        for target_language in languages:
            try:

                print(">--0--")
                tmp = dic_to_dirfile(dic,target_language, elements_dictionary)

                print(">--1--")
                articlessofar[tmp[2]]=tmp[1]

                print(">--2--")
            except KeyError:
                    print(">--3--")
                    url_to_dirfile(article, target_language)
                    print(">--4--")
            except Exception as e:
                    print("ERROR__________________________________________________", e)
        articleurlssofar.append(article)
        

save_obj(headlinessofar,     "headlinessofar")
save_obj(articlessofar,       "articlessofar")
save_obj(articleurlssofar, "articleurlssofar")

def img_thumb_url(key):
    return re.sub("img/", "img/thumbnails/", articlessofar[key]["imgaddr"])

#get most recent 9 articles and get their "keys"
def form_index(target_language):
  
    homepage_text="welcome my friend we have carpets."
 
    html = open(SUBFOLDER + "templates/index.html").read()
    
    from datetime import date
    hoy  = date.today()
    d1   = hoy.strftime("%d/%m/%Y")
    
    html = re.sub(r"\$\$date%%", d1, html)

    html = re.sub(r"\$\$home%%",           elements_dictionary["homepage-"+target_language],           html)
    html = re.sub(r"\$\$archive%%",        elements_dictionary["archive-"+target_language],            html)
    html = re.sub(r"\$\$about%%",          elements_dictionary["about us-"+target_language],           html)
    html = re.sub(r"\$\$jp-translation%%", elements_dictionary["scientific turk-"+target_language],  html)
    html = re.sub(r"\$\$latest-articles%%",elements_dictionary["latest-articles-"+target_language],    html)
    
    html = re.sub(r"\$\$slogan1%%",       slogans[0],    html)
    html = re.sub(r"\$\$slogan2%%",       slogans[1],    html)
    html = re.sub(r"\$\$slogan3%%",       slogans[2],    html)
    html = re.sub(r"\$\$date%%", d1, html)
    
    #save these to elements dictionary
    html = re.sub(r"\$\$homepage-text%%",  elements_dictionary["hometext-"+target_language],    html)
    
    html = re.sub(r"\$\$see-more%%",  elements_dictionary["see-more-"+target_language],    html)
    
    html = re.sub(r"\$\$target-language%%",target_language,  html)

    asf_sorted = sorted(articlessofar.keys(), key=lambda x: articlessofar[x]['date'], reverse=True)

    asfl = []
    for key in asf_sorted:
        if(articlessofar[key]["lang"]==target_language):
            asfl.append(key)
            
    writenum = min(len(asfl),22)
    
    for i in range (writenum):
        #j = writenum-i-1
        j=i+1
        key = asfl[i]
    
        html = re.sub(r"\$\$article-link"+repr(j)+"%%",   articlessofar[key]["pathfromlang"][1:],           html)
        print(articlessofar[key]["pathfromlang"])
        html = re.sub(r"\$\$headline"+repr(j)+"%%",           articlessofar[key]["headline"],           html)
        if(articlessofar[key]["imgaddr"][:2]!=".."):
            html = re.sub(r"\$\$headline-img"+repr(j)+"%%",      articlessofar[key]["imgaddr"],         html)
        else:
            html = re.sub(r"\$\$headline-img"+repr(j)+"%%",      img_thumb_url(key)[6:],              html)
            
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

#get most recent 9 articles and get their "keys"
def form_archive(target_language):
 
    html = open(SUBFOLDER + "templates/archive.html").read()
    
    html = re.sub(r"\$\$date%%", d1, html)

    html = re.sub(r"\$\$home%%",           elements_dictionary["homepage-"+target_language],           html)
    html = re.sub(r"\$\$archive%%",        elements_dictionary["archive-"+target_language],            html)
    html = re.sub(r"\$\$about%%",          elements_dictionary["about us-"+target_language],           html)
    html = re.sub(r"\$\$jp-translation%%", elements_dictionary["scientific turk-"+target_language],  html)
    html = re.sub(r"\$\$latest-articles%%",elements_dictionary["latest-articles-"+target_language],    html)
    
    html = re.sub(r"\$\$homepage-text%%",  elements_dictionary["hometext-"+target_language],    html)
    
    html = re.sub(r"\$\$slogan1%%",       slogans[0],    html)
    html = re.sub(r"\$\$slogan2%%",       slogans[1],    html)
    html = re.sub(r"\$\$slogan3%%",       slogans[2],    html)
    html = re.sub(r"\$\$date%%", d1, html)
    
    html = re.sub(r"\$\$target-language%%",target_language,  html)

    asf_sorted = sorted(articlessofar.keys(), key=lambda x: articlessofar[x]['date'], reverse=True)

    asfl = []
    for key in asf_sorted:
        if(articlessofar[key]["lang"]==target_language):
            asfl.append(key)
            
    writenum = len(asfl)
    
    archive_text = ""
    
    for i in range (writenum):
        #j = writenum-i-1
        j = i
        key = asfl[j]
        
        link = articlessofar[key]["pathfromlang"][1:]
        titl = articlessofar[key]["headline"]
        date = articlessofar[key]["date"]
        meta = articlessofar[key]["meta"]
        
        article_text = f"<p>{date} <a href=\"{link}\" style=\"font-weight:900;color:chocolate\">{titl}</a>\n<br>\n"
        
        article_text += f"<small style=\"color:gray\">{meta}</small></p>\n<br>\n"
    
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

#get most recent 9 articles and get their "keys"
def form_about(target_language):
 
    html = open(SUBFOLDER + "templates/about.html").read()

    html = re.sub(r"\$\$home%%",           elements_dictionary["homepage-"+target_language],           html)
    html = re.sub(r"\$\$archive%%",        elements_dictionary["archive-"+target_language],            html)
    html = re.sub(r"\$\$about%%",          elements_dictionary["about us-"+target_language],           html)
    html = re.sub(r"\$\$jp-translation%%", elements_dictionary["scientific turk-"+target_language],  html)
    
    html = re.sub(r"\$\$slogan1%%",       slogans[0],    html)
    html = re.sub(r"\$\$slogan2%%",       slogans[1],    html)
    html = re.sub(r"\$\$slogan3%%",       slogans[2],    html)
    html = re.sub(r"\$\$date%%", d1, html)
    
    #save these to elements dictionary
    html = re.sub(r"\$\$about-us%%",  elements_dictionary["about us-"+target_language],    html)
    html = re.sub(r"\$\$about-text%%",  elements_dictionary["abouttext-"+target_language],    html)
    
    html = re.sub(r"\$\$homepage-text%%",  elements_dictionary["hometext-"+target_language],    html)
    
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

refresh_archives()

refresh_abouts()

refresh_indices()

