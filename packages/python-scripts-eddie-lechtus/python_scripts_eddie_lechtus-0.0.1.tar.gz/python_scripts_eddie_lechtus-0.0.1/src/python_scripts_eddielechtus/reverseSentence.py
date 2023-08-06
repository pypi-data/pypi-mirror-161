# Python code to Reverse each word
# of a Sentence individually

# Function to Reverse words
def reverseWordSentence(Sentence):
    # All in One line
    return ' '.join(word[::-1] for word in Sentence.split(" "))


# Driver's Code
Sentence = "Geeks for Geeks"
print(reverseWordSentence(Sentence))