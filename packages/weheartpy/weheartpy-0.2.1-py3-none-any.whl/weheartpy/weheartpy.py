import requests
from bs4 import BeautifulSoup as bs
from .handler import Error, NoCollectionsFound, NoPostsFound, ConnectionError, NoUsersFound
from .models import Entry, Collection, User


class WeHeartIt():
	'''
	the WeHeartIt class.

	eg. instantiating the class:
	``
	whi = WeHeartIt()
	popular_posts = whi.popular()
	``
	
	'''
	
	def __init__(self) -> None:
		err = requests.get("https://weheartit.com")
		try:
			err.raise_for_status()
		except requests.HTTPError:
			raise ConnectionError(f"The API cannot connect to weheartit.com\nREASON: {err.reason}\nhelp: Try checking your network connection.")
				
		self.status = err.status_code
		self.url = err.url
		
	def popular(self) -> list[Entry]:
		'''
		return a list of ``Entry`` objects of the popular images.
		-
		-
		```
		whi = WeHeartIt()
		entries = whi.popular()
		for entry in entries:
			print(entry.id)
			print(entry.username)
			print(entry.image)
			print(entry.url)
		```
		'''
		res = requests.get("https://weheartit.com")
		res = bs(res.text)
		images = res.find_all('a', {'class': 'entry js-blc js-blc-t-heart btn-heart btn btn-heart-circle js-heart-button'})

		entries = []

		for img in images:
			image = f"https://data.whicdn.com/images/{img['data-entry-id']}/original.jpg"

			entry = Entry(id=int(img['data-entry-id']),
			username=img['data-hearter-username'],
			entry=img['href'],
			image=image)

			entries.append(entry)
			
		if len(entries) == 0:
			raise NoPostsFound('No posts were found. This might be a useragent or a website problem. Are you sure weheartit.com still has a popular images section?\nSOURCE: WeHeartIt.popular | match case "low"\n')
			return
		return entries

	def search_collections(self, query: str) -> list[Collection]:
		'''
		return a list of ``Collection`` objects resulting from the query.

		```
		from weheartpy import WeHeartIt
		whi = WeHeartIt()
		cocs = whi.search_collections("anime pfp")
		for c in cocs:
			print(c.title, c.link)
		```
		'''
		res = requests.get(f"https://weheartit.com/search/collections?query={query}&sort=most_recent")
		
		find = bs(res.text)
		atags = find.find_all('a', {'class':'js-blc js-blc-t-collection collection-name text-overflow-parent'})
		collections = []
		for a in atags:
			link = a['href']
			pop = bs(str(a))
			title = pop.find_all('span', {'class': 'text-primary'})
			title = (title[0]).text
			username = pop.find_all('small')
			username = (((username[0]).text).replace('by @', '')).strip()
			collections.append(Collection(username=username, title=title, link=link))

		if len(collections) == 0:
			raise NoCollectionsFound("the API could not find any collections with that query! Try with something else.")
			return
		return collections

	def search_entries(self, query: str, sort: str=None) -> list[Entry]:
		'''
		returns a list of ``Entry`` objects according to your search query.
		+ params
		+ + sort: `str`: sort the type of entries. Only one option `most_popular`. When left empty the API will go for most recent instead.
		

		```
		whi = WeHeartIt()
		entries = whi.search_entries("mean girls", sort="most_popular")
		for entry in entries:
			print(entry.image, entry.url, entry.username)
		```
		'''
		url = f"https://weheartit.com/search/entries?query={query}" if sort == None else f"https://weheartit.com/search/entries?query={query}&sort=most_popular"
		res = requests.get()
		
		find = bs(res.text, features="lxml")
		
		entries = find.find_all('a', {'class': 'js-entry-detail-link js-blc js-blc-t-entry'})
		usernames = find.find_all('a', {'class': 'entry js-blc js-blc-t-heart btn-heart btn btn-heart-circle js-heart-button'})
		
		rentries = []

		try:
			for e, u in zip(entries, usernames):
				image = "https://weheartit.com/images/" + u['data-entry-id'] + "/original.jpg" 
				id = int(u['data-entry-id'])
				entry = Entry(id=id, title=e['title'], username=u['data-hearter-username'], entry=e['href'], image=image)
				rentries.append(entry)
		except:
			raise NoPostsFound("Could not find any entries related to that search query. Try again with a different one or check your search query."); return

		return rentries

	def search_users(self, query: str) -> list[User]:
		'''
		returns a list of ``User``s according to search query. The number of users is limited to top 40 users thats relevant to your search query. The ``User`` object will return users usernames, names and links to their avatars.

		+ params
		+ + query: `str`: search query that you'd like to search.

		```
		whi = WeHeartIt()
		hearters = whi.search_users("sophie")
		for user in hearters:
			print(user.name, user.username, user.avatar)

		```


		'''
		res = requests.get(f"https://weheartit.com/search/users?query={query}")
		
		find = bs(res.text, features="lxml")
		
		entries = find.find_all('span', {'class': 'text-overflow'})
		
		users = []
		
		for e in entries:
			e = bs(str(e), features="lxml")
			name = (e.find('span', {'class': 'text-big'})).text.strip()
			username = (e.find('small')).text[1:]
			avatar = find.find('img', {'alt': f'{name}', 'class': 'avatar'})
			avatar = avatar['src']
			users.append(User(username=username, name=name, avatar=avatar))

		if len(users) == 0: raise NoUsersFound("weheartpy could not find any users related to that search query. Try again with a different one or check your query.\n"); return

		return users


		

    