import sys, os
from bs4 import BeautifulSoup
import urllib3
import urllib
http = urllib3.PoolManager()

video_urls = []

person_ids = {
    'barack_obama': 55625,
    'donald_trump': 20967,
    'hilary_clinton': 19027,
    'bernie_sanders': 994,
    'ted_cruz': 1019953,
    'john_kasich': 1620,
    'mike_pence': 85219,
    'marco_rubio': 87599,
    'carly_fiorina': 82727,
    'bill_clinton': 1651,
    'gary_johnson': 20244,
    'rand_paul': 9265241,
    'ben_carson': 47822,
    'jeb_bush': 4776,
    'mike_huckabee': 24776,
    'chris_christie': 1007174,
    'lindsey_graham': 36782,
    'rick_santorum': 2249,
    'joe_biden': 34
}

def construct_base_url(person_id):
    return "https://www.c-span.org/search/?sdate=12%2F01%2F2015&edate=12%2F01%2F2016&searchtype=Videos&sort=Most+Recent+Airing&text=0&all%5B%5D=campaign&all%5B%5D=2016&personid%5B%5D="+str(person_id)+"&seriesid%5B%5D=91&formatid%5B%5D=55&show100=&sdate=12%2F01%2F2015&edate=12%2F01%2F2016&searchtype=Videos&sort=Most+Recent+Airing&text=0&all%5B%5D=campaign&all%5B%5D=2016&personid%5B%5D="+str(person_id)+"&seriesid%5B%5D=91&formatid%5B%5D=55&ajax&page="

def get_video_urls(person_id):
    base_url = construct_base_url(person_id)
    video_urls = []
    page = 1
    finished = False
    while(not finished):
        print(page)
        url = base_url + str(page)
        #r = urllib.urlopen(url).read()
        r = http.request('GET',url)
        soup = BeautifulSoup(r.data,"html5lib")
        search_results = soup.find_all("li", class_="onevid")
        if len(search_results) == 0:
            finished = True
        else:
            for i in range(len(search_results)):
                video_urls.append('https://' + search_results[i].a["href"].split('//')[1])
        page += 1
    return video_urls

def get_transcript_url(video_url):
    return(video_url + "&action=getTranscript&transcriptType=cc&service-url=%2Fcommon%2Fservices%2FprogramSpeakers.php&progid=459886&appearance-filter=&personSkip=0&ccSkip=0&transcriptSpeaker=&transcriptQuery=#")

def get_row(row):
    timestamp = row.th.text.replace("\n","")
    speaker = row.strong.text
    p = row.p
    if p is None:
        return None
    else:
        text = row.p.text
        return (timestamp,speaker,text)

def get_subjects(url):
    r = http.request('GET',url)
    soup = BeautifulSoup(r.data, "html5lib")
    subjects = soup.find('div',id='subjects').find_all('li')
    subjects = [(s.a['href'].split('person/?')[1], s.a.text) for s in subjects if 'person' in s.a['href']]
    return(subjects)

def get_transcript(video_url):
    subjects = get_subjects(video_url)
    url = get_transcript_url(video_url)
    r = http.request('GET',url)
    soup = BeautifulSoup(r.data, "html5lib")
    rows = soup.find_all('tr')
    row_list = [get_row(row) for row in rows]
    row_list = [r for r in row_list if r is not None]
    return(subjects, row_list)

def save_transcript(filename, url, subjects, t):
    with open(filename,'w') as f:
        f.write(url + '\n')
        f.write(str(subjects) + '\n')
        for row in t:
            f.write(row[0] + '\t' + row[1] + '\t' + row[2] + '\n')

#if __name__ == '__main__':
for person in person_ids.keys():
    print("Processing " + person)
    os.system("mkdir ~/cspan/transcripts/" + person)
    urls = get_video_urls(person_ids[person])
    index = 0
    for url in urls:
        subjects, t = get_transcript(url)
        if len(t) > 0:
            print(url)
            filename = "/home/jrgillick/cspan/transcripts/" + person + "/" + person + "_" + str(index) + ".txt"
            save_transcript(filename, url, subjects, t)
            index += 1




