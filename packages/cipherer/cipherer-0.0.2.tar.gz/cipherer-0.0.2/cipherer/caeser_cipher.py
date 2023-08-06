def encrypt(text, rot_num):
  import string
  a = list(string.ascii_lowercase)
  def shift_1(letter):
    a2 = list(string.ascii_lowercase)
    if letter in a:
      find = a2.index(letter)
      if find != 25:
        a3 = a2[find + 1]
      else:
        find = 0
        a3 = a2[find]
    else:
      a3 = letter
    return a3
  def shift_n(text, rot_num):
    for i in range(0, int(rot_num)):
      text = shift_1(text)
    return text
  n = 0
  f = ""
  text = text.lower()
  for i in range(0, len(text)):
    if n != len(text) - 1:
      ab = shift_n(text[n], rot_num)
      f = f + ab
      n += 1
    else:
      ab = shift_n(text[len(text) - 1], rot_num)
      f = f + ab
      text = f
  return text
def decrypt(text):
  def ccans(text, rot_num):
    return "Rot " + str(rot_num) + ":" + str(encrypt(text, 26 - rot_num))
  n = 0
  for i in range(0, 26):
    print(ccans(text, n))
    n += 1