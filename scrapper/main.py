import sys
import re
import urllib2
from bs4 import BeautifulSoup
from mechanize import Browser
from tabulate import tabulate
import fpdf
import string

'''
   Currently supports:  #star-movies
            #sony-max
            #movies-now
            #romedy-now
            #movies-ok
            #sony-pix
            #hbo
            #filmy
            #star-gold
'''

web_url = "http://tvinfo.in/"
web_url2= "http://tvscheduleindia.com/channel/"
base_url = 'http://www.imdb.com/find?q='

#Method to initialize pdf object
def pdf_save(data_movies,headers):
    pdf = fpdf.FPDF(format='letter')
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Tv Timings !",ln=1, align="C")
    #pdf.cell(200, 10, str(tabulate(data_movies,headers)),0,1, align="l")
    for data in data_movies:
        str1 = "Movie: " + str(data[0]) + "  Time: " + str(data[1])+ "  Rating: " + str(data[2])
        pdf.cell(200, 10, str1,0,1, align="l")
    pdf.output('La-Z-Boy.pdf')

def getBSoup(url):
    req = urllib2.urlopen(url)
    soup = BeautifulSoup(req.read(), "lxml")
    return soup


def search_channel(channel,channel2):
    channel_url = web_url + channel + ".html"
    soup = getBSoup(channel_url)
    time = []
    ratings = []
    title_search = re.compile('/title/tt\d+')

    movie_name = soup.find_all('p', {"class": "title2"})

    channel2_url= web_url2 + channel2
    soup2 = getBSoup(channel2_url)

    for s in soup2.find_all("strong"):
        if s.string:
            s.string.replace_with(s.string.strip())

    movie_name2 = soup2.find_all("strong")

    for i in range(0,len(movie_name2)):
        movie_name2[i]=movie_name2[i].text

    for i in range(0, len(movie_name)):
        movie_name[i] = movie_name[i].text
    #print movie_name

    time1 = soup.find_all('div', {"class": "col-lg-12"})

    for s in soup2.find_all('b',{"class":"from"}):
        if s.string:
            s.string.replace_with(s.string.strip())

    for s in soup2.find_all('b',{"class":"to"}):
        if s.string:
            s.string.replace_with(s.string.strip())

    time2_from = soup2.find_all('b',{"class":"from"})
    time2_to = soup2.find_all('b',{"class":"to"})
    
    for i in range(0,len(time2_from)):
        time2_from[i]=time2_from[i].text

    for i in range(0,len(time2_to)):
        time2_to[i]=time2_to[i].text

    for i in range(1, len(time1)-1, 2):
        time.append(time1[i].text[0:13].strip(''))
    time = [x for x in time if x != '']

    for i in range(0,len(movie_name2)):
        if(movie_name2[i] not in movie_name):
            movie_name.append(movie_name2[i])
            time.append(time2_from[i]+"-"+time2_to[i])

    # time = filter(None, time)

    for i in range(0, len(movie_name)):
        movie_search = '+'.join(movie_name[i].split())
        movie_url = base_url + movie_search + '&s=all'
        br = Browser()
        br.open(movie_url)
        link = br.find_link(url_regex=re.compile(r'/title/tt.*'))
        res = br.follow_link(link)

        soup = BeautifulSoup(res.read(), "lxml")
        movie_title = soup.find('title').contents[0]
        rate = soup.find('span', itemprop='ratingValue')
        if rate is not None:
            ratings.append(str(rate.contents[0]))
        else:
            ratings.append("-")
    headers = ['Movies', 'Time', 'Rating']
    data_movies = []
    for i in range(0, len(movie_name)):
        data_movies.append([str(movie_name[i]), str(time[i]), ratings[i]])
    print tabulate(data_movies, headers=headers)

    #Saving to pdf
    print("Want to save as pdf? Y/N")
    choice = raw_input().lower()
    if choice == 'y':
        pdf_save(data_movies,headers)
        print('Saved!')
    else:
        print('Bye!')

def main():
    if(len(sys.argv) > 2):
        channel = str(sys.argv[1] + "-" + sys.argv[2])
        channel2 = str(sys.argv[1]+ "-" +sys.argv[2])
        channel2 = channel2.title()
    else:
        channel = str(sys.argv[1])
        channel2 = str(sys.argv[1])
        channel2 = channel2.upper()

    movie_rating = search_channel(channel,channel2)

if __name__ == '__main__':
    main()
