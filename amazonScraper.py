import csv
import requests
from pathlib import Path
from bs4 import BeautifulSoup

def getASINlinks(soup):
	asin = []
	listing = soup.find("ul", {"id": "s-results-list-atf"})
	for item in listing.findAll("li"):
		_item = []
		_item.append(item.get("data-asin"))
		link = item.find("a", {"class": "s-access-detail-page"})
		_item.append(link.get("href"))
		asin.append(_item)
	return asin

def getProductInfo(asinList):
	asin = asinList[0]
	url = asinList[1]
	html = requests.get(url)
	soup = BeautifulSoup(html.text, "html.parser")
	data = {}
	data["asin"] = asin
	data["url"] = url
	
	try:
		data["title"] = soup.find("span", {"id": "productTitle"}).get_text().strip()
	except AttributeError:
		data["title"] = "None"
	try:
		data["edition"] = soup.find("span", {"id": "bookEdition"}).get_text().strip()
	except AttributeError:
		data["edition"] = "None"
	try:
		author = []
		_author = soup.find_all("a", {"class": "contributorNameID"})
		[author.append(a.get_text().strip()) for a in _author]
		author = "&".join(author)
		data["author"] = author
	except AttributeError:
		data["author"] = "None"
	try:
		data["rating"] = soup.find("span", {"id": "acrPopover"}).get("title").strip()
	except AttributeError:
		data["rating"] = "None"
	try:
		_price_rent = soup.find("div", {"id": "rentOfferAccordionRow"})
		price_rent = _price_rent.find("span", {"class": "header-price"}).get_text().strip()
		data["price_rent"] = price_rent
	except AttributeError:
		data["price_rent"] = "None"
	try:
		_price_used = soup.find("div", {"id": "usedOfferAccordionRow"})
		price_used = _price_used.find("span", {"class": "header-price"}).get_text().strip()
		data["price_used"] = price_used
	except AttributeError:
		data["price_used"] = "None"
	try:
		_price_new = soup.find("div", {"id": "newOfferAccordionRow"})
		price_new = _price_new.find("span", {"class": "header-price"}).get_text().strip()
		data["price_new"] = price_new
	except AttributeError:
		data["price_new"] = "None"
	try:
		data["availability"] = soup.find("div", {"id": "availability"}).get_text().strip()
	except AttributeError:
		data["availability"] = "None"
	return data

def save(asin, productInfo):
	filename = "ComputerScienceBooks.csv"
	path = Path(filename)
	with open(filename, "a", newline = "") as f:
		fieldnames = productInfo.keys()
		writer = csv.DictWriter(f, fieldnames = fieldnames)
		if not path.is_file():
			writer.writeheader()
			writer.writerow(fieldnames)
		writer.writerow(productInfo)

def scrape(url):
	try:
		html = requests.get(url)
		soup = BeautifulSoup(html.text, "html.parser")
		title = soup.title
		print(title)
		
		print("ASIN list generating...")
		asinList = getASINlinks(soup)
		
		productInfo = {}
		for data in asinList:
			print("Getting product info of %s..." %str(data[0]))
			productInfo[data[0]] = getProductInfo(data)
			print("Gathered product info")
			print("Saving to CSV...")
			save(data[0], productInfo[data[0]])
			print("Saved")
	except:
		print("Error loading page")
		exit()
def main():
	pageNum = 1
	while True:
		print("Page %d" %pageNum)
		url = "https://www.amazon.com/s/ref=sr_pg_2?fst=p90x%3A1&rh=i%3Aaps%2Ck%3Acomputer+science+books&page=" + str(pageNum) + "&keywords=computer+science+books&ie=UTF8&qid=1536598814"
		scrape(url)
		pageNum += 1

if __name__ == "__main__":
	main()