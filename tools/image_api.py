import os
from typing import List
import requests

from config import settings


class ImageTool:
	def __init__(self):
		# Pick provider based on available keys
		self.provider = None
		self.unsplash_key = settings.UNSPLASH_API_KEY
		self.pexels_key = settings.PEXELS_API_KEY

		if self.unsplash_key:
			self.provider = "unsplash"
			self.base_url = "https://api.unsplash.com"
		elif self.pexels_key:
			self.provider = "pexels"
			self.base_url = "https://api.pexels.com"
		else:
			raise ValueError(
				"No image API key found. Set UNSPLASH_API_KEY or PEXELS_API_KEY in .env"
			)

	def search_images(self, query: str, limit: int = 10) -> List[str]:
		try:
			limit = max(1, min(limit, 15))
			if self.provider == "unsplash":
				return self._search_unsplash(query, limit)
			else:
				return self._search_pexels(query, limit)
		except Exception as e:
			print(f"Image search error: {e}")
			return []

	def _search_unsplash(self, query: str, limit: int) -> List[str]:
		url = f"{self.base_url}/search/photos"
		params = {
			"query": query,
			"per_page": limit,
			"orientation": "landscape",
			"order_by": "relevant",
		}
		headers = {"Authorization": f"Client-ID {self.unsplash_key}"}
		r = requests.get(url, params=params, headers=headers, timeout=10)
		r.raise_for_status()
		data = r.json()

		urls: List[str] = []
		for item in data.get("results", []):
			width = item.get("width")
			height = item.get("height")
			# prefer landscape and reasonable size
			if isinstance(width, int) and isinstance(height, int) and width <= height:
				continue
			u = item.get("urls", {})
			url_choice = u.get("regular") or u.get("full") or u.get("small")
			if url_choice:
				urls.append(url_choice)
		return urls

	def _search_pexels(self, query: str, limit: int) -> List[str]:
		url = f"{self.base_url}/v1/search"
		params = {
			"query": query,
			"per_page": limit,
			"orientation": "landscape",
		}
		headers = {"Authorization": self.pexels_key}
		r = requests.get(url, params=params, headers=headers, timeout=10)
		r.raise_for_status()
		data = r.json()

		urls: List[str] = []
		for item in data.get("photos", []):
			src = item.get("src", {})
			# prefer landscape rendition; fallback to large
			url_choice = src.get("landscape") or src.get("large") or src.get("original")
			if url_choice:
				urls.append(url_choice)
		return urls

