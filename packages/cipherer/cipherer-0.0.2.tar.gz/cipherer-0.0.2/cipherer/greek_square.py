G_square_dict = {
    "A": "11", "B": "12", "C": "13", "D": "14", "E": "15",
    "F": "21", "G": "22", "H": "23", "I": "24", "K": "25",
    "L": "31", "M": "32", "N": "33", "O": "34", "P": "35",
    "Q": "41", "R": "42", "S": "43", "T": "44", "U": "45",
    "V": "51", "W": "52", "X": "53", "Y": "54", "Z": "55"
}
nums_to_letters = {v: k for k, v in G_square_dict.items()}
def encrypt(text):
  a = G_square_dict.keys()
  n = 0
  ntext = ""
  text = text.upper()
  for i in range(0, len(text)):
    if text[n] not in a:
      ntext += text[n] + " "
    else:
      ntext += G_square_dict[text[n]] + " "
    n += 1
  return ntext

def dumb_split(string):
  output = []
  word = ""
  for char in string:
      if char == ' ':
          output.append(word)
          word = ""
      else:
          word += char
  if word != "":
      output.append(word)
  return output

def decrypt(text):
  nums = dumb_split(text.strip())
  output = ""
  for num in nums:
    if num not in nums_to_letters:
        output += num
    else:
        output += nums_to_letters[num]
  return output.title()