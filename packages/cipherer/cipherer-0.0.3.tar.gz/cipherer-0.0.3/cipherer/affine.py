from string import ascii_lowercase
alphabet = list(ascii_lowercase)

def letter_to_num(letter):
  a = alphabet.index(letter)
  return a   

def num_to_letter(num):
  return alphabet[num]

def encrypt_letter(letter, a, b):
  letter = letter.lower()
  return num_to_letter((a*letter_to_num(letter)+b) % len(alphabet))


def encrypt(text, a, b):
  output = ""
  for char in text:
    if char in alphabet:
        output += encrypt_letter(char, a, b)
    else:
        output += char
  return output