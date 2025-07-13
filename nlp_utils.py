import spacy

# Load spaCy NLP model
nlp = spacy.load("en_core_web_sm")

def extract_questions(text):
    """
    Uses spaCy to split text into sentences and return sentences ending with a '?'.
    """
    doc = nlp(text)
    questions = [sent.text.strip() for sent in doc.sents if sent.text.strip().endswith('?')]
    return questions

def is_human_sender(sender_email: str) -> bool:
    """
    Returns True if sender does not appear to be a bot, notification, or newsletter.
    """
    keywords_to_exclude = ["no-reply", "noreply", "newsletter", "slack", "notification", "mailer", "mailbot", "automated"]
    return all(kw not in sender_email.lower() for kw in keywords_to_exclude)
