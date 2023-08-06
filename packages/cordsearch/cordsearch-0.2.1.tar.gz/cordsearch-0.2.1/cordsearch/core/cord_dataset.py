import numpy as np
import nltk
from tqdm import tqdm
from datasets import load_dataset
from datasets.dataset_dict import DatasetDict
from sentence_transformers import SentenceTransformer


class CordDataset(DatasetDict):
	"""This class loads the Cord19 dataset and contains useful functions for search and comparison.

		Attributes:
			embedding_model: Any sentence-transformers model the user chooses to generate embeddings of the Cord text data.

		Properties:
			train: Use this to access the training split of the loaded data. In the case of Cord19, this is all the data.
			abstracts: Use this to access the available abstracts within the Cord dataset.
			bodytexts: Use this to access the available full texts within the Cord dataset.
	"""
	def __init__(self, embedding_model=SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')):
		super().__init__(load_dataset('cord19', 'fulltext'))
		self.embedding_model = embedding_model
		self._abstract_sentence_embeddings = dict()  # dict of dicts, keyed by [abstract_id][sentence_id]
		self._abstract_embeddings = dict()  # dict, keyed by [abstract_id]
		self._bodytext_sentence_embeddings = dict()  # dict of dicts, keyed by [bodytext_id][sentence_id]
		self._bodytext_embeddings = dict()  # dict, keyed by [bodytext_id]

	@property
	def train(self):
		return self['train']

	@property
	def abstracts(self):
		return self.train['abstract']
	
	@property
	def doi(self):
		return self.train['doi']

	@property
	def bodytexts(self):
		return self.train['fulltext']

	def abstract_sentence(self, abstract_id, sentence_id):
		return nltk.sent_tokenize(self.abstracts[abstract_id])[sentence_id]

	def bodytext_sentence(self, bodytext_id, sentence_id):
		return nltk.sent_tokenize(self.bodytexts[bodytext_id])[sentence_id]

	def parse_abstract(self, abstract_id):
		return nltk.sent_tokenize(self.abstracts[abstract_id])

	def parse_bodytext(self, bodytext_id):
		return nltk.sent_tokenize(self.bodytexts[bodytext_id])

	def num_abstract_sentences(self, abstract_id):
		return len(self.parse_abstract(abstract_id))

	def num_bodytext_sentences(self, bodytext_id):
		return len(self.parse_bodytext(bodytext_id))

	def abstract_sentence_embeddings(self, abstract_id, sentence_id):
		if abstract_id not in self._abstract_sentence_embeddings.keys():
				self._abstract_sentence_embeddings[abstract_id] = dict()

		if sentence_id not in self._abstract_sentence_embeddings[abstract_id].keys():
				sentence = self.abstract_sentence(abstract_id, sentence_id)
				self._abstract_sentence_embeddings[abstract_id][sentence_id] = self.embedding_model.encode(sentences=sentence)

		return self._abstract_sentence_embeddings[abstract_id][sentence_id]

	def bodytext_sentence_embeddings(self, bodytext_id, sentence_id):
		if bodytext_id not in self._bodytext_sentence_embeddings.keys():
			self._bodytext_sentence_embeddings[bodytext_id] = dict()

		if sentence_id not in self._bodytext_sentence_embeddings[bodytext_id].keys():
			sentence = self.bodytext_sentence(bodytext_id,sentence_id)
			self._bodytext_sentence_embeddings[bodytext_id][sentence_id] = self.embedding_model.encode(sentences=sentence)

		return self._bodytext_sentence_embeddings[bodytext_id][sentence_id]

	def abstract_embeddings(self, abstract_id):
		if abstract_id not in self._abstract_embeddings.keys():
			abstract = self.abstracts[abstract_id]
			self._abstract_embeddings[id] = self.embedding_model.encode(sentences=abstract)
		return self._abstract_embeddings[id]

	def bodytext_embeddings(self, bodytext_id):
		if bodytext_id not in self._bodytext_embeddings.keys():
			bodytext = self.bodytexts[bodytext_id]
			self._bodytext_embeddings[id] = self.embedding_model.encode(sentences=bodytext)
		return self._bodytext_embeddings[id]

	def compute_similarity(self, embedding1, embedding2):
		return np.dot(embedding1, embedding2)

	def paper_locator(self, DOI=str):
		"""Use this function to determine if a research paper is in the CORD-19 dataset.

		This function searches for the specified doi in the CORD metadata. If there is a match, the function returns True
		and displays the index at which the paper occurs in the metadata. This index can then be used for other CordSearch functions.
		If there is not a match, the function returns False because the paper is not in CORD-19. For example:
				
				paper_locator('10.1186/cc987')

		Args:
			DOI: A string containing the doi of the given paper

		Returns:
			A boolean indicating whether the paper was located in the CORD-19 dataset. If True, the index at which it was found
			is also returned.
		
		Raises:
		"""
		if DOI in self.doi:
			return True, self.doi.index(DOI) 
		else:
			return False, "This paper is not in CORD-19"
		


	def quick_find_similar_sentences(self, abstract_id: int, sentence_id: int, top_k: int = 1):
		"""Use this function to find sentences within Cord abstracts that are similar to the designated sentence.

		This function uses cosine similarity to find similar sentences across the abstracts contained in the Cord19
		dataset. By specifying a sentence with the id of the abstract it is contained in and the id of its position in
		the abstract, the most similar sentences will be ordered and displayed. This output is a list of dictionaries,
		wherein each dictionary corresponds to one sentence comparison. For example, if an interesting result is located
		at the 3rd sentence of the 3rd abstract and you would like the 2 most similar sentences to this result type:

			quick_find_similar_sentences(2,2,2).

		Args:
			abstract_id: Index for a given abstract.
			sentence_id: Index for a given sentence in the selected abstract.
			top_k: An integer indicating the number of most similar sentences you would like displayed in the output.

		Returns:
			A list of dictionaries containing the relevant information of the most similar sentences found. These
			dictionaries are sorted from highest to lowest similarity score, and contain the abstract_id, sentence_id,
			and similarity score of the sentence compared to. For example:

				[{'abstract_id': 2, 'sentence_id': 0, 'similarity': 0.632745}].

		Raises:
			IndexError: list index out of range.
		"""
		sentence_embedding = self.abstract_sentence_embeddings(abstract_id, sentence_id)
		matches = list()
		for abs_id in tqdm(range(len(self.abstracts))):  
			for sent_id in range(self.num_abstract_sentences(abs_id)):
				if abstract_id == abs_id and sentence_id == sent_id:
					continue

				sim = self.compute_similarity(sentence_embedding, self.abstract_sentence_embeddings(abs_id, sent_id))
				matches.append({'abstract_id': abs_id, 'sentence_id': sent_id, 'similarity': sim})
				sorted_matches = sorted(matches, key=lambda key_value: key_value['similarity'], reverse=True)[:top_k]
		return sorted_matches

	def find_similar_sentences(self, bodytext_id: int, sentence_id: int, top_k: int=1):
		"""Use this function to find sentences within Cord fulltexts that are similar to the designated sentence.

		This function uses cosine similarity to find similar sentences across the fulltexts contained in the Cord19 dataset.
		By specifying a sentence with the id of the fulltext it is contained in and the id of its position in the fulltext,
		the most similar sentences will be ordered and displayed. This output is a list of dictionaries, wherein each dictionary
		corresponds to one sentence comparison. For example, if an interesting result is located at the 3rd sentence of the 3rd fulltext
		and you would like the 2 most similar sentences to this result type: find_similar_sentences(2,2,2).

		Args:
			bodytext_id: An integer indicating the index at which the fulltext is located in the list of fulltexts 'self.fulltext'.
			sentence_id: An integer indicating the index at which the sentence is located in the list of sentences parsed from the designated abstract.
			top_k: An integer indicating the number of most similar sentences you would like displayed in the output.

		Returns:
			A list of dictionaries containing the relevant information of the most similar sentences found. These dictionaries are sorted from highest to
			lowest similarity score, and contain the abstract_id, sentence_id, and similarity score of the sentence compared to. For example:

			[{'bodytext_id': 1, 'sentence_id': 5, 'similarity': 0.433562}]

		Raises:
			IndexError: list index out of range.
		"""
		sentence_embedding = self.bodytext_sentence_embeddings(bodytext_id, sentence_id)
		matches = list()
		for bod_id in tqdm(range(len(self.bodytexts))):
			for sent_id in range(self.num_bodytext_sentences(bod_id)):
				if bodytext_id == bod_id and sentence_id == sent_id:
					continue

				sim = self.compute_similarity(sentence_embedding, self.bodytext_sentence_embeddings(bod_id, sent_id))
				matches.append({'bodytext_id': bod_id, 'sentence_id': sent_id, 'similarity': sim})
				sorted_matches = sorted(matches, key=lambda key_value: key_value['similarity'], reverse=True)[:top_k]
		return sorted_matches

	def find_similar_abstracts(self, abstract_id: int, top_k=1):
		"""Use this function to find abstracts within the Cord19 dataset that are similar to the designated abstract.

		This function uses cosine similarity to find similar abstracts across the abstracts contained in the Cord19 dataset.
		By specifying an abstract with its id, the most similar abstracts in the dataset will be displayed. This output is
		a list of dictionaries, wherein each dictionary corresponds to one abstract comparison. For example, if you are interested
		in finding the 2 most similar abstracts to the 8th abstract type: find_similar_abstracts(7,2).

		Args:
			abstract_id: An integer indicating the index at which the abstract is located in the list of abstracts 'self.abstract'.
			top_k: An integer indicating the number of most similar abstracts you would like displayed in the output.

		Returns:
			A list of dictionaries containing the relevant information of the most similar abstracts found. These dictionaries are sorted
			from highest to lowerst similarity score, and contain the abstract_id and similarity score of the abstract compared to.

				For example: [{'abstract_id': 3, 'similarity': 0.392417}].

		Raises:
			IndexError: list index out of range.
		"""
		abstract_embedding = self.abstract_embeddings(abstract_id)

		matches = list()
		for abs_id in tqdm(range(len(self.abstracts))):
			if abstract_id == abs_id:
				continue
			sim = self.compute_similarity(abstract_embedding, self.abstract_embeddings(abs_id))
			matches.append({'abstract_id': abs_id, 'similarity': sim})
			sorted_matches = sorted(matches, key=lambda key_value: key_value['similarity'], reverse=True)[:top_k]

		return sorted_matches

	def find_similar_papers(self, bodytext_id: int, top_k=1):
		"""Use this function to find fulltexts within the Cord19 dataset that are similar to the designated fulltext.

		This function uses cosine similarity to find similar fulltexts across the fulltexts contained in the Cord19 dataset.
		By specifying a fulltext with its id, the most similar fulltexts in the dataset will be displayed. This output is a
		list of dictionaries, wherein each dictionary corresponds to one fulltext comparison. For example, if you are interested
		in finding the 2 most similar fulltexts to the 8th fulltext type: find_similar_papers(7,2).

		Args:
			bodytext_id: An integer indicating the index at which the fulltext is located in the list of fulltexts 'self.fulltext'.
			top_k: An integer indicating the number of most similar fulltexts you would like displayed in the output.

		Returns:
			A list of dictionaries containing the relevant information of the most similar fulltexts found. These dictionaries are sorted
			from highest to lowest similarity score, and contain the bodytext_id and similarity score of the fulltext compared to.

				For example: [{'bodytext_id': 5, 'similarity': 0.454932}]

		Raises:
			IndexError: list index out of range.
		"""
		bodytext_embedding = self.bodytext_embeddings(bodytext_id)

		matches = list()
		for bod_id in tqdm(range(len(self.bodytexts))):
			if bodytext_id == bod_id:
				continue
			sim = self.compute_similarity(bodytext_embedding, self.bodytext_embeddings(bod_id))
			matches.append({'bodytext_id': bod_id, 'similarity': sim})
			sorted_matches = sorted(matches, key=lambda key_value: key_value['similarity'], reverse=True)[:top_k]

		return sorted_matches
