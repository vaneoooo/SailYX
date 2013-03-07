import urllib2
from bs4 import BeautifulSoup

def qc(seq, idfun=None):
   if idfun is None:
       def idfun(x): return x
   seen = {}
   result = []
   for item in seq:
       marker = idfun(item)
       if marker in seen: continue
       seen[marker] = 1
       result.append(item)
   return result


def moviespider():
    url = 'http://theater.mtime.com/China_Sichuan_Province_Luzhou_XuYongXian/3527/'
    
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page)

    original = soup.find_all(class_='table')
    m_count = len(original)
    movie_list = []
    movie_name = []
    movie_time = []
    movie_price = []
    
    for i in range(0,m_count):
        name_temp = []
        time_temp = []
        price_temp = []
        
        name_temp.append(original[i].find(class_='c_000').text)

        for t in original[i].find_all('strong'):
            time_temp.append(t.text)
        time_temp=qc(time_temp)
        for p in original[i].find_all('em'):
            price_temp.append(p.text)
            
        movie_name.extend(name_temp)
        movie_time.append(time_temp)
        movie_price.append(price_temp)
        
#        for time in qc(m_list.find_all('strong')):
#            movie_time.append(time)
#        for price in m_list.find_all('em'):
#            movie_time.append(price)
    movie_list.append(movie_name)
    movie_list.append(movie_time)
    movie_list.append(movie_price)
    
#    for i in range(0,len(movie_list[0])):
#        print ''.join(movie_list[0][i])
#        print ',    '.join(movie_list[1][i])
#        print ',    '.join(movie_list[2][i])

    return movie_list

    