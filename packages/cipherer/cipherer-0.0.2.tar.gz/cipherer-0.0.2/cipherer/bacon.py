from string import ascii_lowercase
import re
alphabet = list(ascii_lowercase)

def letter_to_binary(letter):
  return bin(alphabet.index(letter))[2:].zfill(5)

def binary_to_abs(binary, a="a", b="b"):
  out = re.sub("1", b, binary)
  out = re.sub("0", a, out)
  return out

def encrypt_letter(letter, a="a", b="b"):
  return binary_to_abs(letter_to_binary(letter), a, b)

def encrypt(text, a='a', b='b'):
  output = ""
  for char in text:
      if char in alphabet:
          output += encrypt_letter(char, a, b)
      else:
          output += char
      output += ' '
  return output
    
          