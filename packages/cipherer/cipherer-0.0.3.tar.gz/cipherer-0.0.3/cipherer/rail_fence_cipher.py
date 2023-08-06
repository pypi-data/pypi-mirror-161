def generate_empty_rails(n):
    rails = []
    for i in range(0, n):
        rails.append([])
    return rails
def generate_rails(message, rails):
    i=0
    increasing_index = True
    for char in message:
        rails[i].append(char)
        if i == len(rails)-1:
            increasing_index = False
        if increasing_index:
            i += 1
        else:
            i -= 1
    return rails
def rail_to_output(rail):
  out = ""
  for object in rail:
    out += object
  return out
def rails_to_output(rails):
  output = ""
  for rail in rails:
    output += rail_to_output(rail) + ' '
  return output
def encrypt(message, n):
    rails = generate_empty_rails(n)
    generate_rails(message, rails)
    return rails_to_output(rails)