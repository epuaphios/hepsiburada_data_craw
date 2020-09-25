import re
import requests
from bs4 import BeautifulSoup as bs
from elasticsearch import Elasticsearch
import json
import shutil
import argparse
import sys

class product_search():

    def __init__(self,*args, **kwargs):
        super(product_search, self).__init__()
        for i in range(1,int(2)):
          self.ul = "https://www.hepsiburada.com/tefal/tavalar-c-22203?filtreler=satici:Hepsiburada&siralama=artanfiyat&sayfa="+ str(i)
          self.padi = self.ul.split("/")
          self.d_adi= self.padi[len(self.padi)-1].split("-")[0]+"_"+self.padi[len(self.padi)-1].split("-")[1]
          self.hb = "http://www.hepsiburada.com"
          self.r = requests.get(self.ul)
          if self.r.status_code == 200:
             self.soap = bs(self.r.text, "html.parser")
             self.get_product_links()
             self.f_json = {}
          else:
             print("Hata: " + str(self.r.url))


    def get_product_links(self):

            sp = self.soap("ul", {'class': re.compile('^product-list results-container')})[0]
            for i in sp("a"):
                ln = i.get("href")
                if ln.startswith("/"):
                    self.hb += ln
                    # print(self.hb)
                    self.get_product_detail(self.hb)
                self.hb = "http://www.hepsiburada.com"


    def get_product_detail(self, lnk):
                r2 = requests.get(lnk)
                if r2.status_code == 200:
                    self.prc = {}
                    self.soap2 = bs(r2.text, "html.parser")
                    self.pName = self.soap2.html.head.title.get_text()

                    pSpec = self.soap2("div", {"id": "tabProductDesc",
                                               "class": "list-item-detail product-detail box-container"})[0]("table")

                    pNewP = self.soap2("span", {"class": "price"})[0]["content"]

                    sy = 0
                    for i in pSpec:
                        for l in i("div", {"id": "productTechSpecContainer"}):
                            self.tech = l.get_text().strip()
                            self.dsctech = self.tech.split("\n")
                            while True:
                                try:
                                    self.dsctech.remove("")
                                except ValueError:
                                    break
                            sy += 1
                    self.stch = {}
                    d = 0
                    while d < len(self.dsctech):
                        if self.dsctech[d] == "Diğer":
                            self.dsctech.remove(self.dsctech[d])
                            # d += 1
                            pass
                        else:
                            self.stch.update({self.dsctech[d]: self.dsctech[d + 1]})
                            d += 2
                    self.f_json = {"dcsTech": self.stch, "pPrice": pNewP ,"link":lnk}
                    res = es.index(index="hepsiburada", body=self.f_json)
                    print(res['result'])


if __name__ == "__main__":
    es = Elasticsearch(['http://192.168.1.82:9200'])
    product_search(sys.argv[1:])
