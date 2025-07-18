import re
import threading
from collections import deque
from queue import Queue, Empty
import time

class SentenceDetector:
    """
    Advanced sentence boundary detection for real-time streaming text
    """

    def __init__(self, min_length=15, max_length=200):
        self.min_length = min_length
        self.max_length = max_length

        # Sentence ending patterns
        self.sentence_endings = re.compile(r'[.!?]+\s*')
        self.break_patterns = [
            r'[,;]\s+',  # Comma and semicolon breaks
            r'\s+(?:and|but|or|however|therefore|meanwhile)\s+',  # Conjunctions
            r'\s+[-–—]\s+',  # Dashes
            r'\s+\(.*?\)\s+',  # Parentheses
        ]

        # Compile break patterns
        self.break_regex = [re.compile(pattern) for pattern in self.break_patterns]

        # Buffer for incomplete sentences
        self.buffer = ""
        self.sentence_queue = Queue()

    def add_chunk(self, chunk):
        """Add a text chunk and process for sentence boundaries"""
        self.buffer += chunk
        self._process_buffer()

    def _process_buffer(self):
        """Process the buffer for complete sentences"""
        while self.buffer:
            sentence = self._extract_sentence()
            if sentence:
                self.sentence_queue.put(sentence)
            else:
                break

    def _extract_sentence(self):
        """Extract a complete sentence from the buffer"""
        text = self.buffer.strip()

        if not text:
            return None

        # Check for natural sentence endings
        match = self.sentence_endings.search(text)
        if match and match.start() >= self.min_length:
            sentence = text[:match.end()].strip()
            self.buffer = text[match.end():]
            return sentence

        # Force break for very long sentences
        if len(text) > self.max_length:
            return self._force_break(text)

        return None

    def _force_break(self, text):
        """Force a break in a long sentence at a good location"""
        # Try to find a good break point
        for regex in self.break_regex:
            matches = list(regex.finditer(text[self.min_length:]))
            if matches:
                # Use the first good break point
                break_pos = matches[0].end() + self.min_length
                sentence = text[:break_pos].strip()
                self.buffer = text[break_pos:]
                return sentence

        # Last resort: break at word boundary
        words = text.split()
        if len(words) > 10:
            mid_point = len(words) // 2
            sentence = ' '.join(words[:mid_point])
            self.buffer = ' '.join(words[mid_point:])
            return sentence

        return None

    def get_sentence(self, timeout=0.1):
        """Get a complete sentence from the queue"""
        try:
            return self.sentence_queue.get(timeout=timeout)
        except Empty:
            return None

    def flush(self):
        """Flush remaining buffer content as a sentence"""
        if self.buffer.strip():
            sentence = self.buffer.strip()
            self.buffer = ""
            return sentence
        return None

    def has_sentences(self):
        """Check if there are sentences ready"""
        return not self.sentence_queue.empty()